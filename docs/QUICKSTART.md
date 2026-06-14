# ⚡ LogicMem Quickstart — 5 Minutes to Persistent Memory

> **Goal:** By the end of this guide, you'll have a Python script that stores
> memories, searches them, and uses the reasoning engine — in under 5 minutes.**

## Prerequisites

- Python 3.11 or later
- A LogicMem API key ([get one free at logicmem.io](https://logicmem.io))

## Step 1 — Install

```bash
pip install logicmem
```

## Step 2 — Set Your API Key

```bash
export LOGICMEM_API_KEY="lm_your_api_key_here"
```

Or create a `.env` file:

```
LOGICMEM_API_KEY=lm_your_api_key_here
```

## Step 3 — Your First Memory Script

Create `quickstart.py`:

```python
import os
from logicmem import LogicMem

# Initialize with your API key
memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

# ── Store a preference ──────────────────────────────────────
memory.log(
    text="Ed prefers urgent messages via Telegram, not email.",
    category="preference",
    importance=8,
)
print("✅ Memory stored")

# ── Store a task ────────────────────────────────────────────
memory.log(
    text="Review Q3 proposal by Friday. "
         "Priority: cost breakdown first, then timeline.",
    category="task",
    importance=9,
)
print("✅ Task stored")

# ── Search memories ─────────────────────────────────────────
results = memory.recall(
    query="user communication preferences",
    limit=3,
)
print(f"\n🔍 Found {len(results)} memories:")
for r in results:
    print(f"  [{r.get('category','?')}] {r['text'][:80]}")

# ── Session briefing ────────────────────────────────────────
brief = memory.session(client_id="ed_creed")
print(f"\n📋 Session briefing:")
print(f"  Confidence: {brief.get('confidence', '?')}")
print(f"  Relationship trend: {brief.get('relationship_trend', '?')}")
print(f"  Active constraints: {brief.get('active_constraints', [])}")

# ── Reasoning ───────────────────────────────────────────────
answer = memory.reason(
    question="Should we prioritize mobile or web dashboard first?",
    context="Ed is a solo founder with limited engineering bandwidth.",
    mode="fast",  # fast / deep / exhaustive
)
print(f"\n🧠 Reasoning result (confidence: {answer.get('confidence', '?')})")
print(f"  {answer.get('answer', 'No answer returned')[:200]}")
```

## Step 4 — Run It

```bash
python quickstart.py
```

Expected output:

```
✅ Memory stored
✅ Task stored

🔍 Found 1 memories:
  [preference] Ed prefers urgent messages via Telegram, not email.

📋 Session briefing:
  Confidence: 87
  Relationship trend: improving
  Active constraints: ['limited_budget', 'solo_founder']

🧠 Reasoning result (confidence: 82)
  Web dashboard should be prioritized first because...
```

## Step 5 — Connect via MCP

Add LogicMem to your MCP client config (Claude Desktop, Cursor, Windsurf, etc.):

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

## What's Next?

- **[MCP-PROTOCOL.md](MCP-PROTOCOL.md)** — Full protocol reference for MCP clients
- **[A2A.md](A2A.md)** — Agent-to-agent memory sharing guide
- **[EXAMPLES.md](EXAMPLES.md)** — All examples (voice, multi-agent, audit, etc.)
- **[SECURITY.md](SECURITY.md)** — Security model and best practices
