# Pre-registration amendments A3–A5, deviation D2 (2026-10-05, second session)

Recorded **before** any of the analyses below were computed. The Layer-1 reproduction scan was running
when this file was written; none of its outputs had been opened. SHA-256 of this file is recorded in the
pre-registration §10 table.

## A3 — RQ1 robustness to the feature-activity confound (Layer 1)

Motivation: Layer 2 showed that 9/13 revisions are feature-driven layer additions/removals, so S2n and the
revision label may share a common cause (activity).

- Label: amendment A2 (layers-list content change within 92 days; ignore_imports-only edits are negative).
- Covariates per quarter, from the same 12-month window as S2n:
  (i) `log_n` = log(commits retained by the §3 filter);
  (ii) `new_pkgs` = number of sub-packages of any declared container/parent that exist at the snapshot but did
  not exist 12 months earlier (proxy for new-feature activity).
- Model: pooled logistic regression with repository fixed effects; predictors z-scored within repository:
  `y ~ z(S2n) + z(log_n) + z(new_pkgs) + repo`. Inference: within-repository label permutation (5,000) of
  the S2n coefficient's likelihood-ratio statistic; also the AUC of S2n residualised on the two covariates
  within repository.
- Decision rule: H1 is reported as **robust to activity** if beta_S2n > 0 and one-sided permutation
  p < 0.10; otherwise as **explained by activity**. Both the A2-relabelled unadjusted AUC and the adjusted
  result are reported.
- Additional-target rule (§4): for all 106 mature repositories, the first appearance of the declaration
  file is determined from the GitHub commits API on the declaration path (oldest commit). Any repository
  not among the 15 already screened whose declaration is present at >= 8 quarterly snapshots up to and
  including 2026-10-01 is screened with the §3 thresholds and, if it passes, added to the pooled H1 test
  (with and without it reported). The handover's `clone_info.json` covers only 65 repositories, so this
  check is redone rather than assumed.

## A4 — Pre-registered prediction check that is due now

§5 prediction "openedx-learning `publishing` contains a second change cause" is checkable now. Procedure:
every non-merge commit touching `publishing` after the 2026-03 containers extraction (as of 2026-10-05) is
classified by cause from its subject/body and diff stat into {versioning/draft-state, containers/
hierarchy, API surface, other}. Classification is done by two independent raters (the author pipeline and a
separately prompted LLM rater blind to the hypothesis); Cohen's kappa reported. Confirmation: one non-
container cause accounts for >= 30% of those commits.

## A5 — Layer 4 pilot specification (kopf), fixed before any agent run

Snapshot: kopf `51b664f` (last commit before 2026-01-01). Follow-up tasks: the 10 PR groups in
`l4_baseline.json` (deviation D1 rule), taken as they are, without discretion.

**C-proposal derivation uses only pre-snapshot history.** The follow-up PRs are the test set and are not
consulted when choosing the refactoring. (The handover note suggested inspecting the 7 baseline PRs that
touch the bottom; that would leak the outcome and is not done.)

- C (full loop): apply the §6 decision table at the snapshot (12-month window). If it yields EXTRACT or
  PROMOTE, that is the proposal. If it yields HOLD, the fallback is fixed now: among bottom-third units, take
  the unit U with the most retained commits in the window; within U take the direct sub-module m with the
  highest count of commits that also touch a higher-ranked unit of the same contract (ties: larger m);
  EXTRACT m one rank up as a new sibling layer. The proposal (target declaration + move plan) is written to
  `l4_plans/kopf_C.json` and hashed before the refactoring is executed.
- B (co-change recommendation): file-level move recommendation in the style of de Oliveira et al. (2019):
  for each .py file f in a declared unit with >= 4 window commits, compute co-change support with each other
  unit; recommend moving f to unit V if support(f, V) > support(f, own unit's other files) and
  support(f, V) >= 3. At most 3 recommendations (highest support). Declaration unchanged. Written to
  `l4_plans/kopf_B.json` and hashed before execution.
- Refactoring execution (B and C): one refactoring per condition, performed by the same coding agent as the
  follow-up tasks, under the §7 gates: lint-imports passes on the condition's declaration (original for B,
  updated for C), full test suite has no new failures relative to the snapshot, no edge added to the
  declaration (C only adds the extracted layer; it relaxes nothing), no new top-level module outside the
  declaration. Up to 3 attempts. The accepted refactored tree is frozen and hashed; all follow-up runs of
  that condition start from it. If C fails all 3 attempts, the §7 stop rule applies (report and stop).
  The mutation-score gate is not wired in this pilot (recorded as a known gap).

## D2 — Agent backend and isolation (deviation from §7 "same model, two models")

- Agent: Claude Code sub-agent, model Sonnet 5.5, identical task prompt template across conditions
  (`l4_prompt_template.md`). One model only in the pilot; the second model is deferred to the full run.
- Isolation: each run gets a fresh directory created from `git archive` of the condition's frozen tree,
  re-initialised as a new git repository with a single commit. No project history is present, so the human
  follow-up PR cannot be read from the clone. The prompt forbids network access to the upstream project.
- Acceptance spec: the human PR's test files are copied in; the agent must not edit them (checked by hash).
- Tests run in WSL Ubuntu, CPython 3.12, one virtual environment per condition built from the snapshot's
  dependency specification.
- Repetitions: 3 per task x condition (90 follow-up runs), as in the handover plan.
- Outcomes (computed by the harness, never reported by the agent): (a) declared units changed under the
  condition's own declaration [primary, as §3]; (a') units changed with moved files mapped back to their
  snapshot unit [sensitivity, guards against relabelling artefacts]; (b) files changed; (b') lines
  added+deleted; (c) spec passed (strict: every spec test that fails at baseline passes, and no test passing
  at baseline fails); lint-imports violations; touches-bottom (reported, but **not** used as evidence for
  H3 because extraction changes bottom membership by construction); wall time; turns/tokens when available.
- Analysis: per-task means over repetitions; paired Cohen's d (C−A, C−B, B−A) on (a) with bootstrap 95% CI
  over tasks; linear mixed model `units ~ condition + (1|task)`; Wilcoxon signed-rank as a check. H3/H4
  decision thresholds unchanged from §8. N = 10 tasks makes this a pilot; it is reported as such.
