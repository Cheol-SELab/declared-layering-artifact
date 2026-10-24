Declared Layering as a Revisable Hypothesis -- Replication Package
==================================================================

Scripts, data and records for:
Declared Layering as a Revisable Hypothesis: Python Layer Contracts, Their
Drift from Observed Change, and Agent-Executed Re-Layering

Authors: Cheol Young Park, Shou Matsumoto, Joongyoon Lee
Contact: cheol@selab.ai
Repository: https://github.com/Cheol-SELab/declared-layering-artifact

This is a research archive. The Layer-1 signal analysis is exploratory (its
definitions were frozen after a pilot on the same repositories); Layers 2-4 were
registered before their data were produced, but the registration was not
timestamped by a third party. The Layer-4 intervention is a feasibility pilot
(two repositories, 16 tasks, one agent and one model); its records do not
establish that re-layering helps or harms in general. The manuscript calls
Layers 1-4 "Steps 1-4".

Start here (Python 3.11+)
-------------------------
  python -B verify_public.py       file inventory, amendment hashes, sealed identities
                                   (standard library only)
  python -B reproduce_results.py   recomputes the registered and post hoc reports from
                                   the archived records and compares them byte for byte
                                   with the stored reports (needs numpy, scipy, pandas,
                                   statsmodels)
  python -B posthoc/fetch_clones.py <new dir>
  python -B reproduce_results.py --clones <new dir>
                                   additionally re-mines the subject repositories at the
                                   recorded commits (S2n variants, Layer-2 location)

reproduce_results.py covers the Layer-4 reports for kopf and kedro, the pooled
Layer-4 model, the Layer-1 leave-one-out and bootstrap figures, the population
figures and the post hoc reports below. It runs the study scripts unchanged, except that the evaluation
host's record root C:/vdm/l4 is redirected to layer4/ in a temporary copy.
The full run takes about two hours, almost all of it the permutation tests of
posthoc_l1.py and posthoc_l1_extra.py.

Post hoc analyses (not registered; reported as post hoc in the manuscript)
-------------------------------------------------------------------------
posthoc/posthoc_l1.py  RQ1: both labels; exact circular-shift permutation within
                       repository (overlapping windows); non-overlapping windows;
                       prospective past-only z-score; precision, recall and false
                       alarms at fixed thresholds; pooled AUC with the control
                       repositories; activity direction, activity-controlled model
                       under both labels, S2n shrunk toward the repository mean.
posthoc/posthoc_l1_extra.py
                       RQ1, second review round: leave-one-out and residualized AUC
                       under both labels; declaration regimes (post-revision
                       indicator, time since revision, z within regime); S2 in place
                       of S2n; Monte Carlo error; bk-user with its round-3 values.
posthoc/posthoc_s2n_variants.py
                       RQ1 with S2n recomputed from the repositories under each
                       implementation choice (numerator, path filter, sweep cut-off
                       5/10/none, bottom rank, expanded units, contract choice).
                       Variant 0 must reproduce the archived S2n exactly. Needs clones.
posthoc/posthoc_rq2.py RQ2: sealed proposals against the mechanically diffed
                       revisions; location hits against random-unit baselines.
                       Needs clones.
posthoc/posthoc_l4.py  RQ3-RQ5 with the task as the unit: per-task differences,
                       exact Wilcoxon and sign tests, smallest attainable p.
posthoc/posthoc_l4_extra.py
                       Lines changed with the task as the unit; edits to test files
                       outside the specification; units touched by the human change
                       in the kedro tasks excluded under D6.
posthoc/posthoc_pop.py Funnel counts; revisions per declaration-year; Kaplan-Meier
                       time to first revision; repository age by cohort.
posthoc/figures_v2.py  Revised Figures 1 and 2 (figures/v2/).
posthoc/fetch_clones.py
                       Clones the ten subject repositories at the recorded HEADs.
posthoc/RATER_PROVENANCE.txt
                       Models and prompts of the prediction-check raters and the AI
                       tools used in the study, from the study session log.
posthoc/results/       Outputs of the scripts above.

Registration
------------
registration/REGISTRATION_rev23_en.md
                       English translation of the registration document (revision 23,
                       with the full change log). The Korean original is not part of
                       the archive; registration/README.txt records its SHA-256.

Known discrepancies in archived records (files kept unchanged because they are hashed)
------------------------------------------------------------------------------------
- PREREG_AMENDMENTS_2026-10-05g.md (D6d) says the kedro removal came "twenty days" after
  the snapshot; commit 60f676e is dated 2023-10-24, 23 days after 2023-10-01.
- The registration change log records the Layer-2 result as 7 mismatches and 6 misses;
  pilot/LAYER2_RESULTS.md's own table, without the two quarters it excludes, gives 8 and 5.
- A4 and E5 describe prediction-check rater 1 as "the author pipeline"; it was a separate
  sub-agent with the same prompt as rater 2 (posthoc/RATER_PROVENANCE.txt).
- The "detail" fields of study/data/layer2_proposals.json contain a mis-encoded arrow
  (the UTF-8 bytes of the arrow U+2192 decoded as cp1252); the file is sealed and left as is.
- blind_scan.py passes the window dates to git without a time of day; git reads them at the current
  time of day, so S2n can differ by 0.01-0.02 in a few quarters with the time at which a scan runs.
  posthoc_s2n_variants.py pins git's clock (GIT_TEST_DATE_NOW) to the archived scans (2026-10-05 23:05 UTC).
- The registration worded the S2n numerator as a share of commits; blind_scan.py counts
  unit touches. posthoc_s2n_variants.py reports both.

Contents
--------
study/                 Study workspace as used, byte-identical (code, data and records).
  scripts/             Population search and scanner (gh_search.py, gh_probe_decl.py,
                       pop_decl_history.py), snapshot/S2n scanner (blind_scan.py),
                       Layer-1 analysis (l1_analysis.py, l1_robustness.py), Layer-4
                       harness and workers (l4h.py, l4_worker.py, l4_bases*.py,
                       l4_basesuite.py), Layer-4 analysis (l4_analyze.py,
                       l4_pooled.py), figures (fig1_adoption.py, fig2_s2n.py).
  data/                Population declaration histories (pop_decl_history.json,
                       gh_decl.json), sealed Layer-2 proposals (layer2_proposals.json),
                       clone identities and Layer-4 human baselines.
  results/             Layer-1 quarter tables and scans (l1, l1_utc, l1_repro),
                       Layer-4 reports (l4), population figures (pop_stats.txt).
  a4/                  Prediction check (Section 5.4): commit list, rater prompts,
                       ratings of both raters.
  l4_plans/            Sealed Layer-4 plans (tie_rule/ holds the plans used).
  l4_prompts/          Agent prompt template, refactoring prompts and every per-run
                       prompt (runs_kedro_void1/ = voided runs, correction E2).
  l4_usage.jsonl       Agent usage log (tokens, tool calls, minutes).
  PREREG_AMENDMENTS_*  Amendment, deviation and correction files with SHA-256 hashes
                       and PREREG_AMENDMENTS_MANIFEST.sha256.
  L4_OPERATIONS_LOG.md Operational events that changed no recorded outcome.
pilot/                 Pilot rounds 1-3 (scans, replication notes, early harness)
                       written before the Layer-1 definitions were frozen.
layer4/<repo>/         Layer-4 records from the evaluation host (kedro, kopf):
  results/             One record per run, including replays of the human change.
  results_invalid/     Records superseded under deviations D5/E4, kept separately.
  runs/, bases/        Run and base metadata (.meta.json, apply status).
  run_diffs/           The agent's change in each run, as a patch against the run's
                       base tree (exported from the run directories; empty patches
                       are runs or replays that changed nothing or did not apply).
  void1/runs/          Metadata of the six voided early kedro runs (E2).
  C_moves.json         Move map of the frozen re-layering.
  C_refactor_nodocs.patch
                       kedro frozen re-layering as registered (SHA-256 c454b546...);
                       C_refactor.patch is the same change including documentation.
  C_refactor_derived.patch
                       kopf frozen re-layering, derived for this archive as the diff
                       between the frozen A and C trees (no patch file was stored).
  logs/                Evaluation logs.
layer4/operations/     Queue files, worker scripts and logs of the evaluation host.
figures/               Figures 1 and 2 as first drawn; figures/v2/ the versions in the manuscript.

Not included
------------
- Clones of the subject repositories and the full run/base working trees
  (identified by upstream commits in the records; about 175,000 files).
- The Python environments used for test execution (CPython 3.12 for kopf,
  3.10 for kedro, dependencies as of the snapshot date; see the logs).
- Agent runs cannot be replayed from this archive: the agent was a Claude Code
  sub-agent (Sonnet 5.5, deviation D2) invoked interactively; per-run prompts
  and the resulting changes are archived instead.
Scripts keep the absolute paths of the evaluation host (C:/vdm, /home/claude);
they are archived as executed and were not edited.
