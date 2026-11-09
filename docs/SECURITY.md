# Security Model

> **How LogicMem handles your agent memory data, and what this repo can and cannot tell you.**

This repo contains the client SDK and a local MCP bridge. The LogicMem server runs in LogicMem's cloud and is not in this repo, so server-side details (storage encryption, key management, hosting) are not documented or verifiable here. Ask [security@logicmem.io](mailto:security@logicmem.io) if you need them for a review.

---

## In transit

- The SDK and the local MCP server talk to `https://api.logicmem.io`; MCP clients talk to `https://mcp.logicmem.io/mcp`. Both are HTTPS only.
- As of October 2026 the docs said both endpoints negotiate TLS 1.3 with a modern client. A handshake from the Nov 9, 2026 audit to `api.logicmem.io`, `mcp.logicmem.io`, and `logicmem.io` negotiated TLS 1.3 (`TLS_AES_256_GCM_SHA384`) and the certificate verified (SAN `*.logicmem.io`). That is one client handshake. It does not prove older TLS versions are disabled.
- The SDK uses `requests`, which validates server certificates by default.

---

## Authentication

```
Authorization: Bearer lm_your_api_key
```

- Keys start with `lm_` and are issued to pilot teams ([logicmem.io/design-partner](https://logicmem.io/design-partner/)).
- Send the key in the `Authorization` header. The SDK and `logicmem-server` never put it in the URL.
- Keyless checks are not a universal auth policy. On Nov 9, 2026, about 8:03–8:10 AM ET, keyless GET of `/sse`, `/mcp/sse`, and `/mcp`, and keyless POST `initialize` and `tools/list`, returned HTTP 401 on both `api.logicmem.io` and `mcp.logicmem.io`. Later that day, about 4:15 PM ET, keyless POST `initialize`, `tools/list`, and an unknown method, plus keyless GET, against `https://mcp.logicmem.io/mcp` only, also returned HTTP 401. The POST error text mentioned a bearer `lm_` key or an OIDC token. Authenticated session behavior was not replayed. The local stdio server still answers `initialize` and `tools/list` on stdin without a key; the REST call behind a tool still needs one.
- An operator runbook dated Nov 8, 2026 lists these for direct HTTP and was not replayed here: `Authorization: Bearer lm_...`, `Accept: application/json, text/event-stream`, a descriptive `User-Agent`, `X-Agent-ID`, and `Mcp-Session-Id` after `initialize`. No session id was observed, because the keyless calls stopped at 401.

---

## Tenant scoping

Calls include a `client_id` string you choose. The SDK sends it and does not check it against the API key. This page does not claim that one key may write every `client_id`, and it does not claim the opposite as a fully tested rule.

Use a `client_id` your key is meant to use. A Nov 9, 2026 check returned HTTP 403 for a foreign `client_id` on that check's route. That is dated counterevidence against a general cross-tenant bypass. It was not repeated in this audit, and it is not a complete allow-list.

```python
# Two writes with one key only if that key is permitted to use both ids.
# This SDK does not know the answer. Prefer the id issued for the key.
memory.log(text="...", client_id="demo-tenant")
```

Several agent keys inside one workspace are compatible with one workspace scope. A declared `agent_id` is not a second credential. See [A2A-PROTOCOL.md](A2A-PROTOCOL.md).

---

## Audit trail

Some operations made through the API and MCP connector are written to tamper-evident, hash-linked records. Not every endpoint writes an audit entry yet. An Oct 27, 2026 server snapshot that is not in this repository kept two records: a hash-linked audit log that included rows such as `RECALL` and a correction write, and a selected-write chain limited to `LOG`, `SHARE`, `BROADCAST`, `SUPERSEDE`, `ARCHIVE`, and `MEMORY_MERGE` (not `RECALL`). Do not treat the selected-write list as "recall is unaudited." Whether production still matches that snapshot, and whether `logicframe_correction_log` is the correction row, was not established. `AuditChain.verify()` asks the server to re-check. It does not walk the hashes in this process.

```
Genesis entry
     │
     ▼
Entry 1 (prev_hash + operation → hash)
     │
     ▼
Entry 2 (prev_hash + operation → hash)
```

Because each entry includes the previous entry's hash, a modified, deleted or reordered past entry breaks the chain from that point, and that shows up when you re-check it with `AuditChain.verify()` (SDK) or the `logicframe_audit_verify` MCP tool. Tamper-evident means changes are detectable, not that they are impossible. Chain verification alone does not detect removal of the most recent entries.

---

## Data handling this repo can and cannot state

- **Embeddings.** [EMBEDDING-FALLBACK.md](EMBEDDING-FALLBACK.md) says the server, not this SDK, tries Cohere `embed-v4.0`, then another Cohere model, then local Ollama, then a deterministic token-hash vector. A public `GET /memory/health` on 2026-11-09 returned `"embedding": "embed-v4.0"`. That matches the name of the first tier. It does not show the fallback running, and this audit did not trace a write to Cohere. Retention of that text is not stated here.
- **Corrections.** `AuditChain.log_correction()` POSTs the original text, the corrected text, and the reason to `/memory/correction/log`. The client and the README describe that post as stored and queued for the server's DPO training pipeline. The training job is not in this repository. This page does not state what is trained, on whose data, whether tenants are separated, how long corrections are kept, or how to opt out. Those are open questions for the operator, not a policy invented here.
- **Sharing flags.** `agent_id` and `is_private` are caller-supplied fields. They are not described here as a privacy guarantee.

## Regulatory record-keeping

LogicMem is designed to support record-keeping such as [EU AI Act Article 12](https://logicmem.io/eu-ai-act-article-12/). It is a building block for your records, not a compliance certificate. Nothing here is legal advice.

---

## Reporting security issues

Found a security issue? Email **security@logicmem.io** with details. Please do not open a public issue.

---

## Best practices

1. **Never log or commit API keys**; use environment variables or a secrets manager
2. **Rotate keys periodically**; ask support@logicmem.io for a new key
3. **Use separate keys per agent** where you can
4. **Add client-side rate limiting** to avoid HTTP 429s
5. **Verify the audit chain** regularly for high-stakes workloads
