# Clarification E5 — reporting decisions made after the Layer-4 analysis (recorded 2026-10-06)

None of these changes any computed value; they fix how registered terms are read and reported.

1. RQ5 condition. RQ5 concerns repositories "where S2n is high but the declaration is never revised". A6 described
   kedro as "never revised"; at repository level this is wrong (its layer lists were revised in 2021 and 2023, both
   removing a layer: `versioning`, `extras.datasets`). The reading used in the paper is unit-level: the high-S2n
   unit `kedro.io` was never revised. This reading was chosen after the Layer-4 analysis and is reported as such.
2. Signal strength. A6 called kedro the strong-signal case by its bottom-layer S2n of 1.2–2.0 in 2022–2023. At the
   Layer-4 snapshots themselves S2n was 1.06 (kedro, 2023-10-01, 102 window commits) and 1.29 (kopf, 2026-01-01,
   25 window commits). The paper reports both.
3. D6d wording. D6d (`PREREG_AMENDMENTS_2026-10-05g.md`) calls the kedro removal "an out-of-sample observation".
   A6 had already recorded that the removal task was visible before the plan was generated. The paper follows A6
   and reports the removal as an observation, not as confirmation; D6d's wording is superseded.
4. A4 raters. The paper describes the raters as registered in A4: the authoring pipeline (an LLM assistant that
   knew the prediction) and a separately prompted LLM rater blind to it.
5. Provenance. The Layer-1 leave-one-repository-out range and the repository-cluster bootstrap interval are now
   produced by `scripts/l1_robustness.py` (`results/l1/L1_robustness.txt`); d_av and the A6 pooled model by
   `scripts/l4_pooled.py` (`results/l4/L4_pooled.txt`).
