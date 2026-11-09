# Five-minute TrustVault demo recording script

Record this against the deployed URL after replacing demo passwords and adding safe demo accounts. Keep the browser and terminal/API docs visible where useful.

1. **0:00–0:40 — Sign in and roles.** Sign in as the owner. Show the document dashboard. Briefly explain owner, viewer and admin boundaries from `README.md`.
2. **0:40–1:20 — Upload and search.** Upload a small `sample.txt` in the HR category. Search by filename and category. Point out that the file is stored under a random key in private storage, not served from `/static`.
3. **1:20–2:10 — Grant least privilege.** Share the file with the viewer account using `read`. Sign in as that viewer in a separate browser profile and download the file. Show the audit event.
4. **2:10–3:10 — Attack attempt.** Sign in as the second viewer with no grant. Use `/docs` or curl to call `GET /api/documents/{id}` and `/download` directly. Show 403 responses and the refused events in the admin audit view. Do not rely on hidden UI buttons.
5. **3:10–4:00 — Revoke immediately.** As owner, revoke the first viewer. Repeat the direct detail/download calls with the same viewer token. Show that the next request is denied. Explain that an already-streaming response cannot be recalled.
6. **4:00–4:40 — Audit integrity.** Sign in as admin, open activity and run “Verify audit integrity”. Explain the HMAC key is separate from the database and disclose the tail-truncation limitation plus planned external WORM checkpoint.
7. **4:40–5:00 — Close honestly.** Show tests (`pytest -q`), `THREATS.md`, `PROMPTS.md`, and list unfinished work: cloud deployment, immutable external audit anchoring, MFA/rate limiting, malware scanning, and restore/retention.

Do not claim a public deployment, immutable log storage, or protection against a compromised application host unless those controls have actually been implemented and independently tested.
