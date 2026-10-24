"""Post hoc sensitivity of the RQ1 result to the S2n implementation (added after peer review; not registered).

Re-mines the five test repositories at the archived quarterly snapshots with the study scanner
(study/scripts/blind_scan.py, imported unchanged) and recomputes S2n under variants of each implementation
choice. Variant 0 is the implementation as run; it must reproduce the S2n values of l1_quarters_v2.csv exactly,
otherwise the script stops. Labels and the quarter set are taken from l1_quarters_v2.csv and are the same for
every variant.

Variants (one choice changed at a time, then all wording-literal choices together):
  numerator   touch  = bottom units' share of unit touches (as run); commit = share of all mined commits that touch
              the bottom; commit in contract = the same share among commits that touch a unit of the contract
  filter      as run = excludes paths containing "openedx_core" or "/version"; generic = only version files
              (version.py, _version.py, __version__.py) are excluded
  sweep       commits touching at most 6 units kept (as run); at most 4 or 9 (the registered cut-offs 5 and 10);
              no cut-off
  bottom      rank <= 0.34 (as run); rank 0 only (the single declared bottom layer); rank <= 0.5
  expanded    sub-packages created by prefix expansion are dropped from the contract (as run); they inherit the
              rank of the declared unit they were expanded from
  contract    the contract with the largest unnormalized bottom share (as run); the contract with the largest S2n

Needs clones of the subject repositories at the commits printed in the report (the clones are not part of the
replication package; fetch_clones.py recreates them). Uses numpy only, besides the scanner.
Usage: python posthoc_s2n_variants.py <repos_dir> <l1_quarters_v2.csv> <out.txt>   (output must not exist)
"""
import collections
import csv
import datetime as dt
import io
import math
import os
import random
import re
import statistics as st
import sys
import tarfile
import subprocess
from pathlib import Path

import numpy as np

# git reads a --since/--until date without a time of day as that date at the current time of day, so the scanner's
# window edges move with the time at which it runs. The archived scans ran on 2026-10-05 at about 23:05 UTC; pin
# git's notion of "now" to that moment (GIT_TEST_DATE_NOW, seconds since the epoch) so that the scans reproduce.
os.environ["GIT_TEST_DATE_NOW"] = "1791241500"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "study" / "scripts"))
import blind_scan as bs  # noqa: E402

REPOS_DIR, SRC, DST = sys.argv[1], sys.argv[2], sys.argv[3]
DECL_DIR = {"ggshield": "", "bk-user": "src/bk-user", "openedx-learning": "", "legadilo": "", "kedro": ""}
ROWS = [r for r in csv.DictReader(open(SRC, encoding="utf-8")) if r["valid"] == "True"]
TESTS = sorted(DECL_DIR)
VERSION_FILE = re.compile(r"(^|/)_{0,2}version_{0,2}\.py$")
out = open(DST, "x", encoding="utf-8")


def p(*a):
    print(*a)
    print(*a, file=out)
    out.flush()


# ---------- raw snapshot data (mirrors blind_scan.score_snapshot up to the scoring step) ----------
def raw_snapshot(date):
    commit = bs.snapshot_commit(date)
    contracts = bs.parse_declaration(commit)
    units, rank_in = {}, {}
    for cid, rks in contracts:
        depth = len(rks)
        for r, sibs in enumerate(rks):
            for mod in sibs:
                units[mod] = mod
                rank_in.setdefault(mod, {})[cid] = (depth - 1 - r) / max(depth - 1, 1)
    bs.discover_prefixes(commit, list(units))
    paths = sorted({pp.rstrip("/") for u in units for pp in bs.MOD_PREFIX.get(u, []) if pp.endswith("/")}) or ["."]
    data = subprocess.run(["git", "-C", bs.REPO, "archive", commit, *paths], capture_output=True).stdout
    tree_paths = [m.name for m in tarfile.open(fileobj=io.BytesIO(data)).getmembers()]
    expanded_from, done = {}, set()
    while True:
        todo = [U for U in units if U not in done and any(v != U and v.startswith(U + ".") for v in units)]
        if not todo:
            break
        for U in todo:
            done.add(U)
            for pp in bs.module_to_pathprefixes(U):
                if not pp.endswith("/"):
                    continue
                subs = {x[len(pp):].split("/")[0] for x in tree_paths if x.startswith(pp) and "/" in x[len(pp):]}
                for sd in subs:
                    if sd.startswith("_") or sd in ("migrations", "tests"):
                        continue
                    cand = f"{U}.{sd}"
                    if cand not in units:
                        units[cand] = cand
                        expanded_from[cand] = U
    for cand, par in expanded_from.items():
        bs.MOD_PREFIX[cand] = [pr + cand.rsplit(".", 1)[1] + "/" for pr in bs.MOD_PREFIX.get(par, []) if pr.endswith("/")]
    ordered = sorted(units, key=len, reverse=True)
    prefixes = {mod: bs.module_to_pathprefixes(mod) for mod in ordered}
    memo = {}

    def unit_of(path):
        if path not in memo:
            memo[path] = next((mod for mod in ordered for pp in prefixes[mod] if path.startswith(pp)), None)
        return memo[path]

    since = (dt.date.fromisoformat(date) - dt.timedelta(days=30 * bs.WINDOW_MONTHS)).isoformat()
    log = bs.git("log", f"--since={since}", f"--until={date}", "--no-merges", "--name-status", "-M", "--reverse",
                 "--format=---%H", commit)
    rename, commits = {}, []
    for block in log.split("---")[1:]:
        files = []
        for line in block.strip().splitlines()[1:]:
            parts = line.split("\t")
            if parts[0].startswith("R") and len(parts) == 3:
                rename[parts[1]] = parts[2]
                files.append(parts[2])
            elif len(parts) == 2:
                files.append(parts[1])
        commits.append(files)

    def resolve(x):
        seen = set()
        while x in rename and x not in seen:
            seen.add(x)
            x = rename[x]
        return x

    fcount = collections.Counter(u for u in (unit_of(x) for x in tree_paths
                                             if x.endswith(".py") and "migrations/" not in x and "/tests/" not in x) if u)
    root = {}
    for cand in expanded_from:
        r = cand
        while r in expanded_from:
            r = expanded_from[r]
        root[cand] = r
    return dict(contracts=contracts, rank_in=rank_in, root=root, unit_of=unit_of, resolve=resolve,
                commits=commits, fcount=fcount)


def base_filter(f):
    return (f.endswith(".py") and "migrations/" not in f and "/tests/" not in f and not f.startswith("tests/")
            and not f.endswith("/__init__.py") and "openedx_core" not in f and "/version" not in f)


def generic_filter(f):
    return (f.endswith(".py") and "migrations/" not in f and "/tests/" not in f and not f.startswith("tests/")
            and not f.endswith("/__init__.py") and not VERSION_FILE.search(f))


AS_RUN = dict(numerator="touch", filt="as run", max_units=6, bottom="0.34", expanded="drop", contract="max share")


def s2n(raw, numerator, filt, max_units, bottom, expanded, contract):
    keep = base_filter if filt == "as run" else generic_filter
    mined = []
    for files in raw["commits"]:
        us = sorted({u for u in (raw["unit_of"](raw["resolve"](f)) for f in files if keep(f)) if u})
        if us and (max_units is None or len(us) <= max_units):
            mined.append(us)
    n = len(mined)
    cnt = collections.Counter()
    for us in mined:
        cnt.update(us)
    best_share, best = 0.0, 0.0
    for cid, rks in raw["contracts"]:
        mods = [m for sibs in rks for m in sibs]
        if len(mods) < 3:
            continue
        rank = {m: raw["rank_in"][m][cid] for m in mods}
        if expanded == "inherit":
            for cand, r in raw["root"].items():
                if r in rank and cand not in rank:
                    rank[cand] = rank[r]
        if bottom == "0.34":
            bot = {m for m in rank if rank[m] <= 0.34}
        elif bottom == "rank 0":
            bot = {m for m in rank if rank[m] == 0}
        else:
            bot = {m for m in rank if rank[m] <= 0.5}
        if numerator == "touch":
            share = sum(cnt.get(m, 0) for m in bot) / (sum(cnt.get(m, 0) for m in rank) or 1)
        elif numerator == "commit":
            share = sum(1 for us in mined if bot.intersection(us)) / max(n, 1)
        else:
            inside = [us for us in mined if rank.keys() & set(us)]
            share = sum(1 for us in inside if bot.intersection(us)) / max(len(inside), 1)
        ftot = sum(raw["fcount"].get(m, 0) for m in rank) or 1
        fshare = sum(raw["fcount"].get(m, 0) for m in bot) / ftot
        value = share / fshare if fshare > 0 else 0.0
        if contract == "max share":
            if share >= best_share:
                best_share, best = share, value
        elif value >= best:
            best = value
    return round(best, 2)


# ---------- statistics (as in posthoc_l1.py) ----------
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


def perm_within(sc, lab, grp, n=20000, seed=20261024):
    rng = random.Random(seed)
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
    P = sum(lab)
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


# ---------- run ----------
p("Post hoc: sensitivity of RQ1 to the S2n implementation (five test repositories, archived quarters and labels)")
p("Clones used (HEAD):")
raws = {}
for repo in TESTS:
    bs.configure(os.path.join(REPOS_DIR, repo), DECL_DIR[repo])
    p(f"  {repo:18s} {bs.git('rev-parse', 'HEAD').strip()}")
    for r in sorted((r for r in ROWS if r["repo"] == repo), key=lambda r: r["date"]):
        raws[(repo, r["date"])] = raw_snapshot(r["date"])
keys = sorted(raws)
stored = {(r["repo"], r["date"]): float(r["S2n"]) for r in ROWS}
base = {k: s2n(raws[k], **AS_RUN) for k in keys}
bad = [k for k in keys if abs(base[k] - stored[k]) > 1e-9]
p(f"\nVariant 0 reproduces the archived S2n in {len(keys) - len(bad)} of {len(keys)} quarters")
if bad:
    p("  mismatches: " + ", ".join(f"{k[0]} {k[1]} {base[k]} vs {stored[k]}" for k in bad))
    sys.exit(1)

VARIANTS = [
    ("0  as run", {}),
    ("1  numerator = commit share", dict(numerator="commit")),
    ("1b commit share within contract", dict(numerator="commit in contract")),
    ("2  generic path filter", dict(filt="generic")),
    ("3  sweep cut-off 5 units", dict(max_units=4)),
    ("4  sweep cut-off 10 units", dict(max_units=9)),
    ("5  no sweep cut-off", dict(max_units=None)),
    ("6  bottom = rank 0 only", dict(bottom="rank 0")),
    ("7  bottom = rank <= 0.5", dict(bottom="0.5")),
    ("8  expanded units inherit rank", dict(expanded="inherit")),
    ("9  contract with largest S2n", dict(contract="max S2n")),
    ("10 1+2+8 (wording-literal)", dict(numerator="commit", filt="generic", expanded="inherit")),
    ("10b 1b+2+8", dict(numerator="commit in contract", filt="generic", expanded="inherit")),
]
label = {k: {lab: next(r[lab] == "True" for r in ROWS if (r["repo"], r["date"]) == k) for lab in ("y_a2", "y_orig")}
         for k in keys}
p("\nPooled AUC of within-repository z-scored S2n; p from 20,000 within-repository label permutations and from the")
p("exact circular-shift permutation (all rotations). Per-repository AUC under A2 in the order " + ", ".join(TESTS) + ".")
p(f"{'variant':34s} {'changed':>7s}  {'AUC A2':>6s} {'p perm':>6s} {'p circ':>6s}  {'AUC orig':>8s} {'p circ':>6s}  per-repository (A2)")
for name, change in VARIANTS:
    params = {**AS_RUN, **change}
    vals = {k: s2n(raws[k], **params) for k in keys}
    changed = sum(abs(vals[k] - base[k]) > 1e-9 for k in keys)
    sc, grp, per = [], [], []
    for repo in TESTS:
        ks = [k for k in keys if k[0] == repo]
        z = zfull([vals[k] for k in ks])
        sc += z
        grp += [repo] * len(ks)
        per.append(auc(z, [label[k]["y_a2"] for k in ks]))
    res = []
    for lab in ("y_a2", "y_orig"):
        y = [label[k][lab] for k in keys]
        res.append((auc(sc, y), perm_within(sc, y, grp) if lab == "y_a2" else None, perm_circular(sc, y, grp)))
    (a2, pw, pc), (ao, _, pco) = res
    p(f"{name:34s} {changed:7d}  {a2:6.3f} {pw:6.4f} {pc:6.4f}  {ao:8.3f} {pco:6.4f}  " + " ".join(f"{x:.2f}" for x in per))
out.close()
