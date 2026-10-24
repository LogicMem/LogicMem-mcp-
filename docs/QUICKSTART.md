# ⚡ LogicMem Quickstart — your first tamper-evident record

> **Goal:** a Python script that stores memories, searches them, and uses the
> reasoning engine, then an MCP client connected to LogicMem.

## Prerequisites

- Python 3.11 or later
- A LogicMem API key (`lm_...`). Keys are issued to pilot teams while self-serve sign-up is being rebuilt: [request a pilot](https://logicmem.io/design-partner/).

## Step 1 — Install

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install "logicmem[cli] @ git+https://github.com/LogicMem/LogicMem-mcp-.git"
```

> Install from GitHub as shown. The `logicmem` package on PyPI is an older 0.1.1 build.

## Step 2 — Set your API key

```bash
export LOGICMEM_API_KEY="lm_your_api_key_here"
```

The script below reads the key from this environment variable. Never commit the key to git.

## Step 3 — Your first script

Create `quickstart.py`:

```python
import os
from logicmem import LogicMem

memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])
CLIENT = "quickstart-demo"

# ── Store a preference ──────────────────────────────────────
memory.log(
    text="The user prefers urgent messages via Telegram, not email.",
    category="preference",
    importance=8,
    client_id=CLIENT,
)
print("✅ Memory stored")

# ── Store a task ────────────────────────────────────────────
memory.log(
    text="Review Q3 proposal by Friday. "
         "Priority: cost breakdown first, then timeline.",
    category="task",
    importance=9,
    client_id=CLIENT,
)
print("✅ Task stored")

# ── Search memories ─────────────────────────────────────────
results = memory.recall(
    query="user communication preferences",
    limit=3,
    client_id=CLIENT,
)
print(f"\n🔍 Found {len(results)} memories:")
for r in results:
    print(f"  [{r.get('category', '?')}] {str(r.get('text', ''))[:80]}")

# ── Session briefing ────────────────────────────────────────
brief = memory.session(client_id=CLIENT)
print("\n📋 Session briefing:")
print(f"  {brief}")

# ── Reasoning ───────────────────────────────────────────────
answer = memory.reason(
    question="Should we prioritize mobile or web dashboard first?",
    context="The user is a solo founder with limited engineering bandwidth.",
    mode="fast",  # fast / deep / exhaustive
)
print(f"\n🧠 Reasoning result (confidence: {answer.get('confidence', '?')})")
print(f"  {str(answer.get('answer', 'No answer returned'))[:200]}")
```

## Step 4 — Run it

```bash
python quickstart.py
```

You should see the two ✅ lines, then the memories found, a session briefing and a reasoning answer. The exact text, counts and confidence numbers depend on your data and the server.

## Step 5 — Connect via MCP

**Hosted server (recommended).** In your MCP client's settings, add a streamable-HTTP server with URL `https://mcp.logicmem.io/mcp` and header `Authorization: Bearer lm_your_api_key`.

**Local stdio server.** For clients that launch a command (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "logicmem": {
      "command": "logicmem-server",
      "env": { "LOGICMEM_API_KEY": "lm_your_api_key" }
    }
  }
}
```

If the client cannot find `logicmem-server`, use the full path from `which logicmem-server`, or `"command": "python3", "args": ["-m", "logicmem.cli"]` with the same `env`.

## What's next?

- **[MCP-PROTOCOL.md](MCP-PROTOCOL.md)** — Hosted MCP server reference
- **[A2A-PROTOCOL.md](A2A-PROTOCOL.md)** — Agent-to-agent memory sharing guide
- **[EXAMPLES.md](EXAMPLES.md)** — More examples (voice, multi-agent, audit, etc.)
- **[SECURITY.md](SECURITY.md)** — Security model and best practices
