"""Fig. 2: quarterly S2n per repository with quarters followed by a net revision of the layer lists (A2 label).
Usage: python fig2_s2n.py <l1_quarters_v2.csv> <out.png>   (output must not exist)"""
import csv, datetime, pathlib, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

src, out = sys.argv[1], pathlib.Path(sys.argv[2])
if out.exists():
    sys.exit(f"refusing to overwrite {out}")
rows = list(csv.DictReader(open(src, encoding="utf-8")))
PANELS = [("ggshield", "test"), ("bk-user", "test"), ("openedx-learning", "test"), ("legadilo", "test"),
          ("kedro", "test"), ("kopf", "control"), ("wemake-python-styleguide", "control")]
INK, INK2, GRID, BLUE, ORANGE = "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6", "#eb6834"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7})
fig, axes = plt.subplots(2, 4, figsize=(7.16, 3.3), dpi=300, sharey=True)
ymax = max(float(r["S2n"]) for r in rows if r["repo"] in dict(PANELS)) * 1.08
for ax, (repo, role) in zip(axes.flat, PANELS):
    rr = [r for r in rows if r["repo"] == repo]
    t = [datetime.date.fromisoformat(r["date"]) for r in rr]
    v = [float(r["S2n"]) for r in rr]
    ax.axhline(1.0, color=INK2, linewidth=0.6, linestyle=(0, (3, 2)), zorder=1)
    ax.plot(t, v, color=BLUE, linewidth=1.4, zorder=2)
    pos = [(a, b) for a, b, r in zip(t, v, rr) if r["y_a2"] == "True"]
    cen = [(a, b) for a, b, r in zip(t, v, rr) if r["censored"] == "True"]
    if pos:
        ax.scatter(*zip(*pos), s=26, marker="D", color=ORANGE, edgecolor="white", linewidth=0.8, zorder=3)
    if cen:
        ax.scatter(*zip(*cen), s=20, marker="o", facecolor="white", edgecolor=INK2, linewidth=0.8, zorder=3)
    ax.set_title(f"{repo} ({role}, {len(pos)} rev.)", fontsize=7, color=INK, loc="left")
    ax.set_ylim(0, ymax)
    ax.xaxis.set_major_locator(mdates.YearLocator(2 if (t[-1] - t[0]).days > 1500 else 1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, length=2, labelsize=6.5)
for ax in axes[:, 0]:
    ax.set_ylabel("S2n", color=INK2)
leg = axes.flat[-1]
leg.axis("off")
leg.plot([], [], color=BLUE, linewidth=1.4, label="S2n at quarterly snapshot")
leg.scatter([], [], s=26, marker="D", color=ORANGE, edgecolor="white", label="net revision of layer\nlists in next 92 days")
leg.scatter([], [], s=20, marker="o", facecolor="white", edgecolor=INK2, label="outcome window not\nyet elapsed")
leg.plot([], [], color=INK2, linewidth=0.6, linestyle=(0, (3, 2)), label="S2n = 1 (change in\nproportion to size)")
leg.legend(loc="center left", frameon=False, fontsize=6.5, labelcolor=INK)
fig.tight_layout(pad=0.4, w_pad=0.6, h_pad=0.8)
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out)
print("written", out)
