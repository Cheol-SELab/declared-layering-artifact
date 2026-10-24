You are a coding agent performing an approved architectural refactoring in a Python repository.

Repository (work only inside this directory): C:/vdm/l4/kopf/C_work
It is a standalone git repository with a single commit. Do not access the network, do not clone or look up the
upstream project, and do not read files outside this directory.

## Approved proposal
The layering declaration is `.importlinter` (import-linter). In the contract "The internal core must be
layered" (`core-layers`) the layers are, top to bottom: `kopf._core.reactor`, `kopf._core.engines`,
`kopf._core.intents`, `kopf._core.actions`.

Change history shows that the module `kopf._core.actions.loggers` changes together with higher layers far more
often than the rest of `kopf._core.actions`; it is a separate reason for change. The approved proposal is:

**EXTRACT `kopf._core.actions.loggers` out of `kopf._core.actions` into a new layer `kopf._core.loggers`,
placed directly above `kopf._core.actions` in `core-layers`** (new order: reactor, engines, intents, loggers,
actions).

## What to do
1. Move the module file `kopf/_core/actions/loggers.py` to `kopf/_core/loggers.py` (new module path
   `kopf._core.loggers`). Use `git mv`.
2. Update every import and reference in `kopf/`, `tests/`, `examples/` and `docs/` to the new path. Keep the
   public API of `kopf` (names re-exported in `kopf/__init__.py`) unchanged.
3. Update `.importlinter`: insert `kopf._core.loggers` between `kopf._core.intents` and `kopf._core.actions`
   in `core-layers`. Do not remove, relax or reorder anything else, and do not add `ignore_imports` entries.
4. Moving the module upward may create imports from `kopf._core.actions` into `kopf._core.loggers` (now an
   upward, forbidden direction). Resolve every such violation properly (for example, dependency inversion
   through a protocol/type in a lower layer, passing the logger in, or moving the specific code that needs it),
   without changing behaviour.
5. Change no behaviour. Do not modify test logic; editing tests is allowed only to update import paths or
   `mocker.patch`/monkeypatch target strings that name the moved module.

## Gates (all must hold before you finish)
- `lint-imports` reports 0 broken contracts. Run: `wsl -e bash -lc "~/vdm/bin/kt C:/vdm/l4/kopf/C_work --lint"`
- The test suite has no new failures. Run:
  `wsl -e bash -lc "~/vdm/bin/kt C:/vdm/l4/kopf/C_work tests --ignore=tests/e2e -q --timeout=120 -x"`
  (about 5 minutes; you may first run a subset such as `tests/logging tests/posting`). If a test fails, check
  whether it also fails on the untouched baseline `C:/vdm/l4/kopf/A_frozen` with the same command (pre-existing
  environmental failures are acceptable; new ones are not). Do not modify A_frozen.
- No new top-level modules outside the declaration.

When finished, reply with: the list of files you changed, how you resolved each upward import, and the final
lint-imports and test summary lines. Do not commit; leave the changes in the working tree.
