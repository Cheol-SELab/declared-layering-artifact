# Pilot (Layer 1): Does declared–observed discrepancy carry signal?  — v2 (corrected)

Date: 2026-10-05. Subjects: openedx/openedx-learning (16 quarterly snapshots 2023-01 → 2026-10) and
seddonym/import-linter (control). Tools: `cochange_pilot.py` (manual units), `blind_scan.py`
(automatic: parses `.importlinter` at each snapshot, expands container layers to fixpoint,
rename-aware co-change over the preceding 12 months, static imports from AST; declaration-change
dates are joined only after scoring).

## What the blind scan found

| Score | Definition | AUC vs "declaration revised next quarter" (12 quarters with ≥10 commits, 5 positives) |
|---|---|---|
| S2 bottom-layer share | share of window commits touching the declared most-stable layer | **0.70** |
| S1 hidden pairs | unit pairs co-changing (sup≥3, conf≥0.5) with no static import either way | 0.59 |
| S3 uncovered units | sub-packages under a declared container not named in any layer | 0.51 |

- The two highest S2 values each immediately preceded the two major restructures:
  S2=0.80 at 2026-01-01 → 4 declaration revisions in 2026-02/03; S2=0.73 at 2024-04-01 → revision 2024-04-23.
  S2=0.78 at 2024-10-01 was a false alarm (no revision for 9 months).
- A binary OR-flag over S1/S2/S3 fires every quarter: precision = base rate (0.44). Thresholds are useless;
  only score *level* carries information, and only S2 clearly so.

## Corrections to the v1 findings

1. **"sections/subsections/units were merged" — RETRACTED.** They were moved together in 2026-02 but still
   exist as separate applets at HEAD, subclassing `Container`. They are also still **undeclared** in the applet
   layering at HEAD. This is an open discrepancy, not a resolved one.
2. **"hidden coupling" (S1) is largely confounded.** Of the no-static-edge co-change pairs, most co-commits also
   touched `publishing` (collections~components 9/11; sections~units 14/16) — a common dependency changing in the
   same commit — and several are repo-wide sweep commits (reformat, release). S1 as defined measures ripple and
   sweeps, not hidden coupling. It needs (a) conditional co-change excluding commits that touch a shared static
   dependency, and (b) exclusion of commits touching > k units.
3. **The extraction finding STANDS.** Container code (13 `*container*` functions) lived in `publishing`, the
   declared bottom layer; `publishing` was touched in 21/41 pre-restructure commits; on 2026-03-26 a `containers`
   applet was created and `publishing/api.py` now has 0 container functions (containers/api.py has 20).
   This is the S2 signal: a declared-stable layer carrying feature volatility → extract the cause.
4. **Declaration loophole STANDS.** `backup_restore` imported `openedx_learning.api.authoring_models`, outside the
   declared layer `api.authoring`; later resolved by flattening `api`.

## Control: seddonym/import-linter (2023-09 → 2026-09)

All co-change pairs with support ≥ 3 follow a static import edge in the declared direction; no upward imports;
6 declaration revisions, all additive. The method reports nothing to fix. Negative control behaves as expected.

## What this does and does not show

- Shows: in one architecture-conscious repo, the volatility of the declared bottom layer is a moderate
  leading indicator (AUC 0.70, N=12) of the maintainers revising their declaration, and the two largest
  restructures were each preceded by the two largest S2 peaks. Humans revised the declaration 14 times —
  the loop is already run manually and slowly.
- Does not show: that automatic proposals match human decisions (Layer 2), that agents execute them correctly
  (Layer 3), or that subsequent change cost falls (Layer 4). S1 and S3 are not yet usable as predictors.

## Open (forward) discrepancies at HEAD — registered as predictions

- `sections`, `subsections`, `units` undeclared since 2025-03; method says: declare (as siblings at one layer) or merge.
- `collections ~ components` co-change sup 10 conf 0.77, but mostly via `publishing` → not a boundary problem;
  the real question is why `publishing` still appears in 30/73 commits after the extraction.

## Next

1. Redefine S1 as conditional co-change; exclude sweep commits; re-run.
2. Replace S2 "bottom share" with a rank discordance over all layers (declared stability rank vs observed change rank).
3. Add 3–5 repos; the control shows the method is quiet where it should be, but one positive case is not evidence.
