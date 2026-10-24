"""Further post hoc Layer-4 analyses requested in the second review round (not registered).

  1. Lines changed per run: per-task mean difference C - A with exact Wilcoxon and sign tests (task as the unit).
  2. Runs that edited test files outside the acceptance specification, per task and condition.
  3. kedro tasks excluded under deviation D6: declared units touched by the maintainers' change on the A base,
     compared with the six analysed tasks (Layer-4 human baselines, study/data/l4_baseline.json).
Usage: python posthoc_l4_extra.py <study/results/l4> <layer4> <study/data/l4_baseline.json> <out.txt>
       (output must not exist)
"""
import itertools
import json
import math
import pathlib
import statistics as st
import sys

L4, RECORDS, BASELINE, DST = (pathlib.Path(a) for a in sys.argv[1:5])
RUNS = {"kopf": "L4_kopf_runs.json", "kedro": "L4_kedro_E4_runs.json"}
KEDRO_PR = {"2297d23": "3147", "2f526b6": "2926", "3f2a226": "3115", "60f676e": "3187", "69a6fe1": "3211",
            "ab576bc": "2987", "00f035a": "3188", "5752f68": "3081", "cd83bad": "3145", "0cd8ecc": "3095"}
EXCLUDED = ["00f035a", "5752f68", "cd83bad", "0cd8ecc"]
out = open(DST, "x", encoding="utf-8")


def p(*a):
    print(*a)
    print(*a, file=out)


def exact_wilcoxon(d):
    nz = [x for x in d if abs(x) > 1e-12]
    k = len(nz)
    if k == 0:
        return 1.0
    a = sorted(abs(x) for x in nz)
    rank, i = {}, 0
    while i < k:
        j = i
        while j + 1 < k and abs(a[j + 1] - a[i]) < 1e-12:
            j += 1
        for v in a[i:j + 1]:
            rank[round(v, 9)] = (i + j) / 2 + 1
        i = j + 1
    rk = [rank[round(abs(x), 9)] for x in nz]
    mean = sum(rk) / 2
    dev = abs(sum(r for r, x in zip(rk, nz) if x > 0) - mean)
    return sum(abs(sum(r for r, s in zip(rk, signs) if s) - mean) >= dev - 1e-9
               for signs in itertools.product((0, 1), repeat=k)) / 2 ** k


def exact_sign(d):
    nz = [x for x in d if abs(x) > 1e-12]
    k = len(nz)
    if k == 0:
        return 1.0
    pos = sum(x > 0 for x in nz)
    return min(1.0, 2 * sum(math.comb(k, i) for i in range(0, min(pos, k - pos) + 1)) / 2 ** k)


p("1. Lines changed per run (agent runs r1-r3); unit of analysis = task")
for repo, f in RUNS.items():
    runs = [r for r in json.load(open(L4 / f, encoding="utf-8")) if r["rep"].startswith("r")]
    by = {}
    for r in runs:
        by.setdefault(r["task"], {}).setdefault(r["cond"], []).append(r["lines_changed"])
    d = {t: st.mean(v["C"]) - st.mean(v["A"]) for t, v in sorted(by.items())}
    mA = st.mean(r["lines_changed"] for r in runs if r["cond"] == "A")
    mC = st.mean(r["lines_changed"] for r in runs if r["cond"] == "C")
    medA = st.median(st.mean(v["A"]) for v in by.values())
    medC = st.median(st.mean(v["C"]) for v in by.values())
    p(f"  {repo}: run mean A {mA:.0f}, C {mC:.0f}; median of task means A {medA:.0f}, C {medC:.0f}; "
      f"C<A in {sum(x < 0 for x in d.values())} of {len(d)} tasks; exact Wilcoxon p={exact_wilcoxon(list(d.values())):.3f}, "
      f"sign test p={exact_sign(list(d.values())):.3f}")
    p("    per task (C - A): " + ", ".join(f"{t} {v:+.0f}" for t, v in d.items()))

p("\n2. Runs that edited test files outside the acceptance specification (archived run records)")
for repo in RUNS:
    recs = [json.load(open(x, encoding="utf-8")) for x in sorted((RECORDS / repo / "results").glob("*_r[0-9].json"))]
    tally = {}
    for r in recs:
        if r.get("other_test_files_edited"):
            tally.setdefault((r["task"], r["cond"]), []).append(r["rep"])
    total = {c: sum(1 for r in recs if r["cond"] == c) for c in ("A", "C")}
    edited = {c: sum(len(v) for (t, cc), v in tally.items() if cc == c) for c in ("A", "C")}
    p(f"  {repo}: A {edited['A']}/{total['A']} runs, C {edited['C']}/{total['C']} runs; "
      + "; ".join(f"{t} {c} {','.join(v)}" for (t, c), v in sorted(tally.items())))

p("\n3. kedro: maintainers' change on the A base, declared units touched (human baselines)")
base = {e["pr"]: e for e in json.load(open(BASELINE, encoding="utf-8")) if e["repo"] == "kedro"}
for group, tasks in (("analysed", [t for t in KEDRO_PR if t not in EXCLUDED]), ("excluded (D6)", EXCLUDED)):
    vals = [base[KEDRO_PR[t]]["units"] for t in tasks]
    io = sum("io" in base[KEDRO_PR[t]]["unit_list"] for t in tasks)
    p(f"  {group:14s} tasks={len(tasks)} mean units {st.mean(vals):.2f}; touching kedro.io {io}; "
      + ", ".join(f"{t} (#{KEDRO_PR[t]}) {base[KEDRO_PR[t]]['units']} {'/'.join(base[KEDRO_PR[t]]['unit_list'])}"
                  for t in tasks))
out.close()
