"""Fig. 1: first appearance of an import-linter layers contract per half-year (population of 106 mature repositories).
Usage: python fig1_adoption.py <pop_decl_history.json> <out.png>   (output must not exist)"""
import collections, json, pathlib, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

src, out = sys.argv[1], pathlib.Path(sys.argv[2])
if out.exists():
    sys.exit(f"refusing to overwrite {out}")
d = json.load(open(src, encoding="utf-8"))
cnt = collections.Counter()
for r in d.values():
    y, m = int(r["decl_first"][:4]), int(r["decl_first"][5:7])
    cnt[(y, 1 if m <= 6 else 2)] += 1
first, last = min(cnt), max(cnt)
bins = [(y, h) for y in range(first[0], last[0] + 1) for h in (1, 2) if first <= (y, h) <= last]
vals = [cnt[b] for b in bins]
labels = [f"{y}\nH{h}" for y, h in bins]

INK, INK2, GRID, BLUE = "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
fig, ax = plt.subplots(figsize=(3.5, 2.2), dpi=300)
bars = ax.bar(range(len(bins)), vals, width=0.72, color=BLUE, edgecolor="white", linewidth=0.8, zorder=2)
# the last half-year is partial (observation ends early October 2026): hatch it and say so
bars[-1].set_hatch("////"); bars[-1].set_facecolor("#86b6ef")
for i, v in enumerate(vals):
    if v:
        ax.text(i, v + 0.8, str(v), ha="center", va="bottom", color=INK, fontsize=7)
years = sorted({y for y, _ in bins})
ax.set_xticks([i for i, b in enumerate(bins)], ["" for _ in bins])
for y in years:
    idx = [i for i, b in enumerate(bins) if b[0] == y]
    ax.text(sum(idx) / len(idx), -0.06, str(y), transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=6.5, color=INK2)
ax.set_ylabel("Repositories (first layers contract)", color=INK2, fontsize=7)
ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(INK2)
ax.tick_params(axis="y", colors=INK2, length=0, labelsize=7)
ax.set_ylim(0, max(vals) * 1.18)
ax.text(len(bins) - 1, vals[-1] * 0.5, "to\nOct", ha="center", va="center", fontsize=6, color=INK)
fig.tight_layout(pad=0.3)
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out)
print(dict(zip([f"{y}H{h}" for y, h in bins], vals)), "total", sum(vals))
