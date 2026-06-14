# Security Model

> **How LogicMem protects your agent memory data.**

---

## Overview

LogicMem is designed for production AI agent workloads, including
defense and government applications that require the highest levels of
security and auditability.

---

## Encryption

### At Rest

- **Algorithm:** AES-256-GCM
- **Key Management:** Per-tenant keys managed via CNSA 2.0-compatible KMS
- **Scope:** All memory entries, embeddings, and metadata are encrypted
  before being written to storage

### In Transit

- **Protocol:** TLS 1.3 (minimum TLS 1.2)
- **Certificate:** Validated against the operating system's CA store

### Embeddings

- **Vector embeddings** are stored encrypted at rest
- **Query vectors** are never stored — only computed in memory during search

---

## Authentication

### API Keys

- Every agent has a unique API key
- Keys are prefixed (e.g., `lm_live_...`) to distinguish from test keys
- Keys are hashed at rest — we never store or log the raw key value
- Rotate keys via the dashboard or API without downtime

### Request Authentication

```
Authorization: Bearer lm_your_api_key
```

All requests must include the API key in the `Authorization` header.
Query string authentication is not supported.

---

## Multi-Tenant Isolation

### Client ID

The `client_id` parameter provides **logical isolation** between tenants:

```python
memory.log(text="...", client_id="tenant-a")  # only visible to tenant-a
memory.log(text="...", client_id="tenant-b")  # only visible to tenant-b
```

Even if two tenants use the same agent ID, memories are isolated by `client_id`.

---

## Audit Trail

Every memory operation is logged to an **immutable hash-linked chain**:

```
Genesis Block
     │
     ▼
Block 1 (prev_hash + ops → hash)
     │
     ▼
Block 2 (prev_hash + ops → hash)
     │
     ▼
Block 3 (prev_hash + ops → hash)
```

Any tampering (modified entry, deleted entry, reordered entry) breaks the
chain and is detectable via `AuditChain.verify()`.

---

## Key Rotation

When rotating encryption keys:

1. Generate a new key via the dashboard or API
2. LogicMem re-encrypts all data with the new key in the background
3. The old key is archived to `~/.config/logicframe/old-keys/`
4. Both servers restart cleanly with the new key
5. Verify with `AuditChain.verify()` after rotation

**Never expose the raw encryption key in logs, chat history, or messages.**

---

## Compliance

- **CNSA 2.0:** Suite B cryptography for defense and national security workloads
- **GDPR:** Data residency options for EU customers
- **SOC 2 Type II:** In progress (expected Q3 2026)

---

## Reporting Security Issues

Found a security issue? Email **security@logicmem.io** with details.
We respond within 24 hours and aim to resolve critical issues within 7 days.

---

## Best Practices

1. **Never log API keys** — use environment variables
2. **Rotate keys periodically** — every 90 days for production
3. **Use separate keys per agent** — not shared keys across agents
4. **Enable rate limiting** — on your side to prevent abuse
5. **Verify audit chain** — weekly for high-stakes workloads
