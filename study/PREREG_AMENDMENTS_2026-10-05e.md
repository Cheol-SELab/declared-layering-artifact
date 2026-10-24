# Deviation D4 and the §4 additional-target check (2026-10-05, before any follow-up agent run)

## D4 — task base = the human PR's parent commit
Replaying the 10 kopf human PRs on the snapshot showed that 3 of them (bad8649, 91f7ae0, 017dbe0) do not apply:
they build on intermediate commits made after the snapshot. With a snapshot base, the acceptance spec of such a
task would require code the task does not describe. Therefore, for every task and both repositories:
- Base(A, task) = the PR's parent commit (LF export).
- Base(C, task) = Base(A, task) + the frozen condition-C refactoring commit, re-applied by 3-way cherry-pick
  (kopf: 10/10 clean); references to moved modules in files added after the snapshot are rewritten with the same
  move map used for acceptance specs (kopf: one test file, tests/posting/test_loggers_setting.py, in 2 bases).
- Base(B, task) analogously for kedro.
- Lint and full-suite baselines are recorded per (condition, task) base; "no new failures" is judged against
  the base of the same (condition, task).
The refactoring itself (what is moved and where) is unchanged; it is still derived from pre-snapshot history only.

## §4 additional-target rule
From the 106-repository declaration histories (blobless clones, `data/pop_decl_history.json`), 14 unique
repositories have a declaration at >= 8 quarterly snapshots by 2026-10-01; 13 were screened before. The new one,
bluesky/ophyd-async (declared 2024-12-10, 8 snapshots), fails the registered screens: declared-bottom file share
about 0.83 (> 0.40) before its 2026-02 revision, and a single positive quarter. It is not added to the H1 pool.
