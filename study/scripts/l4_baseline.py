"""Layer-4 human baseline (condition A as actually lived): first 10 post-snapshot PR commits with code+tests.
Propagation = number of declared units touched (scanner units at the snapshot, incl. expansion)."""
import sys, re, json, collections, statistics as st
sys.argv = ["x"]; import blind_scan as bs

CASES = [("kedro", "", "2023-10-01", "kedro"), ("r3/JujensGh__legadilo", "", "2025-10-01", "legadilo"),
         ("r3/nolar__kopf", "", "2026-01-01", "kopf"), ("openedx-learning", "", "2026-01-01", "openedx-learning")]

def units_at(commit):
    contracts = bs.parse_declaration(commit)
    units, rank_in = {}, {}
    for cid, ranks in contracts:
        depth = len(ranks)
        for r, sibs in enumerate(ranks):
            for mod in sibs:
                units[mod] = mod; rank_in.setdefault(mod, {})[cid] = (depth - 1 - r) / max(depth - 1, 1)
    bs.discover_prefixes(commit, list(units))
    names = bs.git("ls-tree", "-r", "--name-only", commit).splitlines()
    done = set()
    while True:
        todo = [U for U in units if U not in done and any(v != U and v.startswith(U + ".") for v in units)]
        if not todo: break
        for U in todo:
            done.add(U)
            for pp in bs.MOD_PREFIX.get(U, []):
                if not pp.endswith("/"): continue
                for sd in {n[len(pp):].split("/")[0] for n in names if n.startswith(pp) and "/" in n[len(pp):]}:
                    if sd.startswith("_") or sd in ("migrations", "tests"): continue
                    c = f"{U}.{sd}"
                    if c not in units: units[c] = c; bs.MOD_PREFIX[c] = [pp + sd + "/"]; rank_in[c] = dict(rank_in.get(U, {}))
    ordered = sorted(units, key=len, reverse=True)
    def unit_of(p):
        for m in ordered:
            for pp in bs.MOD_PREFIX.get(m, []):
                if p.startswith(pp): return m
    bottom = {m for m, rk in rank_in.items() if any(v <= 0.34 for v in rk.values())}
    return unit_of, bottom

rows = []
for repo, dd, date, name in CASES:
    bs.configure(repo, dd)
    snap = bs.snapshot_commit(date)
    unit_of, bottom = units_at(snap)
    log = bs.git("log", f"--since={date}", "--no-merges", "--reverse", "--name-only", "--format=---%H %s", "HEAD")
    taken = []; groups = collections.OrderedDict()
    for block in log.split("---")[1:]:
        lines = block.strip().splitlines(); head = lines[0]
        m = re.search(r"\(#(\d+)\)|#(\d+)", head)
        key = (m.group(1) or m.group(2)) if m else head[:12]
        g = groups.setdefault(key, {"head": head, "files": set()}); g["files"] |= set(lines[1:])
    for key, g in groups.items():
        head = g["head"]; files = sorted(g["files"]); m = True
        code = [f for f in files if f.endswith(".py") and "/tests/" not in f and not f.startswith("tests/") and "migrations/" not in f and not f.endswith("__init__.py")]
        tests = [f for f in files if f.endswith(".py") and ("/tests/" in f or f.startswith("tests/") or "/test_" in f)]
        if not (code and tests): continue
        if re.match(r"(docs?|chore|ci|build|style|release|bump|refactor|test)", head.split(" ", 1)[1].lower()): continue
        us = {u for u in map(unit_of, code) if u}
        if not us: continue
        taken.append(dict(repo=name, pr=key[:7], subject=head.split(" ", 1)[1][:60], files=len(code), units=len(us),
                          touches_bottom=bool(us & bottom), unit_list=sorted(u.split(".")[-1] for u in us)))
        if len(taken) == 10: break
    rows += taken
    print(f"\n== {name} (snapshot {snap[:7]} @ {date}) — first {len(taken)} PR commits with code+tests")
    for t in taken:
        print(f"  #{t['pr']:>5s} files={t['files']:2d} units={t['units']} bottom={'Y' if t['touches_bottom'] else '-'}  {t['subject']}  {t['unit_list']}")
    if taken:
        print(f"  median units={st.median(t['units'] for t in taken)}  mean files={st.mean(t['files'] for t in taken):.1f}  touches bottom: {sum(t['touches_bottom'] for t in taken)}/{len(taken)}")
json.dump(rows, open("/mnt/user-data/outputs/pilot/l4_baseline.json", "w"), indent=1)
