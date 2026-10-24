# Documentation Index

Welcome to the LogicMem documentation. Everything lives right here in this repo.

## 📚 All documentation

| Document | What it covers |
|----------|---------------|
| **[QUICKSTART.md](QUICKSTART.md)** | Install, get an API key, first script — start here |
| **[MCP-PROTOCOL.md](MCP-PROTOCOL.md)** | Hosted MCP server and local bridge: tools and parameters |
| **[A2A-PROTOCOL.md](A2A-PROTOCOL.md)** | Agent-to-agent memory sharing |
| **[SECURITY.md](SECURITY.md)** | Transport, authentication, audit chain |
| **[EXAMPLES.md](EXAMPLES.md)** | Code examples — log, recall, session, reason, A2A, audit, errors |
| **[EMBEDDING-FALLBACK.md](EMBEDDING-FALLBACK.md)** | How the server handles embedding-provider outages |
| **[CONTRACT-TESTS.md](CONTRACT-TESTS.md)** | MCP contract test harness (`tests/contract_tests.py`) |
| **[MONITORING.md](MONITORING.md)** | Synthetic monitor script (`monitoring/synthetic_monitor.py`) |
| **[CONTRIBUTING.md](../CONTRIBUTING.md)** | How to contribute to this repo |

## 🚦 Start here

**New to LogicMem?** → Read [QUICKSTART.md](QUICKSTART.md) first.

**Want more code?** → [EXAMPLES.md](EXAMPLES.md). Framework integrations (LangChain, CrewAI, etc.) are not written yet; contributions welcome.

**Building with MCP directly?** → [MCP-PROTOCOL.md](MCP-PROTOCOL.md).

## 📁 Repo structure

```
LogicMem-mcp-/
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── docs/                 ← this folder
├── src/logicmem/         ← the Python SDK
│   └── cli/              ← logicmem-server (local MCP bridge)
├── tests/contract_tests.py
├── monitoring/synthetic_monitor.py
└── webhooks/dispatcher.py
```
