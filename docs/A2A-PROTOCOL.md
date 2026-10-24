# A2A — Agent-to-Agent Memory Sharing

> **How AI agents share memory through LogicMem.**

---

## What is A2A?

A2A (agent-to-agent) sharing lets agents that work for the same user or
project write memories to a shared pool and read what other agents wrote,
instead of each agent keeping its own isolated memory. Agents fetch shared
memories by polling (`receive_memory()` / `sync()`); nothing is pushed to them.

```
┌──────────────────┐         ┌──────────────────┐
│  Agent A         │         │  Agent B         │
│  (Researcher)    │         │  (Executor)      │
│  share_memory() ─┼──┐   ┌──┼─► sync()         │
└──────────────────┘  │   │  └──────────────────┘
                      ▼   │
                 LogicMem shared pool
```

---

## Key concepts

### Agent ID

Each agent has an identifier, unique within a `client_id`:

```python
import os
from logicmem.a2a import A2AClient

a2a = A2AClient(
    api_key=os.environ["LOGICMEM_API_KEY"],
    agent_id="researcher-claude",
)
```

### Client ID

The `client_id` is an organization or project namespace. You pass it to
each call (it is not a constructor argument):

```python
a2a_a = A2AClient(api_key=key_a, agent_id="agent-a")
a2a_b = A2AClient(api_key=key_b, agent_id="agent-b")

a2a_a.register(name="Agent A", client_id="team-alpha")
a2a_b.register(name="Agent B", client_id="team-alpha")
```

### Registry

Agents **register** before they share. Registration is one call and can be done on startup.

---

## Python SDK usage

### 1. Register your agent

```python
result = a2a.register(
    name="Claude Researcher Agent",
    agent_type="agent",
    client_id="project-x",
)
print(result)
```

### 2. List other agents

```python
agents = a2a.list_agents(client_id="project-x")
for agent in agents:
    print(agent.get("agent_id"), agent.get("status"))
```

### 3. Share a memory

```python
result = a2a.share_memory(
    target_agent_id="claude-executor",
    memory={
        "text": "User needs Q3 report by Friday. High priority.",
        "category": "task",
    },
    importance=9,
    client_id="project-x",
)
print(result)
```

### 4. Receive shared memories

```python
shared = a2a.receive_memory(client_id="project-x", limit=10)
for entry in shared:
    print(entry.get("text"))
```

### 5. Sync (skip your own shares)

```python
new_memories = a2a.sync(since_timestamp="2026-06-13T10:00:00Z", client_id="project-x")
for entry in new_memories:
    print(entry.get("text"))
```

### 6. Write to the shared pool

```python
a2a.write_shared(
    text="User is a solo founder. Keep suggestions practical and few.",
    category="context",   # general / a2a_discovery / decision / context
    importance=8,
    is_private=False,
    client_id="project-x",
)
```

### 7. Heartbeat

```python
a2a.heartbeat(status="online", client_id="project-x")  # online / busy / away
```

---

## Use cases

### Researcher → executor handoff

```python
researcher_a2a.share_memory(
    target_agent_id="agent-executor",
    memory={
        "text": "Competitor analysis complete. "
                "3 main players: A (enterprise), B (SMB), C (startup). "
                "User should focus on B market segment.",
        "category": "decision",
    },
    client_id="project-x",
)

# The executor picks it up on its next poll
context = executor_a2a.sync(client_id="project-x")
```

### Federated teams

Several agents working for the same user write to one shared pool:

```python
for agent_id in ["agent-sales", "agent-support", "agent-success"]:
    a2a = A2AClient(api_key=api_key, agent_id=agent_id)
    a2a.write_shared(
        text=f"User engaged with {agent_id} today.",
        category="general",
        importance=5,
        client_id="user-123",
    )
```

---

## REST endpoints used by the SDK

| Method | Endpoint | SDK method |
|--------|----------|------------|
| POST | `/memory/agent/register` | `register()` |
| GET | `/memory/org/agents` | `list_agents()` |
| POST | `/memory/agent/heartbeat` (fields in query string) | `heartbeat()` |
| POST | `/memory/shared/write` | `share_memory()`, `write_shared()` |
| GET | `/memory/shared/updates` | `receive_memory()`, `sync()` |

All on `https://api.logicmem.io`, with `Authorization: Bearer <api_key>`.

### Scoping

- Each agent authenticates with an API key.
- Shared memories are written with a `client_id`; read them back with the same `client_id`.
- `is_private` is sent to the server as the entry's private flag.

### Rate limits

A2A calls count against the same rate limit as other memory calls. Keep heartbeats infrequent (for example every 30–60 seconds).

---

## MCP integration

**Local bridge (`logicmem-server`):** `logicmem_a2a_register`, `logicmem_a2a_heartbeat`, `logicmem_a2a_list_agents`, `logicmem_a2a_write_shared`, `logicmem_a2a_sync`.

**Hosted server (`mcp.logicmem.io/mcp`):** `logicframe_memory_share` (share an existing memory with another agent) and `logicframe_memory_sync_check` (memories other agents stored since a timestamp).
