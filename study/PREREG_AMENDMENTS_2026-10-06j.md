# Correction E4 — empty specification result (recorded 2026-10-06, after the registered kedro analysis)

Finding: in kedro run A_2f526b6_r2 the specification invocation returned no JUnit results, although the same
specification yielded 73 results on the task base (`pre_spec`) and the run's full suite passed every reference
test (no reference test among its failures; its failures equal the base's). The record therefore failed strict
acceptance through a missing measurement, not through a failing test.

Rule (extends D5 to specification runs): when the specification invocation returns no results although the base
yielded results, the record is a measurement failure; it is set aside in `results_invalid/` and the run is
re-evaluated once, unchanged. A scan of all 128 Layer-4 records (kopf and kedro) found exactly one record meeting
this condition. Records of documentation task 20de08c have no specification tests on the base either (D5b) and
are not affected.

Reporting: the registered analysis as first run (`results/l4/L4_kedro.txt`) is kept and reported. The
re-evaluated analysis is written to a new file and reported beside it. The H3 decision does not depend on this
record, because acceptance does not enter the primary outcome (units touched).
