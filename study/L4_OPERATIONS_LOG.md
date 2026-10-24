# Layer-4 operations log (events that changed no recorded outcome)

- 2026-10-05 ~23:45. The kopf/kedro evaluation worker was stopped by the host's background-job time limit with
  59 of 80 kopf records written. Unfinished items were re-queued; partially created replay directories were set
  aside unevaluated (`old_replays/stale5`).
- 2026-10-05 23:55–23:58. WSL stopped accepting commands under load (load average ~50 on 20 cores; six concurrent
  evaluations with 8 test workers each). Ten evaluations ended with a harness exception before writing any
  record. The harness now treats a non-numeric reply when polling for the exit code as transient. The Ubuntu
  distribution was restarted, partial replay directories were set aside (`old_replays/stale6`, `stale7`), and the
  59 unfinished items were re-queued with four concurrent evaluations. No result record was written, changed or
  removed by these events.
