#!/usr/bin/env bash
# Bump the plugin version across all five files that carry a "version" field.
#
# Usage:
#   ./scripts/bump-version.sh 0.5.0
#
# Files updated:
#   .claude-plugin/plugin.json
#   .claude-plugin/marketplace.json
#   .codex-plugin/plugin.json
#   .cursor-plugin/plugin.json
#   gemini-extension.json

set -euo pipefail

NEW_VERSION="${1:-}"

if [ -z "$NEW_VERSION" ]; then
    echo "Usage: $0 <new-version>"
    echo "Example: $0 0.5.0"
    exit 1
fi

# Validate semver format (major.minor.patch)
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Error: version must be semver format (e.g. 0.5.0)"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

FILES=(
    ".claude-plugin/plugin.json"
    ".claude-plugin/marketplace.json"
    ".codex-plugin/plugin.json"
    ".cursor-plugin/plugin.json"
    "gemini-extension.json"
)

echo "Bumping version to $NEW_VERSION in:"

for file in "${FILES[@]}"; do
    full_path="$PLUGIN_ROOT/$file"
    if [ ! -f "$full_path" ]; then
        echo "  ⚠️  $file — not found, skipping"
        continue
    fi

    # Extract current version for display
    current=$(grep -o '"version": *"[^"]*"' "$full_path" | head -1 | grep -o '"[0-9][^"]*"' | tr -d '"')

    # Replace the version field value (handles both "version": "x.y.z" and nested in plugins array)
    sed -i.bak "s/\"version\": *\"[0-9][^\"]*\"/\"version\": \"$NEW_VERSION\"/g" "$full_path"
    rm -f "${full_path}.bak"

    echo "  ✅  $file ($current → $NEW_VERSION)"
done

echo ""
echo "Done. Verify with: grep -r '\"version\"' .claude-plugin .codex-plugin .cursor-plugin gemini-extension.json"
