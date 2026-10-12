# Example Glossary: Identity

> This is a complete example of `docs/glossary/identity.md`, following
> `references/glossary-template.md`. A small context: two terms is a normal size.

---

# Identity

Authenticates users and issues the proof that they signed in.

## Language

**User**
A person who can sign in with an email and a password.
_Avoid_: account, member
_In code_: `User`

**Access Token**
Proof that a User signed in, presented with each request they make afterwards.
_Avoid_: session token, auth token, login token
_In code_: `AccessToken`
