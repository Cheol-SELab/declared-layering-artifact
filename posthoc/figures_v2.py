"""Revised Figures 1 and 2 for the second review round (the published originals stay in figures/).

Figure 1: first appearance of a layers contract per half-year, every bar labelled with its half-year.
Figure 2: quarterly S2n for the five test and four control repositories, with the within-repository z-score on the
right axis (the scale used by the pooled AUC), the per-repository AUC under the A2 label in each title, and the
declaration changes (first snapshot after each net revision of the layer lists) as vertical lines.
Usage: python figures_v2.py <pop_decl_history.json> <l1_quarters_v2.csv> <out_dir>   (files must not exist)
"""
import collections
import csv
import datetime
import json
import pathlib
import statistics as st
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HIST, QUARTERS, OUT = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
F1, F2 = OUT / "fig1_adoption_v2.png", OUT / "fig2_s2n_v2.png"
for f in (F1, F2):
    if f.exists():
        sys.exit(f"refusing to overwrite {f}")
OUT.mkdir(parents=True, exist_ok=True)
INK, INK2, GRID, BLUE, ORANGE = "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})

# ---- Figure 1
d = json.load(open(HIST, encoding="utf-8"))
cnt = collections.Counter()
for r in d.values():
    y, m = int(r["decl_first"][:4]), int(r["decl_first"][5:7])
    cnt[(y, 1 if m <= 6 else 2)] += 1
first, last = min(cnt), max(cnt)
bins = [(y, h) for y in range(first[0], last[0] + 1) for h in (1, 2) if first <= (y, h) <= last]
vals = [cnt[b] for b in bins]
fig, ax = plt.subplots(figsize=(5.2, 2.4), dpi=300)
bars = ax.bar(range(len(bins)), vals, width=0.72, color=BLUE, edgecolor="white", linewidth=0.8, zorder=2)
bars[-1].set_hatch("////")
bars[-1].set_facecolor("#86b6ef")
for i, v in enumerate(vals):
    ax.text(i, v + 0.8, str(v), ha="center", va="bottom", color=INK, fontsize=7)
ax.set_xticks(range(len(bins)), [f"H{h}\n{y}" if h == 1 or i == 0 else f"H{h}" for i, (y, h) in enumerate(bins)],
              fontsize=6.5, color=INK2)
ax.set_ylabel("Repositories", color=INK2, fontsize=7.5)
ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(INK2)
ax.tick_params(axis="y", colors=INK2, length=0, labelsize=7)
ax.tick_params(axis="x", length=0)
ax.set_ylim(0, max(vals) * 1.2)
ax.text(len(bins) - 1, vals[-1] * 0.5, "Jul–\nOct", ha="center", va="center", fontsize=6, color=INK)
fig.tight_layout(pad=0.3)
fig.savefig(F1)
plt.close(fig)

# ---- Figure 2
rows = list(csv.DictReader(open(QUARTERS, encoding="utf-8")))
PANELS = [("ggshield", "test"), ("bk-user", "test"), ("openedx-learning", "test"), ("legadilo", "test"),
          ("kedro", "test"), ("kopf", "control"), ("wemake-python-styleguide", "control"),
          ("import-linter", "control"), ("sqlfluff", "control")]


def auc(scores, labels):
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return None
    return sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))


plt.rcParams.update({"font.size": 7})
fig, axes = plt.subplots(3, 3, figsize=(7.16, 5.6), dpi=300, sharey=True)
ymax = max(float(r["S2n"]) for r in rows if r["repo"] in dict(PANELS)) * 1.08
for ax, (repo, role) in zip(axes.flat, PANELS):
    rr = sorted((r for r in rows if r["repo"] == repo), key=lambda r: r["date"])
    t = [datetime.date.fromisoformat(r["date"]) for r in rr]
    v = [float(r["S2n"]) for r in rr]
    lab = [r["y_a2"] == "True" for r in rr]
    for k in range(1, len(rr)):
        if lab[k - 1]:
            ax.axvline(t[k], color=INK2, linewidth=0.5, linestyle=(0, (1, 1.5)), zorder=1)
    ax.axhline(1.0, color=INK2, linewidth=0.6, linestyle=(0, (4, 2)), zorder=1)
    ax.plot(t, v, color=BLUE, linewidth=1.3, zorder=2)
    pos = [(a, b) for a, b, y in zip(t, v, lab) if y]
    cen = [(a, b) for a, b, r in zip(t, v, rr) if r["censored"] == "True"]
    if pos:
        ax.scatter(*zip(*pos), s=24, marker="D", color=ORANGE, edgecolor="white", linewidth=0.8, zorder=3)
    if cen:
        ax.scatter(*zip(*cen), s=18, marker="o", facecolor="white", edgecolor=INK2, linewidth=0.8, zorder=3)
    a = auc(v, lab)
    ax.set_title(f"{repo} ({role}); {len(pos)} rev." + (f"; AUC {a:.2f}" if a is not None else ""),
                 fontsize=6.8, color=INK, loc="left")
    ax.set_ylim(0, ymax)
    m, s = st.mean(v), st.pstdev(v) or 1.0
    sec = ax.secondary_yaxis("right", functions=(lambda x, m=m, s=s: (x - m) / s, lambda z, m=m, s=s: z * s + m))
    sec.tick_params(colors=INK2, length=2, labelsize=6)
    sec.spines["right"].set_color(GRID)
    ax.xaxis.set_major_locator(mdates.YearLocator(2 if (t[-1] - t[0]).days > 1500 else 1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    for side in ("top", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, length=2, labelsize=6.5)
for ax in axes[:, 0]:
    ax.set_ylabel("S2n", color=INK2)
for ax in axes[:, -1]:
    ax.text(1.2, 0.5, "z within repository", transform=ax.transAxes, rotation=90, va="center", fontsize=6.5,
            color=INK2)
handles = [plt.Line2D([], [], color=BLUE, linewidth=1.3),
           plt.Line2D([], [], marker="D", color=ORANGE, linestyle="none", markeredgecolor="white", markersize=5),
           plt.Line2D([], [], marker="o", color=INK2, markerfacecolor="white", linestyle="none", markersize=4.5),
           plt.Line2D([], [], color=INK2, linewidth=0.6, linestyle=(0, (4, 2))),
           plt.Line2D([], [], color=INK2, linewidth=0.5, linestyle=(0, (1, 1.5)))]
fig.legend(handles, ["S2n at quarterly snapshot", "net revision of the layer lists in the next 92 days",
                     "outcome window not yet elapsed", "S2n = 1 (dashed)", "new declaration (dotted)"],
           loc="lower center", ncol=3, frameon=False, fontsize=6.5)
fig.tight_layout(pad=0.4, w_pad=1.4, h_pad=0.9, rect=(0, 0.07, 1, 1))
fig.savefig(F2)
print("written", F1, F2)
