# Layer 4 — status after day 1

Date: 2026-10-05. Goal: three-arm comparison (A fixed check / B co-change recommendation / C full loop) on
follow-up changes, outcome = propagation (declared units touched per change).

## Done

**1. Follow-up change sets fixed (pre-reg §7, with one recorded deviation).**
GitHub API was rate-limited and the token had been revoked, so the label rule ("first 10 closed
enhancement/feature issues") could not be applied. Used the fallback named in the pre-reg comment: first 10
post-snapshot PR groups that touch both code and tests, excluding docs/chore/ci/build/style/release/refactor.
Deviation logged in pre-reg §10.

**2. Human baseline = what condition A costs in reality** (`l4_baseline.txt`, `l4_baseline.json`)

| Repo | Snapshot | Follow-up PRs | Median units touched | Mean files | PRs touching declared bottom |
|---|---|---|---|---|---|
| kedro | 2023-10-01 | 10 | 1.0 | 5.2 | **5 / 10** |
| kopf | 2026-01-01 | 10 | 1.5 | 2.8 | **7 / 10** |
| legadilo | 2025-10-01 | 10 | 1.0 | 2.9 | 2 / 10 |
| openedx-learning | 2026-01-01 | 1 usable | — | — | the first PRs *are* the restructure; needs a later snapshot |

kopf: 7 of 10 feature changes enter the declared most-stable layer. kedro: 5 of 10, two of them repo-wide
renames spanning 3–5 units. This is the quantity Layer 4 must move: after extracting the volatile cause from
the bottom, bottom-touching should fall without total units rising.

**3. Harness built and validated end to end** (`l4_harness.py`)
- worktree at snapshot → PR's test files copied in as acceptance spec → baseline run (records
  pre-existing environmental failures) → agent → gates (`lint-imports` on the repo's own declaration, spec
  tests, no new failures) → metrics (files, declared units, bottom touched, tokens).
- Agent backends: `replay` (human PR diff; pipeline check only) and `anthropic` (tool loop; needs
  `ANTHROPIC_API_KEY`, not available in this container).
- Validation run kedro #3145 / condition A / replay: spec extracted (4 failing → 3 after; 2 are Python-3.12
  environment failures present before the PR), `lint-imports` rc 0, propagation 1 file · 1 unit (`config`,
  bottom). Pipeline correct.

## Not done (needs an API key and ~2 weeks of compute)

- Condition B/C worktrees: apply the refactoring (co-change recommendation / §6 proposal) before the agent runs.
  For kedro the C proposal is EXTRACT from `io` (top sub-module `core.py`, r=0.25 → actually HOLD at 2023-10 under
  the table; use the 2021-10 PROMOTE or hand-specify the Containers-style extraction) — must be decided and
  logged before running.
- Agent runs: 4 repos × 10 PRs × 3 conditions × 5 repeats × 2 models = 1,200 runs. At ~50k tokens/run ≈ 60M
  tokens. Budget decision needed; a 1-repo pilot (kopf, 10 × 3 × 3 × 1 = 90 runs) first.
- `spec_passed` logic to tighten: require every test that fails at baseline *because of the new spec* (not
  environmental) to pass; currently "fewer failures and no new ones".
- Mutation gate not wired (mutmut on bottom units only).

## Open decisions for the author

1. API budget and which model(s).
2. For kopf (the strongest case): which bottom sub-module to extract under condition C — the harness needs a
   concrete move plan; the §6 table at 2026-01 returned HOLD-ambiguous for ggshield-style cases, so kopf's
   plan must be derived and logged before any run.
3. Whether openedx-learning stays in Layer 4 (snapshot must move to 2026-04 so follow-ups are features, not the
   restructure itself).
