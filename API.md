# API authorization reference

All protected endpoints require `Authorization: Bearer <JWT>`. The server resolves the user from the token and checks the active account on each request. Document IDs are not secrets; knowing an ID grants no authority.

| Method | Endpoint | Allowed caller | Server-side rule |
|---|---|---|---|
| POST | `/api/auth/login` | Anonymous | Valid active account credentials |
| GET | `/api/auth/me` | Any authenticated user | Current active principal |
| GET | `/api/users` | Owner or admin | Viewer is denied; returns active user directory for sharing |
| POST | `/api/documents` | Owner or admin | Viewer denied; validates extension, size, and content signature |
| GET | `/api/documents` | Any authenticated user | Returns own docs and explicitly granted docs; admin gets metadata overview |
| GET | `/api/documents/{id}` | Owner or read/edit grantee | `can_read` checked; successful read audited |
| GET | `/api/documents/{id}/download` | Owner or read/edit grantee | `can_read` checked immediately before file response; download audited |
| PATCH | `/api/documents/{id}` | Owner or edit grantee | `can_edit` checked; metadata update audited |
| PUT | `/api/documents/{id}/content` | Owner or edit grantee | `can_edit` checked; replacement file validated and audited |
| DELETE | `/api/documents/{id}` | Owner or edit grantee | `can_edit` checked; soft delete audited |
| POST | `/api/documents/{id}/grants` | Document owner only | Named active user; permission must be `read` or `edit` |
| DELETE | `/api/documents/{id}/grants/{user_id}` | Document owner only | Removes grant; next request is denied |
| GET | `/api/documents/{id}/grants` | Document owner only | Lists that document's grants |
| GET | `/api/admin/audit` | Admin only | Audit event listing; includes denied attempts |
| GET | `/api/admin/audit/verify` | Admin only | Verifies HMAC chain |
| GET | `/api/admin/documents` | Admin only | Metadata overview only; no file bytes |

Denied attempts against an existing document are written to the audit log before the API returns 403. A nonexistent/deleted ID returns 404. Authentication failures are recorded as login-denied events. OpenAPI docs are at `/docs`.
