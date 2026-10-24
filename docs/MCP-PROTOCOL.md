# MCP Protocol Reference

> **Reference for the LogicMem Model Context Protocol servers.**

## Two interfaces

| Interface | URL / command | Tool prefix | Auth |
|-----------|---------------|-------------|------|
| **Hosted MCP server** (recommended) | `https://mcp.logicmem.io/mcp` | `logicframe_*` | Bearer key for `tools/call` |
| **Local stdio bridge** (this repo) | `logicmem-server` | `logicmem_*` | `LOGICMEM_API_KEY` env var or `--api-key` |

Most of this document describes the **hosted server**. The local bridge's tools are listed at the end.

**Transport:** JSON-RPC requests over HTTPS POST (the server reports MCP protocol version `2024-11-05` in `initialize`).
**Authentication:** `Authorization: Bearer <api_key>` header. `initialize` and `tools/list` are public; `tools/call` requires a key.

The tool list below was checked against the live server's `tools/list` on 2026-10-24. The server exposes many more tools than listed here; `tools/list` is the source of truth.

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
  -H "Authorization: Bearer lm_your_api_key" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

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

Re-check the integrity of the audit chain and hash chain. No arguments. The server describes the result as `chain_valid`, `total_entries` and `failed_at_entry` (null if clean).

### `logicframe_memory_share`

Share an existing memory with another agent.

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
| `limit` | number | ❌ | Max entries |

### Other hosted tools

Including `logicframe_correction_log`, `logicframe_conversations_store`, `logicframe_conversations_resume`, `logicframe_intelligence`, `logicframe_confidence`, `logicframe_trace`, `logicframe_memory_stats` and `logicframe_health`. Run `tools/list` for the full list and each tool's input schema.

---

## Errors (hosted)

The server answers with an HTTP status and a JSON body with an `error` message, for example:

| HTTP status | When |
|-------------|------|
| `401` | `tools/call` without a valid API key |
| `404` | Unknown MCP method |
| `429` | Rate limit exceeded; back off and retry |
| `5xx` | Server error |

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
