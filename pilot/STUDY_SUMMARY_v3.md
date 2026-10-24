# Layer-1 study, round 3: full population via GitHub code search

Date: 2026-10-05. Scanner: `blind_scan.py` (v3: TOML/INI, sub-directory declarations, tree-based module
path discovery, rename-aware co-change, sweep-commit filter, size-normalised S2n). Evaluation: `pool_eval.py`.

## 1. Population funnel (new, and itself a finding)

| Stage | Count |
|---|---|
| Non-fork GitHub repos with an import-linter layers declaration (code search, 4 queries, capped at 1,000/query) | 1,907 |
| … created ≥2 years ago, pushed within 12 months, not archived | 138 |
| … with a layers contract of ≥3 layers | 106 |
| … declaration present for ≥8 quarters (≤2024-10) | 15 (14 unique) |
| … passing intent/health screens (stability ordering, not aspirational, not under construction, ≥10 commits/quarter, ≥2 revisions) | **5 valid tests** + 3 controls |

### Adoption curve — when the declaration first appeared (106 mature repos)

| 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (to Oct) |
|---|---|---|---|---|---|---|
| 2 | 2 | 2 | 6 | 4 | 18 | **67** (40 in Jul–Sep alone) |

Among repositories that are themselves ≥2 years old, machine-readable layer declarations were rare until 2024
and then multiplied roughly 15× in 2025–26, coinciding with the spread of coding agents (e.g. dify: declared
2025-09, revised ~50 times since). Consequence for research: almost no repo has a declaration history long
enough to test "does volatility predict revision"; the outcome variable barely exists in the wild.

### Three kinds of declaration found (screening criteria that emerged)

1. **Kept**: ≤5 upward imports in code, revisions rare and additive (ggshield, sqlfluff, wemake, import-linter).
2. **Aspirational**: declaration present, 55–76 upward imports tolerated for years (blueking-paas, bk-iam-saas).
   Declared-vs-observed comparison is meaningless because the declaration is not the operative architecture.
3. **Under construction**: ≥10 revisions in the first year, violations rising (dify 10→100, physicsnemo 13 revisions/9 mo).
Plus two measurement traps: contracts that encode a *rule* rather than an ordering (napari: "qt must not be
imported", 2 layers) and bottom layers that are the bulk of the code (mlrun: `mlrun` library = bottom; UKHSA
after 2024-07). The size-normalised S2n = (change share) / (file share) addresses the second.

## 2. Results on the five valid tests

Outcome = layers-declaration content revised in the following quarter. Quarters with <10 commits dropped.

| Repo | Quarters | Positives | AUC S2 | AUC S2n | Pattern |
|---|---|---|---|---|---|
| ggshield | 13 | 3 | 0.90 | 0.90 | two highest quarters precede the 2026 revision cluster |
| bk-user | 13 | 2 | 0.57 | **0.70** | highest S2n (2.08) immediately precedes 2024-04 revision; 2026 high with no revision |
| openedx-learning | 12 | 5 | 0.70 | 0.67 | two highest precede two largest restructures |
| legadilo | 11 | 3 | 0.38 | 0.58 | weak |
| kedro | 21 | 3 | 0.30 | 0.41 | reverse: bottom stays volatile (S2n>1) for years, no revision |

**Pooled (S2n z-scored within repo): 70 quarters, 16 positives, AUC = 0.65, permutation p = 0.037.**

Controls (0 revisions): wemake (S2 0.03–0.27, quiet), import-linter (quiet), kopf (S2 0.45–0.64 persistently —
a kedro-type case: declared bottom volatile for 5 years, never revised).

## 3. Reading

- The declared-bottom-volatility signal is a **weak but non-random** leading indicator of teams revising
  their layering (AUC 0.65 pooled, 0.58–0.90 in 4 of 5 repos), with one clear counter-case.
- The counter-cases (kedro, kopf) are not noise: both show a declared-stable layer carrying sustained change
  for years with nobody touching the declaration. Whether that is "false alarm" or "unaddressed debt" cannot be
  decided with revision as the outcome. This is the strongest argument, now backed by data, for moving the
  study to a change-cost outcome (Layer 4).
- S1 ("hidden coupling") remains retired: wherever inspected it was common-cause ripple or sweep commits.
- The adoption curve reframes the paper's motivation: declarations are now being written at scale, often by or
  alongside agents, mostly in the last 12 months — and a third of the mature ones are aspirational or still
  being rewritten. A method that measures whether a declaration matches reality arrives exactly when the
  declarations do.

## 4. Threats specific to this round

- Code search caps at 1,000 results per query; the four queries overlap, so the 1,907 is a lower bound.
- Declaration-first dates from `git log -S importlinter` can miss moves between files (edx-platform shows 2026-01
  though an older setup.cfg declaration may exist in a fork lineage).
- Intent screening (kept/aspirational/under-construction) was decided after seeing the data; thresholds
  (upward ≤5, revisions ≥10/yr) must be pre-registered for the main study.
- Five repos; a single additional counter-case would move the pooled AUC materially.

## 5. Next

1. Pre-register: S2n definition, screening thresholds, outcome = subsequent change propagation (files/modules
   per later commit) rather than revision; register kedro `io/pipeline/config` and kopf bottom layers as
   intervention candidates.
2. Layer 2: for the 16 positive quarters, generate proposals automatically and compare with what the teams did.
3. Layer 4: on kedro/kopf/openedx-learning/ggshield snapshots, run the three-arm comparison (fixed check /
   co-change recommendation / full loop) with agent-implemented follow-up issues.
