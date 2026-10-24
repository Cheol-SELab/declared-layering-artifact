# Correction E3 — empty kedro base-suite records (recorded 2026-10-05, before any kedro evaluation)

Three kedro base-suite runs (A_ab576bc, A_69a6fe1, A_60f676e) returned no JUnit results and were written as
records with zero tests; the base-suite script did not keep the exit code or log. A zero-test baseline would make
every test failure in an agent run look new, so these records are invalid. Correction: the D5 rule (an empty JUnit
result is re-run once; if still empty, no record is written and the failure is reported) now also applies to base
suites, and each record keeps the exit code. The three records are set aside in `C:/vdm/l4/kedro/bases/invalid/`
and the suites are re-run. Any further empty record from the running batch is handled the same way.
No kedro run had been evaluated.
