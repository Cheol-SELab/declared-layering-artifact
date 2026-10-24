# Deviation D6 — kedro Layer-4 pilot: B not executable, task eligibility, mechanical conflict rule
(recorded 2026-10-05, before any kedro agent follow-up run)

## D6a. Condition B (co-change moves without changing the declaration) is not executable as sealed
Sealed B plan (dedupe-corrected, A6): session.py -> framework.cli, parallel_runner.py -> io, runner.py -> io.
Refactoring agent (Sonnet 5.5, same gates): move 1 done; moves 2 and 3 cannot be made without breaking the
declared contracts ("Pipeline and IO are independent"; runner code inside the io layer would import pipeline and
framework upward), and the gates forbid relaxing contracts. Under the registered rule (B that fails its gates is
reported as not executable), B is not run. We report this as a result: two of the three co-change move
recommendations conflict with the declared layering.

## D6b. Task eligibility for kedro (A and C)
The frozen C refactoring (extract kedro.io.partitioned_dataset into a new layer kedro.partitioned, patch SHA-256
c454b546e96fe942588a9d79f5461ef986e03afe3b276a16b87831097d2c4dfc, documentation hunks excluded) is re-applied to each
task's parent commit (D4). Eligible tasks: those where it re-applies by three-way cherry-pick, or by the single
mechanical rule below. Excluded before any run, from both conditions:
- 00f035a, 5752f68: their parents no longer contain the target module, because the maintainers removed
  PartitionedDataset and IncrementalDataset from kedro.io in 60f676e (2023-10-24), itself one of the ten tasks.
- cd83bad, 0cd8ecc: their parents lie on a line with the pre-0.19 contract set (`extras.datasets` layer), where the
  refactoring conflicts in core.py, pyproject.toml and tests.
Remaining: 2f526b6, 3f2a226, 2297d23, ab576bc, 69a6fe1, 60f676e (6 tasks x 2 conditions x 3 repetitions = 36 runs).

## D6c. Mechanical conflict rule (kedro C only)
When the only conflict is kedro/io/__init__.py (caused by the upstream DataSet->Dataset rename), take the
parent's version, delete the `from .partitioned_dataset import ...` re-export and the four names from `__all__`,
and let kedro/partitioned/__init__.py re-export only the names the moved module defines at that parent. Applied to
ab576bc and 60f676e. Afterwards every C base is translated with the move map (module and symbol level) and gated by
lint and a full-suite baseline before use.

## D6d. Observation, not a test
The registered decision table selected `kedro.io.partitioned_dataset` (sealed plan SHA-256 b80fbd20...) from the
twelve months before the snapshot. Twenty days after the snapshot the maintainers removed this module from
kedro.io (60f676e). This is reported as an out-of-sample observation about *where* the signal pointed; the action
taken (removal) differs from the proposal (extraction).

## D6e. Harness
WSL interpreter chosen per repository; kedro specification tests run with `-p no:cov -o addopts= --timeout=300`;
task file lists parsed per line (paths with spaces); kedro specification = changed files under `tests/` only
(project-template test files are not package tests). The kedro prompt differs from kopf only in the declaration
location (pyproject.toml), the interpreter variable and the test commands.
