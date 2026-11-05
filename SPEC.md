# App Studio decisions

The durable agreement between learner and AI. Update only agreed decisions and
actual evidence; pending is a valid state. Keep explanations/help in
[LEARNING.md](LEARNING.md), not a second copy here.

## Current stage

- **Current feature:** APP-003 kept; all three lessons complete.
- **Status:** Fix-It Desk homepage, member accounts and server-enforced member/admin roles implemented and checked; learner contributions recorded in LEARNING.md.
- **Next step:** Deployment to the existing server is a later, separately agreed scope.
- **Implementation marker:** `studio.json` is `implemented_through: 3`.

This repository owns application code. Server/proxy changes and production
deployment are outside these three local-development lessons. Prepared helpers
are reusable foundations, not evidence that unfinished routes are implemented.

## APP-001 · Branded homepage

**Scope:** make the neutral FastAPI homepage express one chosen identity with
a simple original SVG mark, coherent copy, navigation and shared style tokens.
Keep account actions honest about their unfinished state.

| Decision | Agreement |
|---|---|
| Visitor and concrete use situation | An employee at a small business whose laptop, printer or Wi-Fi just stopped working and who needs help fast |
| Reused IS117 brand, or name / promise / primary archetype | New brand (not IS117). **Fix-It Desk** / "Tell us what broke. We handle the rest." / **The Caregiver**. Voice: calm, plain-spoken, reassuring. Learner's reason: "Fix-It Desk is an easy and fast way to troubleshoot technical issues for small businesses. I've always enjoyed tech troubleshooting and its relevant to my major." (Name and archetype picked from coach-offered options.) |
| One visible choice and visitor benefit | Learner: "The simple visible choice makes it much easier for the visitor to navigate the site. Its straightforward and simple no need for unnecessary scrolling." Implemented as one main "Report a problem" button on a short page (concrete form suggested by coach). |
| Own issue / branch / PR | [Issue #1](https://github.com/mohammedhammoudeh8/my-app-studio/issues/1) · branch `app-001` · PR: see Evidence |

**Keep when:** the agreed identity is visible and usable at desktop/narrow widths;
full foundation + APP-001 checks pass; AI review and the learner's actual check
interpretation/browser observation/keep reason are recorded; reviewed evidence
and verified GitHub state are linked below.

## APP-002 · Signup, login and logout

**Scope:** add browser forms and REST behavior for member signup, login, a private
dashboard and logout backed by SQLite. Reuse the prepared password/JWT/CSRF/session
helpers; keep data local. New accounts cannot choose their role.

| Decision | Agreement |
|---|---|
| Expected public/private behavior and account flow | Homepage public. Signup (username + 15–128 character password) creates a **member** and sends you to Log in. Login opens `/dashboard` ("Your member space") and sets an HttpOnly, SameSite=Lax session cookie holding a signed, expiring JWT. Anonymous `/dashboard` redirects to `/login`; anonymous `GET /api/me` returns 401; after login it returns 200 with only `id`, `username`, `role`. Logout (POST + CSRF) revokes the session on the server. HTML forms and JSON API (`/api/csrf`, `/api/signup`, `/api/login`, `/api/me`, `/api/logout`) call the same prepared helpers in `app/security.py`. |
| Valid and rejected cases to demonstrate | Valid: signup → login → dashboard → `/api/me` 200 → logout. Rejected: duplicate username (409), short/long password, bad username or a `role` field at signup (422), wrong password and unknown user (same generic 401), too many attempts (429), missing/wrong CSRF or foreign Origin (403), `GET /api/logout` (405), a copied cookie after logout (401). |
| Own issue / branch / PR | [Issue #3](https://github.com/mohammedhammoudeh8/my-app-studio/issues/3) · branch `app-002` · PR: see Evidence |

**Keep when:** the agreed forms/API work; duplicate/invalid signup and wrong
credentials are rejected; passwords are hashed; authentication uses validated,
expiring JWTs with protected cookies and CSRF; private requests require a live
session and logout revokes it. Full cumulative checks, AI review, actual learner
contributions and GitHub state are recorded. This is not a production-security certification.

## APP-003 · Server-enforced roles

**Scope:** enforce a small member/admin boundary in the API and browser. Assign
roles only through the trusted local terminal command; use current server-side
permissions, including for an existing session after a role change.

| Visitor | Homepage | Member area | Admin area/API |
|---|---|---|---|
| Anonymous | Allowed | Login required | Login required |
| Member | Allowed | Allowed | Forbidden |
| Admin | Allowed | Allowed | Allowed |

| Decision | Agreement |
|---|---|
| Intended admin-only result | `/admin` page (heading "Administration") lists usernames and roles, read-only, no hashes. `GET /api/admin` returns the admin's username plus account and admin counts. Both read the user's **current role from the database** on every request via the prepared `require_admin`/`authenticate` helpers; a role claim inside the JWT is never trusted. The Admin menu link shows only for admins, which is presentation only. Roles change only with the trusted local command `studio.py user role USERNAME --role admin|member`; signup stays member-only. |
| Actual allowed/denied request evidence | Anonymous: `GET /api/admin` 401, `/admin` redirects to `/login`. Member: `GET /api/admin` 403, `/admin` 403 "Admin access required". Admin (after the trusted command, same session): both 200. Demoted back to member: both 403 again without logging out. A re-signed token claiming `role: admin` still gets 403. |
| Own issue / branch / PR | [Issue #5](https://github.com/mohammedhammoudeh8/my-app-studio/issues/5) · branch `app-003` · PR: see Evidence |

**Keep when:** a direct request cannot bypass the role boundary, role changes
take effect as specified, new signup remains member-only, and full cumulative
checks plus AI review pass. Link the learner's actual interpretation/observation,
reviewed record and verified GitHub result. Hidden navigation alone is insufficient.

## Evidence

Link actual files/checks and the student's own issues/PRs. No fabricated URLs,
customer research or claims that a timestamp proves learning.

| Feature | Files / own issue / PR | Actual checks and learner observations | Kept / GitHub state |
|---|---|---|---|
| APP-001 | `app/brand.json`, `app/static/logo.svg`, `app/templates/home.html`, `app/templates/base.html`, `studio.json` · [issue #1](https://github.com/mohammedhammoudeh8/my-app-studio/issues/1) | `check --lesson APP-001` and full `check` passed locally on Windows incl. Chromium (after enabling Developer Mode for a symlink test). First AI draft failed `test_chosen_brand_reaches_the_homepage` (apostrophe escaped as `&#39;`); fixed by rewording. Learner interpretation/observation in [LEARNING.md](LEARNING.md#app-001) | Kept; PR and CI linked in the PR |
| APP-002 | `app/features/accounts.py`, `app/templates/signup.html`, `login.html`, `dashboard.html`, `home.html`, `studio.json` · [issue #3](https://github.com/mohammedhammoudeh8/my-app-studio/issues/3) | `check --lesson APP-002` and full `check` passed locally on Windows (96 foundation, 14 APP-002 contracts, real Chromium journey). Learner interpretation of `test_logout_revokes_a_copied_token` and browser observation in [LEARNING.md](LEARNING.md#app-002) | Kept; PR and CI linked in the PR |
| APP-003 | `app/features/roles.py`, `app/templates/admin.html`, `app/templates/admin_denied.html`, `app/static/site.css` (table styles), `studio.json` · [issue #5](https://github.com/mohammedhammoudeh8/my-app-studio/issues/5) | `check --lesson APP-003` and full `check` passed locally on Windows (foundation, all 18 APP-001–003 contracts, real Chromium journey including role promotion/demotion via the trusted command). Learner interpretation of `test_a_role_claim_cannot_override_the_current_database_role` and browser observation in [LEARNING.md](LEARNING.md#app-003) | Kept; PR and CI linked in the PR |

The instructor's reference branches show possible implementations. They do not
establish this repository's completion or the learner's own reasoning.
