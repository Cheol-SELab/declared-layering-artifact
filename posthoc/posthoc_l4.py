"""Post hoc Layer-4 analyses added after peer review (not registered): the task as the unit of analysis.

For each repository and pooled over both, per-task mean differences C - A (declared units touched under the
condition's own declaration and in the A-frame), an exact Wilcoxon signed-rank test and an exact sign test on the
non-zero task differences, and the smallest two-sided p-value each test can reach with that many non-zero tasks.
Reads the archived run summaries in ../study/results/l4/. Usage: python posthoc_l4.py <out.txt> (must not exist).
"""
import itertools
import json
import math
import pathlib
import statistics as st
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent / "study" / "results" / "l4"
RUNS = {"kopf": "L4_kopf_runs.json", "kedro": "L4_kedro_E4_runs.json"}
out = open(sys.argv[1], "x", encoding="utf-8")


def p(*a):
    print(*a)
    print(*a, file=out)


def task_diffs(runs, key):
    by = {}
    for r in runs:
        if r["rep"].startswith("r"):
            by.setdefault(r["task"], {}).setdefault(r["cond"], []).append(r[key])
    return {t: st.mean(v["C"]) - st.mean(v["A"]) for t, v in sorted(by.items()) if "A" in v and "C" in v}


def exact_wilcoxon(d):
    """Two-sided exact signed-rank p on non-zero differences (average ranks for ties), by full enumeration."""
    nz = [x for x in d if abs(x) > 1e-12]
    k = len(nz)
    if k == 0:
        return 1.0, 1.0
    a = sorted(abs(x) for x in nz)
    rank = {}
    i = 0
    while i < k:
        j = i
        while j + 1 < k and abs(a[j + 1] - a[i]) < 1e-12:
            j += 1
        for v in a[i:j + 1]:
            rank[round(v, 9)] = (i + j) / 2 + 1
        i = j + 1
    rk = [rank[round(abs(x), 9)] for x in nz]
    w_obs = sum(r for r, x in zip(rk, nz) if x > 0)
    mean = sum(rk) / 2
    dev = abs(w_obs - mean)
    count = sum(abs(sum(r for r, s in zip(rk, signs) if s) - mean) >= dev - 1e-9
                for signs in itertools.product((0, 1), repeat=k))
    return count / 2 ** k, 2 / 2 ** k


def exact_sign(d):
    nz = [x for x in d if abs(x) > 1e-12]
    k = len(nz)
    if k == 0:
        return 1.0
    pos = sum(x > 0 for x in nz)
    tail = sum(math.comb(k, i) for i in range(0, min(pos, k - pos) + 1)) / 2 ** k
    return min(1.0, 2 * tail)


data = {repo: json.load(open(HERE / f)) for repo, f in RUNS.items()}
for key, label in (("units_own", "declared units, own declaration"), ("units_Aframe", "declared units, A-frame")):
    p(f"\n== {label} ({key}); unit of analysis = task (mean of three runs per condition)")
    pooled = []
    for repo, runs in data.items():
        d = task_diffs(runs, key)
        pooled += list(d.values())
        pw, pmin = exact_wilcoxon(list(d.values()))
        nonzero = sum(abs(x) > 1e-12 for x in d.values())
        p(f"  {repo}: tasks={len(d)} non-zero={nonzero} mean diff={st.mean(d.values()):+.3f} "
          f"exact Wilcoxon p={pw:.3f} (smallest attainable {pmin:.3f}) sign test p={exact_sign(list(d.values())):.3f}")
        p("    per task: " + ", ".join(f"{t} {v:+.2f}" for t, v in d.items()))
    pw, pmin = exact_wilcoxon(pooled)
    nonzero = sum(abs(x) > 1e-12 for x in pooled)
    p(f"  pooled: tasks={len(pooled)} non-zero={nonzero} mean diff={st.mean(pooled):+.3f} "
      f"exact Wilcoxon p={pw:.3f} (smallest attainable {pmin:.4f}) sign test p={exact_sign(pooled):.3f}")
out.close()
