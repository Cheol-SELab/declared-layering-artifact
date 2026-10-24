"""Layer-4 refactoring plans (amendment A5): condition C (pre-registered §6 decision table, with the A5 fallback)
and condition B (file-level co-change move recommendation). Uses ONLY the 12-month window before the snapshot.

Usage: python l4_plans.py <repo_path> <snapshot_date> <out_dir> [decl_subdir]
Writes <out_dir>/<repo>_C.json and <repo>_B.json (exclusive create) and prints their SHA-256.
"""
import collections, datetime as dt, hashlib, itertools, json, os, sys
import blind_scan as bs

REPO, DATE, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
bs.configure(REPO, sys.argv[4] if len(sys.argv) > 4 else "")
name = os.path.basename(REPO.rstrip("/"))
snap = bs.snapshot_commit(DATE)
contracts = bs.parse_declaration(snap)

# ---- units and ranks exactly as the scanner defines them (incl. expansion of prefix units) ----
units, rank_in = {}, {}
for cid, ranks in contracts:
    for r, sibs in enumerate(ranks):
        for m in sibs:
            units[m] = m
            rank_in.setdefault(m, {})[cid] = (len(ranks) - 1 - r) / max(len(ranks) - 1, 1)
bs.discover_prefixes(snap, list(units))
names = bs.git("ls-tree", "-r", "--name-only", snap).splitlines()
done = set()
while True:
    todo = [U for U in units if U not in done and any(v != U and v.startswith(U + ".") for v in units)]
    if not todo:
        break
    for U in todo:
        done.add(U)
        for pp in bs.MOD_PREFIX.get(U, []):
            if not pp.endswith("/"):
                continue
            for sd in {n[len(pp):].split("/")[0] for n in names if n.startswith(pp) and "/" in n[len(pp):]}:
                if sd.startswith("_") or sd in ("migrations", "tests"):
                    continue
                c = f"{U}.{sd}"
                if c not in units:
                    units[c] = c; bs.MOD_PREFIX[c] = [pp + sd + "/"]; rank_in[c] = dict(rank_in.get(U, {}))
ordered = sorted(units, key=len, reverse=True)


def unit_of(p):
    for m in ordered:
        for pp in bs.MOD_PREFIX.get(m, []):
            if p.startswith(pp):
                return m


# ---- window commits with rename resolution (same filters as the scanner) ----
since = (dt.date.fromisoformat(DATE) - dt.timedelta(days=360)).isoformat()
log = bs.git("log", f"--since={since}", f"--until={DATE}", "--no-merges", "--name-status", "-M", "--reverse", "--format=---%H", snap)
rename, raw = {}, []
for block in log.split("---")[1:]:
    lines = block.strip().splitlines(); files = []
    for l in lines[1:]:
        parts = l.split("\t")
        if parts[0].startswith("R") and len(parts) == 3:
            rename[parts[1]] = parts[2]; files.append(parts[2])
        elif len(parts) == 2:
            files.append(parts[1])
    raw.append((lines[0], files))


def resolve(p):
    seen = set()
    while p in rename and p not in seen:
        seen.add(p); p = rename[p]
    return p


commits = []
for h, files in raw:
    fs = sorted({resolve(f) for f in files if f.endswith(".py") and "migrations/" not in f and "/tests/" not in f
                 and not f.startswith("tests/") and not f.endswith("/__init__.py") and "/version" not in f})
    us = {unit_of(f) for f in fs} - {None}
    if us and len(us) <= 6:
        commits.append((h, fs, us))

bottom = {u for u, rk in rank_in.items() if any(v <= 0.34 for v in rk.values())}


def higher_in_same_contract(u, others):
    return any(cid in rank_in.get(o, {}) and rank_in[o][cid] > rank_in[u][cid] for o in others for cid in rank_in.get(u, {}))


# ---- condition C: §6 decision table ----
cnt = collections.Counter(u for _, _, us in commits for u in us)
U = max(sorted(bottom), key=lambda u: (cnt.get(u, 0), u)) if bottom else None
prefix = next((pp for pp in bs.MOD_PREFIX.get(U, []) if pp.endswith("/")), None)
sub_n, sub_up = collections.Counter(), collections.Counter()
for _, fs, us in commits:
    if U not in us or not prefix:
        continue
    subs = set()
    for f in fs:
        if f.startswith(prefix):
            rest = f[len(prefix):]
            subs.add(rest.split("/")[0].removesuffix(".py"))
    up = higher_in_same_contract(U, us - {U})
    for s in subs:
        sub_n[s] += 1; sub_up[s] += up
tot_U = cnt.get(U, 0)
r = {s: sub_up[s] / sub_n[s] for s in sub_n}
mean_r = sum(sub_up.values()) / max(sum(sub_n.values()), 1)
decision, target = "HOLD", None
def loc(sub):  # size of a sub-module at the snapshot (lines), used only to break ties ("larger m")
    tot = 0
    for n in names:
        if prefix and (n == prefix + sub + ".py" or n.startswith(prefix + sub + "/")) and n.endswith(".py"):
            tot += len((bs.read_file(snap, n) or "").splitlines())
    return tot
top = max(((s, sub_n[s]) for s in sub_n), key=lambda t: (t[1], loc(t[0]), t[0])) if sub_n else (None, 0)
if top[0] and tot_U and top[1] / tot_U >= 0.40 and r[top[0]] >= 0.5:
    decision, target = "EXTRACT", f"{U}.{top[0]}"
elif tot_U and mean_r >= 0.5 and (not top[0] or top[1] / tot_U < 0.40):
    decision, target = "PROMOTE", U
table_decision = decision
fallback = None
if decision == "HOLD":  # A5 fallback, fixed before any run
    m = max(sorted(sub_up), key=lambda s: (sub_up[s], sub_n[s], loc(s), s)) if sub_up else None
    if m and sub_up[m] > 0:
        decision, target = "EXTRACT", f"{U}.{m}"
        fallback = "A5: most-co-changed-with-higher-layer sub-module of the busiest bottom unit"
plan_C = dict(repo=name, snapshot_date=DATE, snapshot=snap, window_since=since, window_commits=len(commits),
              bottom_units=sorted(bottom), U=U, U_commits=tot_U, submodules={s: dict(n=sub_n[s], with_higher=sub_up[s], r=round(r[s], 2)) for s in sorted(sub_n)},
              mean_r=round(mean_r, 2), tie_rule="count, then larger sub-module (lines), then name", sub_loc={s: loc(s) for s in sorted(sub_n)}, table_decision=table_decision, decision=decision, target=target, fallback=fallback)

# ---- condition B: file-level co-change move recommendation ----
fcnt = collections.Counter(f for _, fs, _ in commits for f in fs)
recs = []
for f, n in fcnt.items():
    if n < 4 or not unit_of(f):
        continue
    own = unit_of(f); sup_own = 0; sup = collections.Counter()
    for _, fs, _ in commits:
        if f not in fs:
            continue
        others = [g for g in fs if g != f]
        if any(unit_of(g) == own for g in others):
            sup_own += 1
        for v in {unit_of(g) for g in others} - {own, None}:
            sup[v] += 1
    for v, s in sup.items():
        if s > sup_own and s >= 3:
            recs.append(dict(file=f, from_unit=own, to_unit=v, support_to=s, support_own=sup_own, file_commits=n))
recs.sort(key=lambda x: (-x["support_to"], x["file"]))
plan_B = dict(repo=name, snapshot_date=DATE, snapshot=snap, window_since=since, window_commits=len(commits),
              rule="move f to unit V if support(f,V) > support(f, own unit) and support(f,V) >= 3; files with >= 4 commits; top 3",
              candidates=recs, recommendations=recs[:3])

os.makedirs(OUT, exist_ok=True)
for tag, plan in (("C", plan_C), ("B", plan_B)):
    path = os.path.join(OUT, f"{name}_{tag}.json")
    data = json.dumps(plan, indent=1, sort_keys=True).encode()
    with open(path, "xb") as fh:
        fh.write(data)
    print(tag, hashlib.sha256(data).hexdigest(), path)
print(json.dumps(plan_C, indent=1)); print(json.dumps(plan_B["recommendations"], indent=1), len(recs), "candidates")
