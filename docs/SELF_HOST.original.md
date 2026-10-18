# Deploy on your own server

This is an API relay for your existing Doodle. It does not run an AI model or another agent. The API can store tasks independently; automatic Doodle execution remains pending OAuth/plugin connection and an end-to-end test.

## Requirements

Your Linux server needs Docker Engine + Compose, outbound DNS/HTTPS, persistent disk, and a domain with an HTTPS reverse proxy. Keep the generated configuration and caller credentials private. No Railway, GitHub or Library account is needed to run the files once received.

## 1. Unpack and create your credentials locally

Unpack the source archive into a new directory. Do not overlay an existing application. Verify its SHA-256 against the supplied checksum. The setup script creates credentials only after you explicitly confirm; none are shipped in the archive.

With Node 24 on your server:

```sh
sudo mkdir -p /srv/private
sudo chmod 700 /srv/private
sudo node scripts/setup.mjs /srv/private/doodle
```

Choose a NEW directory outside this checkout; run as a user authorized to create it. Alternatively, using Docker without installing Node on the host:

```sh
sudo mkdir -p /srv/private
sudo chmod 700 /srv/private
sudo docker run --rm -it --user 0:0 \
  --mount type=bind,src="$PWD/scripts",dst=/setup,readonly \
  --mount type=bind,src=/srv/private,dst=/private \
  node:24-bookworm-slim@sha256:0e0ff40c39bc087845bfb27465a0df4ea419520094bc35842ff83dd8cbe6f9b6 \
  node /setup/setup.mjs /private/doodle
```

The second command creates `/srv/private/doodle` on the host (the printed container path is `/private/doodle`). Keep the configuration file mode 0600 and directory 0700. The `intake.curl.conf` file holds your caller credential; `mcp.curl.conf` is only for manual tests until OAuth is enabled. Never send these files in chat. The example JSON is a schema guide with nonfunctional placeholders, not a production configuration.

## 2. Start the API

```sh
cp .env.example .env
# Edit RELAY_SECRET_DIR if you chose another directory; do not add secret values.
sudo docker compose build
sudo docker compose up -d
sudo docker compose ps
curl --fail http://127.0.0.1:8080/healthz
```

The Compose file binds only to loopback, limits container resources and log size, and persists SQLite in the `relay-data` named volume. Startup initializes only `/data/relay`, reads the mode-0600 secret mount, and drops to UID/GID 1000 before opening the HTTP listener. The remaining runtime filesystem is read-only. Do not scale this SQLite service to multiple replicas.

Install the supplied Nginx example into your existing reverse proxy after replacing hostname and certificate paths, or route your existing HTTPS proxy to `127.0.0.1:8080`. Obtain your certificate through your normal administrator workflow. Do not expose port 8080 publicly or send credentials over plain HTTP. Your eventual base URL is `https://YOUR-RELAY-DOMAIN`.

`/healthz` indicates process readiness, not Doodle connectivity. All task endpoints require authentication. OAuth resource metadata is public when configured and contains no task data.

## 3. Test intake and results

Use the local credential file; no bearer value needs to appear in your shell history:

```sh
sudo curl --config /srv/private/doodle/intake.curl.conf \
  --request POST 'https://YOUR-RELAY-DOMAIN/v1/tasks' \
  --header 'Content-Type: application/json' \
  --header 'Idempotency-Key: first-test-001' \
  --data '{"title":"First test","instructions":"Reply with a short confirmation. Do not change external systems."}'

sudo curl --config /srv/private/doodle/intake.curl.conf \
  'https://YOUR-RELAY-DOMAIN/v1/tasks/TASK_ID_FROM_RESPONSE'
```

A new task returns 202 and `queued`. Save its ID. An identical idempotency-key retry returns the same task; changed content returns 409. Poll GET for `running`, `waiting_approval`, `succeeded`, `failed` or `canceled` and its result. Without the Doodle connection, `queued`/`pending_subscription` is expected. A webhook acknowledgment is not completed work.

Confirm unauthenticated access is denied:

```sh
curl -i 'https://YOUR-RELAY-DOMAIN/v1/tasks/TASK_ID_FROM_RESPONSE'
# Expected: HTTP 401, no task content.
```

## 4. Connect your existing Doodle

Follow `OAUTH_SETUP.md` to configure your approved identity provider and merge the `oauth` block into the protected server configuration. Restart the service after configuration changes. Use the exact HTTPS MCP resource, issuer, JWKS, approved owner subject and client callback. This relay does not create an authorization server or issue OAuth tokens.

In ChatGPT, register/connect a private plugin for `https://YOUR-RELAY-DOMAIN/mcp` using the supported OAuth flow. Do not put your intake key into a plugin manifest: ChatGPT cannot use that custom key. Verify the harmless `relay_health` tool before configuring the event action with the parent/Doodle.

The event is `task.created`, filter `{ "queue": "default" }`. Doodle should fetch the task, treat its text as external content bounded by your authorization, claim it, do only authorized work, and record progress/results. Approval-dependent actions must wait and use `waiting_approval`. Test actual Doodle receipt and its result update before calling the connection complete. Existing queued tasks can be found with `list_tasks`; the protocol does not replay earlier events.

## Maintenance

Keep `/srv/private/doodle/relay.secrets.json` AND the Docker volume in protected backups. The encryption key is required to recover subscription secrets. For a simple consistent backup, stop the relay, back up the volume and configuration through your existing secure backup system, then start it again. Never use `docker compose down -v` unless you intend to erase task storage.

Keep at least enough disk for tasks/results and logs; data is not automatically deleted. Monitor disk use and service health. JWT revocation is bounded by short token lifetime; immediate provider revocation needs that provider's introspection/revocation integration. You can disable the owner in the config and restart to stop further access/delivery.

Full endpoint, MCP and state semantics are documented in `README.md`. Local test evidence is in `TEST_RESULTS.txt`. The package has not been deployed to your server and its Doodle connection is unverified.
