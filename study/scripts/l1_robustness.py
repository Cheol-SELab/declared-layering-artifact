"""Layer-1 robustness figures reported in Section V-B: pooled AUC of within-repository z-scored S2n (A2 labels),
leave-one-repository-out AUCs, and a repository-cluster bootstrap 95% interval; plus S2n at the Layer-4 snapshots.
Usage: python l1_robustness.py <l1_quarters_v2.csv> <out.txt>   (output must not exist)"""
import csv, random, statistics as st, sys

src, dst = sys.argv[1], sys.argv[2]
rows = [r for r in csv.DictReader(open(src, encoding="utf-8"))]
test = [r for r in rows if r["valid"] == "True"]
out = open(dst, "x", encoding="utf-8")


def p(*a):
    print(*a); print(*a, file=out)


def zrows(rs):
    by = {}
    for r in rs:
        by.setdefault(r["repo"], []).append(r)
    res = []
    for repo, g in by.items():
        v = [float(r["S2n"]) for r in g]
        m, s = st.mean(v), st.pstdev(v) or 1.0
        res += [(repo, (x - m) / s, r["y_a2"] == "True") for x, r in zip(v, g)]
    return res


def auc(pairs):
    pos = [x for _, x, y in pairs if y]; neg = [x for _, x, y in pairs if not y]
    if not pos or not neg:
        return float("nan")
    w = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return w / (len(pos) * len(neg))


repos = sorted({r["repo"] for r in test})
z = zrows(test)
p(f"Pooled AUC (within-repo z-scored S2n, A2 labels): {auc(z):.3f}  quarters={len(z)} positives={sum(y for *_, y in z)}")
loo = {rp: auc([t for t in z if t[0] != rp]) for rp in repos}
p("Leave-one-repository-out: " + ", ".join(f"{k} {v:.3f}" for k, v in loo.items())
  + f"  (range {min(loo.values()):.2f}-{max(loo.values()):.2f})")
rng = random.Random(20261005); B = 10000; boots = []
by = {rp: [t for t in z if t[0] == rp] for rp in repos}
for _ in range(B):
    smp = [t for rp in (rng.choice(repos) for _ in repos) for t in by[rp]]
    a = auc(smp)
    if a == a:
        boots.append(a)
boots.sort()
p(f"Repository-cluster bootstrap (B={B}, seed 20261005): 95% CI {boots[int(0.025 * len(boots))]:.2f}-{boots[int(0.975 * len(boots)) - 1]:.2f}")
p("S2n at the Layer-4 snapshots: " + ", ".join(
    f"{r['repo']} {r['date']} S2n={r['S2n']} (n={r['n']})" for r in rows
    if (r["repo"], r["date"]) in {("kopf", "2026-01-01"), ("kedro", "2023-10-01")}))
out.close()
