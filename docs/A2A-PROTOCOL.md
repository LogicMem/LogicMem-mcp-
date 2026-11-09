# A2A — LogicMem agent-to-agent sharing

> **How agents share memory through LogicMem's own API.**

LogicMem A2A sharing is LogicMem's REST API (`/memory/agent/register`, `/memory/shared/write`, `/memory/shared/updates`, and the related calls below). It is not an implementation of the [Agent2Agent (A2A) protocol](https://a2a-protocol.org/). Checked 2026-11-09: that site titles itself the Agent2Agent protocol. This SDK does not send agent cards or that protocol's task methods.

---

## What this SDK does, and what a hosted listener is

Agents that share a workspace can write to a shared pool and read what was written.

**This Python SDK only checks in.** `receive_memory()` and `sync()` call `GET /memory/shared/updates`. They do not open a stream and they do not receive webhooks. Nothing in this package pushes a share to another process.

**A hosted listener is a different path, and it was not re-tested on current production in the audit that edited this page.** Ed Creed reports that his configured Leonard, Linus, and Claude listeners, kept on, communicate and respond to tasks. That is one operator's setup. It is not a latency number and not a statement about every MCP client. An Oct 27, 2026 server snapshot, which is not in this repository, described MCP SSE delivery (`notifications/message`, and raw SSE paths) with **no replay**, and signed webhooks that retry and can be delivered more than once or dead-lettered. Historical samples from Oct 24–25, 2026 were not repeated here, and this page does not publish them as a speed claim.

A share being stored, a listener being notified, and the other agent acting are three events. A notification does not prove receipt or execution. There is no delivery guarantee in this document.

`webhooks/dispatcher.py` in this repo is a local file queue: 5 attempts, then a dead-letter file, and a reconciler that can deliver the same item again because it does not rewrite that file. The Oct 27 snapshot's hosted outbox was described with different limits (12 attempts or 7 days). These are not documented as the same component. Neither was run against production for this audit. Do not point customer traffic at the dispatcher's localhost paths.

### Catch-up limit

`sync(limit=50)` is the default. There is no offset parameter in this client. The method returns a list. If the server also sent `total_new`, this client drops it. An Oct 27, 2026 snapshot of hosted catch-up returned newest first, sliced to `limit` (default 50), included `total_new`, and had no cursor. Live parity is unknown.

If you keep a checkpoint: compare a `total_new` you can see with the number of entries you actually kept. When the server returned only a slice, **do not advance the checkpoint** to the newest timestamp in that slice. Raising `limit` is the only knob this client has. It does not page. Record an incomplete catch-up when the slice is shorter than the backlog you still need. This client cannot see `total_new` unless you call the HTTP API yourself and read the raw JSON.

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

Each agent has a label you declare and send as `agent_id`. The SDK does not authenticate it. In an Oct 27, 2026 server snapshot, agent ids were self-declared inside a workspace, and a target id routed a share rather than proving other agents in that workspace cannot read it. Whether that is still true on the deployed server was not re-tested. Cross-workspace access in that snapshot was described as key-bound. A Nov 9, 2026 check returned HTTP 403 for a foreign `client_id` on that check's route. That is dated counterevidence against a general cross-tenant bypass. It is not a full policy, and this audit did not repeat the call. Do not treat a declared agent id or `is_private` as a privacy boundary. `is_private` is forwarded on the write. This client does not enforce it.

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

# The executor sees it on its next sync() check-in, if this SDK is what it runs.
# A hosted listener, if one is configured, is a separate path. See above.
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
- `is_private` is sent to the server as a flag. This SDK does not prove who can read the entry. A declared `agent_id` routes the share. It is not a separate credential.

### Rate limits

A2A calls count against the same rate limit as other memory calls. Keep heartbeats infrequent (for example every 30–60 seconds).

---

## MCP integration

**Local bridge (`logicmem-server`):** `logicmem_a2a_register`, `logicmem_a2a_heartbeat`, `logicmem_a2a_list_agents`, `logicmem_a2a_write_shared`, `logicmem_a2a_sync`.

**Hosted server (`mcp.logicmem.io/mcp`):** `logicframe_memory_share` (share an existing memory with another agent) and `logicframe_memory_sync_check` (memories other agents stored since a timestamp).
