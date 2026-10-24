# Replication across six repositories — result: the leading-indicator claim does NOT replicate

Date: 2026-10-05. Same scanner (`blind_scan.py`), same pre-fixed definitions:
S2 = share of commits in the preceding 12 months touching the declared bottom third of layers;
outcome = "layers declaration content revised in the next quarter". Quarterly snapshots; quarters with <10 commits dropped.

| Repo | Declared since | Quarters | Revisions (positives) | S2 range | AUC(S2) | Reading |
|---|---|---|---|---|---|---|
| openedx-learning | 2022-08 | 12 | 5 | 0.35–0.80 | **0.70** | Two largest S2 peaks (0.80, 0.73) immediately precede the two largest restructures |
| kedro | 2021-10 | 21 | 3 | 0.17–0.53 | **0.30** | S2 rises 0.17→0.42 into the 2023-Q4 revision cluster (6 revisions), but keeps rising to 0.53 afterwards with no revision — bottom layers (io, pipeline, config) stay volatile |
| sqlfluff | 2023-11 | 12 | 1 | 0.07–0.24 | 0.36 (1 pos.) | Bottom (types, helpers, errors) is quiet; volatility sits in `parser` (rank 3 of 6) — declaration consistent |
| wemake-python-styleguide | 2019-07 | 28 | 0 | 0.03–0.27 | n/a | Never revised; bottom quiet — negative control |
| edx-platform | 2026-01 | 4 | 0 | 0.10–0.14 | n/a | Too recent; bottom (xblock_serializer, content_tagging) quiet; `content_libraries` (rank 1) carries volatility — consistent |
| napari | 2024-03 | — | — | — | n/a | Both contracts are 2-layer "qt must not be imported" rules, not a stability ordering. S2 is not meaningful. Excluded. |
| import-linter (earlier) | 2019-04 | — | 6 additive | low | n/a | Control; co-change follows declared edges |

## What replicated and what did not

**Did not replicate:** "high S2 predicts declaration revision next quarter." Only openedx-learning shows it;
kedro shows the opposite ordering (AUC 0.30). With revisions this rare (0–5 per repo over years), the outcome
variable itself is the problem: most teams never revise a layers declaration, so S2 can be persistently high
with no revision (kedro 2025–2026 at ~0.5) and we cannot tell "false alarm" from "unaddressed debt".

**Did replicate (descriptive):** where a layers contract encodes a stability ordering, the declared bottom is
in fact quiet in 4 of 5 analysable repos (S2 ≤ 0.27). The two exceptions are openedx-learning (bottom =
`publishing`, which carried the Containers feature until extracted) and kedro (bottom = `io`/`pipeline`/`config`,
S2 ≈ 0.5 and rising). In the one exception that had an active revision culture, the signal preceded the fix.

**Also replicated:** co-change among declared units overwhelmingly follows declared static edges; "hidden
coupling" pairs without a static edge are mostly explained by a shared dependency changing in the same commit
or by sweep commits. S1 as a signal is retired.

## Methodological lessons (these change the study design)

1. **Declaration revision is a bad outcome variable.** It measures team culture, not architectural need.
   The outcome must be change cost (Layer 4): propagation extent and effort of *subsequent* changes.
2. **Not every layers contract is a stability ordering.** napari uses it as a forbidden rule. Subjects must be
   screened for intent (comments, ADRs, ≥3 layers) before S2 is applied.
3. **A persistently volatile declared bottom (kedro) is the interesting case, not the predictive one.**
   The research question becomes: does extracting the volatile cause from the declared bottom reduce
   subsequent change propagation? That is an intervention study (Layers 2–4), and kedro `io` is a candidate subject.
4. **Pre-registration worked.** Definitions were fixed after openedx-learning and before the other five;
   that is why the failure to replicate is visible rather than tuned away.

## Status of the research question

The loop's first arrow (measurement → discrepancy) is supported descriptively (declared-bottom volatility is
rare, and where present it coincided with later extraction in the one repo we can check) but NOT as a
predictor of what teams do. The study should pivot from "does the signal predict revisions" to
"does acting on the signal reduce subsequent change cost", with kedro and openedx-learning as the two
positive cases and sqlfluff/wemake/edx-platform as negatives where the method should propose nothing.
