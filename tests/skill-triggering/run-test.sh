#!/usr/bin/env bash
# Test that a pragmatic-devx skill triggers on a natural language prompt.
# Usage: ./run-test.sh <skill-name> <prompt-file> [max-turns]
#
# Tests whether Claude triggers the expected skill based on a realistic user
# prompt — without explicitly naming the skill. Requires the Claude Code CLI
# and the pragmatic-devx plugin installed or available via --plugin-dir.

set -e

SKILL_NAME="$1"
PROMPT_FILE="$2"
MAX_TURNS="${3:-3}"

if [ -z "$SKILL_NAME" ] || [ -z "$PROMPT_FILE" ]; then
    echo "Usage: $0 <skill-name> <prompt-file> [max-turns]"
    echo "Example: $0 pragmatic-spec-create ./prompts/pragmatic-spec-create.txt"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

TIMESTAMP=$(date +%s)
OUTPUT_DIR="/tmp/pragmatic-devx-tests/${TIMESTAMP}/skill-triggering/${SKILL_NAME}"
mkdir -p "$OUTPUT_DIR"

PROMPT=$(cat "$PROMPT_FILE")

echo "=== Skill Triggering Test ==="
echo "Skill:       $SKILL_NAME"
echo "Prompt file: $PROMPT_FILE"
echo "Max turns:   $MAX_TURNS"
echo "Plugin dir:  $PLUGIN_DIR"
echo "Output dir:  $OUTPUT_DIR"
echo ""

cp "$PROMPT_FILE" "$OUTPUT_DIR/prompt.txt"

LOG_FILE="$OUTPUT_DIR/claude-output.json"
cd "$OUTPUT_DIR"

echo "Running claude -p with natural language prompt..."
timeout 300 claude -p "$PROMPT" \
    --plugin-dir "$PLUGIN_DIR" \
    --dangerously-skip-permissions \
    --max-turns "$MAX_TURNS" \
    --output-format stream-json \
    > "$LOG_FILE" 2>&1 || true

echo ""
echo "=== Results ==="

# Check if skill was triggered — match with or without plugin namespace prefix
SKILL_PATTERN='"skill":"([^"]*:)?'"${SKILL_NAME}"'"'
if grep -q '"name":"Skill"' "$LOG_FILE" && grep -qE "$SKILL_PATTERN" "$LOG_FILE"; then
    echo "✅ PASS: Skill '$SKILL_NAME' was triggered"
    TRIGGERED=true
else
    echo "❌ FAIL: Skill '$SKILL_NAME' was NOT triggered"
    TRIGGERED=false
fi

echo ""
echo "Skills triggered in this run:"
grep -o '"skill":"[^"]*"' "$LOG_FILE" 2>/dev/null | sort -u || echo "  (none)"

echo ""
echo "First assistant response (truncated):"
grep '"type":"assistant"' "$LOG_FILE" | head -1 \
    | jq -r '.message.content[0].text // .message.content' 2>/dev/null \
    | head -c 500 || echo "  (could not extract)"

echo ""
echo "Full log: $LOG_FILE"

if [ "$TRIGGERED" = "true" ]; then
    exit 0
else
    exit 1
fi
