"""Post hoc population analyses added after peer review (not registered).

  1. Funnel counts that can be recomputed from the archived files (the 1,907 search hits are recorded in
     pilot/STUDY_SUMMARY_v3.md; the raw search output was not archived).
  2. Revisions per declaration-year of exposure, by cohort of first appearance (data end 2026-10-05).
  3. Kaplan-Meier estimate of the probability that a declaration's layer lists are still unrevised after 0.25, 0.5,
     1 and 2 years, with right-censoring at the data end.
  4. Repository age at the first declaration, by cohort.
Usage: python posthoc_pop.py <gh_decl.json> <pop_decl_history.json> <out.txt>   (output must not exist)
"""
import datetime as dt
import json
import statistics as st
import sys

GH, HIST, DST = sys.argv[1], sys.argv[2], sys.argv[3]
END = dt.date(2026, 10, 5)
out = open(DST, "x", encoding="utf-8")


def p(*a):
    print(*a)
    print(*a, file=out)


D = lambda s: dt.date.fromisoformat(s[:10])
gh = json.load(open(GH, encoding="utf-8"))
hist = json.load(open(HIST, encoding="utf-8"))
revs = lambda r: r["layer_revisions"] if isinstance(r["layer_revisions"], list) else json.loads(r["layer_revisions"].replace("'", '"'))

p("1. Funnel")
p(f"  created >= 2 years before 2026-10-05, pushed within a year, not archived (gh_decl.json): {len(gh)}")
p(f"  ... with a layers contract of >= 3 layers: {sum(1 for r in gh.values() if (r.get('max_layers') or 0) >= 3)} "
  f"(pop_decl_history.json: {len(hist)})")

cohort = lambda r: "before 2025" if r["decl_first"][:4] < "2025" else r["decl_first"][:4]
p("\n2. Layer-list revisions per declaration-year of exposure (first appearance to 2026-10-05)")
for name in ("before 2025", "2025", "2026", "all"):
    rs = [r for r in hist.values() if name == "all" or cohort(r) == name]
    years = sum((END - D(r["decl_first"])).days / 365.25 for r in rs)
    n_rev = sum(len(revs(r)) for r in rs)
    never = sum(not revs(r) for r in rs)
    p(f"  {name:11s} declarations={len(rs):3d} exposure={years:6.1f} declaration-years "
      f"(median {st.median((END - D(r['decl_first'])).days / 365.25 for r in rs):.2f} y) revisions={n_rev:4d} "
      f"rate={n_rev / years:.2f} per declaration-year; never revised {never} ({never / len(rs):.0%})")
for floor in (1, 2):
    rs = [r for r in hist.values() if (END - D(r["decl_first"])).days / 365.25 >= floor]
    p(f"  declarations observed for >= {floor} year(s): {len(rs)}; never revised {sum(not revs(r) for r in rs)}")

p("\n3. Kaplan-Meier: probability that the layer lists are still unrevised")
events = []
for r in hist.values():
    first = sorted(D(x) for x in revs(r))
    t = ((first[0] if first else END) - D(r["decl_first"])).days / 365.25
    events.append((t, bool(first)))
events.sort()
surv, at_risk, i, curve = 1.0, len(events), 0, []
while i < len(events):
    t = events[i][0]
    d = sum(1 for x in events if x[0] == t and x[1])
    c = sum(1 for x in events if x[0] == t)
    if d:
        surv *= 1 - d / at_risk
    curve.append((t, surv, at_risk))
    at_risk -= c
    i += c
for h in (0.25, 0.5, 1, 2):
    s = [x for x in curve if x[0] <= h]
    n_risk = sum(1 for t, _ in events if t >= h)
    p(f"  after {h:>4} years: {s[-1][1] if s else 1.0:.2f} (declarations still at risk: {n_risk})")
p(f"  first revisions observed: {sum(e for _, e in events)}; censored without revision: {sum(not e for _, e in events)}")

p("\n4. Repository age at first declaration (years)")
for name in ("before 2025", "2025", "2026"):
    ages = [(D(r["decl_first"]) - D(r["created"])).days / 365.25 for r in hist.values() if cohort(r) == name]
    p(f"  {name:11s} n={len(ages):3d} median {st.median(ages):.1f}; < 1 year {sum(a < 1 for a in ages)}, "
      f">= 2 years {sum(a >= 2 for a in ages)}")
out.close()
