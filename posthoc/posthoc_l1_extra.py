"""Further post hoc Layer-1 analyses requested in the second review round (not registered).

Reads the archived quarter table and, for section 6, the round-3 pilot scan of bk-user. No clone is needed.
  1. Leave-one-repository-out AUC under both labels.
  2. Activity-residualized S2n under both labels.
  3. Declaration regimes: positives that directly follow a revision; S2n z-scored within declaration regimes;
     the activity-controlled model with a post-revision indicator or the time since the last revision added.
  4. The unnormalized bottom-layer share S2 in place of S2n.
  5. Monte Carlo error of the permutation p-values (registered runs: 5,000 permutations; post hoc: 20,000).
  6. bk-user with the four round-3 values that the canonical scan did not reproduce.
Usage: python posthoc_l1_extra.py <l1_quarters_v2.csv> <pilot/blind_scan_bk-user.txt> <out.txt>
       (output must not exist)
"""
import csv
import math
import random
import re
import statistics as st
import sys
import warnings

import numpy as np
from statsmodels.discrete.conditional_models import ConditionalLogit

warnings.filterwarnings("ignore")
SRC, PILOT_BK, DST = sys.argv[1], sys.argv[2], sys.argv[3]
ROWS = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["valid"] == "True"]
for r in ROWS:
    for k in ("n", "S2", "S2n", "log_n", "new_pkgs"):
        r[k] = float(r[k])
    for k in ("y_orig", "y_a2"):
        r[k] = r[k] == "True"
TESTS = sorted({r["repo"] for r in ROWS})
G = {repo: sorted((r for r in ROWS if r["repo"] == repo), key=lambda r: r["date"]) for repo in TESTS}
LABELS = ("y_a2", "y_orig")
out = open(DST, "x", encoding="utf-8")
rng = random.Random(20261025)


def p(*a):
    print(*a)
    print(*a, file=out)
    out.flush()


def zfull(values):
    m, s = st.mean(values), st.pstdev(values) or 1.0
    return [(v - m) / s for v in values]


def auc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return float("nan")
    return sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))


def ranks(scores):
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    rk = [0.0] * len(scores)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def pooled(groups, label, scorer):
    sc, lab, grp = [], [], []
    for repo, g in groups.items():
        for x, r in zip(scorer(g), g):
            sc.append(x)
            lab.append(r[label])
            grp.append(repo)
    return sc, lab, grp


def perm_within(sc, lab, grp, n=20000):
    obs = auc(sc, lab)
    idx = {g: [i for i, x in enumerate(grp) if x == g] for g in sorted(set(grp))}
    ge = 0
    for _ in range(n):
        y = list(lab)
        for ii in idx.values():
            vals = [y[i] for i in ii]
            rng.shuffle(vals)
            for i, v in zip(ii, vals):
                y[i] = v
        ge += auc(sc, y) >= obs - 1e-12
    return ge / n


def perm_circular(sc, lab, grp):
    rk = ranks(sc)
    idx = {g: [i for i, x in enumerate(grp) if x == g] for g in sorted(set(grp))}
    contrib = []
    for ii in idx.values():
        y = [lab[i] for i in ii]
        rr = [rk[i] for i in ii]
        m = len(ii)
        contrib.append(np.array([sum(rr[k] for k in range(m) if y[(k - s) % m]) for s in range(m)]))
    obs = sum(c[0] for c in contrib)
    sums = np.zeros(1)
    for c in contrib:
        sums = (sums[:, None] + c[None, :]).ravel()
    return float(np.mean(sums >= obs - 1e-9))


def zcol(V, grp, key):
    col = np.zeros(len(V))
    for repo in sorted(set(grp)):
        ii = np.where(grp == repo)[0]
        col[ii] = zfull([V[i][key] for i in ii])
    return col


def cond_logit(label, signal="S2n", extra=None, n_perm=2000):
    """Conditional logit of the label on z(signal), z(log commits), z(new packages) [+ z(extra)];
    one-sided within-repository permutation test of the signal's likelihood-ratio statistic."""
    V = [r for g in G.values() for r in g]
    grp = np.array([r["repo"] for r in V])
    cols = [zcol(V, grp, signal), zcol(V, grp, "log_n"), zcol(V, grp, "new_pkgs")]
    if extra:
        cols.append(zcol(V, grp, extra))
    y = np.array([int(r[label]) for r in V])
    Xf, Xr = np.column_stack(cols), np.column_stack(cols[1:])
    fit = lambda yy, X: ConditionalLogit(yy, X, groups=grp).fit(disp=0, method="bfgs", maxiter=500)
    mf, mr = fit(y, Xf), fit(y, Xr)
    stat = 2 * (mf.llf - mr.llf)
    r2 = random.Random(1)
    ge = 0
    for _ in range(n_perm):
        yy = y.copy()
        for repo in sorted(set(grp)):
            ii = np.where(grp == repo)[0]
            vals = yy[ii].copy()
            r2.shuffle(vals)
            yy[ii] = vals
        a_, b_ = fit(yy, Xf), fit(yy, Xr)
        ge += a_.params[0] > 0 and 2 * (a_.llf - b_.llf) >= stat
    return mf, stat, ge / n_perm


full_z = lambda g: zfull([r["S2n"] for r in g])

# 1. Leave one repository out
p("1. Leave-one-repository-out pooled AUC (within-repository z-scored S2n)")
for label in LABELS:
    vals = []
    for left in TESTS:
        sc, lab, _ = pooled({k: v for k, v in G.items() if k != left}, label, full_z)
        vals.append(auc(sc, lab))
    p(f"  label={label:6s} " + ", ".join(f"{t} {a:.3f}" for t, a in zip(TESTS, vals))
      + f"  (range {min(vals):.2f}-{max(vals):.2f})")

# 2. Activity-residualized S2n
p("\n2. AUC of S2n residualized on z(log commits) and z(new packages) within repository")
res_by = {}
for repo, g in G.items():
    zs, zl, zp = full_z(g), zfull([r["log_n"] for r in g]), zfull([r["new_pkgs"] for r in g])
    A = np.column_stack([np.ones(len(g)), zl, zp])
    coef, *_ = np.linalg.lstsq(A, np.array(zs), rcond=None)
    res_by[repo] = list(np.array(zs) - A @ coef)
for label in LABELS:
    sc, lab, grp = pooled(G, label, lambda g: res_by[g[0]["repo"]])
    p(f"  label={label:6s} AUC={auc(sc, lab):.3f} within p={perm_within(sc, lab, grp):.4f} "
      f"circular p={perm_circular(sc, lab, grp):.4f}")

# 3. Declaration regimes (a revision in quarter t gives a new declaration from the snapshot of quarter t+1)
p("\n3. Declaration regimes (regimes delimited by A2-positive quarters)")
for repo, g in G.items():
    regime, start = 0, 0
    for t, r in enumerate(g):
        if t and g[t - 1]["y_a2"]:
            regime, start = regime + 1, t
        r["regime"] = regime
        r["post"] = float(bool(t and g[t - 1]["y_a2"]))
        r["since"] = math.log1p(t - start)
for label in LABELS:
    pos = [r for g in G.values() for r in g if r[label]]
    p(f"  label={label:6s} positives={len(pos)}; directly after an A2 revision (first quarter of a new declaration): "
      f"{sum(r['post'] > 0 for r in pos)}")


def regime_z(g):
    outz = []
    for r in g:
        same = [x["S2n"] for x in g if x["regime"] == r["regime"]]
        outz.append(0.0 if len(same) < 2 else (r["S2n"] - st.mean(same)) / (st.pstdev(same) or 1.0))
    return outz


p("  regimes per repository: " + ", ".join(f"{k} {1 + max(r['regime'] for r in g)}" for k, g in G.items()))
for label in LABELS:
    sc, lab, grp = pooled(G, label, regime_z)
    p(f"  S2n z-scored within declaration regime, label={label:6s}: AUC={auc(sc, lab):.3f} "
      f"within p={perm_within(sc, lab, grp):.4f} circular p={perm_circular(sc, lab, grp):.4f}")
for extra, name in (("post", "post-revision indicator"), ("since", "log(1 + quarters since last revision)")):
    for label in LABELS:
        mf, stat, pp = cond_logit(label, extra=extra)
        p(f"  conditional logit + {name}, label={label:6s}: beta S2n {mf.params[0]:+.3f} (SE {mf.bse[0]:.3f}), "
          f"beta {extra} {mf.params[3]:+.3f} (SE {mf.bse[3]:.3f}); LR {stat:.2f}, one-sided permutation p {pp:.4f} (N=2000)")

# 4. Unnormalized share S2
p("\n4. Unnormalized bottom-layer share S2 in place of S2n")
for label in LABELS:
    sc, lab, grp = pooled(G, label, lambda g: zfull([r["S2"] for r in g]))
    mf, stat, pp = cond_logit(label, signal="S2")
    p(f"  label={label:6s} AUC(z S2)={auc(sc, lab):.3f} within p={perm_within(sc, lab, grp):.4f} "
      f"circular p={perm_circular(sc, lab, grp):.4f}; conditional logit beta S2 {mf.params[0]:+.3f} "
      f"(SE {mf.bse[0]:.3f}), permutation p {pp:.4f} (N=2000)")

# 5. Monte Carlo error
p("\n5. Monte Carlo standard error sqrt(p(1-p)/N) of the reported permutation p-values")
for what, pv, n in (("registered pooled AUC, A2 (L1_ANALYSIS_v2)", 0.003, 5000),
                    ("registered pooled AUC, original label (L1_ANALYSIS)", 0.028, 5000),
                    ("registered A3 LR test, A2", 0.0198, 5000),
                    ("post hoc pooled AUC, A2 (posthoc_l1)", 0.0049, 20000),
                    ("post hoc pooled AUC, original label (posthoc_l1)", 0.0311, 20000)):
    p(f"  {what:52s} p={pv:<7} N={n:6d} MC SE={math.sqrt(pv * (1 - pv) / n):.4f}")
p("  circular-shift p-values over the five test repositories are exact (all 468,468 rotations)")

# 6. bk-user round-3 values
ROW = re.compile(r"(\d{4}-\d\d-\d\d)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s")
pilot = {m[1]: float(m[6]) for m in (ROW.match(line) for line in open(PILOT_BK, encoding="utf-8")) if m}
diff = [(r["date"], r["S2n"], pilot[r["date"]]) for r in G["bk-user"] if r["date"] in pilot and pilot[r["date"]] != r["S2n"]]
p("\n6. bk-user: quarters where the round-3 scan differs from the canonical scan (canonical -> round 3)")
p("  " + ", ".join(f"{d} {a:.2f}->{b:.2f}" for d, a, b in diff)
  + f"; positives among them: {sum(r['y_a2'] for r in G['bk-user'] if r['date'] in {d for d, _, _ in diff})}")
for r in G["bk-user"]:
    r["S2n_r3"] = pilot.get(r["date"], r["S2n"])
for label in LABELS:
    sc, lab, grp = pooled(G, label, lambda g: zfull([r.get("S2n_r3", r["S2n"]) for r in g]))
    p(f"  with round-3 values, label={label:6s}: AUC={auc(sc, lab):.3f} within p={perm_within(sc, lab, grp):.4f} "
      f"circular p={perm_circular(sc, lab, grp):.4f}")
out.close()
