#!/usr/bin/env bash
# Run all skill-triggering tests and report a summary.
# Usage: ./run-all.sh [max-turns]
#
# Each .txt file in prompts/ is treated as a test case.
# The filename (without extension) is the expected skill name.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPTS_DIR="$SCRIPT_DIR/prompts"
MAX_TURNS="${1:-3}"

PASS=0
FAIL=0
FAILED_SKILLS=()

echo "=== Pragmatic DevX — Skill Triggering Tests ==="
echo "Prompts dir: $PROMPTS_DIR"
echo "Max turns:   $MAX_TURNS"
echo ""

for prompt_file in "$PROMPTS_DIR"/*.txt; do
    skill_name=$(basename "$prompt_file" .txt)
    echo "--- Testing: $skill_name"

    if bash "$SCRIPT_DIR/run-test.sh" "$skill_name" "$prompt_file" "$MAX_TURNS"; then
        PASS=$((PASS + 1))
    else
        FAIL=$((FAIL + 1))
        FAILED_SKILLS+=("$skill_name")
    fi
    echo ""
done

echo "=== Summary ==="
echo "✅ Passed: $PASS"
echo "❌ Failed: $FAIL"

if [ ${#FAILED_SKILLS[@]} -gt 0 ]; then
    echo ""
    echo "Failed skills:"
    for s in "${FAILED_SKILLS[@]}"; do
        echo "  - $s"
    done
    exit 1
fi

echo ""
echo "All tests passed."
exit 0
