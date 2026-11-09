# MCP Protocol Reference

> **Reference for the LogicMem Model Context Protocol servers.**

## Two interfaces

| Interface | URL / command | Tool prefix | Auth |
|-----------|---------------|-------------|------|
| **Hosted MCP server** (recommended) | `https://mcp.logicmem.io/mcp` | `logicframe_*` | Bearer key. Keyless `initialize` and `tools/list` returned HTTP 401 on 2026-11-09 (see below). |
| **Local stdio bridge** (this repo) | `logicmem-server` | `logicmem_*` | The stdio handshake does not check a key. REST calls use `LOGICMEM_API_KEY` or `--api-key`. |

Most of this document describes the **hosted server**. The local bridge's tools are listed at the end. Hosted and local tools are not one-to-one. The map is in the README.

**Transport:** Clients such as OpenClaw can set `transport` to `streamable-http`. That is the client config key. The local bridge's `initialize` result uses protocol version `2024-11-05` (this repo's code). The hosted server's protocol version was **not** re-read on 2026-11-09, because keyless `initialize` returned HTTP 401. JSON-RPC POST is how the cURL sample talks to the URL. An operator runbook dated Nov 8, 2026 also describes a GET/SSE stream and a `Mcp-Session-Id` after `initialize`. That session was not replayed here.

**Authentication:** Send `Authorization: Bearer <api_key>`. Do not describe `initialize` or `tools/list` as public. A Nov 9, 2026 morning operator note recorded HTTP 401 for keyless GET `/sse`, `/mcp/sse`, and `/mcp`, and for keyless POST `initialize` and `tools/list`, on both hosts. That contradicts the older "public tools/list" sentence for those requests. It does not set an order between authentication and method routing for every later request, and it was not an authenticated call.

**Direct HTTP (operator runbook, Nov 8, 2026, not replayed):** `Accept: application/json, text/event-stream`, a descriptive `User-Agent`, `X-Agent-ID`, the bearer token, then `Mcp-Session-Id` from `initialize` when one is returned. No authenticated session id is recorded in these docs.

The tool list below was checked against a live `tools/list` on 2026-10-24. It was not reconfirmed on 2026-11-09 because the keyless call returned HTTP 401. `tools/list` with a key is the source of truth. The server may expose more tools than this page.

---

## Authentication

```
Authorization: Bearer lm_your_api_key
Content-Type: application/json
```

API keys are issued to pilot teams: [logicmem.io/design-partner](https://logicmem.io/design-partner/).

### cURL example

```bash
curl -X POST https://mcp.logicmem.io/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer lm_your_api_key" \
  -H "User-Agent: logicmem-docs-example" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "docs-example", "version": "0"}
    }
  }'
```

This sample was not executed against the hosted server in the Nov 9, 2026 audit (no production calls on the patched docs). A keyless POST of the same method returned HTTP 401 that day. If `initialize` returns a session id, send it as `Mcp-Session-Id` on later requests. That header was not observed here. `X-Agent-ID` is the declared agent label from the Nov 8 runbook, not a proof of identity.

---

## Request format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "<tool_name>",
    "arguments": { }
  }
}
```

Response field names are set by the server and may change, so print the result rather than relying on exact fields.

---

## Tool reference (hosted)

### `logicframe_memory_log`

Store a new memory entry.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | ✅ | Memory content. Be specific: who, what, when, why. |
| `category` | string | ❌ | e.g. general, client_identity, decision, preference, contract, correction, interaction, complaint. Default: general |
| `importance` | number | ❌ | Importance 1-10. Default: 7 |
| `tags` | string[] | ❌ | Optional tags |
| `client_id` | string | ❌ | Tenant identifier |
| `agent_id` | string | ❌ | Which agent wrote it |
| `source` | string | ❌ | e.g. voice_call, chat, email, manual |
| `is_permanent` | boolean | ❌ | Mark as permanent |
| `skip_classification` | boolean | ❌ | Faster bulk writes (skips entity extraction and classification) |

**Example:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "logicframe_memory_log",
    "arguments": {
      "text": "The user prefers Telegram for urgent messages. Email only for formal.",
      "category": "preference",
      "importance": 8
    }
  }
}
```

### `logicframe_memory_recall`

Search memories using natural language.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ | What to search for |
| `limit` | number | ❌ | Max results. Default: 5 |

### `logicframe_memory_context`

Get a synthesized narrative about a client, project, or person.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entity` | string | ✅ | Entity name |
| `depth` | string | ❌ | `brief` or `full`. Default: full |

### `logicframe_reason`

Multi-step reasoning that consults memory at each step.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | ✅ | The question to reason about |
| `context` | string | ❌ | Additional context |
| `mode` | string | ❌ | `fast`, `deep` or `exhaustive`. Default: deep |
| `max_steps` | number | ❌ | Max reasoning iterations. Default: 5 |
| `memory_query` | string | ❌ | What to search in memory |
| `client_id` | string | ❌ | Tenant identifier |

### `logicframe_verify`

Check a claim or plan against stored memories.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claim` | string | ✅ | The statement to verify |
| `memory_query` | string | ❌ | What to search (defaults to the claim) |
| `check_type` | string | ❌ | `contradiction`, `support` or `both`. Default: both |
| `client_id` | string | ❌ | Tenant identifier |

### `logicframe_reflect`

Critique a draft answer against memory.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `draft_answer` | string | ✅ | The draft answer |
| `question` | string | ✅ | The original question |
| `memory_query` | string | ❌ | What to search for evidence |
| `client_id` | string | ❌ | Tenant identifier |

### `logicframe_audit_verify`

Ask the server to re-check the audit chain and the hash chain. No arguments in the 2026-10-24 note. That note said the server describes `chain_valid`, `total_entries`, and `failed_at_entry` (null if clean). Those field names were not reconfirmed on 2026-11-09. Two records, and the fact that recall can be on one and not the other, are described in [SECURITY.md](SECURITY.md). A clean report does not prove truth, completeness, or that the newest entries were not removed.

### `logicframe_memory_share`

Share an existing memory with another declared agent id. The id is a route, not a separate credential. `is_private` is not a field in this 2026-10-24 note.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entry_id` | string | ✅ | Entry ID (from recall results) |
| `to_agent` | string | ✅ | Target agent ID |
| `note` | string | ❌ | Optional note |

### `logicframe_memory_sync_check`

Check for memories stored by other agents since a timestamp.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `since_timestamp` | string | ❌ | ISO 8601 timestamp |
| `client_id` | string | ❌ | Tenant identifier |
| `agent_id` | string | ❌ | Your agent ID |
| `limit` | number | ❌ | Max entries to request. An Oct 27, 2026 source snapshot of this MCP tool (`logicframe_memory_sync_check` only, not REST `/memory/shared/updates`) returned newest first, defaulted the slice to 50, included `total_new`, and had no cursor. The SDK's `sync()` is the REST call: it defaults to 50 and drops `total_new`, so it cannot apply that comparison. If a list comes back as long as `limit`, do not treat it as complete and do not advance a checkpoint. A shorter list is not proof of completeness. Do not assume a higher limit is accepted. |

### Other hosted tools

Including `logicframe_correction_log`, `logicframe_conversations_store`, `logicframe_conversations_resume`, `logicframe_intelligence`, `logicframe_confidence`, `logicframe_trace`, `logicframe_memory_stats` and `logicframe_health`. Run `tools/list` for the full list and each tool's input schema.

---

## Errors (hosted)

The server answers with an HTTP status and a JSON body with an `error` message, for example:

| HTTP status | When |
|-------------|------|
| `401` | Keyless requests in the Nov 9, 2026 morning note, including `initialize`, `tools/list`, and the paths named above. Not a claim about authenticated routing order. |
| `404` | Unknown MCP method, as written in the 2026-10-24 notes. Those notes do not record whether the request presented a key. Not rechecked on 2026-11-09. |
| `429` | Rate limit, as written in the 2026-10-24 notes. Auth state was not recorded there. Not rechecked on 2026-11-09. |
| `5xx` | Server error, as written in the 2026-10-24 notes. Not rechecked on 2026-11-09. |

---

## Rate limits

Rate limits depend on your plan. Requests over the limit return HTTP 429.

---

## Local stdio bridge tools (`logicmem-server`)

| Tool | Description |
|------|-------------|
| `logicmem_memory_log` | Store a memory |
| `logicmem_memory_recall` | Search memories |
| `logicmem_memory_session` | Session context summary |
| `logicmem_memory_stats` | Memory stats |
| `logicmem_memory_health` | Server health |
| `logicmem_memory_outcome` | Record how useful a memory was (`entry_id`, `score`) |
| `logicmem_a2a_register` | Register an agent |
| `logicmem_a2a_heartbeat` | Agent heartbeat |
| `logicmem_a2a_list_agents` | List registered agents for a client_id |
| `logicmem_a2a_write_shared` | Write to the shared pool |
| `logicmem_a2a_sync` | Get shared memories for an agent |

Run `logicmem-server --help` for options.
