#!/usr/bin/env bash
# ktd <tag> <run dir> [pytest args...]: detached kt with a private mirror; writes <tag>.log and, on exit, <tag>.rc
TAG="$1"; shift
export VDM_TAG="$(basename "$TAG")"
~/vdm/bin/kt "$@" > "$TAG.log" 2>&1
rc=$?
rm -rf "$HOME/vdm/mirror/"*"_$VDM_TAG"
echo $rc > "$TAG.rc"
