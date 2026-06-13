#!/usr/bin/env bash
# Sync AGENTS.md from CLAUDE.md.
#
# AGENTS.md is the Codex CLI context file — equivalent to CLAUDE.md for Claude Code.
# On Windows (core.symlinks=false) we cannot use a git symlink, so AGENTS.md is
# maintained as a copy with a mirror notice prepended.
#
# Run this after editing CLAUDE.md:
#   bash scripts/sync-agents.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SOURCE="$ROOT/CLAUDE.md"
TARGET="$ROOT/AGENTS.md"

NOTICE='> **Mirror of CLAUDE.md** — This file is kept in sync with `CLAUDE.md`. Edit `CLAUDE.md` and run `scripts/sync-agents.sh` to propagate changes here.'

{
    printf '%s\n\n' "$NOTICE"
    cat "$SOURCE"
} > "$TARGET"

echo "✅ AGENTS.md synced from CLAUDE.md"
