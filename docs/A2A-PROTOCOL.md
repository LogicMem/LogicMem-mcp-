# A2A — Agent-to-Agent Memory Sharing

> **How AI agents share memory in real-time using the LogicMem A2A protocol.**

---

## What is A2A?

A2A (Agent-to-Agent) is a protocol for **real-time memory sharing** between
AI agents. Instead of each agent maintaining its own isolated memory,
agents can share context instantly with other agents working on the same
user or project.

```
┌──────────────────┐         ┌──────────────────┐
│  Agent A         │         │  Agent B         │
│  (Researcher)    │   A2A   │  (Executor)      │
│                  │◄───────►│                  │
│  💾 Memory       │  share  │  💾 Memory       │
│  - Q3 data       │         │  - Q3 data ✅     │
│  - User context  │         │  - Handoff notes │
└──────────────────┘         └──────────────────┘
        │                              │
        └─────────── A2A Relay ◄───────┘
                    (LogicMem)
```

---

## Key Concepts

### Agent ID

Each agent has a unique identifier within a `client_id`:

```python
from logicmem.a2a import A2AClient

a2a = A2AClient(
    api_key="lm_your_api_key",
    agent_id="researcher-claude",  # unique within the client_id
)
```

### Client ID

The `client_id` is an organization or project namespace. Agents in the same
`client_id` can discover and communicate with each other.

```python
# All agents working on the same team
a2a_a = A2AClient(api_key="lm_key_a", agent_id="agent-a", client_id="team-alpha")
a2a_b = A2AClient(api_key="lm_key_b", agent_id="agent-b", client_id="team-alpha")
```

### Registry

Agents must **register** with the A2A registry before they can send or
receive messages. Registration is lightweight and can be done on startup.

---

## Python SDK Usage

### 1. Register Your Agent

```python
from logicmem.a2a import A2AClient

a2a = A2AClient(api_key="lm_your_api_key", agent_id="claude-researcher")

# Register in the A2A registry
result = a2a.register(
    name="Claude Researcher Agent",
    agent_type="agent",
    client_id="project-x",
)
print(f"Registered at {result['endpoint']}")
```

### 2. List Other Agents

```python
# See who else is online in your client_id
agents = a2a.list_agents(client_id="project-x")
for agent in agents:
    print(f"  {agent['agent_id']} — {agent['status']}")
```

### 3. Share a Memory

```python
# Share a memory with another agent
result = a2a.share_memory(
    target_agent_id="claude-executor",
    memory={
        "text": "User needs Q3 report by Friday. High priority.",
        "category": "task",
    },
    importance=9,
)
print(f"Shared: {result['share_id']}")
```

### 4. Receive Shared Memories

```python
# Poll for new shared memories
shared = a2a.receive_memory(client_id="project-x", limit=10)
for entry in shared:
    print(f"From {entry['from_agent_id']}: {entry['text']}")
```

### 5. Sync (Non-Poll)

```python
# Check for new memories since last sync (excludes your own shares)
new_memories = a2a.sync(since_timestamp="2026-06-13T10:00:00Z")
for entry in new_memories:
    print(f"{entry['from_agent_id']}: {entry['text']}")
```

### 6. Write to Shared Pool

```python
# Write directly to the shared pool (no target needed)
a2a.write_shared(
    text="User is a solo founder. Keep suggestions practical and few.",
    category="context",
    importance=8,
    is_private=False,  # all agents in client_id can see
)
```

### 7. Heartbeat

```python
# Send periodic heartbeat to maintain presence
a2a.heartbeat(status="online")  # online / busy / away
```

---

## Use Cases

### Multi-Agent Orchestration

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Orchestrator│ ──► │  Researcher │ ──► │  Executor   │
│  (Router)    │     │             │     │             │
└─────────────┘      └─────────────┘      └─────────────┘
                            │                    │
                            └──── A2A share ──────┘
                                  research context
```

```python
# Researcher shares findings with Executor
researcher_a2a.share_memory(
    target_agent_id="agent-executor",
    memory={
        "text": "Competitor analysis complete. "
                "3 main players: A (enterprise), B (SMB), C (startup). "
                "User should focus on B market segment.",
        "category": "decision",
    },
)

# Executor receives context without user repeating themselves
context = executor_a2a.sync()
```

### Handoff

When shifting from one agent to another (e.g., intake agent → execution agent):

```python
# Intake agent captures the full context
intake_a2a.share_memory(
    target_agent_id="agent-executor",
    memory={
        "text": "User called about urgent billing issue. "
                "Account: acme-corp. "
                "Issue: double-charged for March and April. "
                "Status: escalated to billing team.",
        "category": "interaction",
        "importance": 9,
    },
)
```

### Federated Teams

Multiple agents working on the same user share a memory pool:

```python
# Every agent in the team writes to the shared pool
for agent_id in ["agent-sales", "agent-support", "agent-success"]:
    a2a = A2AClient(api_key=api_key, agent_id=agent_id)
    a2a.write_shared(
        text=f"User engaged with {agent_id} today. "
             f"Full history available in recall.",
        category="general",
        importance=5,
        client_id="user-123",
    )
```

---

## Protocol Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/a2a/register` | Register an agent in the registry |
| POST | `/a2a/list` | List all agents in a client_id |
| POST | `/a2a/heartbeat` | Send agent heartbeat |
| POST | `/a2a/share` | Share a memory with a target agent |
| POST | `/a2a/receive` | Retrieve shared memories for this agent |
| POST | `/a2a/sync` | Sync new shares since timestamp |
| POST | `/a2a/write_shared` | Write to shared pool directly |

### Security

- Agents authenticate with their own API key
- Shared memories are scoped to `client_id` — agents in different
  `client_id` values cannot see each other's shares
- Private shares (`:is_private: true`) are only visible to the target agent
- All shares are logged to the immutable audit chain

### Rate Limits

A2A operations share the same rate limit as core memory operations.
Use heartbeats (every 30s) to maintain presence without hitting limits.

---

## MCP Integration

Agents can also access A2A via the MCP protocol:

| Tool | Description |
|------|-------------|
| `logicmem_a2a_share` | Share a memory with another agent |
| `logicmem_a2a_receive` | Receive shared memories |
| `logicmem_a2a_sync` | Sync new shares since timestamp |
