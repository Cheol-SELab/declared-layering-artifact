# Pre-registration: Volatility-Driven Architecture Study (Layers 2–4)

> **English translation, for reference.** This is a translation of revision 23 of the registration document
> (2026-10-06), whose working language was Korean. Sections 1–9 and the first change-log rows were fixed on
> 2026-10-05; Section 10 is the dated change log. Rows 13 onward of the change log were written in English in
> the original and are reproduced unchanged. The original is not part of this archive; its identity is recorded
> in `registration/README.txt`. Where the translation and the amendment files in `study/` differ, the amendment
> files are authoritative. Numbers are as written on 2026-10-05; several population counts were later recomputed
> and the manuscript reports the recomputed values.

2026-10-05 · SELab

## 1. Status and purpose

This document separates what had already been observed by 2026-10-05 from what is fixed before new data are
seen. Rounds 1–3 (Layer 1) were exploratory; the definitions and thresholds chosen as a result are fixed below and
are applied unchanged to Layers 2–4.

**Already observed (exploratory, hypothesis-generating)**

- 1,907 non-fork repositories contain an import-linter layers declaration. 138 are at least two years old and
  active, 106 have a contract of three or more layers, 15 have a declaration present for at least eight quarters
  (14 without duplicates), and 5 pass screening as valid tests.
- Year in which the declaration was created: 16 in 2019–2024, 18 in 2025, 67 in 2026 (40 in July–September).
- In the 5 valid repositories, the pooled AUC of S2n (the size-normalized change share of the declared bottom
  layer) against "declaration revised in the next quarter" is 0.65, permutation p = 0.037; per repository
  0.41–0.90. kedro runs in the opposite direction; kopf has zero revisions with persistently high S2.
- S1 (co-change without a static dependency) is explained by ripple through a common dependency and by sweep
  commits, and is dropped as an indicator.
- Three kinds of declaration: kept declarations, aspirational declarations (dozens of upward imports left in
  place) and declarations under construction (ten or more revisions in the first year).

**What this document fixes**

Definitions (Section 3), screening criteria and the target list (Section 4), per-repository predictions
(Section 5), the Layer-2 and Layer-4 procedures (Sections 6 and 7), and the analysis plan with confirmation and
disconfirmation conditions (Section 8). Later changes follow the amendment policy of Section 10 and are recorded
with date and reason.

## 2. Research questions and hypotheses

Central question: if boundaries are reorganized according to the volatility signal of the declared bottom layer,
does the propagation of later changes shrink compared with using a fixed architecture check alone?

| No. | Question | Hypothesis (direction stated) | Disconfirmation condition |
|---|---|---|---|
| RQ1 | In valid repositories, does S2n precede a declaration revision in the next quarter? | H1: pooled AUC(S2n) > 0.5, maintained in repositories added beyond the 5 registered ones | Pooled AUC including added repositories ≤ 0.55, or permutation p > 0.10 |
| RQ2 | Do proposals generated automatically for positive quarters match the team's actual revision? | H2: in ≥ 8 of 16 cases the proposal type (extract/promote/hold) and the target module match | ≤ 4 matches, or all matches are "hold" |
| RQ3 | Does re-layering according to the signal reduce the cost of later changes? | H3: in the loop condition (C) the number of modules changed per follow-up issue is smaller than in the fixed-check condition (A), with effect size d ≥ 0.3 | C ≈ A (d < 0.1) or C larger |
| RQ4 | Does the effect arise from co-change recommendations (B) alone? | H4: C < B; revising the declaration adds value | C ≈ B → contribution narrows to "recommendation + agent execution" |
| RQ5 | Are repositories with high S2n and no revision (kedro, kopf) false alarms or neglected debt? | H5: after extraction, later propagation decreases (debt) | If it does not decrease, S2n is an indicator that raises false alarms, and the RQ1 result is reinterpreted |

Side observations (not hypotheses, descriptive): the adoption curve of declarations, the proportions of the three
kinds of declaration, the screening funnel.

## 3. Operational definitions (fixed)

**Unit**: each layer entry of a layers contract. Siblings `a | b` are separate units. A unit that is a prefix of
other units is expanded into its direct sub-packages until a fixed point is reached; sub-packages not in the
declaration are marked as "undeclared units".

**Declared rank**: within a contract, bottom = 0 (most stable), top = 1. Bottom third = rank ≤ 0.34.

**Observation window**: the 12 months before the snapshot date. Snapshots are on the first day of each quarter.
Quarters with fewer than 10 commits are excluded from the analysis.

**Commit filter**: merges excluded; `.py` files only; `migrations/`, `tests/`, `__init__.py` and version files
excluded; a commit touching 7 or more units is excluded as a sweep commit. Renames are followed with `-M` and
resolved to the names at the snapshot.

**S2n (primary indicator)**

```latex
S2n = \frac{\text{commits touching bottom-third units} / \text{all commits}}{\text{.py files in bottom-third units} / \text{all .py files}}
```

1.0 = change proportional to size. If there are several contracts, the largest value is used.

**Upward imports (up)**: the number of statements in which a lower-ranked unit of a contract statically imports a
higher-ranked unit of the same contract. Imports exempted by `ignore_imports` are counted too.

**Outcome — Layer 1 (secondary)**: the content of the layers declaration changes within the next quarter
(92 days). File moves and comment changes are excluded.

**Outcome — Layer 4 (primary)**: when implementing one follow-up issue, (a) the number of units changed, (b) the
number of files changed, (c) the number of test failures and retries, (d) tokens consumed. Propagation = (a).

**Excluded indicators**: S1 (co-change without a static dependency), binary flags.

**Screening thresholds**

| Criterion | Threshold | Basis (rounds 1–3) |
|---|---|---|
| Layers in the contract | ≥ 3 | Two layers = a prohibition rule (napari) |
| Bottom-layer file share | ≤ 40% | mlrun: bottom = the whole library |
| Median upward imports | ≤ 5 | blueking-paas 57, bk-iam-saas 76 = aspirational |
| Declaration revisions in the first 12 months | < 10 | dify 50, physicsnemo 13 = under construction |
| Period the declaration exists | ≥ 8 quarters | Needed for the quarterly test |
| Commits per quarter | ≥ 10 | bidsMReye |

## 4. Target selection

**Population**: 1,907 non-fork repositories obtained by GitHub code search on 2026-10-05
(`importlinter filename:.importlinter`, `importlinter layers filename:pyproject.toml|setup.cfg|tox.ini`). Because
of the cap of 1,000 results per query this is a lower bound. Metadata and declaration information are kept in
`gh_decl.json`.

**Fixed target list (Layer-1 re-test and Layer-2 targets)**

| Repository | Role | Declared since | Quarters | Positives | Note |
|---|---|---|---|---|---|
| GitGuardian/ggshield | Valid test | 2023-08 | 13 | 3 | AUC 0.90 |
| TencentBlueKing/bk-user | Valid test | 2023-08 | 13 | 2 | AUC 0.70 |
| openedx/openedx-learning | Valid test | 2022-08 | 12 | 5 | AUC 0.67 |
| JujensGh/legadilo | Valid test | 2024-03 | 11 | 3 | AUC 0.58 |
| kedro-org/kedro | Valid test, intervention candidate | 2021-10 | 21 | 3 | AUC 0.41, counter-case |
| nolar/kopf | Control, intervention candidate | 2021-05 | 22 | 0 | S2 persistently 0.45–0.64 |
| wemake-services/wemake-python-styleguide | Negative control | 2019-07 | 28 | 0 | Quiet |
| seddonym/import-linter | Negative control | 2019-04 | — | 6 (additive) | Quiet |

**Exclusions and reasons (fixed)**: napari (two-layer prohibition rule), mlrun (bottom = the whole library), UKHSA
data-dashboard-api (S2 degenerate after 2024-07), blueking-paas and bk-iam-saas (aspirational), dify and
physicsnemo (under construction), bidsMReye (< 10 commits per quarter), blueking-apigateway (path mapping failed —
may be re-evaluated after a fix), sqlfluff (one revision, uninformative — control only), openedx-core (duplicate of
openedx-learning).

**Rule for additional targets**: repositories whose declarations pass eight quarters after 2026-10-05
(declarations of 2024-10 to 2025-01: ophyd-async, dodal, abis-mapping, finecode and others) are admitted
automatically by applying the Section 3 thresholds unchanged. Admission is not decided after seeing results.

**Layer-4 targets**: four repositories — kedro, kopf (high need for intervention), openedx-learning and ggshield
(positive cases). In each repository one snapshot just before a positive quarter is used.

## 5. Per-repository predictions

The following are predictions derived from observations as of 2026-10-05 that have not yet been checked. If they
hold, they are recorded as evidence for the method; if not, as disconfirmation.

| Repository | Observation (2026-10-01 snapshot) | Registered prediction | How checked |
|---|---|---|---|
| kedro | S2n of the bottom units io, pipeline, config persistently above 1.0; no declaration revision | Within one of the three units there is a sub-module that changes together with upper layers (framework, runner), and extracting it reduces the number of units changed per follow-up issue by ≥ 20% | Layer 4, condition A vs C |
| kopf | Bottom S2 0.45–0.64; zero declaration revisions in five years | Same pattern as above. However, kopf has a single maintainer, so "not revised" may reflect indifference to the declaration rather than debt — both readings are reported separately | Layer 4, condition A vs C |
| openedx-learning | sections, subsections, units undeclared since 2025-03; co-change among them sup 7, conf 1.0; depend on containers | By 2027-03 they are added to the declaration as sibling layers or merged. If not, S3 (undeclared units) is unsuitable as an indicator | Re-scan 2027-04 |
| openedx-learning | publishing appears in 30 of 73 commits even after the 2026-03 extraction | The extraction is incomplete: publishing contains a second cause of change (candidate: version and draft-state models) | Classification of commit causes |
| ggshield | S2n fell from 1.68 (2026-04) to 1.49 (2026-07) | After the eight revisions of 2026, S2n falls below 1.2. If it does not, those revisions did not remove the cause of change | Re-scan 2027-01 |
| bk-user | S2n 2.00 in 2026-10, no revision | A declaration revision or a reorganization of the bottom layer occurs by 2027-06 | Re-scan 2027-07 |

**Population prediction**: by 2027-10 the number of repositories at least two years old with a layers declaration
grows from 106 to 250 or more, and the share of aspirational and under-construction declarations among them stays
at 30% or more.

## 6. Layer-2 procedure: automatic proposals vs the team's decision

Targets: the 16 positive quarters of the 5 valid repositories. For each quarter a proposal is generated
automatically from the preceding snapshot with the decision table below and compared with the declaration revision
that actually happened in that quarter. Generation is finished before the revisions are viewed, and the result file
is sealed with a hash.

**Decision table (fixed)**

Let U be the bottom-third unit with the largest contribution to S2n. For each direct sub-module of U, count its
changes over 12 months and the share r of those changes made in the same commit as an upper layer.

| Condition | Proposal type | Proposal |
|---|---|---|
| One sub-module m of U accounts for ≥ 40% of U's changes and r(m) ≥ 0.5 | Extract | Move m out of U to the layer one level up |
| U changes evenly overall and mean r ≥ 0.5 | Promote | Raise U's layer rank by one level |
| U changes a lot but r < 0.3 (internal reasons) | Hold | Volatile, but not a boundary problem |
| An undeclared unit co-changes with a declared unit with sup ≥ 5 | Add to declaration | Declare that unit as a sibling layer |
| None of the above | Hold | — |

**Match judgement (fixed)**: same proposal type and same target module = full match; same type only = partial
match; otherwise mismatch. If the team revised but the proposal was hold = miss. The judgement is made blind by one
rater other than the authors, and κ against the authors' judgement is reported.

**Success criterion**: full + partial matches ≥ 8/16 (H2). Misses ≥ 8 means the decision table is too
conservative; mismatches ≥ 8 means the signal does not indicate a direction.

**One case already known**: openedx-learning 2026-01 → extraction of containers. This case informed the design of
the decision table, so it is excluded from the 16 and the evaluation uses 15 cases.

## 7. Layer-4 procedure: three-condition intervention comparison

Four target repositories (kedro, kopf, openedx-learning, ggshield), one snapshot per repository (just before a
positive quarter; for kopf the quarter with the highest S2, 2026-01-01).

**Three conditions**

| Condition | Re-layering | Check | Effect isolated |
|---|---|---|---|
| A Fixed check | None | import-linter run with the original declaration; violations reported to the agent | Architecture enforcement only |
| B Co-change recommendation | The agent executes co-change-based move recommendations (in the manner of de Oliveira 2019); the declaration stays as it is | Recommendation without revisiting the declaration | |
| C Full loop | A proposal from the Section 6 decision table is approved by a person (the author) → executed by the agent → the declaration is updated | Added value of revising the declaration | |

**Acceptance gate (B and C)**: zero violations of the target declaration; all existing tests pass; mutation score
of the bottom layer does not decrease; no new module outside the declaration; the number of declared edges does not
grow (no relaxation). Passing the gate is not correctness, so accepted re-layerings are reviewed blind by a rater
other than the authors (behaviour preserved, structure improved or not).

**Follow-up tasks**: after each snapshot date, the first 10 closed issues labelled enhancement or feature in the
actual issue tracker, in date order. No discretion in selection. The agent implements the same issue on each
condition's code base.

**Controls**: same model, same system prompt, same token budget (fixed cap per issue), same number of retries (3),
5 repetitions per condition. Two models.

**Measures (per issue)**: number of units changed (primary), number of files changed, test failures and retries,
tokens, number of newly introduced violations, functional test pass rate (judged by the tests of the issue's
original PR).

**For RQ5 only**: in kedro and kopf, recompute the bottom-layer S2n before and after the condition-C re-layering. If
S2n < 1.0 over the next 10 issues after re-layering, classify as "debt"; if still > 1.2, as "false alarm".

**Stop rule**: if the gate acceptance rate in condition C is below 20%, this is taken as a problem of the method
itself rather than of the decision table or the agent configuration; Layer 4 is stopped and only the Layer-2 result
is reported.

## 8. Analysis plan

**RQ1**: per-repository AUC(S2n) and the pooled AUC of S2n z-scored within repository. Significance by label
permutation, 5,000 times. Confidence intervals by repository-level bootstrap (repositories resampled with
replacement). The reported quantity is the effect size; p-values are secondary.

**RQ2**: frequencies of full/partial match, mismatch and miss over the 15 cases, and inter-rater κ. Baselines are
the expected match rates of "always extract" and "random type".

**RQ3 and RQ4**: a mixed model with the number of units changed per issue as dependent variable, condition (A/B/C)
as fixed effect, and repository and issue as crossed random effects. Effect size Cohen's d (C−A, C−B). The variance
over the 5 repetitions is reported as well. The two models are fitted separately and checked for consistency.

**RQ5**: for kedro and kopf separately, S2n before and after re-layering and the propagation of the next 10 issues.
N = 2, so described without statistics.

**Confirmation and disconfirmation conditions (fixed)**

| Result | Interpretation | Sentence used in the paper |
|---|---|---|
| H1 holds, H2 ≥ 8, H3 d ≥ 0.3, H4 C < B | Full confirmation | The declaration-revisiting loop reduces the cost of later changes and outperforms the fixed check and recommendations |
| H1 holds, H2 ≥ 8, H3 d ≥ 0.3, H4 C ≈ B | Partial confirmation | The value comes from co-change recommendation plus agent execution; revising the declaration adds nothing |
| H1 holds, H2 < 8 | Signal present but no direction | S2n is a warning indicator, and the remedy must be decided by people |
| H3 d < 0.1 | Disconfirmation | Bottom-layer volatility is unrelated to change cost. Only observational results are reported |
| RQ5 false alarm | Disconfirmation | The kedro and kopf type is normal; state the base false-alarm rate of S2n |

**Multiple comparisons**: five hypotheses were specified in advance and no exploratory indicators are added.
Additional analyses are marked "exploratory".

**Stop rule**: if misses ≥ 10 in Layer 2, the decision table is not changed; it is reported as is and the study
proceeds to Layer 4. The Layer-4 stop rule is in Section 7.

**Reporting**: every result is reported with the full funnel per condition (generated → held → approved → executed →
accepted/rejected), separating the acceptance rate from correctness.

## 9. Decisions already made after the fact (an honest record)

These were decided after looking at the data in rounds 1–3. This document fixes them from now on, but for the 5
repositories already seen the paper states that they are post hoc decisions.

| Decision | When, why | Effect |
|---|---|---|
| S1 indicator dropped | Round 2. In openedx-learning most co-change pairs were explained by ripple through publishing | All claims based on S1 withdrawn |
| S2 → S2n size normalization | Round 3. In mlrun the bottom = the whole library | Earlier S2 AUCs (openedx 0.70, ggshield 0.90) recomputed with S2n (0.67, 0.90) |
| Sweep-commit filter (7 units or more) | Round 2. Reformat and release commits inflated co-change | The threshold 7 is arbitrary. Sensitivity analysis with 5 and 10 planned |
| Four screening criteria (layers, file share, upward imports, first-year revisions) | Round 3, after seeing napari, mlrun, blueking, dify | The largest post hoc decision. Applied unchanged to additional repositories to test whether it was tuned after the fact |
| Commits per quarter ≥ 10 | Round 2 | bidsMReye excluded |
| Decision-table thresholds 40%, 0.5, 0.3 | When this document was written; not yet applied to any data | First tested in Layer 2 — a genuine pre-registration |
| Outcome changed from declaration revision to change propagation | Round 2. kedro and kopf keep high S2 without revision | Layer-1 result secondary, Layer 4 primary |

Reported wrongly and corrected: "sections and units were merged" (withdrawn; they were only moved), "hidden
coupling found" (withdrawn; common cause), four figures from prior work (to be corrected from primary sources).

## 10. Change log and amendment policy

Sections 3–8 of this document were fixed on 2026-10-05. Later changes follow these rules.

- Changes to definitions, thresholds, targets or hypotheses are recorded in this table with date, reason and the
  values before and after. If the reason for a change is "the result got better", the changed analysis is
  reported as exploratory only.
- New repositories are admitted under the "rule for additional targets" of Section 4 and recorded in this table.
- Changes to the analysis code (`blind_scan.py`, `pool_eval.py`) are tied to the version of this document by
  commit hash.
- The Layer-2 proposals are generated before the team's actual revisions are viewed, and their SHA-256 hash is
  recorded in this table.

| Date | Section | Change | Reason |
|---|---|---|---|
| 2026-10-05 | All | v1.0 fixed | End of round 3 |
| 2026-10-05 | 6 | 15 Layer-2 proposals generated and sealed. SHA-256 145ddb17bdf9c547ef3aebfb5bbc79d32e5986a6edbf9b260f3c325dfd2b5403 | Sealed before opening the actual revisions |
| 2026-10-05 | 6, 8 | Layer-2 result: of 13 valid positives, full 0 · partial 0 · mismatch 7 · miss 6. H2 disconfirmed. Of the team's 13 declaration revisions, 9 add or remove the layer of a new feature application; 2 reorganize the bottom layer | Result recorded |
| 2026-10-05 | 6 | Amendment A1: proposal type remove (take the unit out of the contract) added. Not used to re-judge the existing 15 cases; applies to new cases only | legadilo utils, kedro versioning |
| 2026-10-05 | 3 | Amendment A2: Layer-1 outcome recomputed as "change of the content of the layers lists". kedro 2023-10 and legadilo 2024-07 removed from the positives (`ignore_imports` changes) | Mismatch between definition and labels found |
| 2026-10-05 | 2, 8 | Interpretation added: the RQ1 AUC of 0.65 may be confounded, because feature activity raises bottom-layer volatility and layer additions at the same time. Layer 4 (change cost) reconfirmed as the primary result | Derived from the Layer-2 result |
| 2026-10-05 | 7 | Deviation D1: follow-up tasks selected as "the first 10 PRs after the snapshot that touch code and tests (excluding docs, chore, ci, refactor)" instead of by label. 10 each fixed for kedro, kopf and legadilo; for openedx-learning the snapshot must move to 2026-04 | GitHub API quota exhausted and token revoked; the fallback noted in a comment was used |
| 2026-10-05 | 7 | Condition-A baseline (human PRs) measured: bottom touched kedro 5/10, kopf 7/10, legadilo 2/10. Harness pipeline validated by replaying a human PR (kedro #3145: acceptance tests pass, lint-imports 0 violations, propagation 1 unit). Agent runs after an API key is obtained | Layer 4, day-1 record |
| 2026-10-05 | 3, 4, 5, 7, 8 | Amendment A3 (control of activity confounding in Layer 1: repository fixed-effects logistic model, S2n + log commit count + number of new sub-packages, 5,000 within-repository permutations, "robust to activity" if β > 0 and p < 0.10), A4 (procedure to check the prediction of a second cause of change in openedx-learning publishing), A5 (kopf Layer-4 pilot: the C proposal derived from pre-snapshot history only, follow-up PRs not consulted; B = at most 3 file-level co-change move recommendations), deviation D2 (agent = Claude Code sub-agent, Sonnet 5.5, one model; isolated repository without history; WSL CPython 3.12; 90 runs). Full text in study/PREREG_AMENDMENTS_2026-10-05b.md, SHA-256 9ed006123d2a9a92924c9c3254e3c03ec19138d1a6e133e9560e52f5f31272ca | Fixed before opening the new analysis results. The handover note's advice to "choose the extraction target after looking at the 7 baseline cases" was not adopted, because it leaks results |
| 2026-10-05 | 3, 7 | Deviation D3: tie in the kopf decision table (invocation and loggers, 3 commits each, r = 0.67) resolved by the registered tie rule (larger sub-module, 241 lines vs 158 lines) → C = extraction of loggers (hash 1355eacd…). B produced 0 recommendations, so B ≡ A in kopf. Correction E1: A2 implemented as the net change over the quarter (reproduces the two registered exclusions); the 2026-10-01 quarter has an unobserved outcome window and is reported both included and excluded (censoring). Full text in study/PREREG_AMENDMENTS_2026-10-05c.md, SHA-256 32648f2038307a0fe55682e9f8ddf08a6985971991649bf5aa985efd9efe23c9 | Found that the generator resolved the tie by insertion order. Found that the Layer-1 label implementation departed from the wording of A2. Both recorded before opening results |
| 2026-10-05 | 4, 7 | Amendment A6: second Layer-4 pilot, kedro (snapshot e9a07bb, the 10 follow-up tasks of D1, conditions A, B and C × 3). C = decision table HOLD → kedro.io.partitioned_dataset extracted by the A5 fallback rule (hash b80fbd20…). B = 3 move recommendations reduced to the top one per file (session.py → cli, parallel_runner.py → io, runner.py → io). That follow-up task #3187 removes the same module is reported only as a coincidence. Full text in study/PREREG_AMENDMENTS_2026-10-05d.md, SHA-256 348590cddcb2e5db58144e3e4a4d3c43b818b82bc6d52abdf26bbdff7cd27606 | Found that after size normalization kopf's signal (S2n 0.9–1.0) is weak (based on the predictor; outcome not observed). kedro added as a strong-signal counter-case to secure the RQ5 contrast |
| 2026-10-05 | 4, 7 | Deviation D4: base code of a follow-up task = parent commit of the human PR (A); parent + the frozen C re-layering commit by 3-way cherry-pick (C; kopf 10/10 without conflict). Three human PRs do not apply to the snapshot (they depend on intermediate commits). Test and lint baselines per (condition, task). Section 4 additional targets: only ophyd-async newly qualifies; excluded with bottom file share about 0.83 > 0.40 and one positive. Full text in study/PREREG_AMENDMENTS_2026-10-05e.md, SHA-256 af354d0bb2c5fa15a5ec7de6c7956da3ccb27c2215427acce55094a077776374 | Found while validating human-PR replay. Before agent runs |
| 2026-10-05 | D5 (Layer-4 measurement harness): full kopf suite run detached in WSL with private mirror, --timeout=600 --timeout_method=signal, retry-once then fail loudly; 10 zero-count records excluded and re-evaluated. Empty reference set (docs task 20de08c): acceptance = spec unchanged + contracts kept + no persistent new failure. Exploratory: human change replayed on C base; list of runs editing non-spec tests; low-information tasks flagged (51c078d). | Under machine load pytest-timeout aborted whole sessions (rc 9/143), leaving no JUnit output; documentation task has no acceptance tests. | Before any Layer-4 outcome analysis (all 60 kopf runs finished; no C-vs-A comparison computed). File PREREG_AMENDMENTS_2026-10-05f.md, SHA-256 92359e269253f18d0342ecfa1c09c325cf291172ffdfb9e961437b0b89df577c. |
| 2026-10-05 | D6 (kedro Layer-4): B not executable (2 of 3 sealed moves break declared contracts; not run). Tasks 00f035a, 5752f68 (target module removed upstream by task 60f676e) and cd83bad, 0cd8ecc (divergent pre-0.19 line; C does not re-apply) excluded from A and C; 6 tasks x 2 x 3 = 36 runs. Mechanical conflict rule for kedro/io/__init__.py. Observation: maintainers removed the sealed C target 20 days after the snapshot. | Gates forbid relaxing contracts; per-task bases (D4) cannot carry the refactoring where the module no longer exists or the contract set differs. | Before any kedro follow-up run. File PREREG_AMENDMENTS_2026-10-05g.md, SHA-256 673f3a823e8181eceaaa39985560258c0172d7e8bcfb85e77fb0070d0ddd8e92; C patch c454b546... |
| 2026-10-05 | E2 (kedro environment/spec): kedro-datasets 1.7.0 -> 1.8.0 (current at task dates); test files deleted by a PR excluded from the specification; the first six kedro runs are void and all kedro runs re-run from the same seeded schedule; base suites recomputed. | Acceptance tests could not be collected (missing CSVDataset etc.; git error text written into deleted spec files). | Before any kedro evaluation. File PREREG_AMENDMENTS_2026-10-05h.md, SHA-256 c0934656f341683f835a7c6d93e97e91ba698d27b05110822331b65523094814. |
| 2026-10-05 (E3) | kedro base suites: D5 empty-result rule (re-run once, else no record) extended to base suites; exit code kept | Three base-suite records (A_ab576bc, A_69a6fe1, A_60f676e) had zero tests; they would make every agent failure look new | Before any kedro evaluation; PREREG_AMENDMENTS_2026-10-05i.md sha256 d85f776c… |
| 2026-10-06 (L4 kopf result) | Registered analysis run once (results/l4/L4_kopf.txt). units_own C-A mean -0.033, d_z -0.32 (CI -0.62..0.00), Wilcoxon p 0.317, MixedLM -0.033 (p 0.317). Mechanical H3 rule fires on d_z; d_av = -0.03. Whole difference = one run (C_51c078d_r3) with no code change on the low-information task. Human change touches identical units on A and C bases in 10/10 tasks. | Reported reading: no effect of re-layering on propagation in kopf (weak-signal repository). 'Paired Cohen's d' in the registration is ambiguous between d_z and d_av; both are reported. Strict acceptance A 28/30, C 26/30; all 6 failures are the timing test test_nonthreadsafe_indeed_fails. | After all 80 kopf records; no kedro record analysed |
| 2026-10-06 (L4 kedro result) | Registered analysis (results/l4/L4_kedro.txt): units_own A 1.83, C 2.28; C-A +0.444, d_z +0.89 (CI 0.41..2.04), Wilcoxon p 0.102, MixedLM +0.444 (p<0.001); d_av +0.26. A-frame identical (diff 0). H3 disconfirmed. Extra unit = new layer kedro.partitioned co-touched with kedro.io in 2297d23 (3/3), 3f2a226 (2/3), 60f676e (3/3). All 3 C_60f676e runs kept an empty kedro.partitioned package. | Reading: the extraction split code that keeps changing with io; follow-up changes then cross two declared units. Human replay on C base failed to apply for 2297d23 and 60f676e (io/__init__ conflict); replay comparison uses the other 4 tasks. E4 (empty spec JUnit in A_2f526b6_r2) recorded, sha 2697e93c..., record re-evaluated; first analysis kept. | After all 48 kedro records; E4 found after the analysis and applied to the single affected record of 128 |
| 2026-10-06 (E5 + A6 pooled model) | A6 pooled MixedLM (96 runs, 16 tasks): own +0.146 (CI 0.049..0.243, p 0.003); A-frame -0.021 (p 0.32) [scripts/l4_pooled.py]. E5: RQ5 read at unit level (kedro.io never revised; kedro layer lists revised 2021, 2023); snapshot S2n kedro 1.06, kopf 1.29 reported; D6d 'out-of-sample' superseded by A6 note; A4 raters described as registered. | Reporting clarifications after review; no computed value changed. PREREG_AMENDMENTS_2026-10-06k.md sha 8cb2169b...; manifest PREREG_AMENDMENTS_MANIFEST.sha256 (10 files). | After the Layer-4 analysis |
