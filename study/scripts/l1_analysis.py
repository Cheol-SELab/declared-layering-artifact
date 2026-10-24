"""Layer-1 analysis: reproduction of the pooled AUC, amendment A2 relabelling, amendment A3 activity control.

Inputs: canonical scanner tables in results/l1/blind_scan_<repo>.txt (UTC snapshots).
Outputs: results/l1/L1_ANALYSIS.txt and results/l1/l1_quarters.csv (new files only).
Usage: python l1_analysis.py <repos_dir> <results_dir>
"""
import csv, datetime as dt, math, os, random, re, statistics as st, subprocess, sys
import numpy as np
import blind_scan as bs

REPOS_DIR, RES = sys.argv[1], sys.argv[2]
TAG = sys.argv[3] if len(sys.argv) > 3 else ""
DATA_END = dt.date(2026, 10, 5)  # clone date; quarters whose 92-day outcome window is not observed are censored
VALID = {"ggshield": "", "bk-user": "src/bk-user", "openedx-learning": "", "legadilo": "", "kedro": ""}
CONTROLS = {"kopf": "", "wemake-python-styleguide": "", "import-linter": "", "sqlfluff": ""}
ROW = re.compile(r"(\d{4}-\d\d-\d\d)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+(YES.*|-)$")


def load(name):
    rows = []
    for line in open(os.path.join(RES, f"blind_scan_{name}.txt"), encoding="utf-8"):
        m = ROW.match(line.rstrip())
        if m:
            rows.append(dict(repo=name, date=m[1], n=int(m[2]), S2=float(m[5]), S2n=float(m[6]), up=int(m[8]),
                             y_orig=m[9].startswith("YES")))
    return rows


def layer_lists(commit):
    """Layers-list content only (A2): contract names and ignore_imports are not part of the signature."""
    c = bs.parse_declaration(commit)
    if not c:
        return None
    return tuple(sorted(tuple(tuple(sorted(s)) for s in ranks) for _, ranks in c))


def a2_change_dates():
    out, prev = [], None
    for line in reversed(bs.git("log", "--format=%H %cd", "--date=short", "--", *bs.DECL_FILES).splitlines()):
        h, d = line.split()
        sig = layer_lists(h)
        if sig is not None and prev is not None and sig != prev:
            out.append(d)
        if sig is not None:
            prev = sig
    return out


def parent_prefixes(commit):
    contracts = bs.parse_declaration(commit) or []
    mods = {m for _, ranks in contracts for s in ranks for m in s}
    bs.discover_prefixes(commit, list(mods))
    pars = set()
    for m in mods:
        for pp in bs.MOD_PREFIX.get(m, []):
            if pp.endswith("/"):
                pars.add(pp.rstrip("/").rsplit("/", 1)[0] + "/" if "/" in pp.rstrip("/") else "")
    return pars


def child_pkgs(commit, pars):
    names = bs.git("ls-tree", "-r", "--name-only", commit).splitlines()
    kids = set()
    for n in names:
        if not n.endswith(".py"):
            continue
        for p in pars:
            if n.startswith(p):
                rest = n[len(p):].split("/")
                if len(rest) >= 3:  # <declared module>/<sub-package>/file.py
                    kids.add("/".join(rest[:2]))
    return kids


def new_pkgs(date):
    c1 = bs.snapshot_commit(date)
    c0 = bs.snapshot_commit((dt.date.fromisoformat(date) - dt.timedelta(days=360)).isoformat())
    if not c1 or not c0:
        return 0
    pars = parent_prefixes(c1)
    return len(child_pkgs(c1, pars) - child_pkgs(c0, pars))


def auc(sc, lab):
    pos = [s for s, y in zip(sc, lab) if y]
    neg = [s for s, y in zip(sc, lab) if not y]
    if not pos or not neg:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def z(v):
    mu, sd = st.mean(v), st.pstdev(v)
    return [(x - mu) / sd if sd > 0 else 0.0 for x in v]


rows = []
for name, dd in {**VALID, **CONTROLS}.items():
    bs.configure(os.path.join(REPOS_DIR, name), dd)
    a2 = a2_change_dates()
    for r in load(name):
        if r["n"] < 10:
            continue
        d0 = dt.date.fromisoformat(r["date"])
        r["y_a2_any"] = any(d0 <= dt.date.fromisoformat(c) < d0 + dt.timedelta(days=92) for c in a2)
        # A2 as registered (net change of the layers lists across the quarter; reproduces the two named exclusions)
        s0 = layer_lists(bs.snapshot_commit(r["date"]))
        s1 = layer_lists(bs.snapshot_commit((d0 + dt.timedelta(days=92)).isoformat()))
        r["y_a2"] = s0 is not None and s1 is not None and s0 != s1
        r["censored"] = d0 + dt.timedelta(days=92) > DATA_END
        r["log_n"] = math.log(r["n"])
        r["new_pkgs"] = new_pkgs(r["date"])
        r["valid"] = name in VALID
        rows.append(r)

out = open(os.path.join(RES, f"L1_ANALYSIS{TAG}.txt"), "x", encoding="utf-8")
def p(*a):
    print(*a); print(*a, file=out)

p("Layer-1 analysis (UTC snapshots, quarters with >= 10 window commits)\n")
p(f"{'repo':26s} {'Q':>3s} {'pos_orig':>8s} {'pos_A2':>6s} {'AUC_orig':>8s} {'AUC_A2':>7s}  S2n range   new_pkgs range")
CENSOR = "censor" in TAG
for name in list(VALID) + list(CONTROLS):
    R = [r for r in rows if r["repo"] == name and not (CENSOR and r["censored"])]
    f = lambda a: f"{a:.2f}" if a is not None else "n/a"
    p(f"{name:26s} {len(R):3d} {sum(r['y_orig'] for r in R):8d} {sum(r['y_a2'] for r in R):6d} "
      f"{f(auc([r['S2n'] for r in R], [r['y_orig'] for r in R])):>8s} {f(auc([r['S2n'] for r in R], [r['y_a2'] for r in R])):>7s}  "
      f"{min(r['S2n'] for r in R):.2f}-{max(r['S2n'] for r in R):.2f}   {min(r['new_pkgs'] for r in R)}-{max(r['new_pkgs'] for r in R)}")

CENSOR = "censor" in TAG
V = [r for r in rows if r["valid"] and not (CENSOR and r["censored"])]
for r_ in V:
    pass
zs, zl, zp, rep = [], [], [], []
for name in VALID:
    R = [r for r in V if r["repo"] == name]
    zs += z([r["S2n"] for r in R]); zl += z([r["log_n"] for r in R]); zp += z([r["new_pkgs"] for r in R]); rep += [name] * len(R)
for r, a, b, c in zip(V, zs, zl, zp):
    r["zS2n"], r["zlogn"], r["znew"] = a, b, c


def perm_auc(scores, labels, groups, within, N=5000, seed=0):
    rng = random.Random(seed); obs = auc(scores, labels); cnt = 0
    for _ in range(N):
        if within:
            lab = list(labels)
            for g in set(groups):
                idx = [i for i, gg in enumerate(groups) if gg == g]
                vals = [lab[i] for i in idx]; rng.shuffle(vals)
                for i, v in zip(idx, vals): lab[i] = v
        else:
            lab = list(labels); rng.shuffle(lab)
        cnt += auc(scores, lab) >= obs
    return obs, cnt / N


for lab_key in ("y_orig", "y_a2"):
    lab = [r[lab_key] for r in V]
    a, pa = perm_auc(zs, lab, rep, within=False)
    _, pw = perm_auc(zs, lab, rep, within=True)
    p(f"\nPooled {lab_key}: quarters={len(V)} positives={sum(lab)}  AUC={a:.3f}  perm p (pooled shuffle)={pa:.3f}  perm p (within-repo)={pw:.3f}")

# ---- A3: conditional (fixed-effects) logistic regression + within-repo permutation of the LR statistic ----
from statsmodels.discrete.conditional_models import ConditionalLogit
import warnings
warnings.filterwarnings("ignore")
y = np.array([int(r["y_a2"]) for r in V]); g = np.array(rep)
X_full = np.column_stack([zs, zl, zp]); X_red = np.column_stack([zl, zp])


def fit_ll(yv, X):
    m = ConditionalLogit(yv, X, groups=g).fit(disp=0, method="bfgs", maxiter=500)
    return m.llf, m


def lr(yv):
    llf, mf = fit_ll(yv, X_full); llr, _ = fit_ll(yv, X_red)
    return 2 * (llf - llr), mf


stat, mf = lr(y)
beta = mf.params[0]
rng = random.Random(1); ge = 0; N = 5000
for _ in range(N):
    yy = y.copy()
    for gg in set(rep):
        idx = np.where(g == gg)[0]; vals = yy[idx].copy(); rng.shuffle(vals); yy[idx] = vals
    s_, m_ = lr(yy)
    ge += (m_.params[0] > 0 and s_ >= stat) if beta > 0 else 0
p("\nA3 conditional logit (A2 labels), predictors z-scored within repo:")
for nm, b, se in zip(["S2n", "log_n", "new_pkgs"], mf.params, mf.bse):
    p(f"  beta_{nm:8s} = {b:+.3f}  (SE {se:.3f})")
p(f"  LR statistic for S2n = {stat:.3f}; one-sided within-repo permutation p = {ge / N:.4f} (N={N})")
p(f"  Decision (A3): {'ROBUST to activity' if beta > 0 and ge / N < 0.10 else 'EXPLAINED by activity / not supported'}")

# residualised AUC
res = []
for name in VALID:
    idx = [i for i, rr in enumerate(rep) if rr == name]
    A = np.column_stack([np.ones(len(idx)), [zl[i] for i in idx], [zp[i] for i in idx]])
    coef, *_ = np.linalg.lstsq(A, np.array([zs[i] for i in idx]), rcond=None)
    res += list(np.array([zs[i] for i in idx]) - A @ coef)
a, pw = perm_auc(res, list(y.astype(bool)), rep, within=True)
p(f"  AUC of activity-residualised S2n (A2 labels) = {a:.3f}; within-repo permutation p = {pw:.3f}")
p(f"\nActivity alone (A2 labels): AUC log_n = {auc(zl, list(y.astype(bool))):.3f}; AUC new_pkgs = {auc(zp, list(y.astype(bool))):.3f}")
p(f"Spearman-like: corr(zS2n, zlog_n) = {np.corrcoef(zs, zl)[0,1]:+.2f}; corr(zS2n, znew_pkgs) = {np.corrcoef(zs, zp)[0,1]:+.2f}")

with open(os.path.join(RES, f"l1_quarters{TAG}.csv"), "x", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["repo", "date", "n", "S2", "S2n", "up", "y_orig", "y_a2_any", "y_a2", "censored", "log_n", "new_pkgs", "valid"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
out.close()
