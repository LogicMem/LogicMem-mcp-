# LogicMem: prove what your AI did

Tamper-evident, hash-chained records of what your AI agents did and relied on, so you can show an auditor whether anything was changed. This is the open-source SDK and MCP connector. Records are kept and verified on the LogicMem server, in our cloud.

> Observability tells you what broke. LogicMem shows what happened.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blueviolet)](https://modelcontextprotocol.io)

---

## The problem

Six months from now, an auditor asks what your AI agent did and what it relied on. Ordinary logs can be edited, and nobody can prove they weren't.

## What LogicMem gives you

A tamper-evident, hash-chained record of your agents' key memory operations, so you can show whether anything was changed. Shared memory across vendors comes with it.

---

## What is in this repo

- **Python SDK** (`logicmem`, MIT licensed): a client for the LogicMem REST API at `https://api.logicmem.io`.
- **Local MCP server** (`logicmem-server`): a stdio bridge that serves `logicmem_*` tools to MCP clients.
- **Docs** for the hosted MCP server at `https://mcp.logicmem.io/mcp`, which serves `logicframe_*` tools.

The LogicMem server itself (storage, reasoning engine, audit chain) is not in this repo; it runs in LogicMem's cloud.

**Access:** API keys are issued to pilot teams. Pilots run 30 days, from $500/mo: [logicmem.io/design-partner](https://logicmem.io/design-partner/).

---

## Install

Use a virtual environment (works on macOS, Linux and Windows):

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# SDK only
pip install git+https://github.com/LogicMem/LogicMem-mcp-.git

# SDK + local MCP server (logicmem-server)
pip install "logicmem[cli] @ git+https://github.com/LogicMem/LogicMem-mcp-.git"
```

> Install from GitHub as shown. The `logicmem` package on PyPI is an older 0.1.1 build with out-of-date links.

---

## Quick start

### 1. Get an API key

Keys start with `lm_`. They are issued to pilot teams while self-serve sign-up is being rebuilt: request one at **[logicmem.io/design-partner](https://logicmem.io/design-partner/)**. Treat the key like a password.

Requests over your rate limit return HTTP 429 (`RateLimitError` in the SDK).

### 2. Use the Python SDK

```python
import os
from logicmem import LogicMem

memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

# Store a memory
memory.log(
    text="User prefers urgent messages via Telegram, not email.",
    category="preference",
    importance=8,
)

# Search memories
results = memory.recall(query="user communication preferences")
for r in results:
    print(r.get("text"))

# Session briefing (a context summary from the server)
brief = memory.session(client_id="default")
print(brief)
```

### 3. Reasoning engine

```python
answer = memory.reason(
    question="Should we prioritize the mobile app or web dashboard first?",
    context="User is a solo founder with limited engineering bandwidth.",
    mode="deep",  # fast / deep / exhaustive
)
print(answer.get("answer"))
print(answer.get("confidence"))
```

`verify()`, `reflect()` and `intelligence()` exist on the client but always raise `NotImplementedError`: those features run only as MCP tools (`logicframe_verify`, `logicframe_reflect`, `logicframe_intelligence`) on the hosted server. Call them from an MCP client (see below).

### 4. Agent-to-agent (A2A) memory sharing

```python
import os
from logicmem.a2a import A2AClient

a2a = A2AClient(api_key=os.environ["LOGICMEM_API_KEY"], agent_id="agent-researcher")

# Register this agent
a2a.register(name="Researcher Agent", agent_type="agent", client_id="team-alpha")

# Share context with another agent
a2a.share_memory(
    target_agent_id="agent-executor",
    memory={"text": "User needs Q3 report by Friday. High priority."},
    category="task",
    importance=9,
    client_id="team-alpha",
)

# In the other agent: fetch memories shared by other agents
executor = A2AClient(api_key=os.environ["LOGICMEM_API_KEY"], agent_id="agent-executor")
for entry in executor.sync(client_id="team-alpha"):
    print(entry.get("text"))
```

### 5. Verify the audit chain

```python
from logicmem.audit import AuditChain

audit = AuditChain(memory)  # pass a LogicMem client

# Ask the server to re-check the hash chain
print(audit.verify())

# Log a correction (stored on the server and queued for its training pipeline)
audit.log_correction(
    original="The user prefers email for urgent messages.",
    corrected="The user prefers Telegram for urgent messages, not email.",
    reason="User explicitly stated Telegram in a call.",
)
print(audit.dpo_stats())
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Your AI Agent                           │
│              (Claude, GPT, any MCP client)                   │
└──────────────────────────────────────────────────────────────┘
          │ MCP (hosted or local stdio)        │ Python SDK
          ▼                                    ▼
┌───────────────────────────┐      ┌───────────────────────────┐
│ Hosted MCP server         │      │ REST API                  │
│ mcp.logicmem.io/mcp       │      │ api.logicmem.io           │
│ logicframe_* tools        │      │ (also used by             │
│                           │      │  logicmem-server)         │
└───────────────────────────┘      └───────────────────────────┘
          └──────────────► LogicMem server ◄──────────┘
                 memory · reasoning · A2A · audit chain
```

---

## Connect an MCP client

### Option A: hosted MCP server URL

Add LogicMem as a **streamable-http** MCP server. Example for OpenClaw (`~/.openclaw/openclaw.json`):

```json
{
  "mcp": {
    "servers": {
      "logicmem": {
        "transport": "streamable-http",
        "url": "https://mcp.logicmem.io/mcp",
        "headers": {
          "Authorization": "Bearer lm_YOUR_API_KEY"
        }
      }
    }
  }
}
```

Other clients (Claude Code, Cursor and similar) use the same URL and header in their own MCP settings.

### Option B: local stdio server

If your client works better with a local command, install the CLI extra:

```bash
pip install "logicmem[cli] @ git+https://github.com/LogicMem/LogicMem-mcp-.git"
logicmem-server --help
```

Then point your client at the `logicmem-server` command:

```json
{
  "mcp": {
    "servers": {
      "logicmem": {
        "command": "logicmem-server",
        "env": {
          "LOGICMEM_API_KEY": "lm_YOUR_API_KEY",
          "LOGICMEM_CLIENT_ID": "your-client-id"
        }
      }
    }
  }
}
```

### Check your setup

```bash
openclaw mcp list   # LogicMem should be listed
```

Then ask your agent to store a note with `logicframe_memory_log` (hosted) or `logicmem_memory_log` (local) and recall it.

### Environment variables (for `logicmem-server`)

The Python SDK does not read these; pass `api_key` and `base_url` to `LogicMem(...)` instead.

| Variable | Default | Description |
|----------|---------|-------------|
| `LOGICMEM_API_KEY` | — | Your API key (`lm_...`), issued to [pilot teams](https://logicmem.io/design-partner/) |
| `LOGICMEM_SERVER_URL` | `https://api.logicmem.io` | Override the LogicMem REST API URL |
| `LOGICMEM_CLIENT_ID` | `default` | Default client_id for memory operations |
| `LOGICMEM_TIMEOUT` | `30` | HTTP request timeout in seconds |

---

## MCP reference

**Hosted MCP endpoint:** `https://mcp.logicmem.io/mcp` (JSON-RPC over HTTPS POST)
**REST API base URL:** `https://api.logicmem.io`

**Authentication:** `Authorization: Bearer <api_key>`. `initialize` and `tools/list` are public; `tools/call` requires a key.

> **Tool name prefix:** the hosted server serves `logicframe_*` tool names
> (e.g. `logicframe_memory_log`, `logicframe_memory_recall`). The local pip
> server (`logicmem-server`) serves `logicmem_*` tool names. Both use the same backend.

### Commonly used hosted tools

The hosted server lists many more tools; run `tools/list` to see them all.

| Tool | Description |
|------|-------------|
| `logicframe_memory_log` | Store a new memory with category, importance, tags |
| `logicframe_memory_recall` | Search memories with natural language |
| `logicframe_memory_context` | Get context about a client, project, or person |
| `logicframe_reason` | Multi-step reasoning that consults memory |
| `logicframe_verify` | Check a claim against stored memories |
| `logicframe_reflect` | Critique a draft answer against memory |
| `logicframe_intelligence` | Look for patterns and overdue items |
| `logicframe_audit_verify` | Verify integrity of the audit chain |
| `logicframe_correction_log` | Log a correction (queued for DPO training) |
| `logicframe_conversations_store` | Store conversation state for auto-resume |
| `logicframe_conversations_resume` | Retrieve stored conversation state |

See [MCP-PROTOCOL.md](docs/MCP-PROTOCOL.md) for details.

---

## Security

- **In transit:** HTTPS (the hosted endpoints negotiate TLS 1.3)
- **Audit:** key memory operations made through the API and MCP connector (for example log, recall and correct) are logged to a tamper-evident, hash-linked chain that you can re-check with `logicframe_audit_verify` or `AuditChain.verify()`. Not every endpoint writes an audit entry yet.
- **API keys:** sent as a Bearer token; keep them out of code and git

See [SECURITY.md](docs/SECURITY.md).

---

## Documentation

| Doc | What you need |
|-----|--------------|
| **[Start here](docs/QUICKSTART.md)** | Install + first script |
| **[MCP protocol](docs/MCP-PROTOCOL.md)** | Hosted MCP server reference |
| **[A2A sharing](docs/A2A-PROTOCOL.md)** | Agent-to-agent memory |
| **[Security](docs/SECURITY.md)** | Transport, auth, audit chain |
| **[Code examples](docs/EXAMPLES.md)** | All examples in one place |
| **[Embedding fallback](docs/EMBEDDING-FALLBACK.md)** | How the server handles embedding-provider outages |
| **[Doc index](docs/INDEX.md)** | Everything else |

## Links

- 🌐 [logicmem.io](https://logicmem.io) — Product
- 🚀 [Quickstart](https://logicmem.io/quickstart/) — Connect your agents and verify the audit chain
- 🧪 [Pilots](https://logicmem.io/design-partner/) — 30-day pilots from $500/mo
- 📜 [EU AI Act Article 12](https://logicmem.io/eu-ai-act-article-12/) — LogicMem is designed to support record-keeping such as EU AI Act Article 12 (not legal advice)
- 📧 [support@logicmem.io](mailto:support@logicmem.io)

---

## Contributing

Contributions welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md). We especially welcome MCP client examples, framework integrations (LangChain, CrewAI, etc.), A2A extensions, and SDKs in other languages.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT License. See [LICENSE](LICENSE).
