"""Layer-4 harness (amendment A5 / deviation D2).

Sub-commands
  base <repo> <cond> <frozen_dir>          register a frozen condition tree (git-initialised, single commit)
  suite <repo> <cond>                       full-suite baseline of a frozen tree (junit -> results)
  prep <repo> <cond> <task> <rep>           create an isolated run dir: frozen tree + the PR's test files (spec)
  replay <repo> <cond> <task>               apply the human PR's non-test diff into a fresh run dir (reference)
  eval <repo> <cond> <task> <rep|replay>    measure a finished run (never trusts the agent's report)

Layout: C:/vdm/l4/<repo>/{<cond>_frozen, runs/<cond>_<task>_<rep>, results/*.json}; tests run in WSL via ~/vdm/bin/kt.
Move maps for refactored conditions: C:/vdm/l4/<repo>/<cond>_moves.json  {"old.module": "new.module", ...}
"""
import hashlib, json, os, pathlib, re, shutil, subprocess, sys, tarfile, io, time
import xml.etree.ElementTree as ET
import blind_scan as bs

L4 = pathlib.Path("C:/vdm/l4")
REPOS = pathlib.Path("C:/vdm/repos")
SNAP = {"kopf": "51b664fa12087cacd62a46b6bcdf8daf3dbc64fc", "kedro": "e9a07bb7344fa9b1b7cad1e50bbca5ae4aea9ca0"}
TASKS = {"kopf": ["bad8649", "51c078d", "91f7ae0", "e2c7056", "017dbe0", "624c6d2", "f325f02", "956cd65", "a6403c4", "20de08c"],
         "kedro": ["2f526b6", "3f2a226", "2297d23", "ab576bc", "69a6fe1", "60f676e"]}
# kedro tasks excluded before any kedro run (deviation D6): cd83bad, 0cd8ecc (parent on a divergent pre-0.19 line; C does not
# re-apply), 00f035a, 5752f68 (target module already removed upstream by 60f676e)
TASKS_KEDRO_REGISTERED = ["2f526b6", "3f2a226", "2297d23", "ab576bc", "cd83bad", "0cd8ecc", "69a6fe1", "60f676e", "00f035a", "5752f68"]
SPEC_ARGS = {"kopf": ["-q", "--timeout=120"], "kedro": ["-q", "-p", "no:cov", "-o", "addopts=", "--timeout=300"]}
FULL_ARGS = {"kopf": ["tests", "--ignore=tests/e2e", "-q", "--timeout=600", "--timeout_method=signal"],
             "kedro": ["tests", "-q", "-p", "no:cov", "-o", "addopts=", "--timeout=300", "--timeout_method=signal", "-n", "8"]}


def run(cmd, cwd=None, timeout=3600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def git(d, *a):
    return run(["git", "-C", str(d), *a])[1]


def venv_for(run_dir):
    """WSL venv of the repository a run/base directory belongs to (kedro needs its own interpreter and deps)."""
    return "~/vdm/venv-kedro" if "/kedro/" in str(run_dir).replace("\\", "/") else "~/vdm/venv-kopf"


def wsl_kt(run_dir, *args, timeout=3600):
    return run(["wsl", "-e", "bash", "-lc", f"VDM_VENV={venv_for(run_dir)} ~/vdm/bin/kt " + " ".join(f"'{x}'" for x in [str(run_dir).replace("\\", "/"), *args])], timeout=timeout)


def junit(run_dir, rel_xml):
    p = pathlib.Path(run_dir) / rel_xml
    if not p.exists():
        return {}
    out = {}
    for tc in ET.parse(p).getroot().iter("testcase"):
        tid = f"{tc.get('classname')}::{tc.get('name')}"
        st = "passed"
        for ch in tc:
            if ch.tag in ("failure", "error"):
                st = "failed"
            elif ch.tag == "skipped":
                st = "skipped"
        out[tid] = st
    return out


def pytest_junit(run_dir, args, tag, timeout=3600):
    """Run pytest in WSL; junit XML is written in WSL /tmp and read back. Returns (rc, tail, {test_id: status})."""
    import uuid
    tag_id = f"/tmp/vdm_{uuid.uuid4().hex}"
    xml = tag_id + ".xml"
    # detached inside WSL (setsid/nohup) so that Windows-side process-tree kills of wsl.exe cannot truncate a long run;
    # completion is detected by polling for the exit-code file
    q = " ".join(f"'{x}'" for x in [str(run_dir).replace("\\", "/"), *args, f"--junitxml={xml}"])
    pre = f"VDM_VENV={venv_for(run_dir)} "
    subprocess.run(["wsl", "-e", "bash", "-lc", f"{pre}setsid -f ~/vdm/bin/ktd {tag_id} {q} < /dev/null > /dev/null 2>&1"],
                   capture_output=True, timeout=120)
    t0 = time.time(); rc = None
    while time.time() - t0 < timeout:
        time.sleep(10)
        p = subprocess.run(["wsl", "-e", "bash", "-lc", f"cat {tag_id}.rc 2>/dev/null"], capture_output=True, text=True, timeout=120)
        if p.stdout.strip().lstrip("-").isdigit():  # wsl.exe transport errors (UTF-16 text) are transient: keep polling
            rc = int(p.stdout.strip()); break
    out = subprocess.run(["wsl", "-e", "bash", "-lc", f"tail -c 4000 {tag_id}.log; rm -f {tag_id}.log {tag_id}.rc"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120).stdout
    if rc is None:
        rc = -1; out += " [harness] timeout"
    r = subprocess.run(["wsl", "-e", "bash", "-lc", f"cat {xml} && rm -f {xml}"], capture_output=True, timeout=600)
    res = {}
    raw = r.stdout
    i = raw.find(b"<testsuites"); i = raw.find(b"<testsuite") if i < 0 else i
    if r.returncode == 0 and i >= 0:
        try:
            root = ET.fromstring(raw[i:])
        except ET.ParseError:
            return rc, out[-3000:] + " [harness] junit parse error", res
        for tc in root.iter("testcase"):
            tid = f"{tc.get('classname')}::{tc.get('name')}"
            st = "passed"
            for ch in tc:
                if ch.tag in ("failure", "error"):
                    st = "failed"
                elif ch.tag == "skipped":
                    st = "skipped"
            res[tid] = st
    return rc, out[-3000:], res


def init_git(d, msg):
    git(d, "init", "-q"); git(d, "config", "user.email", "h@x"); git(d, "config", "user.name", "harness")
    git(d, "config", "core.autocrlf", "false")
    git(d, "add", "-A"); git(d, "commit", "-q", "-m", msg)


def task_info(repo, task):
    src = REPOS / repo
    full = git(src, "rev-parse", task).strip()
    files = [f for f in git(src, "show", "--name-only", "--format=", full).splitlines() if f.strip()]  # paths may contain spaces
    tests = [f for f in files if f.endswith(".py") and (f.startswith("tests/") or "/tests/" in f or "/test_" in f)]
    if repo == "kedro":  # project-template and starter test files are not runnable tests of the package
        tests = [f for f in tests if f.startswith("tests/")]
    code = [f for f in files if f.endswith(".py") and f not in tests and "/tests/" not in f]
    msg = git(src, "show", "-s", "--format=%s%n%n%b", full).strip()
    return dict(commit=full, tests=tests, code=code, message=msg, all_files=files)


def moves(repo, cond):
    p = L4 / repo / f"{cond}_moves.json"
    return json.loads(p.read_text()) if p.exists() else {}


def translate(text, mv):
    for old, new in sorted(mv.items(), key=lambda kv: -len(kv[0])):
        text = re.sub(rf"\b{re.escape(old)}\b", new, text)
        text = text.replace(old.replace(".", "/"), new.replace(".", "/"))
        o_par, o_leaf = old.rsplit(".", 1); n_par, n_leaf = new.rsplit(".", 1)
        text = re.sub(rf"from {re.escape(o_par)} import ([^\n]*)\b{o_leaf}\b",
                      lambda m: f"from {o_par} import {m.group(1)}{o_leaf}" if n_par == o_par else m.group(0), text)
    return text


def fix_from_imports(text, mv):
    """`from a.b import leaf` where a.b.leaf moved to x.y.leaf -> `from x.y import leaf` (spec translation only)."""
    for old, new in mv.items():
        o_par, o_leaf = old.rsplit(".", 1); n_par, n_leaf = new.rsplit(".", 1)
        def rep(m):
            names = [n.strip() for n in m.group(1).split(",") if n.strip()]
            if o_leaf not in [n.split(" as ")[0] for n in names]:
                return m.group(0)
            rest = [n for n in names if n.split(" as ")[0] != o_leaf]
            moved = [n for n in names if n.split(" as ")[0] == o_leaf]
            lines = [f"from {n_par} import {', '.join(n.replace(o_leaf, n_leaf, 1) for n in moved)}"]
            if rest:
                lines.insert(0, f"from {o_par} import {', '.join(rest)}")
            return "\n".join(lines)
        text = re.sub(rf"^from {re.escape(o_par)} import ([^\n(]+)$", rep, text, flags=re.M)
        # parenthesised (possibly multi-line) form: from a.b import (x, leaf, y)
        def rep_par(m):
            names = [n.strip() for n in m.group(1).replace("\n", " ").split(",") if n.strip()]
            if o_leaf not in [n.split(" as ")[0] for n in names]:
                return m.group(0)
            rest = [n for n in names if n.split(" as ")[0] != o_leaf]
            moved = [n for n in names if n.split(" as ")[0] == o_leaf]
            lines = [f"from {n_par} import {', '.join(n.replace(o_leaf, n_leaf, 1) for n in moved)}"]
            if rest:
                lines.insert(0, f"from {o_par} import ({', '.join(rest)})")
            return "\n".join(lines)
        text = re.sub(rf"^from {re.escape(o_par)} import \(([^)]*)\)", rep_par, text, flags=re.M)
    return text


def run_dir(repo, cond, task, rep):
    return L4 / repo / "runs" / f"{cond}_{task}_{rep}"


def prep(repo, cond, task, rep, replay=False):
    frozen = L4 / repo / "bases" / f"{cond}_{task}"  # D4: per-task base (PR parent [+ refactoring])
    d = run_dir(repo, cond, task, rep)
    if d.exists():
        sys.exit(f"exists: {d}")
    shutil.copytree(frozen, d, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    info = task_info(repo, task)
    mv = moves(repo, cond)
    spec = []
    for f in info["tests"]:
        if subprocess.run(["git", "-C", str(REPOS / repo), "cat-file", "-e", f"{info['commit']}:{f}"]).returncode != 0:
            continue  # test file deleted by the PR: not part of the acceptance specification
        content = git(REPOS / repo, "show", f"{info['commit']}:{f}")
        if mv:
            content = fix_from_imports(translate(content, mv), mv)
        p = d / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline="\n")
        spec.append(f)
    init_git(d, "snapshot + acceptance spec")
    meta = dict(repo=repo, cond=cond, task=task, rep=rep, commit=info["commit"], spec=spec, code_in_pr=info["code"],
                spec_sha={f: hashlib.sha256((d / f).read_bytes()).hexdigest() for f in spec}, message=info["message"],
                moves=mv, created=time.strftime("%Y-%m-%dT%H:%M:%S"))
    # baseline: spec tests with the spec in place, before any implementation
    rc, out, res = pytest_junit(d, [*spec, *SPEC_ARGS[repo]], "pre")
    meta["pre_spec"] = res
    (d.parent / f"{d.name}.meta.json").write_text(json.dumps(meta, indent=1))
    if replay:
        patch = run(["git", "-C", str(REPOS / repo), "format-patch", "-1", info["commit"], "--stdout", "--", *info["code"]])[1]
        if mv:
            patch = translate(patch, mv)
        (d / ".pr.patch").write_text(patch, encoding="utf-8", newline="\n")
        rc, out = run(["git", "-C", str(d), "apply", "--3way", ".pr.patch"])
        (d / ".pr.patch").unlink()
        meta["replay_apply_rc"] = rc; meta["replay_apply_out"] = out[-1500:]
        (d.parent / f"{d.name}.meta.json").write_text(json.dumps(meta, indent=1))
    return d, meta


def units_for(tree_repo, commit="HEAD"):
    """Declared units (incl. expansion) of a git tree, as the scanner defines them."""
    bs.configure(str(tree_repo))
    contracts = bs.parse_declaration(commit) or []
    units, rank_in = {}, {}
    for cid, ranks in contracts:
        for r, sibs in enumerate(ranks):
            for m in sibs:
                units[m] = m; rank_in.setdefault(m, {})[cid] = (len(ranks) - 1 - r) / max(len(ranks) - 1, 1)
    bs.discover_prefixes(commit, list(units))
    prefix = dict(bs.MOD_PREFIX)
    names = bs.git("ls-tree", "-r", "--name-only", commit).splitlines()
    done = set()
    while True:
        todo = [U for U in units if U not in done and any(v != U and v.startswith(U + ".") for v in units)]
        if not todo:
            break
        for U in todo:
            done.add(U)
            for pp in prefix.get(U, []):
                if not pp.endswith("/"):
                    continue
                for sd in {n[len(pp):].split("/")[0] for n in names if n.startswith(pp) and "/" in n[len(pp):]}:
                    if sd.startswith("_") or sd in ("migrations", "tests"):
                        continue
                    c = f"{U}.{sd}"
                    if c not in units:
                        units[c] = c; prefix[c] = [pp + sd + "/"]; rank_in[c] = dict(rank_in.get(U, {}))
    ordered = sorted(units, key=len, reverse=True)

    def unit_of(p):
        for m in ordered:
            for pp in prefix.get(m, []):
                if p.startswith(pp):
                    return m
    bottom = {m for m, rk in rank_in.items() if any(v <= 0.34 for v in rk.values())}
    return unit_of, bottom


def evaluate(repo, cond, task, rep):
    d = run_dir(repo, cond, task, rep)
    meta = json.loads((d.parent / f"{d.name}.meta.json").read_text())
    git(d, "add", "-A")
    ns = git(d, "diff", "--cached", "-M", "--name-status", "HEAD").splitlines()
    numstat = git(d, "diff", "--cached", "-M", "--numstat", "HEAD").splitlines()
    git(d, "reset", "-q")
    changed = []
    for l in ns:
        parts = l.split("\t")
        changed += parts[1:]
    spec = set(meta["spec"])
    code = sorted({f for f in changed if f.endswith(".py") and f not in spec and not f.startswith("tests/")
                   and "/tests/" not in f and not f.endswith(".patch")})
    test_edits = sorted({f for f in changed if f.endswith(".py") and f not in spec and (f.startswith("tests/") or "/tests/" in f)})
    lines = 0
    for l in numstat:
        a, b, f = (l.split("\t") + ["", ""])[:3]
        if f.endswith(".py") and f.split(" => ")[-1].rstrip("}") not in spec and not f.startswith("tests/"):
            lines += (int(a) if a.isdigit() else 0) + (int(b) if b.isdigit() else 0)
    spec_intact = all(hashlib.sha256((d / f).read_bytes()).hexdigest() == h for f, h in meta["spec_sha"].items() if (d / f).exists())
    # propagation under the condition's own declaration (declaration as it stands at the run's initial commit)
    unit_of, bottom = units_for(d, "HEAD")
    own = sorted({u for u in map(unit_of, code) if u})
    # A-frame: map moved modules back to the snapshot unit
    inv = {v.replace(".", "/"): k.replace(".", "/") for k, v in meta.get("moves", {}).items()}
    def back(p):
        for n, o in sorted(inv.items(), key=lambda kv: -len(kv[0])):
            if p.startswith(n + "/") or p == n + ".py":
                return o + p[len(n):]
        return p
    unit_A, bottom_A = units_for(L4 / repo / "bases" / f"A_{task}", "HEAD")
    aframe = sorted({u for u in (unit_A(back(f)) for f in code) if u})
    # tests
    rc_s, out_s, spec_res = pytest_junit(d, [*meta["spec"], *SPEC_ARGS[repo]], "spec")
    rc_l, out_l = wsl_kt(d, "--lint")
    broken = re.search(r"(\d+) broken", out_l)
    rc_f, out_f, full = pytest_junit(d, FULL_ARGS[repo], "full", timeout=5400)
    if not full:  # harness-level failure (no junit read back): retry once, then fail loudly rather than record zeros
        rc_f, out_f, full = pytest_junit(d, FULL_ARGS[repo], "full", timeout=5400)
        if not full:
            raise RuntimeError(f"full suite produced no junit results (rc={rc_f}): {out_f[-800:]}")
    # flaky-test guard: failures that passed in the (cond, task) base are re-run once; only persistent ones count
    base_p = L4 / repo / "bases" / f"suite_{cond}_{task}.json"
    base_failed = set(json.loads(base_p.read_text())["failed"]) if base_p.exists() else set()
    spec_mods = {s.replace("/", ".").removesuffix(".py") for s in meta["spec"]}
    cand = sorted(t for t, v in full.items() if v == "failed" and t not in base_failed and not any(t.startswith(m) for m in spec_mods))
    persistent = []
    if cand:
        node_ids = []
        for t in cand:
            mod, name = t.rsplit("::", 1)
            parts = mod.split(".")
            # classname "tests.a.b.test_x.TestCls" or "tests.a.b.test_x"
            for k in range(len(parts), 0, -1):
                f = "/".join(parts[:k]) + ".py"
                if (d / f).exists():
                    node_ids.append(f + "::" + "::".join(parts[k:] + [name]))
                    break
        rc_r, out_r, rer = pytest_junit(d, [*node_ids[:300], "-q", "-p", "no:cov", "-o", "addopts=", "--timeout=300"], "rerun", timeout=3600)
        persistent = sorted(t for t in cand if rer.get(t, "failed") == "failed")
    res = dict(repo=repo, cond=cond, task=task, rep=rep, commit=meta["commit"][:7], spec_files=meta["spec"],
               new_failures_candidates=cand, new_failures_persistent=persistent,
               changed_code_files=len(code), code_files=code, lines_changed=lines, other_test_files_edited=test_edits,
               units_own=len(own), units_own_list=own, units_Aframe=len(aframe), units_Aframe_list=aframe,
               touches_bottom_own=any(u in bottom for u in own), touches_bottom_Aframe=any(u in bottom_A for u in aframe),
               spec_intact=spec_intact, spec_results=spec_res, pre_spec=meta.get("pre_spec", {}),
               lint_rc=rc_l, lint_broken=int(broken.group(1)) if broken else None, lint_tail=out_l[-600:],
               full_counts={k: sum(1 for v in full.values() if v == k) for k in ("passed", "failed", "skipped")},
               full_failed=sorted(t for t, v in full.items() if v == "failed")[:200], full_rc=rc_f,
               evaluated=time.strftime("%Y-%m-%dT%H:%M:%S"))
    out = L4 / repo / "results" / f"{cond}_{task}_{rep}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    cmd, *a = sys.argv[1:]
    if cmd == "prep":
        d, meta = prep(a[0], a[1], a[2], a[3]); print(d); print(json.dumps({k: meta[k] for k in ("spec", "code_in_pr")}))
    elif cmd == "replay":
        d, meta = prep(a[0], a[1], a[2], "replay", replay=True); print(d, meta.get("replay_apply_rc"))
    elif cmd == "eval":
        r = evaluate(a[0], a[1], a[2], a[3])
        print(json.dumps({k: r[k] for k in ("cond", "task", "rep", "changed_code_files", "lines_changed", "units_own", "units_Aframe",
                                            "spec_intact", "lint_broken", "full_counts")}))
    elif cmd == "info":
        print(json.dumps(task_info(a[0], a[1]), indent=1))
