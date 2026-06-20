# MCP Protocol Reference

> **Complete reference for the LogicMem Model Context Protocol server.**

## Important — Two Interfaces

This SDK serves **two different MCP interfaces** with different tool names:

| Interface | URL | Tool Prefix | Auth |
|-----------|-----|-------------|------|
| **Hosted MCP Server** (recommended) | `https://mcp.logicmem.io/mcp` | `logicframe_*` | Required for writes |
| **Local stdio bridge** (pip package) | `logicmem-server` command | `logicmem_*` | Via env vars |

This document describes the **hosted MCP server** at `mcp.logicmem.io` with `logicframe_*` tool names.

## Overview

The LogicMem MCP server implements the [Model Context Protocol](https://modelcontextprotocol.io)
specification, providing a standardized interface for AI agents to access
persistent memory, reasoning, and audit capabilities.

**Protocol version:** JSON-RPC 2.0 over HTTPS POST
**Authentication:** `Authorization: Bearer <api_key>` header
**MCP Endpoint:** `https://mcp.logicmem.io/mcp`

---

## Authentication

All requests must include a valid API key.

### Request Headers

```
Authorization: Bearer lm_your_api_key
Content-Type: application/json
```

### cURL Example

```bash
curl -X POST https://mcp.logicmem.io \
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

## JSON-RPC 2.0 Format

All requests follow the standard JSON-RPC 2.0 format:

### Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "<tool_name>",
    "arguments": { ... }
  }
}
```

### Success Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": { ... }
}
```

### Error Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Invalid Request",
    "data": { ... }
  }
}
```

---

## Tool Reference

### `logicframe_memory_log`

Store a new memory entry.

**Arguments:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | ✅ | Memory content. Be specific — include who, what, when, why. |
| `category` | string | ❌ | Category: general, preference, task, decision, contract, correction, interaction, complaint. Default: general |
| `importance` | integer | ❌ | Importance 1-10. Higher = stronger embedding. Default: 7 |
| `client_id` | string | ❌ | Tenant identifier. Default: default |
| `tags` | string[] | ❌ | Optional string tags |
| `source` | string | ❌ | Source: voice_call, chat, email, manual. Default: mcp |

**Example:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "logicframe_memory_log",
    "arguments": {
      "text": "Ed prefers Telegram for urgent messages. Email only for formal.",
      "category": "preference",
      "importance": 8,
      "client_id": "ed_creed"
    }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "entry_id": "mem_a1b2c3d4",
    "created_at": "2026-06-14T00:00:00Z"
  }
}
```

---

### `logicframe_memory_recall`

Search for relevant memories using natural language.

**Arguments:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | ✅ | Natural language search query |
| `limit` | integer | ❌ | Max results. Default: 5 |
| `client_id` | string | ❌ | Tenant identifier. Default: default |

**Example:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "logicframe_memory_recall",
    "arguments": {
      "query": "Ed communication preferences",
      "limit": 5
    }
  }
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "entries": [
      {
        "entry_id": "mem_a1b2c3d4",
        "text": "Ed prefers Telegram for urgent messages...",
        "category": "preference",
        "importance": 8,
        "score": 0.94,
        "created_at": "2026-06-13T10:30:00Z"
      }
    ],
    "total": 1
  }
}
```

---

### `logicframe_memory_session`

Get a full context briefing for the current session.

**Arguments:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_id` | string | ❌ | Tenant identifier. Default: default |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "relationship_trend": "improving",
    "confidence": 87,
    "conversation_openers": [
      "Ask about the Q3 proposal deadline",
      "Check in on the web dashboard progress"
    ],
    "active_constraints": ["limited_budget", "solo_founder"],
    "critical_gaps": ["unknown_technical_stack", "unconfirmed_timeline"]
  }
}
```

---

### `logicframe_reason`

Multi-step reasoning that consults memory at each step.

**Arguments:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | ✅ | The question or problem to reason about |
| `context` | string | ❌ | Additional context to include |
| `mode` | string | ❌ | fast (2 steps), deep (5 steps), exhaustive (10 steps). Default: deep |
| `max_steps` | integer | ❌ | Override number of reasoning steps |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "answer": "Web dashboard should be prioritized first because...",
    "steps": [
      {
        "step": 1,
        "thought": "Ed is a solo founder with limited bandwidth...",
        "memory_consulted": "limited engineering bandwidth",
        "confidence": 0.82
      }
    ],
    "confidence": 78
  }
}
```

---

### `logicframe_verify`

Verify a claim against stored facts.

**Arguments:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claim` | string | ✅ | The statement to verify |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "verdict": "supported",
    "evidence": [
      {
        "entry_id": "mem_xyz789",
        "text": "Ed prefers Telegram for urgent messages...",
        "created_at": "2026-06-13T10:30:00Z"
      }
    ],
    "confidence": 0.91
  }
}
```

---

### `logicframe_reflect`

Self-critique: evaluate a draft answer against memory.

**Arguments:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `draft_answer` | string | ✅ | The proposed answer to evaluate |
| `question` | string | ✅ | The original user question |
| `memory_query` | string | ❌ | Query used to retrieve supporting memories |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "score": 74,
    "gaps": [
      "Doesn't account for the user's solo founder constraint",
      "No mention of the Friday deadline"
    ],
    "suggestions": [
      "Factor in the limited engineering bandwidth",
      "Reference the Q3 proposal deadline constraint"
    ],
    "verdict": "needs_revision"
  }
}
```

---

### `logicframe_audit_verify`

Verify the integrity of the audit chain.

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "valid": true,
    "chain_length": 4831,
    "last_hash": "a3f8b2c1...",
    "verified_at": "2026-06-14T00:00:00Z"
  }
}
```

---

### `logicframe_a2a_share`

Share a memory entry with another agent in real-time.

**Arguments:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `target_agent_id` | string | ✅ | Recipient agent's ID |
| `text` | string | ✅ | Memory content to share |
| `category` | string | ❌ | Category. Default: general |
| `importance` | integer | ❌ | Importance 1-10. Default: 7 |
| `is_private` | boolean | ❌ | If true, only target agent can see. Default: false |
| `tags` | string[] | ❌ | Optional tags |
| `client_id` | string | ❌ | Organization ID. Default: default |

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "share_id": "shr_abc123",
    "shared_at": "2026-06-14T00:00:00Z",
    "delivered": true
  }
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| `-32600` | Invalid Request — malformed JSON-RPC request |
| `-32601` | Method not found — unknown tool name |
| `-32602` | Invalid params — missing or invalid arguments |
| `-32700` | Parse error — invalid JSON |
| `-32001` | Authentication error — invalid or missing API key |
| `-32002` | Rate limit exceeded — back off and retry |
| `-32003` | Server error — LogicMem server error (5xx) |

---

## Rate Limits

| Tier | Requests/minute | Burst |
|------|----------------|-------|
| Free | 60 | 10 |
| Pro | 600 | 50 |
| Enterprise | Unlimited | — |

Rate limit headers are returned on every response:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1752512460
```
