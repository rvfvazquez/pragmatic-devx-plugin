#!/usr/bin/env bash
# Tag and publish a release for a version that has already been bumped and merged.
#
# Usage:
#   ./scripts/release.sh 0.17.0            # create the tag and the GitHub release
#   ./scripts/release.sh 0.17.0 --dry-run  # run every check and print the release, change nothing
#
# Run it after the bump PR (scripts/bump-version.sh + a RELEASE-NOTES.md section) is
# merged. The tag is created on origin/main, so your checkout and working tree are
# never touched. The release title and body come from the RELEASE-NOTES.md section:
#   ## v<version> (<date>)
#   ### <Heading>      -> release title: "v<version> — <Heading>"
#   <body>             -> release notes

set -euo pipefail

VERSION="${1:-}"
DRY_RUN=false
[ "${2:-}" = "--dry-run" ] && DRY_RUN=true

if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "Usage: $0 <version> [--dry-run]   (version in semver, e.g. 0.17.0)"
    exit 1
fi

TAG="v$VERSION"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

FILES=(
    ".claude-plugin/plugin.json"
    ".claude-plugin/marketplace.json"
    ".codex-plugin/plugin.json"
    ".cursor-plugin/plugin.json"
    "gemini-extension.json"
    "package.json"
)

git fetch -q origin main --tags

if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
    echo "Error: tag $TAG already exists"
    exit 1
fi

# Every manifest on origin/main must carry the version being released.
for file in "${FILES[@]}"; do
    found=$(git show "origin/main:$file" | grep -o '"version": *"[^"]*"' | grep -o '"[0-9][^"]*"' | tr -d '"' | sort -u | tr '\n' ' ')
    if [ "$found" != "$VERSION " ]; then
        echo "Error: $file on origin/main has version(s) '${found% }', expected $VERSION. Merge the bump first."
        exit 1
    fi
done

# Extract the RELEASE-NOTES.md section for this version.
SECTION=$(git show origin/main:RELEASE-NOTES.md | awk -v v="## v$VERSION " 'index($0, v) == 1 {on=1; next} /^## v/ {on=0} on')
if [ -z "$(echo "$SECTION" | tr -d '[:space:]')" ]; then
    echo "Error: no '## v$VERSION' section in RELEASE-NOTES.md on origin/main"
    exit 1
fi

HEADING=$(echo "$SECTION" | grep -m1 '^### ' | sed 's/^### //' || true)
if [ -z "$HEADING" ]; then
    echo "Error: the v$VERSION section has no '### <Heading>' line to use as the release title"
    exit 1
fi
TITLE="$TAG — $HEADING"
NOTES=$(echo "$SECTION" | sed '1,/^### /d' | sed '/./,$!d')

echo "Release: $TITLE"
echo "Commit:  $(git rev-parse --short origin/main) ($(git log -1 --format=%s origin/main))"

if $DRY_RUN; then
    echo "--- notes ---"
    echo "$NOTES"
    echo "--- dry run: nothing created ---"
    exit 0
fi

git tag -a "$TAG" -m "$TAG" origin/main
git push -q origin "$TAG"
printf '%s\n' "$NOTES" | gh release create "$TAG" --title "$TITLE" --notes-file - --latest --verify-tag
