#!/usr/bin/env bash
# human-PR replays on the per-task bases (reference sets and the relabelling-only counterfactual)
REPO=$1; shift; CONDS="$@"
TASKS=$(python -B -c "import l4h;print(' '.join(l4h.TASKS['$REPO']))")
run1(){ c=$1; t=$2; L=/c/vdm/l4/$REPO/logs/replay_${c}_$t.log
  python -B -X utf8 l4h.py replay $REPO $c $t > $L 2>&1 && python -B -X utf8 l4h.py eval $REPO $c $t replay >> $L 2>&1; echo "$c $t rc=$? $(tail -1 $L | cut -c1-260)"; }
export -f run1; export REPO
for c in $CONDS; do for t in $TASKS; do echo "$c $t"; done; done | xargs -P 4 -L 1 bash -c 'run1 $0 $1'
