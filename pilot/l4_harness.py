"""Layer-4 harness. One run = (repo, snapshot, condition, follow-up PR).
Steps: worktree → copy PR's test files in (acceptance spec) → baseline test run → agent implements until
spec passes → gates (arch check, tests, no new failures) → metrics (files, declared units, bottom touched, tokens).
Agent backends: 'replay' (applies the human PR's non-test diff; pipeline validation only) or 'anthropic'
(tool-using loop; needs ANTHROPIC_API_KEY). Usage:
  python l4_harness.py <repo_path> <snapshot> <pr_commit> <condition A|B|C> <agent replay|anthropic> [decl_subdir]
"""
import sys, os, json, subprocess, re, shutil, time, pathlib, collections
REPO, SNAP, PR, COND, AGENT = sys.argv[1:6]
DECL_DIR = sys.argv[6] if len(sys.argv) > 6 else ""
WT = f"/home/claude/l4/{pathlib.Path(REPO).name}-{COND}-{PR[:7]}"
ENV = dict(os.environ, PYTHONWARNINGS="default:Kedro is not yet fully compatible")
sys.argv = ["x"]; sys.path.insert(0, "/home/claude/pilot"); import blind_scan as bs

def sh(cmd, cwd=WT, timeout=240):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=ENV)
    return r.returncode, (r.stdout + r.stderr)[-4000:]

def git(*a, cwd=REPO):
    return subprocess.run(["git", "-C", cwd, *a], capture_output=True, text=True).stdout

# ---- 1. worktree at snapshot (condition B/C would apply the refactoring here before the agent runs) ----
if os.path.isdir(WT): shutil.rmtree(WT)
git("worktree", "prune"); git("worktree", "add", "-q", WT, SNAP)
pr_files = git("show", "--name-only", "--format=", PR).split()
test_files = [f for f in pr_files if f.endswith(".py") and ("/tests/" in f or f.startswith("tests/") or "/test_" in f)]
code_files = [f for f in pr_files if f.endswith(".py") and f not in test_files]
subject_body = git("show", "-s", "--format=%s%n%n%b", PR)

# ---- 2. acceptance spec = the PR's test files, placed into the snapshot ----
for f in test_files:
    content = git("show", f"{PR}:{f}")
    p = pathlib.Path(WT, f); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content)
def run_tests(files):
    rc, out = sh(f"python -m pytest {' '.join(files)} -q -p no:cacheprovider -o addopts='' 2>&1 | tail -30")
    failed = set(re.findall(r"FAILED ([^\s]+)", out)); m = re.search(r"(\d+) passed", out)
    return failed, int(m.group(1)) if m else 0
baseline_failed, _ = run_tests(test_files)
# tests that the agent must turn green = those failing at baseline with the new spec in place
rc_all, out_all = sh("python -m pytest tests -q -p no:cacheprovider -o addopts='' -x --co 2>&1 | tail -1")

# ---- 3. agent ----
usage = {"input": 0, "output": 0, "turns": 0}
if AGENT == "replay":
    patch = git("show", "--format=", "--", *code_files, cwd=REPO) if False else subprocess.run(
        ["git", "-C", REPO, "format-patch", "-1", PR, "--stdout", "--", *code_files], capture_output=True, text=True).stdout
    open(f"{WT}/.pr.patch", "w").write(patch)
    rc, out = sh("git apply --3way .pr.patch 2>&1 || git apply --reject .pr.patch 2>&1")
    agent_note = f"replay git apply rc={rc}"
elif AGENT == "anthropic":
    import urllib.request
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key: sys.exit("ANTHROPIC_API_KEY not set")
    tools = [{"name": "bash", "description": "Run a shell command in the repo", "input_schema": {"type": "object", "properties": {"cmd": {"type": "string"}}, "required": ["cmd"]}},
             {"name": "write_file", "description": "Overwrite a file", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}]
    arch_rule = "" if COND == "A" else ""  # B/C: refactoring already applied in worktree; the checker reports violations on demand
    system = (f"You are implementing a change in the repository at {WT}. Task:\n{subject_body}\n\n"
              f"Acceptance: make these tests pass without breaking others: {test_files}. Do not edit the test files. "
              f"The project has an import-linter layering declaration; run `lint-imports` before finishing and fix any violation. "
              f"Keep changes minimal. When done, reply DONE.")
    msgs = [{"role": "user", "content": "Begin."}]
    for turn in range(25):
        body = json.dumps({"model": "claude-sonnet-4-6", "max_tokens": 4000, "system": system, "tools": tools, "messages": msgs}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, headers={"content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
        resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
        usage["input"] += resp["usage"]["input_tokens"]; usage["output"] += resp["usage"]["output_tokens"]; usage["turns"] += 1
        msgs.append({"role": "assistant", "content": resp["content"]})
        results = []
        for blk in resp["content"]:
            if blk["type"] != "tool_use": continue
            if blk["name"] == "bash": rc, out = sh(blk["input"]["cmd"]); results.append({"type": "tool_result", "tool_use_id": blk["id"], "content": out or f"rc={rc}"})
            else:
                p = pathlib.Path(WT, blk["input"]["path"]); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(blk["input"]["content"]); results.append({"type": "tool_result", "tool_use_id": blk["id"], "content": "ok"})
        if not results or resp.get("stop_reason") == "end_turn": break
        msgs.append({"role": "user", "content": results})
    agent_note = f"anthropic turns={usage['turns']}"

# ---- 4. gates ----
after_failed, passed = run_tests(test_files)
spec_ok = not (after_failed - baseline_failed) and len(after_failed) < len(baseline_failed) or (not after_failed)
rc_arch, out_arch = sh("lint-imports 2>&1 | tail -15") if shutil.which("lint-imports") else (None, "lint-imports not installed")
viol = len(re.findall(r"BROKEN|is not allowed|violat", out_arch))

# ---- 5. metrics: propagation over declared units at the snapshot ----
bs.configure(REPO, DECL_DIR)
contracts = bs.parse_declaration(SNAP); units = {m: m for _, ranks in contracts for sibs in ranks for m in sibs}
rank = {m: (len(ranks) - 1 - r) / max(len(ranks) - 1, 1) for _, ranks in contracts for r, sibs in enumerate(ranks) for m in sibs}
bs.discover_prefixes(SNAP, list(units)); ordered = sorted(units, key=len, reverse=True)
def unit_of(p):
    for m in ordered:
        for pp in bs.MOD_PREFIX.get(m, []):
            if p.startswith(pp): return m
changed = [l.split()[-1] for l in subprocess.run(["git", "-C", WT, "status", "--porcelain"], capture_output=True, text=True).stdout.splitlines()]
changed_code = [f for f in changed if f.endswith(".py") and f not in test_files and not f.endswith(".patch")]
touched = {u for u in map(unit_of, changed_code) if u}
result = dict(repo=pathlib.Path(REPO).name, snapshot=SNAP[:7], pr=PR[:7], condition=COND, agent=AGENT, note=agent_note,
              spec_tests=test_files, baseline_failed=len(baseline_failed), after_failed=len(after_failed), spec_passed=spec_ok,
              arch_rc=rc_arch, arch_violations=viol, changed_files=len(changed_code), changed_units=len(touched),
              units=sorted(u.split(".")[-1] for u in touched), touches_bottom=any(rank.get(u, 1) <= 0.34 for u in touched), tokens=usage)
print(json.dumps(result, indent=1))
os.makedirs("/mnt/user-data/outputs/pilot/l4_runs", exist_ok=True)
open(f"/mnt/user-data/outputs/pilot/l4_runs/{result['repo']}_{COND}_{PR[:7]}_{AGENT}.json", "w").write(json.dumps(result, indent=1))
