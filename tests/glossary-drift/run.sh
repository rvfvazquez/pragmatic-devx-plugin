#!/usr/bin/env bash
# Tests skills/pragmatic-domain-language/scripts/glossary-drift.sh against a throwaway fixture repo.
# Usage: ./run.sh      Exit 0 when every assertion holds, 1 otherwise.
set -u

SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/skills/pragmatic-domain-language/scripts/glossary-drift.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
FAIL=0
ok()   { printf 'ok    %s\n' "$1"; }
bad()  { printf 'FAIL  %s\n' "$1"; FAIL=1; }
has()  { printf '%s\n' "$OUT" | grep -qE -- "$2" && ok "$1" || { bad "$1 (expected /$2/)"; printf '%s\n' "$OUT" | sed 's/^/      | /'; }; }
hasnt(){ printf '%s\n' "$OUT" | grep -qE -- "$2" && { bad "$1 (unexpected /$2/)"; printf '%s\n' "$OUT" | sed 's/^/      | /'; } || ok "$1"; }

cd "$T" && git init -q && git config user.email t@t && git config user.name t
mkdir -p docs/glossary src/ordering src/payments src/notifications
cat > src/ordering/order.go <<'GO'
package ordering
type Order struct{ ID string }
type OrderItem struct{ SKU string }
type OrderLine struct{ SKU string }
type Customer struct{ ID string }
GO
cat > src/payments/service.go <<'GO'
package payments
type Transaction struct{}
type PaymentCharge struct{}
func Pay(customer Customer, customerID string) {}
type Customer struct{}
var accountBalance int
func accountant() {}
GO
echo x > src/notifications/n.go
git add -A && git commit -qm init && SHA="$(git rev-parse --short HEAD)"
echo "// touch" >> src/payments/service.go && git add -A && git commit -qm second
cat > docs/glossary/context-map.md <<MAP
# Context Map

## Contexts

| Context | Glossary | Arch spec | Purpose | Owns | Code | Synced |
|---|---|---|---|---|---|---|
| Ordering | [ordering](./ordering.md) | — | Orders | Order | src/ordering | \`$SHA\` |
| Payments | [payments](./payments.md) | [payments.arch](../arch/payments.arch.md) | Money | Transaction | \`src/payments\`, src/missing | \`$SHA\` |
| Notifications | [notifications](./notifications.md) | — | Tell people | Notification | — | — |
| Identity | [identity](./identity.md) | — | Sign in | User | src/notifications | — |

## Relationships

| From → To | Mechanism | What crosses |
|---|---|---|
| Ordering → Payments | Event | x |
MAP
printf '# Ordering\n\n## Language\n\n**Order**\nA request.\n_Avoid_: purchase\n_In code_: `Order`\n\n**Order Item**\nA product in an Order.\n_Avoid_: line, order line\n_In code_: `OrderItem`\n\n**Customer**\nWho orders.\n_Avoid_: account\n_In code_: `Customer`\n' > docs/glossary/ordering.md
printf '# Payments\n\n## Language\n\n**Transaction**\nOne attempt.\n_Avoid_: operation\n_In code_: `Transaction`\n\n**Charge**\nTaking money.\n_In code_: `Charge`\n\n**Payer**\nWho pays.\n_Avoid_: customer, account, buyer\n_In code_: `Payer`\n' > docs/glossary/payments.md
printf '# Notifications\n\n## Language\n\n**Notification**\nA record.\n_In code_: `Notification`\n' > docs/glossary/notifications.md
printf '# Identity\n\n## Language\n\n**User**\nA person.\n_Avoid_: member\n_In code_: `User`\n' > docs/glossary/identity.md

echo "== full run"
OUT="$(bash "$SCRIPT" 2>&1)"; RC=$?
[ $RC -eq 1 ] && ok "exit 1 when there are findings" || bad "exit code $RC, expected 1"
has   "avoided word as identifier (line)"        'AVOIDED +Order Item +"line" — src/ordering/order.go:4'
has   "multi-word avoided word"                  'AVOIDED +Order Item +"order line"'
has   "stale identifier"                         'STALE +Charge +`Charge` not found'
has   "second stale identifier"                  'STALE +Payer +`Payer` not found'
has   "avoided word in camelCase prefix"         'AVOIDED +Payer +"account" — src/payments/service.go:6 \(1 use\)'
hasnt "accountant is not 'account'"              'service.go:7'
has   "customer avoided for Payer (3 uses)"      'AVOIDED +Payer +"customer"'
hasnt "a term's own identifier is not avoided"   'AVOIDED +Customer'
has   "missing code path"                        'NOPATH +src/missing'
has   "context without a Code value is skipped"  'Notifications +\(no Code column value'
has   "stale in a context with a real path"      'STALE +User +`User` not found'
has   "per-context sync age (Payments: 1 commit)"  'synced [0-9a-f]+ · 1 commit touches these paths since'
has   "per-context sync age (Ordering: 0 commits)"  'synced [0-9a-f]+ · 0 commits touch these paths since'
has   "a context with an empty Synced cell"       'never synced'

echo "== --context filter"
OUT="$(bash "$SCRIPT" --context payments 2>&1)"
has   "only the named context is reported"       '^Payments '
hasnt "other contexts are not reported"          '^Ordering '

echo "== a term's own _In code_ wins over _Avoid_"
printf '\n**Payer legacy**\nSame idea, legacy identifier.\n_Avoid_: customer\n_In code_: `Customer`\n' >> docs/glossary/payments.md
OUT="$(bash "$SCRIPT" --context payments 2>&1)"
hasnt "customer no longer reported once another term's _In code_ is Customer"  'AVOIDED +Payer +"customer"'

echo "== missing glossary file, unknown synced commit"
mv docs/glossary/identity.md "$T/identity.bak"
OUT="$(bash "$SCRIPT" --context identity 2>&1)"
has   "missing glossary file"                    'MISSING +glossary file \./identity\.md'
mv "$T/identity.bak" docs/glossary/identity.md
sed -i 's#| src/notifications | — |#| src/notifications | `deadbee` |#' docs/glossary/context-map.md
OUT="$(bash "$SCRIPT" --context identity 2>&1)"
has   "unknown commit in the Synced cell"        'synced deadbee \(not found in this repository\)'

echo "== clean context exits 0"
printf 'package x\ntype Order struct{}\ntype OrderItem struct{}\ntype Customer struct{}\n' > src/ordering/order.go
OUT="$(bash "$SCRIPT" --context ordering 2>&1)"; RC=$?
[ $RC -eq 0 ] && ok "exit 0 without findings" || bad "exit code $RC, expected 0"
has   "OK line"                                  'OK +3 terms checked'

echo "== no context map"
OUT="$(bash "$SCRIPT" --root "$T/src" 2>&1)"; RC=$?
[ $RC -eq 2 ] && ok "exit 2 without a context map" || bad "exit code $RC, expected 2"

[ $FAIL -eq 0 ] && echo "All glossary-drift tests passed." || echo "Some glossary-drift tests failed."
exit $FAIL
