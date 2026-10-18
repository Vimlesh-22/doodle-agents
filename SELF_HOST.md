# Deploy Doodle Agent's on your own server

This guide is updated for the 2026-10-18 rebuild. Earlier configuration shapes are not compatible: use this release's setup script and example. No deployment has been performed.

1. Use a new directory, Node 24 and npm. Run `npm ci --ignore-scripts` and `npm test`. Install Docker Engine + Compose if using containers. Provision HTTPS through your existing administrator workflow. No Railway or inference service is needed.
2. Generate private credentials yourself after reviewing the setup prompt:

```sh
sudo mkdir -p /srv/private
sudo chmod 700 /srv/private
sudo node scripts/setup.mjs /srv/private/doodle
```

This prompts before generating credentials. It creates mode-0600 `relay.secrets.json`, `intake.curl.conf`, `mcp.curl.conf` in a new mode-0700 directory. For Compose, keep the config root-owned (as produced by sudo setup) so root startup can read it without DAC override capabilities. Keep them outside the checkout. Never send them in chat. No credentials were generated as part of this rebuild.

3. For Docker:

```sh
cp .env.example .env
# Change only directory/port values as needed.
sudo docker compose build
sudo docker compose up -d
curl --fail http://127.0.0.1:8080/healthz
```

The Docker build installs locked dependencies offline from bundled upstream tarballs verified against package-lock.json. Base image download still requires registry access. Compose binds loopback only, limits memory/CPU/log size, and uses a persistent named volume. Root startup initializes only /data/relay, reads the protected configuration, then drops supplementary groups and UID/GID to 1000. Do not run multiple replicas. Never use `docker compose down -v` unless erasing task storage is intended.

For direct Node execution as a non-root user, set `RELAY_CONFIG` to the absolute private JSON path and `RELAY_DB` to a path in your protected persistent directory, then `npm start`. Do not run direct Node as root: the root initializer is intentionally restricted to the container data path.

4. Adapt `examples/nginx.conf` or your existing HTTPS proxy to forward to loopback port 8080. Replace hostname/certificate placeholders. Base URL becomes `https://YOUR-RELAY-DOMAIN`. Keep 8080 private. The application rejects browser Origin headers and has no frontend. Apply edge rate limits to unauthenticated traffic.
5. Follow README curl examples for intake/status. Confirm unauthorized requests return 401. Test restart persistence. Readiness is not Doodle connectivity.
6. Follow `OAUTH_SETUP.md` before connecting a private plugin. Approve the actual callback hostname in the protected config. No callback hostname is guessed or preapproved in source.
7. Back up the configuration and SQLite directory while stopped. Monitor disk, queue limits and failed deliveries. No automated retention, restore service or billing cap is supplied.

The existing Doodle must still be connected and tested end to end. Submitted task content is external data; it cannot grant itself authority to send messages, deploy code or change external systems. Approval-dependent work must pause in the actual Doodle workflow.
