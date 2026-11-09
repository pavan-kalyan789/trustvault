# AI-assisted development log

This log records the initial implementation session on **2026-11-09**. The commits below are real local commits. They were created in one session and therefore do **not** satisfy the challenge's requirement for a week of visible development history. Continue this log and commit actual work on subsequent days; do not represent this initial session as seven days of work. After pushing the repository, replace `YOUR_GITHUB_USERNAME` in the commit links with the actual GitHub owner.

## 2026-11-09 — Backend structure and role boundaries

**Prompt / fair summary:** “Build a FastAPI document-sharing backend with administrator, owner and viewer roles; per-document grants; private storage; and server-side authorization on every document endpoint. Keep admin audit visibility separate from document-content access.”

**Produced:** SQLAlchemy user/document/grant models, JWT authentication, Argon2 password hashing, request-time `can_read` and `can_edit` checks, and document API routes.

**What was wrong / review performed:** A UI-only approach or a blanket admin bypass would fail the challenge's direct-route attack. I reviewed each detail/download/update/content-replacement/delete/grant route and ensured it checks the relevant permission in the API handler. I also added a test that an administrator without a grant cannot download another user's file. The authorization logic is in `app/main.py`, not the browser.

**Correction / evidence:** The backend foundation is in [commit 5891d2e](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/5891d2e571a55ffc7266f2ef354f8d791d9b3bb0) and protected API routes are in [commit 73ad0ef](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/73ad0eff3200fc713ed07578b149003d4d03a810).

## 2026-11-09 — Audit-chain implementation

**Prompt / fair summary:** “Implement an audit trail that records success and denied document access and detects database edits using an HMAC chain whose key is outside the database.”

**Produced:** Canonical JSON event payloads, HMAC-SHA256 event hashes, previous-event links, and an administrator verification endpoint.

**What was wrong / review performed:** The first implementation attempt passed `created_at` twice while constructing the ORM object. The test run caught the `TypeError`; I separated the signed timestamp payload from the ORM field assignment. I also checked SQLite's timezone behavior: values may be returned without timezone metadata, so verification normalizes naive stored timestamps to UTC before recomputing the signature. A tamper test edits a stored event and expects verification to fail.

**Correction / evidence:** [Audit-chain commit 1ff125d](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/1ff125d925c220f3744fce58e4435f4e1d756481) contains the corrected HMAC implementation; [security test commit 73ad0ef](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/73ad0eff3200fc713ed07578b149003d4d03a810) contains the tamper-detection test.

## 2026-11-09 — Adversarial authorization tests

**Prompt / fair summary:** “Write API-level tests proving a stranger cannot read, download, update, replace, delete or share another user's document; prove revocation takes effect on the next request.”

**Produced:** Pytest tests using separate owner, viewer, stranger and admin accounts, plus direct HTTP requests against protected endpoints.

**What was wrong / review performed:** The first test draft used reserved `.test` email domains, which Pydantic's email validator correctly rejected, and omitted a local login helper. I changed the test addresses to `example.com`, added the helper, and reran the tests. I also verified denied attempts are persisted as audit events rather than merely returning 403.

**Correction / evidence:** [Security test commit 73ad0ef](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/73ad0eff3200fc713ed07578b149003d4d03a810) contains the corrected tests. The current run reports **6 passed**.

## 2026-11-09 — Password-hashing dependency review

**Prompt / fair summary:** “Use a modern password hashing implementation compatible with the selected FastAPI stack and Python runtime.”

**Produced:** The initial dependency list used `pwdlib[argon2]`.

**What was wrong / review performed:** Installing requirements in this isolated build environment failed because package-index network access was unavailable and `pwdlib` was not already installed. Rather than leaving an un-runnable dependency, I checked the installed Argon2 implementation and switched the code to `argon2-cffi`'s `PasswordHasher`, retaining Argon2id password hashes and mismatch handling. This is an environment-specific correction, not evidence that `pwdlib` is insecure.

**Correction / evidence:** [Backend foundation commit 5891d2e](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/5891d2e571a55ffc7266f2ef354f8d791d9b3bb0) and [API/test commit 73ad0ef](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/73ad0eff3200fc713ed07578b149003d4d03a810) contain the final dependency and implementation. Confirmed the tests run with the installed Argon2 package.

## 2026-11-09 — File upload and content-edit authorization

**Prompt / fair summary:** “Add safe upload validation and ensure an edit grant is needed before replacing stored file bytes; viewers must not upload.”

**Produced:** Extension allowlist, 10 MiB cap, PDF/PNG/JPEG signature checks, UTF-8 TXT validation, private random storage keys, and a content-replacement endpoint.

**What was wrong / review performed:** The first route sketch allowed any authenticated account to upload. That was broader than the declared role model. I added an explicit viewer-role rejection, added a direct upload-denial test, and tested that a read grant cannot replace content while an edit grant can. I also checked that the storage directory is not mounted as static content.

**Correction / evidence:** [API/test commit 73ad0ef](https://github.com/YOUR_GITHUB_USERNAME/trustvault/commit/73ad0eff3200fc713ed07578b149003d4d03a810) contains the server-side role check, replacement endpoint and test coverage. Storage remains outside the static directory.

---

## Reusable project instructions

- Treat all document IDs and filenames as attacker-controlled input.
- Never rely on frontend visibility for authorization; enforce authorization in the API handler for every read, download, mutation and sharing operation.
- Deny by default. Admin audit access does not imply file-content access.
- Check grants from the database on each request; do not issue permanent public or signed file URLs.
- Log both successful and denied access attempts. Keep the audit HMAC secret outside the database.
- For every security change, add a test that makes a direct HTTP request as a different principal.
- Do not claim a security property that is not tested or explicitly documented as a residual risk.
