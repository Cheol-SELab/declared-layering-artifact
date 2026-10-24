# Replication round 2 — candidate search and four more repositories

Date: 2026-10-05.

## Candidate search (why "15 more" was not reachable this way)

- Guess-probing ~130 well-known Python repos for import-linter layers contracts: 7 hits (~5%).
- Scraping GitHub's dependents page for import-linter: 270 repos surfaced (GitHub stops paging early); 60% had
  a layers contract, but almost all are templates or repos younger than a year with <300 commits.
- Upstreams of forks found this way yielded the only mature additions.
- Screening criteria: ≥2 years of history, ≥500 commits, a layers contract with ≥3 layers that encodes a
  stability ordering, declaration present for ≥4 quarterly snapshots.

| Found | Qualifies | Why not |
|---|---|---|
| GitGuardian/ggshield | **yes** | 3302 commits, declared since 2023-08, 5-level layers contract |
| NVIDIA/physicsnemo | no (descriptive) | declared 2025-12, 13 revisions in 9 months — still being written; S2 degenerate (=1.0) |
| TeKrop/overfast-api | no (descriptive) | declared 2026-09 → one snapshot |
| alan-turing-institute/AIrsenal | no (descriptive) | declared 2026-08 → one snapshot |
| kartverket/automatisk-generalisering | no | declared 2026-10 |
| SACGF/variantgrid, PostHog/posthog, modelscope/evalscope, faststream | no | import-linter present but no layers contract |

Net: 1 new valid test subject. Reaching 15 requires either GitHub code search (needs an API token; a query
such as `"type = layers" path:.importlinter` or `[tool.importlinter]` would list thousands in minutes) or
broadening the declaration source to ArchUnit `layeredArchitecture()` (Java), `tach.toml` (Python) and
`dependency-cruiser` (JS/TS), each needing its own declaration parser.

## ggshield result — second positive case

5 layers: `__main__` > `cmd.*` > `verticals.*` > `core` > `utils`. Bottom third = `core`, `utils`.
13 quarters (2023-10 → 2026-10), 3 quarters followed by a declaration revision.

| Rank by S2 | Quarter | S2 | Revision next Q |
|---|---|---|---|
| 1 | 2026-04 | 0.49 | YES (6 revisions Apr–Jun 2026) |
| 2 | 2026-01 | 0.45 | YES (Feb, Apr 2026) |
| 3–5 | 2025-04/07/10 | 0.38–0.40 | no |
| 6 | 2025-01 | 0.35 | YES (Jan 2025) |
| 7–13 | others | 0.29–0.34 | no |

**AUC(S2) = 0.90.** The two highest S2 quarters are the two that precede the 2026 revision cluster, exactly the
openedx-learning pattern. Not pre-registered as a prediction for this repo specifically, but the definition
was frozen before ggshield was found.

## Updated cross-repo table (valid tests only)

| Repo | Quarters | Positives | AUC(S2) |
|---|---|---|---|
| openedx-learning | 12 | 5 | 0.70 |
| ggshield | 13 | 3 | 0.90 |
| kedro | 21 | 3 | 0.30 |
| sqlfluff | 12 | 1 | (0.36, 1 positive — uninformative) |
| wemake-python-styleguide | 28 | 0 | n/a — control, quiet |
| import-linter | — | 6 additive | n/a — control, quiet |

Descriptive only (declaration too new or degenerate): edx-platform, napari, physicsnemo, overfast-api, AIrsenal.

## Reading

Two of three repos with ≥3 revisions show S2 as a strong leading indicator (0.70, 0.90); one (kedro) shows the
reverse (0.30). Pooled over the three, the signal is above chance but with N=11 positive quarters nothing is
established. The kedro case still argues that "declaration revised" is a culture-dependent outcome; the
intervention design (Layer 4, change-cost outcome) remains the right next step. ggshield is now the third
candidate subject for that design alongside openedx-learning and kedro.
