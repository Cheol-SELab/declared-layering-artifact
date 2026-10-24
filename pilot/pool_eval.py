import re, glob, statistics as st, os
D = "/mnt/user-data/outputs/pilot/"
def load(f):
    rows = []
    for l in open(f):
        m = re.match(r"(\d{4}-\d\d-\d\d)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+(YES|-)", l)
        if m: rows.append(dict(date=m[1], n=int(m[2]), S1=int(m[4]), S2=float(m[5]), S2n=float(m[6]), S3=int(m[7]), up=int(m[8]), y=m[9] == "YES"))
    return rows
def auc(sc, lab):
    pos = [s for s, y in zip(sc, lab) if y]; neg = [s for s, y in zip(sc, lab) if not y]
    if not pos or not neg: return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))

EXCLUDE = {  # screened out, with reason
    "napari": "2-layer forbidden-style contracts (not a stability ordering)",
    "mlrun": "bottom layer is the whole client library (size-dominated)",
    "ukhsa": "degenerate after 2024-07 (S2=1.00)",
    "blueking-paas": "aspirational declaration: 55-63 upward imports tolerated",
    "bk-iam-saas": "aspirational declaration: 76 upward imports",
    "dify": "declaration under construction (50 revisions in 12 months; up to 100 upward imports)",
    "physicsnemo": "declaration under construction (13 revisions in 9 months); S2 degenerate",
    "blueking-apigateway": "path mapping failed (0 commits matched)",
    "bidsMReye": "<10 commits per quarter",
}
print(f"{'repo':24s} {'Q':>3s} {'pos':>3s} {'medUp':>5s} {'S2 range':>11s} {'AUC S2':>7s} {'AUC S2n':>8s}  status")
pooled = []  # (z-scored S2n within repo, label)
summary = []
for f in sorted(glob.glob(D + "blind_scan_*.txt")):
    name = os.path.basename(f)[11:-4]
    rows = [r for r in load(f) if r["n"] >= 10]
    if not rows: continue
    lab = [r["y"] for r in rows]
    a2 = auc([r["S2"] for r in rows], lab); a2n = auc([r["S2n"] for r in rows], lab)
    medup = int(st.median(r["up"] for r in rows))
    status = EXCLUDE.get(name, "")
    if not status and len(rows) < 8: status = f"<8 quarters ({len(rows)})"
    if not status and sum(lab) == 0: status = "control (no revisions)"
    if not status and sum(lab) == 1: status = "1 positive (uninformative)"
    if not status: status = "VALID TEST"
    fmt = lambda a: f"{a:.2f}" if a is not None else "  n/a"
    print(f"{name:24s} {len(rows):3d} {sum(lab):3d} {medup:5d} {min(r['S2'] for r in rows):5.2f}-{max(r['S2'] for r in rows):4.2f} {fmt(a2):>7s} {fmt(a2n):>8s}  {status}")
    if status == "VALID TEST":
        s2n = [r["S2n"] for r in rows]; mu, sd = st.mean(s2n), (st.pstdev(s2n) or 1)
        pooled += [((v - mu) / sd, y) for v, y in zip(s2n, lab)]
        s2 = [r["S2"] for r in rows]; mu2, sd2 = st.mean(s2), (st.pstdev(s2) or 1)
        summary.append((name, len(rows), sum(lab), a2, a2n))
print("\nPooled over VALID TEST repos (S2n z-scored within repo):")
print(f"  quarters={len(pooled)} positives={sum(y for _, y in pooled)}  AUC={auc([z for z, _ in pooled], [y for _, y in pooled]):.2f}")
# permutation p-value for pooled AUC
import random
obs = auc([z for z, _ in pooled], [y for _, y in pooled]); labs = [y for _, y in pooled]; zs = [z for z, _ in pooled]
random.seed(0); cnt = 0; N = 5000
for _ in range(N):
    random.shuffle(labs); cnt += auc(zs, labs) >= obs
print(f"  permutation p (AUC >= observed, labels shuffled across pooled quarters) = {cnt / N:.3f}")
