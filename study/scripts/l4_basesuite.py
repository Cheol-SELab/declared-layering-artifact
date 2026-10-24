"""Lint + full-suite baseline for every per-task base: C:/vdm/l4/<repo>/bases/suite_<cond>_<task>.json"""
import concurrent.futures as cf, json, re, sys
import l4h
REPO, CONDS = sys.argv[1], sys.argv[2].split(",")
def one(ct):
    c, t = ct
    d = l4h.L4 / REPO / "bases" / f"{c}_{t}"
    rc_l, out_l = l4h.wsl_kt(d, "--lint")
    m = re.search(r"(\d+) broken", out_l)
    attempts = []
    for _ in range(2):  # D5 rule: an empty JUnit result is re-run once, then fails loudly (no record is written)
        rc, out, res = l4h.pytest_junit(d, l4h.FULL_ARGS[REPO], f"suite_{c}_{t}", timeout=5400)
        attempts.append(dict(rc=rc, n=len(res), tail=out[-1500:]))
        if res:
            break
    if not res:
        (l4h.L4 / REPO / "bases" / f"suite_{c}_{t}.FAILED.json").write_text(json.dumps(attempts, indent=1))
        return c, t, None, 0, "FAILED"
    fails = sorted(k for k, v in res.items() if v == "failed")
    r = dict(cond=c, task=t, lint_broken=int(m.group(1)) if m else None, n=len(res), failed=fails, rc=rc, attempts=len(attempts))
    (l4h.L4 / REPO / "bases" / f"suite_{c}_{t}.json").write_text(json.dumps(r, indent=1))
    return c, t, r["lint_broken"], len(res), len(fails)
with cf.ThreadPoolExecutor(int(sys.argv[3]) if len(sys.argv) > 3 else 6) as ex:
    only = set(sys.argv[4].split(",")) if len(sys.argv) > 4 else None
    todo = [(c, t) for c in CONDS for t in l4h.TASKS[REPO] if only is None or f"{c}_{t}" in only]
    for x in ex.map(one, todo):
        print(*x, flush=True)
