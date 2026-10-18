# Rebuild provenance and checkpoints

2026-10-18: the selected environment was available but `/workspace/doodle-task-intake` and its archive were absent. The prior archive SHA256 reported in history was 04fa38bcc0689c25a6bdb5938c1e25d8c1fe1e70f88e8779fec270e6f9b3d268. That archive has NOT been recovered.

User approved rebuilding the Doodle API project and eventual private repository push to Vimlesh-22/doodle-agents. This work only rebuilds/tests/packages; parent handles repository access. No push or Railway deployment is part of this execution.

Requirements recovered from conversation: relay into existing Doodle (no replacement agent/inference); authenticated POST intake and GET status/results; owner-scoped MCP get/claim/update tools; durable subscriptions/outbox, idempotency, leases, explicit asynchronous states; signed verified MCP events, public-address-only callbacks; owner-controlled credential provisioning and production OAuth; no public task data; no authorization from external task content.

Surviving exact configuration text in conversation included the Node image digest, the earlier Docker/Compose files, setup script, placeholder OAuth JSON, Nginx example, and SELF_HOST.md. Those are historical reference, not proof of recovered source. The rebuild intentionally revises the config schema, dependency installation, file layout and documentation. Existing secret configurations must not be assumed compatible. No earlier runtime data was recovered.

Checkpoint 1: SQLite, authentication, callback security modules written.
Checkpoint 2: intake, leases, MCP methods, subscription verification and durable outbox written; 14 tests passed.
Checkpoint 3: OAuth and additional expiry/restart tests added; 19 tests passed. Docker and real platform integration have separate validation status in TEST_RESULTS.txt.

Known scope limits: small single-owner/single-process queue; all state in one SQLite JSON row; no retention/admin UI, no expired approval-pause resume operation; no historical event replay; exact callback host approval required; no real IdP/plugin/Doodle test. Production rollout requires operator review and hosted HTTPS validation.

Historical guide text was transcribed from the surviving conversation into SELF_HOST.original.md (reference only; follow the current root SELF_HOST.md for this rebuild).

Checkpoint 4: 22 automated tests passed, syntax checks passed, dependency integrity verified, offline Docker build and container replacement persistence smoke passed. Test container/volume cleanup completed. No production credentials created. Final source-only archive and manifest are in artifacts/.
