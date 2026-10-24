"""Layer-4 pilot analysis (amendment A5 / D2). Reads C:/vdm/l4/<repo>/results/*.json; writes a report (new file).
Usage: python l4_analyze.py <repo> <out_report> [conds=A,C]
"""
import glob, json, os, random, statistics as st, sys
import numpy as np

REPO, OUT = sys.argv[1], sys.argv[2]
CONDS = (sys.argv[3] if len(sys.argv) > 3 else "A,C").split(",")
R = f"C:/vdm/l4/{REPO}"
runs = [json.load(open(f)) for f in glob.glob(f"{R}/results/*.json")]
replay = {r["task"]: r for r in runs if r["rep"] == "replay" and r["cond"] == "A"}


def ref_tests(task):
    """Spec tests that the human change makes pass (reference set), excluding e2e."""
    rp = replay.get(task)
    if not rp:
        return set()
    return {t for t, v in rp["spec_results"].items() if v == "passed" and "e2e" not in t}


def strict_pass(r):
    """Reference spec tests pass, spec untouched, layers kept, and no persistent new failure vs. the task base."""
    ref = ref_tests(r["task"])  # may be empty (e.g. a documentation task whose spec file holds no tests)
    if not r["spec_intact"]:
        return False
    if any(r["spec_results"].get(t) != "passed" for t in ref):
        return False
    return r["lint_broken"] == 0 and not r.get("new_failures_persistent", [])


out = open(OUT, "x", encoding="utf-8")
def p(*a):
    print(*a); print(*a, file=out)


agent = [r for r in runs if r["rep"] != "replay" and r["cond"] in CONDS]
tasks = sorted({r["task"] for r in agent})
for r in agent:
    r["strict"] = strict_pass(r)
p(f"Layer-4 pilot: repo={REPO}, conditions={CONDS}, runs={len(agent)}, tasks={len(tasks)}\n")
p("Human replay (condition A reference):")
for t in tasks:
    rp = replay.get(t)
    if rp:
        p(f"  {t}: files={rp['changed_code_files']} units_own={rp['units_own']} ref_tests={len(ref_tests(t))} lint_broken={rp['lint_broken']}")

metrics = ["units_own", "units_Aframe", "changed_code_files", "lines_changed"]
p("\nPer condition (all runs):")
for c in CONDS:
    rs = [r for r in agent if r["cond"] == c]
    if not rs:
        continue
    p(f"  {c}: n={len(rs)} strict_pass={sum(r['strict'] for r in rs)}/{len(rs)} lint_ok={sum(r['lint_broken'] == 0 for r in rs)}/{len(rs)} "
      + " ".join(f"{m}={st.mean(r[m] for r in rs):.2f}" for m in metrics)
      + f" bottom_own={sum(r['touches_bottom_own'] for r in rs)}/{len(rs)} bottom_A={sum(r['touches_bottom_Aframe'] for r in rs)}/{len(rs)}")


def task_means(c, m, only_pass=False):
    out_ = {}
    for t in tasks:
        v = [r[m] for r in agent if r["cond"] == c and r["task"] == t and (r["strict"] or not only_pass)]
        if v:
            out_[t] = st.mean(v)
    return out_


def paired(a, b, B=10000, seed=0):
    ks = sorted(set(a) & set(b))
    d = np.array([b[k] - a[k] for k in ks], dtype=float)
    if len(d) < 2:
        return len(d), float("nan"), float("nan"), (float("nan"), float("nan")), float("nan")
    sd = d.std(ddof=1)
    dz = d.mean() / sd if sd > 0 else 0.0
    rng = random.Random(seed); boots = []
    for _ in range(B):
        s = [d[rng.randrange(len(d))] for _ in d]
        sds = np.std(s, ddof=1)
        boots.append(np.mean(s) / sds if sds > 0 else 0.0)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    try:
        from scipy.stats import wilcoxon
        pw = wilcoxon(d).pvalue if np.any(d != 0) else 1.0
    except Exception:
        pw = float("nan")
    return len(d), d.mean(), dz, (lo, hi), pw


for only in (False, True):
    p(f"\nPaired by task ({'strict-pass runs only' if only else 'all runs'}); d_z = mean(diff)/sd(diff), 95% bootstrap CI over tasks:")
    for m in metrics:
        for a_, b_ in (("A", "C"), ("A", "B"), ("B", "C")):
            if a_ in CONDS and b_ in CONDS:
                n, md, dz, (lo, hi), pw = paired(task_means(a_, m, only), task_means(b_, m, only))
                p(f"  {m:18s} {b_}-{a_}: tasks={n} mean diff={md:+.3f} d_z={dz:+.2f} CI[{lo:+.2f},{hi:+.2f}] Wilcoxon p={pw:.3f}")

# mixed model on the primary outcome
try:
    import pandas as pd
    import statsmodels.formula.api as smf
    df = pd.DataFrame([dict(units=r["units_own"], cond=r["cond"], task=r["task"]) for r in agent])
    m = smf.mixedlm("units ~ C(cond, Treatment('A'))", df, groups=df["task"]).fit(reml=True)
    p("\nMixed model units_own ~ condition + (1|task):")
    p(m.summary().tables[1].to_string())
except Exception as e:
    p("mixed model failed:", e)

p("\nH3 decision (pre-registered): C < A on units_own with d >= 0.3 -> supported; d < 0.1 or C >= A -> disconfirmed.")
n, md, dz, ci, pw = paired(task_means("A", "units_own"), task_means("C", "units_own"))
verdict = "supported" if (md < 0 and -dz >= 0.3) else ("disconfirmed" if (md >= 0 or -dz < 0.1) else "inconclusive (0.1 <= d < 0.3)")
p(f"  C-A units_own: mean diff {md:+.3f}, d_z {dz:+.2f} -> H3 {verdict} (pilot, {n} tasks)")

# the human change itself replayed on each condition's base: deterministic, free of agent variance
rp_c = {c: {r["task"]: r for r in runs if r["rep"] == "replay" and r["cond"] == c} for c in CONDS}
p("\nHuman change replayed on each base (units touched by the same PR):")
for m in ("units_own", "units_Aframe", "changed_code_files"):
    for a_, b_ in (("A", "C"), ("A", "B")):
        if a_ in CONDS and b_ in CONDS:
            ks = sorted(set(rp_c[a_]) & set(rp_c[b_]))
            diffs = [rp_c[b_][k][m] - rp_c[a_][k][m] for k in ks]
            if ks:
                p(f"  {m:18s} {b_}-{a_}: tasks={len(ks)} sum diff={sum(diffs):+d} per task={diffs}")

# agent cost: last logged usage per run
usage = {}
upath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "l4_usage.jsonl")
if os.path.exists(upath):
    for line in open(upath, encoding="utf-8"):
        u = json.loads(line)
        if u["repo"] == REPO:
            usage[(u["cond"], u["task"], u["rep"])] = u
p("\nAgent cost (sub-agent tokens, tool uses, minutes; last logged entry per run):")
for c in CONDS:
    us = [usage[k] for k in usage if k[0] == c and any(r["cond"] == c and r["task"] == k[1] and r["rep"] == k[2] for r in agent)]
    if us:
        p(f"  {c}: n={len(us)} tokens mean={st.mean(u['subagent_tokens'] for u in us):.0f} median={st.median(u['subagent_tokens'] for u in us):.0f} "
          f"tools mean={st.mean(u['tool_uses'] for u in us):.1f} minutes mean={st.mean(u['duration_ms'] for u in us) / 60000:.1f}")
p("Runs editing non-specification test files: "
  + (", ".join(f"{r['cond']}_{r['task']}_{r['rep']}" for r in agent if r.get("other_test_files_edited")) or "none"))
gate = [r for r in agent if r["cond"] == "C"]
p(f"Stop rule check: C strict acceptance {sum(r['strict'] for r in gate)}/{len(gate)}")
with open(OUT.replace(".txt", "_runs.json"), "x") as fh:
    json.dump([{k: r[k] for k in ("cond", "task", "rep", "strict", "units_own", "units_Aframe", "changed_code_files",
                                  "lines_changed", "lint_broken", "touches_bottom_own", "touches_bottom_Aframe")} for r in agent], fh, indent=1)
