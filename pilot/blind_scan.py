"""Blind quarterly scan of declared-vs-observed discrepancy.
For each snapshot date: checkout declaration + tree at that date, define units from the
declaration, mine co-change over the preceding WINDOW months with rename tracking, compute scores.
Declaration-change dates are NOT used for scoring; they are joined only in the final table.
"""
import ast, collections, configparser, datetime as dt, itertools, os, re, subprocess, sys, tarfile, tempfile, io

REPO = sys.argv[1]
START, END = sys.argv[2], sys.argv[3]          # e.g. 2023-01-01 2026-10-01
WINDOW_MONTHS = int(sys.argv[4]) if len(sys.argv) > 4 else 12
DECL_DIR = (sys.argv[5].strip("/") + "/") if len(sys.argv) > 5 and sys.argv[5].strip("/") else ""
BRANCH = "HEAD"

def git(*a, text=True):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=text).stdout

def snapshot_commit(date):
    return git("rev-list", "-1", f"--before={date}T00:00:00", BRANCH).strip()

def read_file(commit, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{commit}:{path}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

# ---------- declaration ----------
DECL_FILES = [DECL_DIR + f for f in [".importlinter", "setup.cfg", "pyproject.toml", "tox.ini"]]
import tomllib
def _ranks(layers_raw, containers):
    ranks = []
    for l in layers_raw:
        sibs = [x.strip().strip("()") for x in l.split("|")]
        full = []
        for x in sibs:
            full += [f"{c}.{x}" for c in containers] if containers else [x]
        ranks.append(full)
    return ranks

def declaration_text(commit):
    for f in DECL_FILES:
        txt = read_file(commit, f)
        if txt and "importlinter" in txt:
            return f, txt
    return None, None

def parse_declaration(commit):
    f, txt = declaration_text(commit)
    if not txt:
        return None
    contracts = []
    if f.endswith("pyproject.toml"):
        try:
            t = tomllib.loads(txt)["tool"]["importlinter"]
        except Exception:
            return None
        for i, c in enumerate(t.get("contracts", [])):
            if c.get("type") != "layers": continue
            cont = c.get("containers") or []
            if isinstance(cont, str): cont = [cont]
            lay = c["layers"] if isinstance(c["layers"], list) else [c["layers"]]
            contracts.append((c.get("name", str(i)), _ranks(lay, cont)))
    else:
        cp = configparser.ConfigParser(strict=False, allow_no_value=True)
        cp.read_string(txt)
        for sec in cp.sections():
            if not sec.startswith("importlinter:contract") or cp.get(sec, "type", fallback="") != "layers":
                continue
            layers_raw = [l.strip() for l in cp.get(sec, "layers").splitlines() if l.strip() and not l.strip().startswith("#")]
            containers = [l.strip() for l in cp.get(sec, "containers", fallback="").splitlines() if l.strip()]
            contracts.append((sec.split(":")[-1], _ranks(layers_raw, containers)))
    return contracts

MOD_PREFIX = {}
def discover_prefixes(commit, mods):
    """Map each module to directory prefixes found in the tree whose path ends with the module path."""
    global MOD_PREFIX
    MOD_PREFIX = {}
    names = git("ls-tree", "-r", "--name-only", commit).splitlines()
    dirs = {n.rsplit("/", 1)[0] for n in names if "/" in n}
    for mod in mods:
        p = mod.replace(".", "/")
        hits = sorted({d for d in dirs if d == p or d.endswith("/" + p)}, key=len)
        hits = [h for h in hits if h.startswith(DECL_DIR)] or hits
        files = sorted({n for n in names if n == p + ".py" or n.endswith("/" + p + ".py")}, key=len)
        MOD_PREFIX[mod] = [h + "/" for h in hits[:2]] + files[:1]

def module_to_pathprefixes(mod):
    if mod in MOD_PREFIX:
        return MOD_PREFIX[mod]
    # unknown module (e.g. import target): try prefixes of known modules
    for known, pres in MOD_PREFIX.items():
        if mod.startswith(known + "."):
            rest = mod[len(known) + 1:].replace(".", "/")
            return [pr + rest + "/" for pr in pres if pr.endswith("/")] + [pr + rest + ".py" for pr in pres if pr.endswith("/")]
    p = mod.replace(".", "/")
    return [DECL_DIR + p + "/", DECL_DIR + "src/" + p + "/", DECL_DIR + p + ".py", DECL_DIR + "src/" + p + ".py"]

# ---------- co-change with rename tracking ----------
def mine(commit, since, until, unit_of):
    log = git("log", f"--since={since}", f"--until={until}", "--no-merges", "--name-status",
              "-M", "--reverse", "--format=---%H", BRANCH if commit is None else commit)
    rename = {}  # old -> new (chain-resolved lazily)
    def resolve(p):
        seen = set()
        while p in rename and p not in seen:
            seen.add(p); p = rename[p]
        return p
    commits = []
    for block in log.split("---")[1:]:
        lines = block.strip().splitlines()
        files = []
        for l in lines[1:]:
            parts = l.split("\t")
            if parts[0].startswith("R") and len(parts) == 3:
                rename[parts[1]] = parts[2]; files.append(parts[2])
            elif len(parts) == 2:
                files.append(parts[1])
        files = [f for f in files if f.endswith(".py") and "migrations/" not in f and "/tests/" not in f and not f.startswith("tests/")
                 and not f.endswith("/__init__.py") and "openedx_core" not in f and "/version" not in f]
        commits.append(files)
    # resolve names forward to the snapshot's naming, then to units
    out = []
    for files in commits:
        units = sorted({u for u in (unit_of(resolve(f)) for f in files) if u})
        if units and len(units) <= 6:
            out.append(units)
    return out

# ---------- static imports at snapshot ----------
ARCHIVE_PATHS = []
def static_imports(commit, unit_of):
    data = subprocess.run(["git", "-C", REPO, "archive", commit, *ARCHIVE_PATHS], capture_output=True).stdout
    tf = tarfile.open(fileobj=io.BytesIO(data))
    edges = collections.Counter()
    for m in tf.getmembers():
        n = m.name
        if not n.endswith(".py") or "migrations/" in n or "/tests/" in n or n.startswith("tests/"):
            continue
        su = unit_of(n)
        if not su:
            continue
        try:
            tree = ast.parse(tf.extractfile(m).read().decode("utf-8", "replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    base = n.rsplit("/", 1)[0].removeprefix(DECL_DIR).replace("/", ".").removeprefix("src.")
                    parts = base.split(".")
                    base = ".".join(parts[: len(parts) - node.level + 1])
                    mods = [base + ("." + node.module if node.module else "")]
                elif node.module:
                    mods = [node.module]
            for mod in mods:
                du = None
                for pp in module_to_pathprefixes(mod):
                    du = unit_of(pp if pp.endswith("/") else pp + "/") or unit_of(pp)
                    if du: break
                if du and du != su:
                    edges[(su, du)] += 1
    return edges

# ---------- scoring ----------
def score_snapshot(date):
    commit = snapshot_commit(date)
    if not commit:
        return None
    contracts = parse_declaration(commit)
    if not contracts:
        return {"date": date, "commit": commit[:7], "note": "no declaration"}
    # units = every declared layer module across contracts; rank per contract
    units, rank_in = {}, {}
    for cid, ranks in contracts:
        depth = len(ranks)
        for r, sibs in enumerate(ranks):
            for mod in sibs:
                units[mod] = mod
                rank_in.setdefault(mod, {})[cid] = (depth - 1 - r) / max(depth - 1, 1)  # 0 = most stable (bottom), 1 = top
    discover_prefixes(commit, list(units))
    # expand units that act as containers of finer-grained units into their immediate sub-packages (to fixpoint)
    global ARCHIVE_PATHS
    ARCHIVE_PATHS = []
    for u in units:
        for pp in MOD_PREFIX.get(u, []):
            if pp.endswith("/"):
                ARCHIVE_PATHS.append(pp.rstrip("/"))
    ARCHIVE_PATHS = sorted(set(ARCHIVE_PATHS)) or ["."]
    tree_paths = [m.name for m in tarfile.open(fileobj=io.BytesIO(subprocess.run(["git","-C",REPO,"archive",commit,*ARCHIVE_PATHS],capture_output=True).stdout)).getmembers()]
    expanded_from, done = {}, set()
    while True:
        todo = [U for U in units if U not in done and any(v != U and v.startswith(U + ".") for v in units)]
        if not todo: break
        for U in todo:
            done.add(U)
            for pp in module_to_pathprefixes(U):
                if not pp.endswith("/"): continue
                subs = {p[len(pp):].split("/")[0] for p in tree_paths if p.startswith(pp) and "/" in p[len(pp):]}
                for sd in subs:
                    if sd.startswith("_") or sd in ("migrations", "tests"): continue
                    cand = f"{U}.{sd}"
                    if cand not in units:
                        units[cand] = cand; expanded_from[cand] = U
    for cand, par in expanded_from.items():
        MOD_PREFIX[cand] = [pr + cand.rsplit(".", 1)[1] + "/" for pr in MOD_PREFIX.get(par, []) if pr.endswith("/")]
    # longest-prefix match so a sub-layer wins over its parent
    ordered = sorted(units, key=len, reverse=True)
    def unit_of(path):
        for mod in ordered:
            for pp in module_to_pathprefixes(mod):
                if path.startswith(pp):
                    return mod
        return None
    since = (dt.date.fromisoformat(date) - dt.timedelta(days=30 * WINDOW_MONTHS)).isoformat()
    commits = mine(commit, since, date, unit_of)
    n = len(commits)
    cnt, pair = collections.Counter(), collections.Counter()
    for us in commits:
        cnt.update(us); pair.update(itertools.combinations(us, 2))
    edges = static_imports(commit, unit_of)

    # S1 hidden coupling: pairs with support>=3, conf>=0.5, no static edge either way
    hidden = []
    for (a, b), s in pair.items():
        conf = s / min(cnt[a], cnt[b])
        if s >= 3 and conf >= 0.5 and not edges.get((a, b)) and not edges.get((b, a)):
            hidden.append((a, b, s, round(conf, 2)))
    # file counts per unit (for size normalisation)
    fcount = collections.Counter(u for u in (unit_of(p) for p in tree_paths if p.endswith(".py") and "migrations/" not in p and "/tests/" not in p) if u)
    disc_n = 0.0
    # S2 stability discordance: Spearman-like between declared stability (0=bottom) and observed change share
    # computed within each contract; report worst contract
    disc = 0.0
    for cid, ranks in contracts:
        mods = [m for sibs in ranks for m in sibs if cnt.get(m, 0) > 0 or True]
        if len(mods) < 3: continue
        decl = [rank_in[m][cid] for m in mods]
        obs = [cnt.get(m, 0) / max(n, 1) for m in mods]
        # discordance = share of declared-bottom-half mass in observed top-half changes
        bottom = [m for m in mods if rank_in[m][cid] <= 0.34]
        tot = sum(cnt.get(m, 0) for m in mods) or 1
        d = sum(cnt.get(m, 0) for m in bottom) / tot
        ftot = sum(fcount.get(m, 0) for m in mods) or 1
        fshare = sum(fcount.get(m, 0) for m in bottom) / ftot
        if d >= disc:
            disc = d; disc_n = d / fshare if fshare > 0 else 0.0
    # S3 coverage: python packages under declared containers' parents that match no unit
    all_paths = [p for p in tree_paths if p.endswith(".py")]
    parents = {u.rsplit(".", 1)[0] for u in units if "." in u}
    uncovered = set()
    for p in all_paths:
        if "migrations/" in p or "/tests/" in p or p.startswith("tests/"): continue
        for par in parents:
            for pp in module_to_pathprefixes(par):
                if pp.endswith("/") and p.startswith(pp):
                    rest = p[len(pp):].split("/")[0]
                    if rest.endswith(".py") or rest.startswith("_"): continue
                    cand = f"{par}.{rest}"
                    if cand not in units and not unit_of(p):
                        uncovered.add(cand)
    # upward static imports (declared violations visible in code)
    up = 0
    for (a, b), c in edges.items():
        for cid in rank_in.get(a, {}):
            if cid in rank_in.get(b, {}) and rank_in[a][cid] < rank_in[b][cid]:
                up += c
    uncovered = {u for u in expanded_from if cnt.get(u, 0) > 0} | uncovered
    return {"date": date, "commit": commit[:7], "n_commits": n, "n_units": len(units),
            "S1_hidden": len(hidden), "hidden_pairs": hidden, "S2_bottom_share": round(disc, 2), "S2n": round(disc_n, 2),
            "S3_uncovered": len(uncovered), "uncovered": sorted(uncovered), "upward_imports": up,
            "top_changed": cnt.most_common(3)}

# ---------- run ----------
dates = []
d = dt.date.fromisoformat(START)
while d <= dt.date.fromisoformat(END):
    dates.append(d.isoformat())
    m = d.month + 3
    d = d.replace(year=d.year + (m - 1) // 12, month=(m - 1) % 12 + 1)

results = [score_snapshot(x) for x in dates]

# join declaration-change dates ONLY now
decl_changes = []
_prev = None
for line in reversed(git("log", "--format=%H %ad", "--date=short", "--", *DECL_FILES).splitlines()):
    h, d = line.split()
    c = parse_declaration(h)
    sig = repr(c) if c else None
    if sig and sig != _prev:
        decl_changes.append(d)
    _prev = sig if sig else _prev
def changed_next_q(date):
    d0 = dt.date.fromisoformat(date); d1 = d0 + dt.timedelta(days=92)
    return [c for c in decl_changes if d0 <= dt.date.fromisoformat(c) < d1]

print(f"{'snapshot':10s} {'commits':>7s} {'units':>5s} {'S1':>3s} {'S2':>5s} {'S2n':>5s} {'S3':>3s} {'up':>3s}  decl-change next Q")
for r in results:
    if not r or "note" in r:
        print(f"{r['date']:10s}  {r.get('note','')}"); continue
    nxt = changed_next_q(r["date"])
    print(f"{r['date']:10s} {r['n_commits']:7d} {r['n_units']:5d} {r['S1_hidden']:3d} {r['S2_bottom_share']:5.2f} {r['S2n']:5.2f} {r['S3_uncovered']:3d} {r['upward_imports']:3d}  {'YES '+','.join(nxt) if nxt else '-'}")
print("\n== details ==")
for r in results:
    if not r or "note" in r: continue
    print(f"\n{r['date']} ({r['commit']})  top changed: {[(u.split('.')[-1], c) for u, c in r['top_changed']]}")
    for a, b, s, c in r["hidden_pairs"]:
        print(f"   hidden: {a.split('.')[-1]} ~ {b.split('.')[-1]}  sup={s} conf={c}")
    if r["uncovered"]:
        print(f"   uncovered: {[u.split('.')[-1] for u in r['uncovered']]}")

print("\n== prediction summary (flag = S1>=2 or S2>=0.6 or S3>=1 with change count>0) ==")
tp=fp=fn=tn=0
for r in results:
    if not r or "note" in r: continue
    flag = r["S1_hidden"] >= 2 or r["S2_bottom_share"] >= 0.6 or r["S3_uncovered"] >= 1
    truth = bool(changed_next_q(r["date"]))
    tp += flag and truth; fp += flag and not truth; fn += (not flag) and truth; tn += (not flag) and (not truth)
print(f"TP={tp} FP={fp} FN={fn} TN={tn}  precision={tp/max(tp+fp,1):.2f} recall={tp/max(tp+fn,1):.2f}  base rate={ (tp+fn)/max(tp+fp+fn+tn,1):.2f}")
