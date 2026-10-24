#!/usr/bin/env bash
# evalq.sh <repo> <cond_task_rep> ...   evaluate finished runs (sequentially in one background job)
REPO=$1; shift
for run in "$@"; do IFS=_ read c t r <<< "$run"; python -B -X utf8 l4h.py eval $REPO $c $t $r > /c/vdm/l4/$REPO/logs/eval_$run.log 2>&1; echo "$run rc=$? $(tail -1 /c/vdm/l4/$REPO/logs/eval_$run.log | cut -c1-240)"; done
