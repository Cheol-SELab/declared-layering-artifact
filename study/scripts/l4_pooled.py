"""Layer-4 supplementary analysis (registered in A6, plus reporting aids).
1. Pooled mixed model over kopf and kedro: units ~ condition, random intercept per repository, variance component
   per task (A6: "a pooled mixed model with repository and task random effects").
2. Per-repository d_av = mean(task diff) / sqrt((sd_A^2 + sd_C^2) / 2) over task means (alternative reading of
   "paired Cohen's d").
3. Human-change replays: whether the PR applied on each base (replay_apply_rc) and units touched.
Usage: python l4_pooled.py <out.txt>   (output must not exist). Reads results/l4/L4_<repo>_runs.json and the replay
records/meta under C:/vdm/l4/<repo>/.
"""
import json, pathlib, statistics as st, sys, warnings
import pandas as pd
import statsmodels.formula.api as smf

warnings.simplefilter("ignore")
HERE = pathlib.Path(__file__).resolve().parent.parent / "results" / "l4"
L4 = pathlib.Path("C:/vdm/l4")
out = open(sys.argv[1], "x", encoding="utf-8")


def p(*a):
    print(*a); print(*a, file=out)


rows = []
for repo in ("kopf", "kedro"):
    for r in json.load(open(HERE / f"L4_{repo}_runs.json")):
        rows.append(dict(repo=repo, task=f"{repo}:{r['task']}", cond=r["cond"], units_own=r["units_own"],
                         units_Aframe=r["units_Aframe"]))
df = pd.DataFrame(rows)
p("Pooled mixed model (A6): y ~ condition, random intercept per repository, variance component per task")
for y in ("units_own", "units_Aframe"):
    m = smf.mixedlm(f"{y} ~ C(cond, Treatment('A'))", df, groups=df["repo"], re_formula="1",
                    vc_formula={"task": "0 + C(task)"}).fit(reml=True)
    lo, hi = m.conf_int().iloc[1]
    p(f"  {y:13s} C-A = {m.params.iloc[1]:+.3f} (SE {m.bse.iloc[1]:.3f}, 95% CI {lo:+.3f}..{hi:+.3f}, p = {m.pvalues.iloc[1]:.4f}); "
      f"runs = {len(df)}, tasks = {df['task'].nunique()}")

p("\nPer-repository d_av on task means (units_own)")
for repo in ("kopf", "kedro"):
    d = df[df.repo == repo].groupby(["task", "cond"])["units_own"].mean().unstack()
    diff = d["C"] - d["A"]
    sav = ((st.stdev(d["A"]) ** 2 + st.stdev(d["C"]) ** 2) / 2) ** 0.5
    sdz = st.stdev(diff)
    p(f"  {repo}: mean diff {diff.mean():+.3f}; d_av {diff.mean() / sav:+.2f}; d_z {diff.mean() / sdz if sdz else float('nan'):+.2f}; "
      f"tasks with nonzero diff {int((diff != 0).sum())}/{len(diff)}")

p("\nHuman-change replays (units_own; apply rc 0 = PR applied)")
for repo in ("kopf", "kedro"):
    for a in sorted((L4 / repo / "results").glob("A_*_replay.json")):
        t = a.stem.split("_")[1]
        ra = json.load(open(a)); rc_ = json.load(open(L4 / repo / "results" / f"C_{t}_replay.json"))
        ma = json.load(open(L4 / repo / "runs" / f"A_{t}_replay.meta.json"))
        mc = json.load(open(L4 / repo / "runs" / f"C_{t}_replay.meta.json"))
        ok = ma.get("replay_apply_rc") == 0 and mc.get("replay_apply_rc") == 0
        p(f"  {repo} {t}: apply A={ma.get('replay_apply_rc')} C={mc.get('replay_apply_rc')}  units A={ra['units_own']} "
          f"C={rc_['units_own']}  {'compared' if ok else 'NOT COMPARED (PR did not apply)'}")
out.close()
