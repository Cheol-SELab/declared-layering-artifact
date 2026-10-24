"""Post hoc RQ2 analyses added after peer review (not registered).

For every sealed Layer-2 proposal (study/data/layer2_proposals.json) the layer lists at the proposal's snapshot and
92 days later are compared mechanically:
  - revision kind: units added, removed (or renamed), and moved (a unit whose order relative to another unit present
    at both dates changed in some contract);
  - location: is the proposal's bottom unit U among the units the revision removed or moved?
  - chance baselines for the location: a unit drawn at random from all declared units, and from the declared bottom
    (rank <= 0.34), with its expected hit rate;
  - the registered type baselines ("always extract", "random type"): a type match needs a revision of the
    proposal's kind (EXTRACT or PROMOTE moves an existing unit up), so their expected match counts follow from
    the number of revisions that moved a declared unit.
Needs clones of the subject repositories (see posthoc_s2n_variants.py). Standard library plus the study scanner.
Usage: python posthoc_rq2.py <repos_dir> <layer2_proposals.json> <out.txt>   (output must not exist)
"""
import datetime as dt
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "study" / "scripts"))
import blind_scan as bs  # noqa: E402

REPOS_DIR, SRC, DST = sys.argv[1], sys.argv[2], sys.argv[3]
DECL_DIR = {"bk-user": "src/bk-user"}
out = open(DST, "x", encoding="utf-8")


def p(*a):
    print(*a)
    print(*a, file=out)


def order(commit):
    """(declared units, set of (lower, higher) pairs within any contract); None if no declaration."""
    c = bs.parse_declaration(commit)
    if not c:
        return None
    units, below = set(), set()
    for _, rks in c:
        for r, sibs in enumerate(rks):
            units.update(sibs)
            for higher in rks[:r]:
                below.update((m, h) for m in sibs for h in higher)
    return units, below


def bottom(commit):
    c = bs.parse_declaration(commit) or []
    out_ = set()
    for _, rks in c:
        depth = len(rks)
        for r, sibs in enumerate(rks):
            if (depth - 1 - r) / max(depth - 1, 1) <= 0.34:
                out_.update(sibs)
    return out_


props = json.load(open(SRC, encoding="utf-8"))
p("Post hoc RQ2: sealed proposals against the mechanically diffed revision of the layer lists (snapshot vs +92 days)")
p(f"{'repository':17s} {'snapshot':10s} {'proposal':8s} {'U':45s} {'A2':3s} {'added':>5s} {'removed':>7s} "
  f"{'moved':>5s} {'U hit':>5s} {'E[random unit]':>14s} {'E[random bottom]':>16s}")
rows = []
for e in props:
    repo = e["repo"].split("/")[-1].split("__")[-1]
    bs.configure(os.path.join(REPOS_DIR, repo), DECL_DIR.get(repo, ""))
    c0 = bs.snapshot_commit(e["date"])
    c1 = bs.snapshot_commit((dt.date.fromisoformat(e["date"]) + dt.timedelta(days=92)).isoformat())
    (ua, oa), (ub, ob) = order(c0), order(c1)
    common = ua & ub
    removed = sorted(ua - ub)
    added = sorted(ub - ua)
    flipped = {(x, y) for x, y in oa ^ ob if x in common and y in common}
    moved = sorted({u for pair in flipped for u in pair})
    a = ua
    changed = set(removed) | set(moved)
    bot = bottom(c0)
    positive = bool(added or removed or moved)
    hit = e["U"] in changed
    e_all = len(changed) / len(a)
    e_bot = len(changed & bot) / len(bot) if bot else float("nan")
    rows.append(dict(positive=positive, hit=hit, e_all=e_all, e_bot=e_bot, moved=bool(moved), removed=bool(removed),
                     proposal=e["proposal"]))
    p(f"{repo:17s} {e['date']:10s} {e['proposal']:8s} {e['U']:45s} {'yes' if positive else 'no':3s} {len(added):5d} "
      f"{len(removed):7d} {len(moved):5d} {'yes' if hit else 'no':>5s} {e_all:14.2f} {e_bot:16.2f}")
    for kind, lst in (("added", added), ("removed", removed), ("moved", moved)):
        if lst:
            p(f"    {kind}: {', '.join(lst)}")

pos = [r for r in rows if r["positive"]]
p(f"\nA2-positive quarters with a sealed proposal: {len(pos)}")
p(f"  revisions that add units only: {sum(not r['removed'] and not r['moved'] for r in pos)}; "
  f"remove or rename a unit: {sum(r['removed'] for r in pos)}; change the order of units present at both dates: "
  f"{sum(r['moved'] for r in pos)}")
p(f"  location: U among the removed or moved units in {sum(r['hit'] for r in pos)} of {len(pos)}; "
  f"expected under a random declared unit {sum(r['e_all'] for r in pos):.2f}, "
  f"under a random declared-bottom unit {sum(r['e_bot'] for r in pos):.2f}")
p(f"  type: EXTRACT and PROMOTE both move a declared unit up; revisions that moved any declared unit: "
  f"{sum(r['moved'] for r in pos)}. The registered baselines 'always extract' and 'random type' (EXTRACT, PROMOTE,")
p("  HOLD, each with probability 1/3) can match in type only those revisions, and HOLD never counts as a match.")
out.close()
