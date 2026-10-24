"""Create the randomized run schedule, prepare isolated run directories and write one prompt file per run.
Usage: python l4_schedule.py <repo> <conds e.g. A,C> <reps> <prompt_dir>
"""
import json, os, random, sys, concurrent.futures as cf
import l4h

REPO, CONDS, REPS, PDIR = sys.argv[1], sys.argv[2].split(","), int(sys.argv[3]), sys.argv[4]
_tdir = os.path.dirname(PDIR.rstrip("/\\"))
_tp = os.path.join(_tdir, f"l4_prompt_template_{REPO}.md")
TEMPLATE = open(_tp if os.path.exists(_tp) else os.path.join(_tdir, "l4_prompt_template.md"), encoding="utf-8").read()
runs = [(c, t, f"r{k + 1}") for c in CONDS for t in l4h.TASKS[REPO] for k in range(REPS)]
random.Random(20261005).shuffle(runs)
os.makedirs(PDIR, exist_ok=True)


def one(run):
    c, t, rep = run
    d, meta = l4h.prep(REPO, c, t, rep)
    rd = str(d).replace("\\", "/")
    prompt = (TEMPLATE.replace("{RUN_DIR}", rd).replace("{MESSAGE}", meta["message"])
              .replace("{SPEC_LIST}", "\n".join(f"- `{s}`" for s in meta["spec"]))
              .replace("{SPEC_ARGS}", " ".join(meta["spec"])))
    p = os.path.join(PDIR, f"{c}_{t}_{rep}.md")
    with open(p, "x", encoding="utf-8", newline="\n") as fh:
        fh.write(prompt)
    return run, sum(1 for v in meta["pre_spec"].values() if v == "failed")


with cf.ThreadPoolExecutor(6) as ex:
    res = list(ex.map(one, runs))
sched = [dict(order=i, cond=c, task=t, rep=rep, pre_failed=pf) for i, ((c, t, rep), pf) in enumerate(res)]
with open(os.path.join(PDIR, "schedule.json"), "x") as fh:
    json.dump(sched, fh, indent=1)
for s in sched:
    print(s)
