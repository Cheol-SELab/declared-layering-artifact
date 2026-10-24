# Deviation D3 and analysis correction E1 (2026-10-05, recorded before their results were opened)

## D3 — tie in the §6 decision table for kopf (condition C)
At the 2026-01-01 snapshot the busiest bottom unit is `kopf._core.actions` (5 window commits). Two direct
sub-modules tie on every table quantity: `invocation` and `loggers` (3 commits each, r = 0.67, share 60%).
The first generator run resolved the tie by insertion order (`invocation`; plan SHA-256
a20915f4b2e5fd1c4f399ed375e58eb2025ed9d5e6546a8888974529bd5817a0). The tie rule registered in A5 is
"larger m"; operationalised as lines of code at the snapshot it selects `loggers` (241 vs 158 lines).
Plan regenerated with the explicit rule (SHA-256 1355eacd6432ddc66c197345088306036970ee067806d0ce8016f1317a4beda2).
**Condition C target: EXTRACT `kopf._core.actions.loggers` one rank up**, i.e. a new layer directly above
`kopf._core.actions` in the core-layers contract. No follow-up task, agent run or outcome had been produced.
Condition B: the co-change recommender found 0 candidates (25 window commits); for kopf, B is identical to
A and is not run separately (reported as "B = A, no recommendation").

## E1 — Layer-1 label implementation and censoring
(i) A2 is implemented as a **net** change of the layers lists between the snapshot at t and at t+92 days
(contract names and ignore_imports excluded). An "any change within the quarter" implementation flags kedro
2023-10 (merge flip-flops of `kedro.extras.datasets`) and legadilo 2024-07 (a swap reverted after a week),
which A2 explicitly names as non-positives; the net definition reproduces those two exclusions.
(ii) The 2026-10-01 quarter has an unobserved outcome window (data end 2026-10-05). It was counted as a
negative in rounds 1–3. Results are reported both with it (as registered) and censored (corrected).
