# Connect the existing Doodle

This project is an OAuth resource server, not an identity provider. No OAuth client, consent, plugin, callback, or Doodle run has been created. Static manual MCP credentials are not represented as a supported ChatGPT login method.

Choose an approved identity provider. Register the private plugin through the current supported ChatGPT flow and use its actual callback/redirect configuration; never invent redirect URLs. The provider must issue signed JWT access tokens with exact issuer, audience matching your HTTPS `/mcp` resource, owner subject, `tasks:manage` scope, `iat`, and `exp`, with a lifetime no longer than 900 seconds. Accepted signature algorithms are explicitly allowlisted in config. Never paste access tokens/client secrets in chat or source.

Merge the `oauth` block from `examples/relay-config.example.json` into your protected generated JSON. Keep the intake hash, encryption key and owner. Use your actual issuer, HTTPS JWKS URL, audience, subject, scope and algorithm. Set `callbackHosts` to exact platform-supplied callback hostnames approved by the owner. Restart after changes. With OAuth enabled the manual MCP static credential is rejected; intake continues to use its separate key.

Protected resource metadata is at `/.well-known/oauth-protected-resource`. A 401 challenge points there. Provider discovery, authorization, client registration, consent, refresh and administrative setup are the provider/platform's responsibility. No tokens are minted by this relay. A provider that issues opaque access tokens needs a separately implemented and reviewed introspection adapter; this release does not support it.

Connect the private plugin to your HTTPS `/mcp`. First verify harmless `relay_health`. Then, with the owner, configure the event-triggered workflow for `task.created`, arguments `{"queue":"default"}`. Only the supported subscription operation supplies callback URL/signing secret. Do not manually fabricate them.

The workflow should fetch the task, treat its text as untrusted external content, claim it using a stable request ID, perform only owner-authorized actions, record progress or waiting_approval, and finish with a result. Retry write calls with the same request ID. Deduplicate event IDs; delivery may repeat or arrive out of order. The relay does not execute actions itself or override approval requirements.

Finally submit a harmless task, observe actual Doodle receipt and claim, and verify a recorded result through GET status. Until this succeeds, the bridge is pending integration. Local mocked callback/JWT tests do not establish live provider or platform interoperability.
