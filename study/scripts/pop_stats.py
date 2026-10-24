"""Population figures in Section V-A: adoption by year, revision counts, repository age at first declaration.
Usage: python pop_stats.py <pop_decl_history.json> <out.txt>   (output must not exist)"""
import collections, datetime as dt, json, statistics as st, sys
d = json.load(open(sys.argv[1], encoding="utf-8")); out = open(sys.argv[2], "x", encoding="utf-8")
def p(*a): print(*a); print(*a, file=out)
D = lambda s: dt.date.fromisoformat(s[:10])
revs = lambda r: r["layer_revisions"] if isinstance(r["layer_revisions"], list) else json.loads(r["layer_revisions"].replace("'", '"'))
p("repositories", len(d))
p("first declaration by year", dict(sorted(collections.Counter(r["decl_first"][:4] for r in d.values()).items())))
c = collections.Counter(len(revs(r)) for r in d.values())
p("layer-list revisions: 0 ->", c[0], "| 1 ->", c[1], "| >=8 ->", sum(v for k, v in c.items() if k >= 8), "| >=9 ->", sum(v for k, v in c.items() if k >= 9))
rec = [r for r in d.values() if r["decl_first"][:4] in ("2025", "2026")]
age = [(D(r["decl_first"]) - D(r["created"])).days / 365.25 for r in rec]
p(f"2025-2026 declarations: {len(rec)}; repo age at declaration >=2y: {sum(a >= 2 for a in age)}, >=1y: {sum(a >= 1 for a in age)}, median {st.median(age):.1f} y")
p("median commits", st.median(int(r["n_commits"]) for r in d.values()), "median stars", st.median(int(r["stars"]) for r in d.values()))
out.close()
