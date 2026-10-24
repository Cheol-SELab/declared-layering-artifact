You are a coding agent implementing one change request in a Python repository.

Repository (work only inside this directory): C:/vdm/l4/kedro/runs/C_ab576bc_r2
It is a standalone git repository with a single commit. Do not access the network, do not clone or look up the
upstream project or its history, and do not read or modify files outside this directory.

## Change request
MVP for "add-ons" flow within kedro new CLI command (#2987)

* Update prompts.yml

Signed-off-by: SajidAlamQB <90610031+SajidAlamQB@users.noreply.github.com>

* Update starters.py

Signed-off-by: SajidAlamQB <90610031+SajidAlamQB@users.noreply.github.com>

* add post_gen_project in cookiecutter hooks

Signed-off-by: SajidAlamQB <90610031+SajidAlamQB@users.noreply.github.com>

* add confirmation message for the options selected

Signed-off-by: SajidAlamQB <90610031+SajidAlamQB@users.noreply.github.com>

* Update post_gen_project.py

Signed-off-by: SajidAlamQB <90610031+SajidAlamQB@users.noreply.github.com>

* changes based on review

Signed-off-by: SajidAlamQB <90610031+SajidAlamQB@users.noreply.github.com>

* Lint

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove documentation requirements

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove testing requirements

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove leftover linting requirements

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Lint

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add add-on requirements when an addon is selected

Signed-off-by: lrcouto <laurarccouto@gmail.com>

* Correct file path

Signed-off-by: lrcouto <laurarccouto@gmail.com>

* Update tests with new default template files number

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Update tests with add-ons argument

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Make lint

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Lint

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Make tests use all add-ons by default

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Make unit tests use no add-ons by default

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add installing project dependencies to e2e tests

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add linting requirements, organize code

Signed-off-by: lrcouto <laurarccouto@gmail.com>

* Refactor test for all add on options

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add test to check parsing add-ons

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add scaffolding for add-ons tests

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Change name of test class

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Correct test names

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Correct tests directory

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Clean up success message

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Fix logging option

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Update lint add-on logic

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Ensure add-ons message only shows when add-ons are configurable

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add requirement checks to tests

Signed-off-by: lrcouto <laurarccouto@gmail.com>

* Refactor unit tests

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add validation to add ons in config file

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Refactor add-ons flow script

Signed-off-by: lrcouto <laurarccouto@gmail.com>

* Pass through correct repo name in test

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Clean up and clarify text

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Wrap hook script inside main function

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Revert displayed default

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add range validation

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add tests for add-on range validation

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Apply suggestions from code review

Co-authored-by: Merel Theisen <49397448+merelcht@users.noreply.github.com>

* Update kedro/templates/project/hooks/utils.py

Co-authored-by: Merel Theisen <49397448+merelcht@users.noreply.github.com>

* Apply suggestions from code review

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove traceback from add-on validation - review suggestion

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Output add-on names when selected (via CLI)

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Revert 47d935e and fix tests

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Fix test errors

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Try remove validation

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add validation back

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add config file input validation

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add /site-packages/ to coverage report omit

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Lint

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove duplicate error message

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Lint

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove suppression

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Merge develop into fead/add-ons-flow

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Prep for merge

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove suppression

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Apply changes from code review

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add clarification to error messages

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Remove suppression

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Correct files in starter template

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Fix broken link

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add project teardown

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Try be more direct

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Try be more direct pt 2

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Try be more direct pt 3

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Try be more direct pt 4

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Fix clean-up

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Fix type

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Apply suggestions from code review

Co-authored-by: Sajid Alam <90610031+SajidAlamQB@users.noreply.github.com>

* Lint

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add docstring

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

* Add changes to RELEASE.md

Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>

---------

Signed-off-by: SajidAlamQB <90610031+SajidAlamQB@users.noreply.github.com>
Signed-off-by: Ahdra Merali <ahdra.merali@quantumblack.com>
Signed-off-by: lrcouto <laurarccouto@gmail.com>
Co-authored-by: L. R. Couto <57910428+lrcouto@users.noreply.github.com>
Co-authored-by: Ahdra Merali <ahdra.merali@quantumblack.com>
Co-authored-by: lrcouto <laurarccouto@gmail.com>
Co-authored-by: Ahdra Merali <90615669+AhdraMeraliQB@users.noreply.github.com>
Co-authored-by: Merel Theisen <49397448+merelcht@users.noreply.github.com>

## Acceptance tests
These test files describe the required behaviour and are already in place:
- `tests/framework/cli/test_starters.py`
Do not edit them. Make the tests in these files pass (some may fail now because the behaviour is missing) without
breaking other tests. You may add or adjust other tests only if your change genuinely requires it.

## Architecture
The project declares its layering in the `[tool.importlinter]` section of `pyproject.toml` (import-linter). Your
change must keep all contracts kept. Do not edit the `[tool.importlinter]` section.

## Commands (run with the Bash tool)
- Acceptance tests: `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/runs/C_ab576bc_r2 tests/framework/cli/test_starters.py -q -p no:cov -o addopts= --timeout=300"`
- Any tests:        `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/runs/C_ab576bc_r2 <pytest args>"`
- Full suite (about 20 min): `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/runs/C_ab576bc_r2 tests -q -p no:cov -o addopts= --timeout=300 -n 8"`
- Layer check:      `wsl -e bash -lc "VDM_VENV=~/vdm/venv-kedro ~/vdm/bin/kt C:/vdm/l4/kedro/runs/C_ab576bc_r2 --lint"`
About a dozen tests (Jupyter, CLI hooks, cloud protocols) fail in this environment regardless of your change.

Keep the change focused on the request. Run the acceptance tests and the layer check before finishing.
Do not commit. When done, reply with one short paragraph: what you changed and the final acceptance-test and
lint-imports summary lines.
