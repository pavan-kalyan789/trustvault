# TrustVault threat model and accepted risks

## Security invariants

- Default deny: a user can reach content only as its owner or through an explicit per-document grant.
- The server checks permissions on every document endpoint. Hiding a button is not an authorization control.
- Revocation is checked against the database on the next request; no long-lived download URL or cached grant is used.
- Successful and denied access attempts are recorded in a keyed, chained audit log.

## Threat register

| Threat / attack | Mitigation in this build | Residual risk / disposition |
|---|---|---|
| IDOR: change document ID in detail URL | `get_document` followed by `can_read`; otherwise 403 | Covered by cross-user tests |
| IDOR: call download endpoint directly | Same request-time `can_read` check before `FileResponse` | A response already streaming cannot be recalled after revocation |
| IDOR: PATCH/DELETE with another user's ID | `can_edit` required; owner or explicit edit grant only | Edit grantee may soft-delete; owner can restore only by DB operation in this version |
| Unauthorized grant creation/revocation | Grant management requires exact document owner | Admin does not bypass ownership |
| Permission escalation: read grant used to edit/delete | `can_edit` requires `edit`; read is not sufficient | Tested for read-only update denial |
| Admin role treated as universal content access | Admin is not included in `can_read`/`can_edit` | Admin can inspect metadata/audit, not bytes without explicit grant |
| Stale access after revocation | Grant is queried on every request; no presigned URL | Active in-flight transfer remains possible; no chunk-by-chunk revalidation |
| Direct static-file path guessing | Random UUID storage keys; storage folder not mounted by StaticFiles; only API download route exposes bytes | Host/container filesystem administrators can access files by design |
| Filename/path traversal | Original filename reduced to `Path(...).name`; never used as storage path | Filename handling should be hardened for unusual Unicode/control chars |
| Upload executable or spoofed extension | Extension allowlist; size cap; PDF/PNG/JPEG magic bytes; UTF-8 validation for TXT | No antivirus/CDR, archive bomb handling or full parser validation; accepted for limited formats |
| Oversized upload / memory exhaustion | Read limit is `MAX_UPLOAD_BYTES + 1`, default 10 MiB | Upload is buffered in memory; add streaming quotas/rate limits for production |
| Audit row modification | HMAC-SHA256 covers canonical event fields and previous hash; secret separate from DB | Anyone with both DB write access and HMAC secret can forge events |
| Audit event deletion or tail truncation | Chain links detect interior deletion/reordering; admin can verify | Tail truncation cannot be detected without an independently stored checkpoint. Accepted demo limitation; production must anchor hashes in WORM/independent system |
| Audit event insertion/reordering | HMAC and previous-hash continuity detect unauthorized modifications | Concurrent writers need serialized append/locking; SQLite demo is not designed for high write concurrency |
| Audit secret exposure | Secret comes from environment, not database | Host compromise or leaked `.env` defeats authenticity; rotate and restrict secret access |
| JWT theft/replay | Short-lived signed JWT; active-account check each request | No refresh-token revocation list, MFA, device binding or token denylist yet; use HTTPS and shorter expiry in production |
| Disabled account using old JWT | Principal is reloaded and `active` checked on every request | Role changes take effect from DB; token role claim is not trusted for authorization |
| Password brute force / credential stuffing | Argon2 password hashing | No login throttling, CAPTCHA or breached-password checks; accepted only for local demo |
| User enumeration | Login response is generic; user list requires owner/admin | Owner/admin can enumerate active users to grant access; necessary for named sharing, should be tenant-scoped |
| Cross-site scripting through filename/category | UI escapes values before insertion into HTML | Review every future UI rendering path; add CSP and avoid inline handlers in production |
| CSRF | API uses bearer token in Authorization header, not cookie | XSS can steal browser localStorage token; move to secure HttpOnly cookies with CSRF defenses if cookie auth is adopted |
| CORS abuse | No permissive CORS middleware configured | Same-origin deployment assumed; add strict allowlist if frontend hosted separately |
| Database disclosure | Password hashes only; file bytes outside DB | File encryption at rest and DB encryption/backup controls are deployment responsibilities |
| Orphan file after DB failure | Random private storage key avoids exposure | Failed DB commit can leave orphan file; production needs reconciliation job |
| Soft-deleted document access | `get_document` returns 404 for deleted rows | File bytes retained on disk for recovery; no restore/purge workflow yet |
| Search leaking documents | Non-admin list query is constrained to owner or grant subquery | Admin metadata listing is intentionally broad; no multi-tenant boundary in current schema |
| Account role self-escalation | No public role-change endpoint | Admin provisioning is currently via seed/manual DB; production needs audited admin user-management endpoint |
| Dependency/supply-chain compromise | Dependencies declared, versions constrained by minimums | Pin hashes, scan SBOM/dependencies, and use lockfile in deployment |

## Test mapping

- `test_ungranted_user_cannot_read_download_edit_delete_or_change_grants`: IDOR across read, download, update, delete and grant routes; verifies refused attempts are logged.
- `test_grant_and_revoke_take_effect_on_next_request`: explicit grant works and revocation immediately blocks subsequent detail/download requests; read grant cannot edit.
- `test_viewer_cannot_upload`: role boundary.
- `test_invalid_file_type_and_spoofed_pdf_rejected`: upload validation.
- `test_audit_chain_verifies_and_detects_modified_event`: keyed audit tamper detection.
- `test_admin_does_not_automatically_get_file_contents`: no implicit admin content bypass.

## Deliberate scope choices

This version uses per-document grants only; no folder inheritance, group grants, public links or AI permission suggestions. Those features multiply the authorization state space and are intentionally excluded until the basic server-side model is independently reviewed. If AI suggestions are added, they must be advisory only, require human confirmation, and audit both suggestion and decision.
