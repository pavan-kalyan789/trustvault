# TrustVault

Private-by-default document sharing with server-enforced, per-document authorization and a tamper-evident HMAC audit chain. This is a seven-day challenge starter implementation intended for local evaluation and security review; it is **not a claim of production certification**.

## Stack

- FastAPI + SQLAlchemy 2 + SQLite (local/demo database)
- JWT bearer authentication; Argon2 password hashing through `pwdlib`
- Private file storage outside the static web root; random storage keys
- Per-document `read` / `edit` grants; owner-only sharing administration
- HMAC-SHA256 chained audit events; administrator integrity verification
- HTML/CSS/vanilla JS frontend; pytest security tests

## Run on Windows PowerShell

Use **Python 3.12 or 3.13** for the smoothest setup. This project pins SQLAlchemy 2.0.41+ (which supports modern Python typing) and includes `from __future__ import annotations` in the model module to avoid the Python 3.14 annotation issue encountered in the earlier setup.

```powershell
cd C:\Users\VAMSI\Downloads\trustvault-project\trustvault
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated random value into `JWT_SECRET`, generate a **different** value for `AUDIT_SECRET`, and save `.env`. Then:

```powershell
python seed.py
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000. Interactive API docs: http://127.0.0.1:8000/docs.

If PowerShell says script execution is disabled, activate with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again. To check the port: `netstat -ano | findstr ":8000"`. No output means nothing is listening on that port.

### Demo credentials

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@trustvault.local` | `Admin@12345` |
| Document owner | `owner@trustvault.local` | `Owner@12345` |
| Viewer | `viewer@trustvault.local` | `Viewer@12345` |
| Second viewer (attack-test account) | `other@trustvault.local` | `Other@12345` |

**Change or remove these demo credentials before any public deployment.** `seed.py` creates missing accounts but does not reset existing passwords.

## Run with Docker

Install Docker Desktop, copy `.env.example` to `.env`, replace both secrets with different random values, then run `docker compose up --build`. Open http://localhost:8000. The named volume `trustvault_data` persists the SQLite database and private file bytes. This is suitable for a single-instance demo, not a high-availability production deployment.

## Run tests

```powershell
pytest -q
```

Tests exercise direct API requests, not only UI visibility: an ungranted account cannot read, download, update, delete or grant access to another user's document; grants and revocations take effect on the next request; viewer upload is denied; file spoofing is rejected; audit tampering is detected; and administrator role alone does not imply file-content access.

## Permission model

1. `admin`: administers audit visibility and document metadata overview. Admin does **not** implicitly receive document content. An explicit grant is still required to read/download a file they do not own.
2. `owner`: owns uploaded documents, has read/edit rights to those documents, and is the only role allowed to grant/revoke named-user access.
3. `viewer`: can read/download documents only when an explicit `read` or `edit` grant exists. Cannot upload or manage grants.
4. A named `edit` grant permits read/download, metadata edit, content replacement and soft deletion. A `read` grant permits only read/download.
5. No folder inheritance, public links, group grants, or implicit administrator content bypass exists.

The authorization checks are in `app/main.py` (`can_read`, `can_edit`) and are invoked by every document-content or mutation endpoint. The database is queried on every request. No signed permanent file URLs are issued. Revoking a grant therefore denies the next request immediately. A download already in progress when revocation commits cannot be recalled; see `THREATS.md`.

## Storage and audit design

Files are saved as random UUID keys under `STORAGE_DIR`; the original filename is metadata only. The storage directory is not mounted as static content. The only download route checks the authenticated principal against the current database grant before returning bytes. SHA-256 is recorded at upload for integrity identification.

Audit events include successful and refused read/download/update/delete/grant/revoke actions, uploads, login attempts, actor, target, IP, time and details. Each event HMAC covers its canonical fields and previous event hash. The HMAC secret is configured outside the database. Editing an event or breaking the chain fails verification. This is **tamper-evident, not truly immutable**: a database operator could truncate a tail without an externally stored checkpoint. Production deployment must periodically anchor the latest event hash to independently controlled immutable/WORM storage and restrict DB write access.

## Configuration

`.env` variables: `DATABASE_URL`, `STORAGE_DIR`, `JWT_SECRET`, `AUDIT_SECRET`, `ACCESS_TOKEN_MINUTES`, `MAX_UPLOAD_BYTES`. Do not commit `.env`. SQLite is for the challenge/demo; use PostgreSQL with migrations, transaction/locking strategy, backups and tested restore for production. Keep storage private and encrypted at rest, serve only over HTTPS, rotate secrets, and add rate limiting and monitoring before internet exposure.

## API and operations

See [API.md](API.md), [THREATS.md](THREATS.md), and [PROMPTS.md](PROMPTS.md). Database tables are created on app import for this compact demo; `seed.py` creates demo accounts. For production, replace `create_all` with Alembic migrations and use a separate migration identity.

## Current limitations / unfinished challenge deliverables

- No hosted deployment or live public URL is included; deploy to a managed host with persistent private storage, HTTPS, secrets, and PostgreSQL before submission.
- No demo video is included. Record a five-minute walkthrough after deployment.
- No version history, external guest accounts, malware scanning, retention policy, recovery workflow, SSO/MFA, password reset, or rate limiting.
- Audit chain needs external hash anchoring to detect tail truncation. SQLite is not a multi-writer production database.
- The challenge requires evidence of development across seven days. Do not fabricate commit history: continue committing real work daily and keep PROMPTS.md updated with actual tool outputs, mistakes and corrective commit links.
