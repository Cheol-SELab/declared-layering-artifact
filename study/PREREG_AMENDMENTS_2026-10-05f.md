# Deviation D5 — Layer-4 measurement harness (recorded 2026-10-05, before any Layer-4 outcome analysis)

Status at recording: all 60 kopf agent runs (A, C × 10 tasks × 3) have finished. No `l4_analyze.py` output exists;
no C-versus-A comparison of any outcome has been computed or inspected. Individual result files of human-change
replays were seen as they were produced (units touched, test counts) for harness checking.

## D5a. Full-suite execution
Problem: the full kopf suite, run through `wsl -e bash -lc kt ...` with `--timeout=120`, was aborted part-way under
heavy machine load (pytest-timeout ending the whole session, rc 9/143), leaving no JUnit output. Ten result files were
written with zero test counts.
Change:
1. The suite runs detached inside WSL (`setsid -f ~/vdm/bin/ktd`) with a private mirror directory per invocation;
   the harness polls for the exit code.
2. kopf full-suite arguments: `--timeout=600 --timeout_method=signal` (a slow test fails individually instead of
   ending the session). Spec and lint invocations are unchanged.
3. If no JUnit results are read back, the suite is re-run once; if still empty, evaluation fails loudly instead of
   writing a record.
4. The ten zero-count records are excluded (moved to `results_invalid/`) and every affected run is re-evaluated.
Effect on outcomes: none on the primary or A-frame unit counts, files or lines (computed from the diff). The full
suite only feeds the "no persistent new failure" component of acceptance, which still uses the registered
rerun-once rule against the task base's failures.

## D5b. Acceptance when the reference set is empty
The reference set of a task is the set of non-e2e acceptance tests that pass after replaying the human change on the
A base. For a task whose acceptance file contains no tests (documentation task 20de08c: `tests/conftest.py`), the
set is empty; acceptance then reduces to: specification files unchanged, all contracts kept, no persistent new
failure. This rule was fixed in `l4_analyze.py` before any run was evaluated.

## D5c. Reported but not registered
(a) The human change replayed on the C base (same PR, C declaration) is reported as a deterministic secondary
comparison of units touched; it is exploratory. (b) Runs that edit non-specification test files are listed. (c) Tasks
whose acceptance tests already pass on the base (observed: 51c078d) are flagged as low-information; they are not
dropped from the registered analysis.
