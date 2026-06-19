# 🧠 LogicMem — AI Agent Memory Infrastructure

> **Persistent memory, A2A sharing, reasoning engine, and immutable audit trail
> for AI agents via the Model Context Protocol.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blueviolet)](https://modelcontextprotocol.io)

---

## The Problem

AI agents are **stateless by design**. Every session starts from scratch:

```
Session 1                              Session 2
──────────                             ──────────
User: "I'm building a SaaS"     →     User: "How's my SaaS coming?"
Agent: "Tell me more..."              Agent: "I don't know anything
...                                   about your SaaS"
[Session ends]                        
                                      Agent forgot EVERYTHING.
```

This is fine for demos. It's catastrophic for production AI workflows.

## The Solution

LogicMem gives your AI agent **persistent memory** — connect any MCP client
and get:

- 🔍 **Persistent Memory** — Store and search memories across sessions
- 🧠 **Reasoning Engine** — Multi-step reasoning that consults memory
- 🔗 **A2A Memory Sharing** — Agents share context in real-time
- 📋 **Immutable Audit Trail** — Cryptographically verifiable history
- 🎙️ **Voice Memory** — Caller history for VAPI, Retell AI, Bland AI

---

## Open Core Model

This repo is the **LogicMem SDK** — the open-source client for connecting AI agents to the LogicMem memory fabric. The SDK is fully open (MIT licensed). The **reasoning engine and audit chain** run on LogicMem's private server.

| | **Open Source (This Repo)** | **LogicMem Pro / Enterprise** |
|---|---|---|
| **SDK / Client** | ✅ Fully open (MIT) | ✅ Included |
| **Persistent Memory** | ✅ Up to 1,000 ops/mo (free tier) | ✅ Unlimited |
| **A2A Memory Sharing** | ✅ Basic | ✅ Advanced governance + cross-org |
| **Reasoning Engine** | ✅ API call (server-powered) | ✅ Deep / Exhaustive modes |
| **Audit Trail** | ✅ API call (server-verified) | ✅ Tamper-evident ledger + CNSA 2.0 |
| **Voice Agent Memory** | ✅ | ✅ |
| **Deployment** | Cloud (logicmem.io) | Cloud, on-prem, or air-gap |
| **Support** | Community | Dedicated + SLA |

**Why this model?** The SDK gives developers the steering wheel. The LogicMem server is the engine. You get a great developer experience — and your AI gets production-grade memory infrastructure without building it yourself.

---

## Install

```bash
# macOS: add --break-system-packages (Homebrew Python requires it)
pip install --break-system-packages git+https://github.com/LogicMem/LogicMem-mcp-.git

# Linux/Ubuntu (no flag needed):
pip install git+https://github.com/LogicMem/LogicMem-mcp-.git
```

---

## Quick Start (< 5 minutes)

### 1. Get an API Key

Sign up at **[logicmem.io](https://logicmem.io)** → Settings → API Keys → Create Key.

Free tier: **1,000 memory operations/month**.

> ⚠️ **macOS users:** If you see a `PEP 668` error during install, rerun with `--break-system-packages` flag (see Install section above).

### 2. Use the Python SDK

```python
from logicmem import LogicMem

# Initialize the client
memory = LogicMem(api_key="lm_your_api_key")

# Store a memory
memory.log(
    text="User prefers urgent messages via Telegram, not email.",
    category="preference",
    importance=8,
)

# Search memories
results = memory.recall(query="user communication preferences")
print(results[0]["text"])
# → "User prefers urgent messages via Telegram, not email."

# Store a task with context
memory.log(
    text="Review Q3 proposal by Friday. Priority: cost breakdown first, then timeline.",
    category="task",
    importance=9,
)

# Session briefing — full context at start of session
brief = memory.session(client_id="ed_creed")
print(brief["confidence"])   # How confident is the agent about this user?
print(brief["relationship_trend"])  # improving / declining / stable
```

### 3. Reasoning Engine

```python
# Multi-step reasoning with memory at each step
answer = memory.reason(
    question="Should we prioritize the mobile app or web dashboard first?",
    context="User is a solo founder with limited engineering bandwidth.",
    mode="deep",  # fast / deep / exhaustive
)
print(answer["answer"])
print(answer["confidence"])

# Verify a claim against stored facts
verdict = memory.verify("User has a budget of $50k for this project")
print(verdict["verdict"])   # supported / contradicted / inconclusive
print(verdict["evidence"])  # supporting entries

# Self-critique before committing to an answer
review = memory.reflect(
    draft_answer="You should build the web dashboard first.",
    question="What should we prioritize first?",
    memory_query="user preferences priorities",
)
print(review["score"])      # 0-100
print(review["gaps"])       # weaknesses in the answer
```

### 4. Agent-to-Agent (A2A) Memory Sharing

```python
from logicmem.a2a import A2AClient

# Agent A: Share a memory with Agent B
a2a = A2AClient(api_key="lm_agent_a_key", agent_id="agent-researcher")

# Register this agent
a2a.register(name="Researcher Agent", agent_type="agent", client_id="team-alpha")

# Share context with another agent
a2a.share_memory(
    target_agent_id="agent-executor",
    memory={"text": "User needs Q3 report by Friday. High priority."},
    category="task",
    importance=9,
)

# Check for new shared memories from other agents
shared = a2a.sync()
for entry in shared:
    print(f"From {entry['from_agent_id']}: {entry['text']}")
```

### 5. Verify Audit Chain

```python
from logicmem.audit import AuditChain

audit = AuditChain(memory)  # pass LogicMem client

# Verify the audit chain has not been tampered with
result = audit.verify()
print(result["valid"])  # True if chain integrity is intact

# Log a correction (improves the model)
audit.log_correction(
    original="The user prefers email for urgent messages.",
    corrected="The user prefers Telegram for urgent messages, not email.",
    reason="User explicitly stated Telegram in call on 2026-06-10.",
)

# Check DPO training pipeline stats
stats = audit.dpo_stats()
print(f"Correction pairs ready: {stats['ready_count']}")
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
│                 mcp.logicmem.io                              │
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

The server accepts JSON-RPC 2.0 requests over HTTPS.

**Base URL:** `https://mcp.logicmem.io`

**Authentication:** `Authorization: Bearer <api_key>` header.

### Core Tools

| Tool | Description |
|------|-------------|
| `logicmem_memory_log` | Store a new memory with category, importance, tags |
| `logicmem_memory_recall` | Search memories with natural language |
| `logicmem_memory_session` | Get full context briefing for current session |
| `logicmem_reason` | Multi-step reasoning with memory consultation |
| `logicmem_verify` | Verify a claim against stored facts |
| `logicmem_reflect` | Self-critique — evaluate draft against memory |
| `logicmem_audit_verify` | Verify integrity of the audit chain |
| `logicmem_a2a_share` | Share memory with another agent |
| `logicmem_a2a_receive` | Receive shared memory from another agent |

See [MCP-PROTOCOL.md](MCP-PROTOCOL.md) for the full protocol reference.

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

---

## Security

- **Encryption:** AES-256-GCM at rest, TLS 1.3 in transit
- **Compliance:** CNSA 2.0 cryptography for defense/government workloads
- **Audit:** Every operation logged to immutable hash-linked chain
- **API Keys:** Per-agent keys with fine-grained permissions

See [SECURITY.md](SECURITY.md) for the full security model.

---

## Documentation

All documentation lives in the [`docs/`](docs/) folder right here in this repo:

| Doc | What You Need |
|-----|--------------|
| **[📖 Start Here](docs/QUICKSTART.md)** | Install + first 10 lines of code |
| **[🔌 MCP Protocol](docs/MCP-PROTOCOL.md)** | Full protocol reference |
| **[🔗 A2A Sharing](docs/A2A-PROTOCOL.md)** | Agent-to-agent memory |
| **[🔒 Security](docs/SECURITY.md)** | Encryption, CNSA 2.0, audit |
| **[💻 Code Examples](docs/EXAMPLES.md)** | All examples in one place |

## Links

- 🌐 [logicmem.io](https://logicmem.io) — Product
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
