#!/usr/bin/env bash
# Launch Claude Code with a permission layer on top of the stable .claude/settings.json.
#
#   harness/tools/claude-layer.sh exploration [claude args...]   read-only, plan mode, no egress
#   harness/tools/claude-layer.sh delivery    [claude args...]   edit code/tests/docs, dev deploys only
#
# The layer is merged on top; .claude/settings.json (hooks, deny rules) is never swapped out.
set -euo pipefail
LAYER="${1:-}"
case "$LAYER" in
  exploration|delivery) ;;
  *) sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 1 ;;
esac
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
FILE="$ROOT/.claude/perms/${LAYER}.json"
[[ -f "$FILE" ]] || { echo "Missing $FILE. Is the harness installed here?" >&2; exit 1; }
export HARNESS_LAYER="$LAYER"
echo "Permission layer: $LAYER  ($FILE)"
cd "$ROOT"
exec claude --settings "$FILE" "${@:2}"
