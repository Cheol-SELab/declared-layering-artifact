"""Post hoc Layer-1 analyses added after peer review (not registered). Reads the archived quarter table only.

Sections of the report:
  1. Registered statistic under both labels (A2 and the original label), as reported in the manuscript.
  2. Temporal dependence: exact circular-shift permutation within repository (12-month windows overlap by 9 months).
  3. Prospective (past-only) scoring: each quarter is z-scored against the repository's earlier quarters only.
  4. Operational alarm: precision, recall and false alarms per repository-year at fixed thresholds.
  5. Repository inclusion: test repositories plus the controls that have at least ten commits per quarter.
  6. Activity: direction of the commit-volume association, the activity-controlled model under both labels,
     and S2n with commit-count shrinkage (variance stabilisation for quiet quarters).
Usage: python posthoc_l1.py <l1_quarters_v2.csv> <out.txt>   (output must not exist)
"""
import csv
import itertools
import math
import random
import statistics as st
import sys
import warnings

import numpy as np
from statsmodels.discrete.conditional_models import ConditionalLogit

warnings.filterwarnings("ignore")
SRC, DST = sys.argv[1], sys.argv[2]
ROWS = list(csv.DictReader(open(SRC, encoding="utf-8")))
for r in ROWS:
    for k in ("n", "S2", "S2n", "log_n", "new_pkgs"):
        r[k] = float(r[k])
    for k in ("y_orig", "y_a2", "valid"):
        r[k] = r[k] == "True"
TESTS = sorted({r["repo"] for r in ROWS if r["valid"]})
CONTROLS_WITH_POSITIVES = ["import-linter", "sqlfluff"]
ALL_NINE = sorted({r["repo"] for r in ROWS})
out = open(DST, "x", encoding="utf-8")
rng = random.Random(20261024)


def p(*a):
    print(*a)
    print(*a, file=out)


def series(repos, key="S2n"):
    """Per-repository lists in date order: (score, row)."""
    by = {}
    for r in sorted(ROWS, key=lambda r: (r["repo"], r["date"])):
        if r["repo"] in repos:
            by.setdefault(r["repo"], []).append(r)
    return by


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
    """groups: {repo: [rows]}; scorer(rows) -> scores aligned with rows (None = not scored)."""
    sc, lab, grp = [], [], []
    for repo, g in groups.items():
        s = scorer(g)
        for x, r in zip(s, g):
            if x is not None:
                sc.append(x); lab.append(r[label]); grp.append(repo)
    return sc, lab, grp


def perm_within(sc, lab, grp, n=20000):
    obs = auc(sc, lab)
    idx = {g: [i for i, x in enumerate(grp) if x == g] for g in sorted(set(grp))}
    ge = 0
    for _ in range(n):
        y = list(lab)
        for ii in idx.values():
            vals = [y[i] for i in ii]; rng.shuffle(vals)
            for i, v in zip(ii, vals):
                y[i] = v
        ge += auc(sc, y) >= obs - 1e-12
    return obs, ge / n


def perm_circular(sc, lab, grp, exact_limit=2_000_000, n=200000):
    """Rotate each repository's label sequence by an offset (preserves label clustering). Exact when feasible."""
    rk = ranks(sc)
    P = sum(lab); N = len(lab) - P
    idx = {g: [i for i, x in enumerate(grp) if x == g] for g in sorted(set(grp))}
    contrib = []
    for ii in idx.values():
        y = [lab[i] for i in ii]; rr = [rk[i] for i in ii]; m = len(ii)
        contrib.append(np.array([sum(rr[k] for k in range(m) if y[(k - s) % m]) for s in range(m)]))
    obs_sum = sum(c[0] for c in contrib)
    to_auc = lambda s: (s - P * (P + 1) / 2) / (P * N)
    total = math.prod(len(c) for c in contrib)
    if total <= exact_limit:
        sums = np.zeros(1)
        for c in contrib:
            sums = (sums[:, None] + c[None, :]).ravel()
        return to_auc(obs_sum), float(np.mean(sums >= obs_sum - 1e-9)), f"exact over {total} rotations"
    draws = sum(c[np.random.default_rng(7 + i).integers(0, len(c), n)] for i, c in enumerate(contrib))
    return to_auc(obs_sum), float(np.mean(draws >= obs_sum - 1e-9)), f"Monte Carlo {n} rotations"


def full_z(g):
    return zfull([r["S2n"] for r in g])


def past_only(min_prior=4):
    def scorer(g):
        out_ = []
        for t, r in enumerate(g):
            prior = [x["S2n"] for x in g[:t]]
            if len(prior) < min_prior:
                out_.append(None)
            else:
                s = st.pstdev(prior) or 1.0
                out_.append((r["S2n"] - st.mean(prior)) / s)
        return out_
    return scorer


# 1. Registered statistic, both labels
p("1. Registered statistic: pooled AUC of within-repository z-scored S2n (five test repositories)")
G = series(TESTS)
for label in ("y_a2", "y_orig"):
    sc, lab, grp = pooled(G, label, full_z)
    a, pw = perm_within(sc, lab, grp)
    a, pc, how = perm_circular(sc, lab, grp)
    p(f"  label={label:6s} quarters={len(sc)} positives={sum(lab)} AUC={a:.3f} "
      f"within-repo permutation p={pw:.4f}  circular-shift p={pc:.4f} ({how})")

# 2. Non-overlapping windows (every fourth quarter) as a second dependence check
p("\n2. Non-overlapping windows: every fourth quarter per repository, all four phases")
for label in ("y_a2", "y_orig"):
    vals = []
    for phase in range(4):
        sub = {k: v[phase::4] for k, v in G.items()}
        sc, lab, grp = pooled(sub, label, full_z)
        vals.append((auc(sc, lab), len(sc), sum(lab)))
    p(f"  label={label:6s} " + "; ".join(f"phase {i}: AUC {a:.3f} (n={n}, pos={k})" for i, (a, n, k) in enumerate(vals)))

# 3. Prospective scoring
p("\n3. Prospective (past-only) z-score: quarter t scored against quarters < t of the same repository")
for min_prior in (4, 6):
    for label in ("y_a2", "y_orig"):
        sc, lab, grp = pooled(G, label, past_only(min_prior))
        a, pw = perm_within(sc, lab, grp)
        _, pc, how = perm_circular(sc, lab, grp)
        p(f"  min prior quarters={min_prior} label={label:6s} quarters={len(sc)} positives={sum(lab)} "
          f"AUC={a:.3f} within p={pw:.4f} circular p={pc:.4f} ({how})")
sc_raw, lab_raw, _ = pooled(G, "y_a2", lambda g: [r["S2n"] for r in g])
p(f"  absolute S2n (no standardisation), A2 label: AUC={auc(sc_raw, lab_raw):.3f}")

# 4. Operational alarm
p("\n4. Alarm performance (A2 label; base rate = positives / quarters)")
sc_po, lab_po, grp_po = pooled(G, "y_a2", past_only(4))
years_raw = len(sc_raw) / 4
years_po = len(sc_po) / 4
p(f"  base rate all quarters {sum(lab_raw)}/{len(lab_raw)} = {sum(lab_raw) / len(lab_raw):.2f}; "
  f"base rate scored by past-only {sum(lab_po)}/{len(lab_po)} = {sum(lab_po) / len(lab_po):.2f}")
for name, sc, lab, yrs, ths in (("absolute S2n", sc_raw, lab_raw, years_raw, (1.0, 1.25, 1.5)),
                                ("past-only z", sc_po, lab_po, years_po, (0.5, 1.0, 1.5))):
    for th in ths:
        flag = [s > th for s in sc]
        tp = sum(f and y for f, y in zip(flag, lab)); fp = sum(f and not y for f, y in zip(flag, lab))
        p(f"  {name:12s} > {th:<4}: flagged {sum(flag):2d}, true {tp:2d}, precision {tp / max(1, sum(flag)):.2f}, "
          f"recall {tp / sum(lab):.2f}, false alarms per repository-year {fp / yrs:.2f}")

# 5. Repository inclusion
p("\n5. Inclusion: z-scored S2n pooled over more repositories (all have >= 10 commits per quarter)")
for name, repos in (("tests + import-linter + sqlfluff", TESTS + CONTROLS_WITH_POSITIVES), ("all nine", ALL_NINE)):
    Gx = series(repos)
    for label in ("y_a2", "y_orig"):
        sc, lab, grp = pooled(Gx, label, full_z)
        a, pw = perm_within(sc, lab, grp)
        _, pc, how = perm_circular(sc, lab, grp)
        p(f"  {name:32s} label={label:6s} quarters={len(sc)} positives={sum(lab)} AUC={a:.3f} "
          f"within p={pw:.4f} circular p={pc:.4f} ({how})")
    sc, lab, grp = pooled(Gx, "y_a2", past_only(4))
    a, pw = perm_within(sc, lab, grp)
    p(f"  {name:32s} past-only (>=4 prior) A2: quarters={len(sc)} positives={sum(lab)} AUC={a:.3f} within p={pw:.4f}")

# 6. Activity
p("\n6. Activity")
zlog = lambda g: zfull([r["log_n"] for r in g])
for label in ("y_a2", "y_orig"):
    sc, lab, _ = pooled(G, label, zlog)
    pos_n = [r["n"] for g in G.values() for r in g if r[label]]
    neg_n = [r["n"] for g in G.values() for r in g if not r[label]]
    p(f"  label={label:6s} AUC(z log commits)={auc(sc, lab):.3f} (inverse discrimination {1 - auc(sc, lab):.3f}); "
      f"median window commits positive {st.median(pos_n):.1f} vs negative {st.median(neg_n):.1f}")


def cond_logit(label, s2n_key="S2n", n_perm=5000):
    V = [r for g in G.values() for r in g]
    grp = np.array([r["repo"] for r in V])
    def zcol(key):
        col = np.zeros(len(V))
        for repo in sorted(set(grp)):
            ii = np.where(grp == repo)[0]
            col[ii] = zfull([V[i][key] for i in ii])
        return col
    zs, zl, zp = zcol(s2n_key), zcol("log_n"), zcol("new_pkgs")
    y = np.array([int(r[label]) for r in V])
    Xf, Xr = np.column_stack([zs, zl, zp]), np.column_stack([zl, zp])
    fit = lambda yy, X: ConditionalLogit(yy, X, groups=grp).fit(disp=0, method="bfgs", maxiter=500)
    mf, mr = fit(y, Xf), fit(y, Xr)
    stat = 2 * (mf.llf - mr.llf)
    r2 = random.Random(1); ge = 0
    for _ in range(n_perm):
        yy = y.copy()
        for repo in sorted(set(grp)):
            ii = np.where(grp == repo)[0]; vals = yy[ii].copy(); r2.shuffle(vals); yy[ii] = vals
        a_, b_ = fit(yy, Xf), fit(yy, Xr)
        ge += a_.params[0] > 0 and 2 * (a_.llf - b_.llf) >= stat
    return mf, stat, ge / n_perm


for label in ("y_a2", "y_orig"):
    mf, stat, pp = cond_logit(label)
    p(f"  conditional logit, label={label:6s}: beta S2n {mf.params[0]:+.3f} (SE {mf.bse[0]:.3f}), "
      f"log commits {mf.params[1]:+.3f} (SE {mf.bse[1]:.3f}), new packages {mf.params[2]:+.3f} (SE {mf.bse[2]:.3f}); "
      f"LR {stat:.2f}, one-sided permutation p {pp:.4f}")

for m in (10, 25, 50):
    for g in G.values():
        mean_share = st.mean(r["S2"] for r in g)
        for r in g:
            files_share = r["S2"] / r["S2n"] if r["S2n"] else float("nan")
            r[f"S2n_shr{m}"] = ((r["S2"] * r["n"] + m * mean_share) / (r["n"] + m)) / files_share
    sc, lab, grp = pooled(G, "y_a2", lambda g: zfull([r[f"S2n_shr{m}"] for r in g]))
    a, pw = perm_within(sc, lab, grp)
    mf, stat, pp = cond_logit("y_a2", f"S2n_shr{m}")
    p(f"  S2n shrunk toward the repository mean with {m} pseudo-commits: AUC {a:.3f} (within p {pw:.4f}); "
      f"conditional logit beta {mf.params[0]:+.3f} (SE {mf.bse[0]:.3f}), permutation p {pp:.4f}")
out.close()
