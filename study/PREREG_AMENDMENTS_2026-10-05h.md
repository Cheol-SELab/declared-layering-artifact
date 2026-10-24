# Correction E2 — kedro Layer-4 environment and specification (recorded 2026-10-05, before any kedro evaluation)

1. The kedro test environment had kedro-datasets 1.7.0 (resolved as of 2023-10-01). Tasks after the upstream
   DataSet->Dataset rename import `CSVDataset` and similar names, which first appear in kedro-datasets 1.8.0. The
   first six kedro agent runs could not collect their acceptance tests. Correction: kedro-datasets 1.8.0 (the
   release current at the task dates) is installed with `--no-deps`; all kedro base suites are recomputed.
2. For task 60f676e, two acceptance files are deleted by the human PR; the harness had written a git error message
   into them. Correction: test files deleted by the PR are not part of the specification.
3. All kedro runs started before these corrections (A_2297d23_r3, C_69a6fe1_r3, C_ab576bc_r2, A_ab576bc_r2,
   A_60f676e_r1, A_2f526b6_r2) are void, set aside unevaluated in `C:/vdm/l4/kedro/void1/` and
   `l4_prompts/runs_kedro_void1/`, and every kedro run is re-prepared from the same seeded schedule and re-run.
   No kedro result was evaluated before this correction.
