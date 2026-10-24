You are a coding agent performing an approved architectural refactoring in a Python repository.

Repository (work only inside this directory): C:/vdm/l4/kedro/C_work
It is a standalone git repository with a single commit. Do not access the network, do not clone or look up the
upstream project, and do not read files outside this directory.

## Approved proposal
The layering declaration is the `[[tool.importlinter.contracts]]` layers contract in `pyproject.toml`
(containers = "kedro"), top to bottom: framework.cli, framework.session, framework.context, framework.project,
runner, io, pipeline, config.

Change history shows that `kedro.io.partitioned_dataset` changes together with higher layers far more often than
the rest of `kedro.io`; it is a separate reason for change. The approved proposal is:

**EXTRACT `kedro.io.partitioned_dataset` out of `kedro.io` into a new layer `kedro.partitioned`, placed directly
above `io` in the layers contract** (new order: ..., runner, partitioned, io, pipeline, config).

## What to do
1. Create the package `kedro/partitioned/` and move `kedro/io/partitioned_dataset.py` to
   `kedro/partitioned/partitioned_dataset.py` (use `git mv`). Re-export the public classes (PartitionedDataset,
   PartitionedDataSet, IncrementalDataset, IncrementalDataSet) from `kedro/partitioned/__init__.py`.
2. `kedro.io` (now a lower layer) must not import from `kedro.partitioned`, so remove those names from
   `kedro/io/__init__.py` imports and `__all__`. Update every import and reference in `kedro/`, `tests/`,
   `features/`, `docs/` and templates to the new location `kedro.partitioned`. If the data catalog resolves
   short dataset type names (e.g. `type: PartitionedDataset`) through a list of module prefixes, keep those names
   resolvable without adding a static import from a lower layer to a higher one.
3. Update the layers contract in `pyproject.toml`: insert `partitioned` between `runner` and `io`. Do not remove,
   relax or reorder anything else and do not add `ignore_imports` entries. Other contracts (independence,
   forbidden) must stay kept; if one needs the new module listed alongside `kedro.io` to keep its intent, add it
   there and say so.
4. Resolve any import that now points from a lower layer into `kedro.partitioned` without changing behaviour.
5. Change no behaviour. Do not modify test logic; editing tests is allowed only to update import paths, mock/patch
   target strings or type-name strings that name the moved module or classes.

## Gates (all must hold before you finish)
- `lint-imports` reports 0 broken contracts:
  `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/C_work --lint"`
- No new test failures:
  `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/C_work tests -q -p no:cov -o addopts= -n 12"`
  (about 10 minutes; run subsets such as `tests/io tests/framework/context` first). Some tests fail for
  environmental reasons before any change; compare with the untouched baseline `C:/vdm/l4/kedro/A_frozen`
  (same command, do not modify it). New failures are not acceptable.
- No new top-level modules outside the declaration (the new layer is declared).

When finished, reply with: the files you changed, how you handled the public API and type-name resolution, any
contract you had to extend, and the final lint-imports and test summary lines. Do not commit.
