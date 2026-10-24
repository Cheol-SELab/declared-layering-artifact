You are a coding agent performing an approved refactoring in a Python repository.

Repository (work only inside this directory): C:/vdm/l4/kedro/B_work
It is a standalone git repository with a single commit. Do not access the network, do not clone or look up the
upstream project, and do not read files outside this directory.

## Approved proposal (co-change-based move recommendations)
Change history shows that these files change more often with another package than with their own. Move each file
into the recommended package:
1. `kedro/framework/session/session.py`  ->  package `kedro.framework.cli`
2. `kedro/runner/parallel_runner.py`     ->  package `kedro.io`
3. `kedro/runner/runner.py`              ->  package `kedro.io`

## What to do
- Move the files with `git mv`, update every import and reference in `kedro/`, `tests/`, `features/`, `docs/` and
  templates. Keep the public API of the packages the files left (`kedro.framework.session`, `kedro.runner`)
  importable by their old names only if that does not create a forbidden import.
- The layering declaration in `pyproject.toml` must stay as it is: do not add, remove or reorder layers, and do not
  add `ignore_imports` entries. You may update the module path inside an existing `ignore_imports` entry if the
  module it names was moved.
- Change no behaviour. Editing tests is allowed only for import paths and mock/patch target strings.
- If a move cannot be completed without breaking the declaration, do as much as is possible without breaking it,
  and report precisely which move could not be completed and why.

## Gates (all must hold before you finish)
- `lint-imports` reports 0 broken contracts:
  `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/B_work --lint"`
- No new test failures:
  `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/B_work tests -q -p no:cov -o addopts= -n 12"`
  Compare with the untouched baseline `C:/vdm/l4/kedro/A_frozen` (same command; do not modify it).

When finished, reply with: which moves were completed, which were not and why, the files changed, and the final
lint-imports and test summary lines. Do not commit.
