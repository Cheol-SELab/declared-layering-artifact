"""Deviation D4: per-task base trees. Base(A, task) = the human PR's parent commit; Base(C, task) = parent + the
frozen condition refactoring, re-applied by 3-way cherry-pick in a scratch worktree of the full clone.

Usage: python l4_bases.py <repo> <cond> <refactor_frozen_dir or '-'>
  For cond A pass '-'. For a refactored condition pass its frozen tree (e.g. C:/vdm/l4/kopf/C_frozen); the script
  commits that tree on top of the snapshot once (branch vdm-<cond>) and cherry-picks it onto every task parent.
Writes C:/vdm/l4/<repo>/bases/<cond>_<task>/ (git-initialised, LF) and bases/<cond>_<task>.json (apply status).
"""
import json, os, pathlib, shutil, subprocess, sys
import l4h

REPO, COND, FROZEN = sys.argv[1], sys.argv[2], sys.argv[3]
SRC = l4h.REPOS / REPO
OUT = l4h.L4 / REPO / "bases"
OUT.mkdir(parents=True, exist_ok=True)
WT = l4h.L4 / REPO / f"wt_{COND}"
EXTRA = {"kopf": {"kopf/_cogs/helpers/versions.py": '__version__ = version = "1.38.0"\n__version_tuple__ = version_tuple = (1, 38, 0)\n__commit_id__ = commit_id = "vdm"\n'}}


def g(*a, cwd=SRC):
    r = subprocess.run(["git", "-c", "core.autocrlf=false", "-C", str(cwd), *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def resolve_kedro_C(wt):
    """Mechanical conflict rule for the kedro C refactoring (amendment D6): when kedro/io/__init__.py conflicts because
    the task parent renamed *DataSet names, take the parent's version and apply the same edit as the frozen
    refactoring (drop the partitioned re-export block and its __all__ names); kedro/partitioned/__init__.py re-exports
    only the names the moved module defines at that parent. Any other conflicting path -> not resolved."""
    import re
    conflicted = g("diff", "--name-only", "--diff-filter=U", cwd=wt)[1].split()
    if set(conflicted) - {"kedro/io/__init__.py"}:
        return False, f"unresolvable conflicts: {conflicted}"
    p = wt / "kedro/io/__init__.py"
    g("checkout", "--ours", "--", "kedro/io/__init__.py", cwd=wt)
    s = p.read_text(encoding="utf-8")
    s = re.sub(r"^from \.partitioned_dataset import \([^)]*\)\n|^from \.partitioned_dataset import [^\n]*\n", "", s, flags=re.M)
    s = re.sub(r'^\s*"(?:Incremental|Partitioned)Data[Ss]et",\n', "", s, flags=re.M)
    p.write_text(s, encoding="utf-8", newline="\n")
    mod = (wt / "kedro/partitioned/partitioned_dataset.py").read_text(encoding="utf-8")
    names = [n for n in ("IncrementalDataSet", "IncrementalDataset", "PartitionedDataSet", "PartitionedDataset")
             if re.search(rf"^(class {n}\b|{n}:)", mod, flags=re.M)]
    init = ('"""``kedro.partitioned`` provides partitioned and incremental datasets built on\ntop of ``kedro.io``.\n"""\n'
            "from __future__ import annotations\n\nfrom .partitioned_dataset import (\n"
            + "".join(f"    {n},\n" for n in names) + ")\n\n__all__ = [\n" + "".join(f'    "{n}",\n' for n in names) + "]\n")
    (wt / "kedro/partitioned/__init__.py").write_text(init, encoding="utf-8", newline="\n")
    g("add", "kedro/io/__init__.py", "kedro/partitioned/__init__.py", cwd=wt)
    return True, f"resolved kedro/io/__init__.py by rule; partitioned exports {names}"


RESOLVERS = {"kedro": resolve_kedro_C} if COND == "C" else {}

refactor_commit = None
if FROZEN != "-":
    snap = l4h.SNAP[REPO]
    if WT.exists():
        g("worktree", "remove", "--force", str(WT))
    g("worktree", "prune")
    rc, out = g("worktree", "add", "-q", "--detach", str(WT), snap)
    assert rc == 0, out
    if FROZEN.endswith(".patch"):
        # the refactoring as a patch against the snapshot (avoids deleting snapshot files the frozen tree never tracked)
        rc, out = g("apply", "--3way", "--index", str(pathlib.Path(FROZEN).resolve()), cwd=WT)
        assert rc == 0, out
        files = None
    else:
        files = ""
    # replace the worktree content with the frozen refactored tree (tracked files only)
    rc, files = g("ls-files", cwd=FROZEN) if files is not None else (0, None)
    for f in ([] if files is None else subprocess.run(["git", "-C", str(WT), "ls-files"], capture_output=True, text=True).stdout.splitlines()):
        (WT / f).unlink(missing_ok=True)
    for f in ([] if files is None else files.splitlines()):
        dst = WT / f; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pathlib.Path(FROZEN) / f, dst)
    g("add", "-A", cwd=WT)
    rc, out = g("-c", "user.email=h@x", "-c", "user.name=harness", "commit", "-q", "-m", f"vdm condition {COND} refactoring", cwd=WT)
    assert rc == 0, out
    refactor_commit = g("rev-parse", "HEAD", cwd=WT)[1].strip()
    stat = g("show", "--stat", "--format=", "-M", refactor_commit, cwd=WT)[1]
    print("refactor commit", refactor_commit[:9]); print(stat)

for task in l4h.TASKS[REPO]:
    full = g("rev-parse", task)[1].strip()
    parent = g("rev-parse", f"{full}^")[1].strip()
    d = OUT / f"{COND}_{task}"
    if d.exists():
        shutil.rmtree(d, onerror=lambda f, p, e: (os.chmod(p, 0o700), f(p)))
    status = dict(repo=REPO, cond=COND, task=task, parent=parent, refactor_commit=refactor_commit)
    if refactor_commit:
        g("checkout", "-q", "--detach", parent, cwd=WT)
        rc, out = g("-c", "user.email=h@x", "-c", "user.name=harness", "cherry-pick", "-X", "find-renames", refactor_commit, cwd=WT)
        status["cherry_pick_rc"] = rc; status["cherry_pick_out"] = out[-800:]
        if rc != 0 and REPO in RESOLVERS:
            ok, note = RESOLVERS[REPO](WT)
            status["resolved"] = note
            if ok:
                rc = g("-c", "user.email=h@x", "-c", "user.name=harness", "-c", "core.editor=true", "cherry-pick", "--continue", cwd=WT)[0]
                status["cherry_pick_rc_after_resolve"] = rc
        if rc != 0:
            g("cherry-pick", "--abort", cwd=WT)
            (OUT / f"{COND}_{task}.json").write_text(json.dumps(status, indent=1)); print(task, "CHERRY-PICK FAILED"); continue
        tree = "HEAD"; repo_for_archive = WT
    else:
        tree = parent; repo_for_archive = SRC
    d.mkdir(parents=True)
    arch = subprocess.run(["git", "-c", "core.autocrlf=false", "-C", str(repo_for_archive), "archive", tree], capture_output=True).stdout
    subprocess.run(["tar", "-x", "-C", str(d).replace("\\", "/")], input=arch, check=True)
    for rel, content in EXTRA.get(REPO, {}).items():
        p = d / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8", newline="\n")
    l4h.init_git(d, f"base {COND} for {task} (parent {parent[:9]})")
    (OUT / f"{COND}_{task}.json").write_text(json.dumps(status, indent=1))
    print(task, "ok", parent[:9])
if refactor_commit:
    g("worktree", "remove", "--force", str(WT))
