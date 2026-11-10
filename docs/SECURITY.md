# Security Model

> **How LogicMem handles your agent memory data, and what this repo can and cannot tell you.**

This repo contains the client SDK and a local MCP bridge. The LogicMem server is not in this repo. A Nov 9, 2026 read of the source on disk for the running memory service is summarized below. That file's timestamp is at or before the process start. The process memory was not compared byte for byte, so this is not a live-memory proof. Ask [security@logicmem.io](mailto:security@logicmem.io) for a review that needs more than this page.

---

## In transit

- The SDK and the local MCP server talk to `https://api.logicmem.io`; MCP clients talk to `https://mcp.logicmem.io/mcp`. Both are HTTPS only.
- As of October 2026 these docs said both endpoints negotiate TLS 1.3 with a modern client. One handshake on 2026-11-09 to `api.logicmem.io`, `mcp.logicmem.io`, and `logicmem.io` negotiated TLS 1.3 (`TLS_AES_256_GCM_SHA384`) and the certificate verified (SAN `*.logicmem.io`). That is one client handshake. It does not prove older TLS versions are disabled.
- The SDK uses `requests`, which validates server certificates by default.

---

## What the Nov 9, 2026 memory source does

These facts are about the LogicMem memory service customers call. They are not a grade, a certification, or a claim that a separate defense service covers this product.

- **New memory text is encrypted with Fernet** before it is stored. Fernet is AES-128-CBC with HMAC-SHA256. AES-256-GCM in that same file is a decrypt path for older payloads, using HKDF-SHA256. New writes traced from `/memory/log` do not call it.
- **The encryption key is a file on the server**, mode 600 in the source that creates it. It is not a hardware security module, not a customer-held key, and not a separate key per workspace. End-to-end encryption is not what this path does: the server holds the key.
- **Writes require a bearer API key.** A missing, unknown, or suspended key is rejected. A normal key that sends a different workspace id is rejected. Operator keys can write another workspace. A declared `agent_id` is still not a second login.
- **The memory service applies a per-key rate limit.** The default in that source is 1000 requests per minute. Clients can still receive HTTP 429.
- **The audit log is SHA-256 and hash-linked** (each row includes the previous row's hash). The selected-write chain in that source is still `LOG`, `SHARE`, `BROADCAST`, `SUPERSEDE`, `ARCHIVE`, and `MEMORY_MERGE`. Recall can be on the audit log and off that chain. Verification walks rows the server still holds. It does not, by itself, show that the newest rows were removed.
- **Configured webhooks from the listener that this memory source imports** are signed with HMAC-SHA256. Headers are `X-LogicMem-Timestamp` and `X-LogicMem-Signature` (`sha256=`). A failed delivery can be retried. Delivery is not exactly once and is not guaranteed. The local `webhooks/dispatcher.py` queue in this kit is a different program.

### Separate defense service

A second service was running on Nov 9, 2026. It is not the memory API this SDK calls.

- Its own store encrypts with AES-256-GCM. The ordinary store call does not pass an entry id as additional authenticated data.
- A module that derives a per-entry key with HKDF-SHA384 is imported by a key-rotation route, not by that ordinary store.
- Bearer tokens on that service can be checked with Ed25519. A file header mentions PKCE. The code that was read does not implement a PKCE `code_challenge`.
- Pattern checks for injection run on that service's memory routes. They were not on the standard LogicMem memory write path.
- Module names that say compliance, threat intelligence, or CNSA are labels. They are not a SOC 2, CNSA, HIPAA, GDPR, or military-grade certification. Key length alone is not a grade.

## Authentication

```
Authorization: Bearer lm_your_api_key
```

- Keys start with `lm_` and are issued to pilot teams ([logicmem.io/design-partner](https://logicmem.io/design-partner/)).
- Send the key in the `Authorization` header. The SDK and `logicmem-server` never put it in the URL.
- Keyless checks are not a universal auth policy. A Nov 9, 2026 morning operator note (about 8:03–8:10 AM ET) recorded HTTP 401 for keyless GET of `/sse`, `/mcp/sse`, and `/mcp`, and for keyless POST `initialize` and `tools/list`, on both `api.logicmem.io` and `mcp.logicmem.io`. Separately, about 4:15–4:28 PM ET the same day (21:15–21:28 UTC), this review sent disallowed keyless POST `initialize`, `tools/list`, and an unknown method, plus keyless GET, to `https://mcp.logicmem.io/mcp` only. Those also returned HTTP 401. The POST error text mentioned a bearer `lm_` key or an OIDC token. Those afternoon calls were not allowed. They are rejects, not accepted writes, and they are not the morning note. Authenticated session behavior was not replayed. The local stdio server still answers `initialize` and `tools/list` on stdin without a key; the REST call behind a tool still needs one.
- An operator runbook dated Nov 8, 2026 lists these for direct HTTP and was not replayed here: `Authorization: Bearer lm_...`, `Accept: application/json, text/event-stream`, a descriptive `User-Agent`, `X-Agent-ID`, and `Mcp-Session-Id` after `initialize`. No session id was observed, because the keyless calls stopped at 401.

---

## Tenant scoping

Calls include a `client_id` string you choose. The SDK sends it and does not check it against the API key. This page does not claim that one key may write every `client_id`, and it does not claim the opposite as a fully tested rule.

Use a `client_id` your key is meant to use. The Nov 9, 2026 memory source rejects a normal key that sends a different workspace id. Operator keys can write another workspace. A Nov 9, 2026 morning operator note recorded HTTP 403 for a foreign `client_id` on that check's route. That agrees with the source for a normal key. It is not a proof that every route was tested.

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

Because each entry includes the previous entry's hash, a modified, deleted or reordered past entry breaks the chain from that point among the entries the server still holds. A re-check with `AuditChain.verify()` (SDK) or the `logicframe_audit_verify` MCP tool reports that break when the server still has the damaged span. Tamper-evident means changes are detectable, not that they are impossible. Chain verification alone does not detect removal of the most recent entries. This package does not export the chain for a separate check.

---

## Data handling this repo can and cannot state

- **Embeddings.** [EMBEDDING-FALLBACK.md](EMBEDDING-FALLBACK.md) says the server, not this SDK, tries Cohere `embed-v4.0`, then another Cohere model, then local Ollama, then a deterministic token-hash vector. A public health read on 2026-11-09 reported `embedding` `embed-v4.0`. That matches the name of the first tier. It does not show the fallback running, and a write was not traced to Cohere. Retention of that text is not stated here.
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
