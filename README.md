# 🧠 LogicMem MCP — Model Context Protocol for AI Memory

> **The MCP-native memory layer for AI agents. Connect any MCP client and never make your agent forget again.**

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blueviolet)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-yellow)](https://pypi.org/project/logicmem/)

**Stars this repo → signal to the AI community that LogicMem is the memory standard for MCP agents.**

---

## The Problem

AI agents are **stateless by design**. Every session starts from scratch:

```
Session 1                           Session 2
──────────                          ──────────
User: "I'm building a SaaS"    →   User: "How's my SaaS coming?"
Agent: "Tell me more..."           Agent: "I don't know anything
...                                about your SaaS"
[Session ends]                     
                                    Agent forgot EVERYTHING.
```

This is fine for demos. It's catastrophic for production AI workflows.

## The Solution: LogicMem MCP

LogicMem gives your AI agent **persistent memory** via the Model Context Protocol — connect any MCP client and get:

- 🔍 **Persistent Memory** — Store and search across sessions
- 🧠 **Reasoning Engine** — Multi-step reasoning that consults memory
- 🔗 **A2A Memory Sharing** — Agents share context in real-time
- 📋 **Immutable Audit Trail** — Cryptographically verifiable history
- 🔐 **CNSA 2.0 Cryptography** — Military-grade for defense workloads
- 🎙️ **Voice Memory** — Caller history for VAPI, Retell AI, Bland AI

---

## Quickstart (< 5 minutes)

### 1. Get an API Key

Sign up at **[logicmem.io](https://logicmem.io)** → Settings → API Keys → Create Key.

Free tier: **1,000 memory operations/month**.

### 2. Install

```bash
pip install logicmem
```

### 3. Connect via MCP

Add to your MCP client config (Claude Desktop, Cursor, Windsurf, etc.):

```json
{
  "mcpServers": {
    "logicmem": {
      "command": "python3",
      "args": ["-m", "logicmem.mcp", "--key", "lm_your_api_key"]
    }
  }
}
```

### 4. Or Use the Python SDK Directly

```python
from logicmem import LogicMem

memory = LogicMem(api_key="lm_your_api_key")

# Store a memory
memory.log(
    text="User prefers urgent messages via Telegram, not email.",
    category="preference",
    importance=8
)

# Search memories
results = memory.recall(query="user communication preferences")
print(results[0]["text"])
# → "User prefers urgent messages via Telegram, not email."

# Store a task with context
memory.log(
    text="Review the Q3 proposal by Friday. "
         "Priority: cost breakdown first, then timeline.",
    category="task",
    importance=9
)

# Check what your agent knows
context = memory.recall("Q3 proposal deadline")
# → Knows the deadline, knows the priorities
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Your AI Agent                           │
│              (Claude, GPT, Any MCP Client)                    │
└──────────────────────────────────────────────────────────────┘
                             │ MCP
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                   LogicMem MCP Server                        │
│                 mcp.logicmem.io:8423                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐ │
│  │   Memory    │ │  Reasoning │ │    A2A     │ │ Audit  │ │
│  │   Tools     │ │   Engine   │ │   Relay    │ │ Chain  │ │
│  └────────────┘ └────────────┘ └────────────┘ └────────┘ │
└──────────────────────────────────────────────────────────────┘
                             │
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌────────────┐   ┌────────────┐   ┌────────────┐
    │  Memory    │   │   Memory   │   │   Audit   │
    │  Storage   │   │   Index    │   │   Ledger  │
    │(Supabase)  │   │ (Qdrant)   │   │(Hash Chain)│
    └────────────┘   └────────────┘   └────────────┘
```

---

## MCP Protocol Reference

### Server Endpoint

```
https://mcp.logicmem.io
Protocol: JSON-RPC 2.0 over HTTPS POST
Authentication: Bearer token
```

### Core MCP Tools

| Tool | Description |
|------|-------------|
| `logicmem_memory_log` | Store a new memory with category, importance, tags |
| `logicmem_memory_recall` | Search memories with natural language |
| `logicmem_memory_session` | Get full context briefing for current session |
| `logicmem_reason` | Multi-step reasoning with memory consultation |
| `logicmem_verify` | Verify a claim against stored facts |
| `logicmem_reflect` | Self-critique — evaluate a draft against memory |
| `logicmem_audit_verify` | Verify integrity of the audit chain |
| `logicmem_a2a_share` | Share memory with another agent in real-time |
| `logicmem_a2a_receive` | Receive shared memory from another agent |

### Authentication

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

### Example: Log a Memory (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "logicmem_memory_log",
    "arguments": {
      "text": "Ed prefers Telegram for urgent messages. Email only for formal.",
      "category": "preference",
      "importance": 8,
      "client_id": "ed_creed"
    }
  }
}
```

### Example: Recall Memories (JSON-RPC)

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "logicmem_memory_recall",
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
    "entries": [{
      "entry_id": "mem_a1b2c3d4",
      "text": "Ed prefers Telegram for urgent messages...",
      "category": "preference",
      "importance": 8,
      "score": 0.94,
      "created_at": "2026-06-13T10:30:00Z"
    }],
    "total": 1
  }
}
```

---

## A2A: Real-Time Memory Sharing Between Agents

The Agent-to-Agent (A2A) protocol lets AI agents share memory in real-time.

```python
from logicmem.a2a import A2AClient

# Agent A: Share a memory with Agent B
client = A2AClient(api_key="lm_agent_a_key", agent_id="agent-a")

await client.share_memory(
    target_agent_id="agent-b",
    memory={
        "text": "User needs the Q3 report by Friday. Priority: high.",
        "category": "task",
        "importance": 9
    }
)

# Agent B receives it and has full context from Agent A's session
```

**A2A Use Cases:**
- **Multi-agent orchestration:** One agent researches, another executes — they share context
- **Handoff:** Agent A handles intake, passes context to Agent B for execution
- **Supervision:** Supervisor agent monitors subordinate agents' memories
- **Federated teams:** Multiple agents working on the same user share a memory pool

---

## Comparison

| Feature | LogicMem | Mem0 | Letta | Zep |
|---------|:--------:|:----:|:-----:|:---:|
| **MCP-native** | ✅ Full | ⚠️ | ✅ | ⚠️ |
| **Reasoning engine** | ✅ | ❌ | ⚠️ | ❌ |
| **A2A memory sharing** | ✅ | ❌ | ⚠️ | ❌ |
| **Immutable audit trail** | ✅ | ❌ | ❌ | ⚠️ |
| **DPO training pipeline** | ✅ | ❌ | ❌ | ❌ |
| **Voice agent memory** | ✅ | ❌ | ⚠️ | ❌ |
| **Federated memory** | ✅ | ❌ | ❌ | ❌ |
| **CNSA 2.0** | ✅ | ❌ | ❌ | ❌ |

---

## Security

- **Encryption:** AES-256-GCM at rest, TLS 1.3 in transit
- **Compliance:** CNSA 2.0 cryptography for defense/government workloads
- **Audit:** Every operation logged to immutable hash-linked chain
- **API Keys:** Per-agent keys with fine-grained permissions

---

## Links

- 🌐 [logicmem.io](https://logicmem.io) — Product
- 📖 [docs.logicmem.io](https://docs.logicmem.io) — Full documentation
- 💬 [Discord](https://discord.gg/logicmem) — Community
- 📧 [support@logicmem.io](mailto:support@logicmem.io)

---

## Contributing

Contributions welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md).

We especially welcome:
- MCP client examples (more clients → more adoption)
- Framework integrations (LangChain, AutoGPT, CrewAI, etc.)
- A2A protocol extensions
- SDK implementations in other languages

---

## License

MIT License. See [LICENSE](LICENSE).
