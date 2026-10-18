# Doodle Agent's

Private single-owner task intake relay for an **existing Doodle**, rebuilt on 2026-10-18 after the earlier workspace files disappeared. Repository target: `Vimlesh-22/doodle-agents`. This is a rebuild, not recovered original code. It does not run an AI model, call an inference API, or execute submitted code/shell commands.

## Status

Local tests pass; no hosting, real identity-provider integration, plugin registration, Doodle receipt, or GitHub push has been completed by this rebuild. Do not confuse queued tasks or webhook acknowledgments with completed Doodle work. See `TEST_RESULTS.txt`, `SELF_HOST.md`, and `docs/REBUILD.md`.

## API

Use HTTPS behind your reverse proxy. Every task endpoint requires an intake bearer credential. The separate `/mcp` endpoint requires OAuth in production; its static bearer mode exists for manual local testing only.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/healthz` | Anonymous process readiness only |
| POST | `/v1/tasks` | Create a task; requires `Idempotency-Key` and JSON `{title,instructions}` |
| GET | `/v1/tasks/TASK_ID` | Read owner task status, result and delivery state |
| POST | `/mcp` | Authenticated MCP JSON-RPC tools and events |
| GET | `/.well-known/oauth-protected-resource` | Public metadata, only when OAuth configured |

New intake returns 202 with an ID and `queued`. Identical retries return 200 and the same task; changed content under the same key returns 409. Unknown fields are rejected. Keys are 1–128 characters `[A-Za-z0-9_.:-]`; title ≤200 characters, instructions ≤16000. HTTP bodies ≤64 KiB. JSON only. No browser CORS access.

```sh
curl --config /srv/private/doodle/intake.curl.conf \
  --request POST 'https://YOUR-RELAY-DOMAIN/v1/tasks' \
  --header 'Content-Type: application/json' \
  --header 'Idempotency-Key: first-test-001' \
  --data '{"title":"First test","instructions":"Reply with a short confirmation. Do not change external systems."}'
curl --config /srv/private/doodle/intake.curl.conf \
  'https://YOUR-RELAY-DOMAIN/v1/tasks/TASK_ID_FROM_RESPONSE'
```

Credentials stay in owner-only curl config files, never command arguments or chat. Unauthenticated task reads return 401. Intake credentials cannot call MCP; MCP credentials cannot submit tasks.

## MCP tools

POST JSON-RPC requests with `jsonrpc: "2.0"`, a request `id`, `method`, and `params`. Use header `MCP-Protocol-Version: 2026-07-28`. Implemented methods: `server/discover`, `tools/list`, `tools/call`, `events/list`, `events/subscribe`, `events/unsubscribe`. This deliberately small implementation supports synchronous JSON responses and the documented event contract; it is not a general MCP implementation and has not undergone platform interoperability testing.

Tools: `relay_health`, `list_tasks`, `get_task`, `claim_task`, `update_task`. `tools/list` supplies schemas. Task tools are bounded to the configured owner. `list_tasks` returns at most 100 nonterminal tasks; fetch known IDs directly for others.

Claim takes `{task_id,request_id}` and returns a five-minute lease token. Same request retries return the same unexpired lease. Another claimant is rejected until expiration. Every update requires `{task_id,lease_token,request_id,status,result}`. Use a stable request ID for retries; changing its content produces an error. Update statuses: `running`, `waiting_approval`, `succeeded`, `failed`, `canceled`. Updates extend the active lease. Terminal tasks cannot be claimed. Stale lease holders cannot write. Retry receipts remain stored, including terminal updates.

An approval state records a pause only. The relay never grants permission or verifies external approvals. A worker may continue on its live lease only after actual owner approval in the connected workflow. If that lease expires while paused, this release deliberately refuses reclaims: create a new explicitly authorized task referencing the paused task. There is no administrative resume/delete UI yet.

## Events

Event `task.created` accepts exactly `{queue:"default"}`. Payload contains only task ID and queue; fetch content through the authenticated tool. Subscriptions are created by the platform through the documented request, not by a guessed callback. No public task discovery exists.

The relay verifies signed challenges before enabling delivery, stores encrypted signing keys, derives deterministic subscription IDs, grants at most one hour (also capped at OAuth expiration), and supports 60-second old/new signing-key overlap on rotation. Only explicitly configured callback hostnames are permitted. Each connection resolves and checks all addresses, pins a public address, preserves TLS hostname verification, enforces a ten-second deadline, caps response size, and never follows redirects.

SQLite stores tasks, subscription state and delivery outbox atomically. Delivery is at least once: stable event IDs, fresh signatures on retries, at most six attempts with exponential backoff. HTTP 410/413 and permanent 4xx stop retries; 408/429/network/5xx retry. An acknowledgment changes delivery state only. Outbox failures remain inspectable through task delivery state. No historical event replay: tasks submitted before subscribing remain pending_subscription; use list_tasks/get_task to find them.

Protocol reference: https://developers.openai.com/plugins/build/mcp-events (checked 2026-10-18). Real callback registration and platform compatibility remain unverified.

## Operations and limits

Node 24+, one process/replica, local persistent disk. SQLite uses WAL, FULL synchronous writes, and BEGIN IMMEDIATE transactions. The compact single-row JSON state storage is intended for small personal queues, not high throughput. Caps: 16 MiB serialized state (further writes reject atomically at capacity), 10000 retained tasks, 1000 active tasks, 32 subscriptions, 1000 update receipts per task, 120 authenticated requests/minute per credential class. No automatic deletion; monitor disk/memory and archive offline before hitting limits. State rewrites can become costly as history grows. Do not horizontally scale this release.

Use a protected backup of both database and encryption/configuration key. Stop the process before filesystem backup; preserve SQLite sidecar files. Existing JWTs remain valid until expiry (≤15 minutes); disabling the owner in config and restarting blocks further API/delivery. External IdP revocation is not polled. Tasks/results are protected by filesystem permissions, not application-level encryption; use encrypted disks/backups as needed.

Run `npm ci --ignore-scripts`, `npm run check`, `npm test`. Test fixtures are public synthetic values and ephemeral keys, not production credentials. No secrets, database files, node_modules, or account tokens belong in GitHub.
