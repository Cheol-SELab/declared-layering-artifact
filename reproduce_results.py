"""Recompute the manuscript's derived reports (registered and post hoc) from the archived records and compare
them with the stored reports.

The study scripts are run unchanged except that the evaluation host's record root (C:/vdm/l4) is redirected to
this package's layer4/ directory. Everything runs in a temporary copy of the package; the package is not modified.
Requires Python 3.11+, numpy, scipy, pandas and statsmodels. No agent is run.
Usage: python -B reproduce_results.py [--clones <dir>]
  --clones <dir>  also re-mine the subject repositories from clones made by posthoc/fetch_clones.py
                  (posthoc_s2n_variants.py and posthoc_rq2.py); without it these two reports are skipped.
"""
from pathlib import Path
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
CHECKS = [
    # (script and arguments relative to study/scripts, stored report relative to study/)
    (["l4_analyze.py", "kopf", "{out}"], "results/l4/L4_kopf.txt"),
    (["l4_analyze.py", "kedro", "{out}"], "results/l4/L4_kedro_E4.txt"),
    (["l4_pooled.py", "{out}"], "results/l4/L4_pooled.txt"),
    (["l1_robustness.py", "../results/l1/l1_quarters_v2.csv", "{out}"], "results/l1/L1_robustness.txt"),
    (["pop_stats.py", "../data/pop_decl_history.json", "{out}"], "results/pop_stats.txt"),
]
# Post hoc analyses (not registered), run from posthoc/ in the temporary copy.
POSTHOC = [
    (["posthoc_l1.py", "../study/results/l1/l1_quarters_v2.csv", "{out}"], "results/posthoc_l1.txt"),
    (["posthoc_l4.py", "{out}"], "results/posthoc_l4.txt"),
    (["posthoc_l1_extra.py", "../study/results/l1/l1_quarters_v2.csv", "../pilot/blind_scan_bk-user.txt", "{out}"],
     "results/posthoc_l1_extra.txt"),
    (["posthoc_l4_extra.py", "../study/results/l4", "../layer4", "../study/data/l4_baseline.json", "{out}"],
     "results/posthoc_l4_extra.txt"),
    (["posthoc_pop.py", "../study/data/gh_decl.json", "../study/data/pop_decl_history.json", "{out}"],
     "results/posthoc_pop.txt"),
]
# Post hoc analyses that re-mine the subject repositories; run only with --clones <dir> (see posthoc/fetch_clones.py).
WITH_CLONES = [
    (["posthoc_s2n_variants.py", "{clones}", "../study/results/l1/l1_quarters_v2.csv", "{out}"],
     "results/posthoc_s2n_variants.txt"),
    (["posthoc_rq2.py", "{clones}", "../study/data/layer2_proposals.json", "{out}"], "results/posthoc_rq2.txt"),
]


def main():
    clones = sys.argv[sys.argv.index("--clones") + 1] if "--clones" in sys.argv else None
    failures = 0
    with tempfile.TemporaryDirectory(prefix="vdm-repro-") as tmp:
        study = Path(tmp) / "study"
        shutil.copytree(ROOT / "study", study)
        shutil.copytree(ROOT / "posthoc", Path(tmp) / "posthoc")
        shutil.copytree(ROOT / "pilot", Path(tmp) / "pilot")
        shutil.copytree(ROOT / "layer4", Path(tmp) / "layer4")
        for script in (study / "scripts").glob("*.py"):
            text = script.read_text(encoding="utf-8")
            script.write_text(text.replace("C:/vdm/l4", (ROOT / "layer4").as_posix()), encoding="utf-8")
        jobs = [(args, stored, study / "scripts", study) for args, stored in CHECKS]
        jobs += [(args, stored, Path(tmp) / "posthoc", Path(tmp) / "posthoc") for args, stored in POSTHOC]
        if clones:
            jobs += [(args, stored, Path(tmp) / "posthoc", Path(tmp) / "posthoc") for args, stored in WITH_CLONES]
        else:
            print("skipped (no --clones): " + ", ".join(stored for _, stored in WITH_CLONES))
        for n, (args, stored, cwd, base) in enumerate(jobs):
            out = Path(tmp) / f"out{n}.txt"
            cmd = [sys.executable, "-B", "-W", "ignore"] + [a.replace("{out}", str(out)).replace("{clones}", str(clones))
                                                          for a in args]
            # git output of the subject repositories is UTF-8; the clone-based scripts need Python's UTF-8 mode
            env = {**os.environ, "PYTHONUTF8": "1"} if "{clones}" in args else None
            run = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                 env=env)
            same = run.returncode == 0 and filecmp.cmp(out, base / stored, shallow=False)
            failures += not same
            print(f"{'OK  ' if same else 'DIFF'} {' '.join(args[:-1] if args[-1] == '{out}' else args)} -> {stored}")
            if run.returncode:
                print(run.stderr[-2000:])
    print("all reports reproduced" if not failures else f"{failures} report(s) differ")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
