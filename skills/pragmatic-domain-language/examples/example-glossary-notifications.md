# Example Glossary: Notifications

> This is a complete example of `docs/glossary/notifications.md`, following
> `references/glossary-template.md`.
> **Showcases:** a provider's word (*unsubscribe*) kept out of the domain language, and
> a word shared with infrastructure (*message*) resolved so each use means one thing.

---

# Notifications

Tells recipients about events they care about, over the channels they accept.

## Language

**Notification**
The record of one attempt to tell a Recipient about an event over one Channel; its outcome is sent, skipped, or failed.
_Avoid_: alert, reminder

**Recipient**
The person a Notification is addressed to; for order events, the Order's Customer.
_Avoid_: user, target

**Channel**
A way of reaching a Recipient, such as email or push.
_Avoid_: medium
_In code_: `Channel`

**Opt-out**
A Recipient's choice to stop receiving Notifications on a Channel.
_Avoid_: unsubscribe, mute

## Resolved Ambiguities

- "Message" was used for both a **Notification** (what the Recipient gets) and the queue item that triggers it. Only the first is a domain concept; the queue item is an event. Decided in `docs/arch/notification-service.arch.md`.
