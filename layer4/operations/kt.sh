#!/usr/bin/env bash
# kt <windows-or-/mnt path of a run dir> [pytest args...]  -- mirror the dir to WSL ext4 and run pytest there
# VDM_TAG (optional) gives the invocation its own mirror so concurrent runs on one dir cannot clobber each other
set -e
SRC="$1"; shift
case "$SRC" in [A-Za-z]:*) SRC="$(wslpath -u "$SRC")";; esac
NAME="$(echo "$SRC" | sed "s#[/: ]#_#g")"
DST="$HOME/vdm/mirror/$NAME${VDM_TAG:+_$VDM_TAG}"
mkdir -p "$DST"
rsync -a --delete --exclude .git --exclude __pycache__ --exclude .pytest_cache "$SRC/" "$DST/"
cd "$DST"
VENV="${VDM_VENV:-$HOME/vdm/venv-kopf}"
source "$VENV/bin/activate"
export PYTHONPATH="$DST" PYTHONDONTWRITEBYTECODE=1
if [ "${1:-}" = "--lint" ]; then exec lint-imports; fi
exec python -m pytest -p no:cacheprovider "$@"
