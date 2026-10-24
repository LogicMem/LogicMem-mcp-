# Security Model

> **How LogicMem handles your agent memory data, and what this repo can and cannot tell you.**

This repo contains the client SDK and a local MCP bridge. The LogicMem server runs in LogicMem's cloud and is not in this repo, so server-side details (storage encryption, key management, hosting) are not documented or verifiable here. Ask [security@logicmem.io](mailto:security@logicmem.io) if you need them for a review.

---

## In transit

- The SDK and the local MCP server talk to `https://api.logicmem.io`; MCP clients talk to `https://mcp.logicmem.io/mcp`. Both are HTTPS only.
- As of October 2026 both endpoints negotiate TLS 1.3 with a modern client.
- The SDK uses `requests`, which validates server certificates by default.

---

## Authentication

```
Authorization: Bearer lm_your_api_key
```

- Keys start with `lm_` and are issued to pilot teams ([logicmem.io/design-partner](https://logicmem.io/design-partner/)).
- Send the key in the `Authorization` header. The SDK and `logicmem-server` never put it in the URL.
- On the hosted MCP server, `initialize` and `tools/list` are public; `tools/call` requires a key and returns HTTP 401 without one.

---

## Tenant scoping

Memory calls take a `client_id`, which the server uses to group memories by tenant. Use a different `client_id` per tenant:

```python
memory.log(text="...", client_id="tenant-a")
memory.log(text="...", client_id="tenant-b")
```

---

## Audit trail

Memory operations made through the API and MCP connector are logged to a **tamper-evident, hash-linked chain**:

```
Genesis entry
     │
     ▼
Entry 1 (prev_hash + operation → hash)
     │
     ▼
Entry 2 (prev_hash + operation → hash)
```

Because each entry includes the previous entry's hash, a modified, deleted or reordered entry breaks the chain, and that shows up when you re-check it with `AuditChain.verify()` (SDK) or the `logicframe_audit_verify` MCP tool. Tamper-evident means changes are detectable, not that they are impossible.

---

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
