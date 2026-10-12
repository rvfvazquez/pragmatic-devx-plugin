#!/usr/bin/env bash
# glossary-drift.sh — read-only drift report between docs/glossary/ and the code.
#
# Usage: glossary-drift.sh [--root DIR] [--context NAME]
#   --root DIR       project root (default: current directory)
#   --context NAME   check only the context with this name (case-insensitive)
#
# For every context in docs/glossary/context-map.md that has a `Code` column
# (comma-separated paths, relative to the root), it reports:
#   STALE    a term's `_In code_` identifier no longer appears in the code
#   AVOIDED  a word listed under a term's `_Avoid_` is used as an identifier
#            (a term's own `_In code_` identifier is never reported)
#   MISSING  a glossary file the map links to does not exist
#   NOPATH   a Code path does not exist
# Under each context it also prints when it was last synced (the map's `Synced`
# column), as information — never as a finding.
#
# It never writes anything. Exit: 0 no findings · 1 findings · 2 usage error
# or no context map. Needs bash, grep, awk and sed; git is optional (used only
# for each context's `Synced` age: how many commits touched its paths since). Matching is a text heuristic, not a parser: it
# sees what grep sees: comments and strings count as matches (an old name left in a
# comment hides a STALE; an avoided word in a comment is reported), and dynamically
# built or non-Latin identifiers are missed. Treat findings as questions, not verdicts.

set -u

ROOT="$PWD"
ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root)    ROOT="${2:-}"; shift 2 ;;
    --context) ONLY="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,22p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

MAP="$ROOT/docs/glossary/context-map.md"
[ -f "$MAP" ] || { echo "no docs/glossary/context-map.md under $ROOT" >&2; exit 2; }
cd "$ROOT" || exit 2

EXCLUDES=(--exclude-dir=.git --exclude-dir=node_modules --exclude-dir=vendor
          --exclude-dir=dist --exclude-dir=build --exclude-dir=target
          --exclude-dir=.venv --exclude-dir=__pycache__ --exclude-dir=docs
          --exclude-dir=.next --exclude-dir=coverage)

# Fields are separated by \037 (unit separator), not tab: bash `read` collapses runs of
# whitespace IFS characters, which would silently shift empty fields.
# Context map rows -> "name<US>glossary-link<US>code-paths<US>synced". A row counts when one of
# its cells links to a glossary file; the first such cell is the Glossary column.
parse_map() {
  awk -F'|' '
    function trim(s) { gsub(/^[ \t\r]+|[ \t\r]+$/, "", s); return s }
    /^\|/ {
      if ($0 ~ /^\|[ \t:-]+\|/) next
      if (!hdr) {
        hdr = 1
        for (i = 2; i < NF; i++) {
          h = tolower(trim($i))
          if (h == "code" || h ~ /^c.digo$/) codecol = i
          if (h == "synced") syncedcol = i
        }
        next
      }
      link = ""
      for (i = 3; i < NF; i++) {
        if (match($i, /\]\([^)]*\.md\)/)) { link = substr($i, RSTART + 2, RLENGTH - 3); break }
      }
      if (link == "" || link ~ /(^|\/)arch\//) next
      code = (codecol ? trim($codecol) : "")
      synced = (syncedcol ? trim($syncedcol) : "")
      print trim($2) "\037" link "\037" code "\037" synced
    }' "$MAP"
}

# One glossary file -> "term<US>avoid-csv<US>in-code-raw".
parse_terms() {
  awk '
    { sub(/\r$/, "") }
    function flush() { if (term != "") print term "\037" avoid "\037" incode; term = ""; avoid = ""; incode = "" }
    /^#/ { flush(); next }
    /^\*\*[^*]+\*\*[ \t]*$/ { flush(); t = $0; gsub(/^\*\*|\*\*[ \t]*$/, "", t); term = t; next }
    term != "" && /^_Avoid_:/  { a = $0; sub(/^_Avoid_:[ \t]*/, "", a); gsub(/\([^)]*\)/, "", a); avoid = a; next }
    term != "" && /^_In code_:/ { c = $0; sub(/^_In code_:[ \t]*/, "", c); incode = c; next }
    END { flush() }' "$1"
}

trim() { local s="$1"; s="${s#"${s%%[![:space:]]*}"}"; s="${s%"${s##*[![:space:]]}"}"; printf '%s' "$s"; }

# Backticked identifiers in an `_In code_` value.
incode_ids() { printf '%s' "$1" | grep -o '`[^`]*`' | tr -d '`' | sed -E 's/\(.*$//; s/[^A-Za-z0-9_$.].*$//' | grep -v '^$'; }

# grep -E pattern for an avoided word as an identifier component, or empty if unsafe.
avoid_pattern() {
  local w="$1"
  printf '%s' "$w" | grep -Eq '^[A-Za-z][A-Za-z0-9 -]*$' || return 0
  local lw cw uw first rest
  w="$(printf '%s' "$w" | tr -s ' -' ' ')"
  if [[ "$w" == *" "* ]]; then
    # multi-word: order line -> order[_-]?line, case-insensitive (caller passes -i)
    printf 'I:%s' "$(printf '%s' "$w" | tr 'A-Z' 'a-z' | sed 's/ /[_-]?/g')"
    return 0
  fi
  lw="$(printf '%s' "$w" | tr 'A-Z' 'a-z')"
  first="$(printf '%s' "${lw:0:1}" | tr 'a-z' 'A-Z')"; rest="${lw:1}"
  cw="$first$rest"; uw="$(printf '%s' "$lw" | tr 'a-z' 'A-Z')"
  printf 'E:(^|[^A-Za-z])%ss?([^a-z]|$)|%ss?([^a-z]|$)|(^|[^A-Z])%sS?([^A-Z]|$)' "$lw" "$cw" "$uw"
}

FINDINGS=0

# "synced <sha> · N commits touch these paths since" for one context.
sync_line() { # sha paths...
  local sha="$1" n; shift
  if [ -z "$sha" ]; then printf '  never synced\n'; return; fi
  if command -v git >/dev/null 2>&1 && git rev-parse --verify -q "$sha^{commit}" >/dev/null 2>&1; then
    n="$(git rev-list --count "$sha..HEAD" -- "$@" 2>/dev/null)"
    if [ "$n" = 1 ]; then printf '  synced %s · 1 commit touches these paths since\n' "$sha"
    else printf '  synced %s · %s commits touch these paths since\n' "$sha" "$n"; fi
  else
    printf '  synced %s (not found in this repository)\n' "$sha"
  fi
}

while IFS=$'\037' read -r cname glink codecell syncedcell; do
  [ -z "$cname" ] && continue
  if [ -n "$ONLY" ] && [ "$(printf '%s' "$cname" | tr 'A-Z' 'a-z')" != "$(printf '%s' "$ONLY" | tr 'A-Z' 'a-z')" ]; then continue; fi

  codecell="$(printf '%s' "$codecell" | tr -d '`')"
  paths=()
  IFS=',' read -ra raw <<<"$codecell"
  for p in "${raw[@]:-}"; do
    p="$(trim "$p")"
    case "$p" in ""|"—"|"-"|"–") continue ;; esac
    paths+=("$p")
  done

  if [ ${#paths[@]} -eq 0 ]; then
    printf '%s  (no Code column value — skipped)\n' "$cname"
    continue
  fi
  printf '%s  (%s)\n' "$cname" "$(IFS=,; echo "${paths[*]}")"
  sync_line "$(printf '%s' "$syncedcell" | grep -oE '[0-9a-fA-F]{7,40}' | head -1)" "${paths[@]}"

  existing=()
  for p in "${paths[@]}"; do
    if [ -e "$p" ]; then existing+=("$p")
    else printf '  NOPATH   %s does not exist\n' "$p"; FINDINGS=$((FINDINGS + 1)); fi
  done
  [ ${#existing[@]} -eq 0 ] && continue

  gfile="$ROOT/docs/glossary/${glink#./}"
  if [ ! -f "$gfile" ]; then
    printf '  MISSING  glossary file %s\n' "$glink"; FINDINGS=$((FINDINGS + 1)); continue
  fi

  terms="$(parse_terms "$gfile")"
  # all in-code identifiers of this context, lowercased, so a term's own identifier is never "avoided"
  all_ids="$(while IFS=$'\037' read -r _t _a _c; do incode_ids "$_c"; done <<<"$terms" | tr 'A-Z' 'a-z' | sort -u)"

  checked=0; ctx_findings=0
  while IFS=$'\037' read -r term avoid incode; do
    [ -z "$term" ] && continue
    checked=$((checked + 1))

    while IFS= read -r id; do
      [ -z "$id" ] && continue
      if ! grep -rwqIF "${EXCLUDES[@]}" -- "$id" "${existing[@]}" 2>/dev/null; then
        printf '  STALE    %-14s `%s` not found\n' "$term" "$id"
        ctx_findings=$((ctx_findings + 1))
      fi
    done < <(incode_ids "$incode")

    IFS=',' read -ra words <<<"$avoid"
    for w in "${words[@]:-}"; do
      w="$(trim "$w")"; [ -z "$w" ] && continue
      lw="$(printf '%s' "$w" | tr 'A-Z' 'a-z' | tr -d ' -')"
      if printf '%s\n' "$all_ids" | grep -qxF -- "$lw"; then continue; fi
      pat="$(avoid_pattern "$w")"; [ -z "$pat" ] && continue
      flags="-rnIE"; [ "${pat:0:2}" = "I:" ] && flags="-rniIE"
      matches="$(grep $flags "${EXCLUDES[@]}" -- "${pat:2}" "${existing[@]}" 2>/dev/null)"
      [ -z "$matches" ] && continue
      n="$(printf '%s\n' "$matches" | wc -l | tr -d ' ')"
      first="$(printf '%s\n' "$matches" | head -1 | cut -d: -f1,2)"
      printf '  AVOIDED  %-14s "%s" — %s (%s use%s)\n' "$term" "$w" "$first" "$n" "$([ "$n" = 1 ] || echo s)"
      ctx_findings=$((ctx_findings + 1))
    done
  done <<<"$terms"

  [ $ctx_findings -eq 0 ] && printf '  OK       %s term%s checked\n' "$checked" "$([ "$checked" = 1 ] || echo s)"
  FINDINGS=$((FINDINGS + ctx_findings))
done < <(parse_map)

printf '%s finding%s\n' "$FINDINGS" "$([ "$FINDINGS" = 1 ] || echo s)"
[ "$FINDINGS" -eq 0 ] && exit 0 || exit 1
