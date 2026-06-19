# Examples

> **Complete working examples for every LogicMem feature.**

---

## Table of Contents

1. [Basic Memory Operations](#1-basic-memory-operations)
2. [Reasoning Engine](#2-reasoning-engine)
3. [A2A Multi-Agent Sharing](#3-a2a-multi-agent-sharing)
4. [Audit Chain Verification](#4-audit-chain-verification)
5. [Voice Agent Memory (VAPI)](#5-voice-agent-memory-vapi)
6. [Session Context Briefing](#6-session-context-briefing)
7. [DPO Correction Pipeline](#7-dpo-correction-pipeline)
8. [Error Handling](#8-error-handling)

---

## 1. Basic Memory Operations

### Store and Retrieve Preferences

```python
import os
from logicmem import LogicMem

memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

# Store a user preference
memory.log(
    text="Ed prefers urgent messages via Telegram, not email.",
    category="preference",
    importance=8,
    client_id="ed_creed",
)

# Store another preference
memory.log(
    text="Ed is a solo founder. Keep suggestions practical and limited to 2-3 action items.",
    category="preference",
    importance=9,
    client_id="ed_creed",
)

# Search for all preferences
prefs = memory.recall(
    query="Ed communication and work preferences",
    limit=10,
    client_id="ed_creed",
)

for p in prefs:
    print(f"[{p['category']}] {p['text']}")
```

### Store Tasks with Context

```python
# Store a task with rich context
result = memory.log(
    text="Review Q3 proposal by Friday. "
         "Priority order: (1) cost breakdown, "
         "(2) timeline, "
         "(3) technical architecture. "
         "Ed needs to present to investors on Saturday.",
    category="task",
    importance=9,
    tags=["q3", "proposal", "urgent"],
    client_id="ed_creed",
)
print(f"Stored: {result['entry_id']}")

# Later: recall the task
tasks = memory.recall(
    query="Q3 proposal deadline and priority",
    limit=5,
    client_id="ed_creed",
)
for t in tasks:
    if t.get("category") == "task":
        print(t["text"])
```

### Custom API Key Header (for multi-tenant setups)

```python
# Use a specific API key for a tenant
memory = LogicMem(
    api_key="tenant-specific-key",
    base_url="https://api.your-memory-server.com",
)

result = memory.log(
    text="Acme Corp renewed their contract.",
    category="contract",
    client_id="acme-corp",
)
```

---

## 2. Reasoning Engine

### Multi-Step Reasoning

```python
memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

# Ask a complex question that requires reasoning
answer = memory.reason(
    question="Should we prioritize the mobile app or web dashboard first?",
    context="Ed is a solo founder with limited engineering bandwidth. "
            "Current runway is 6 months. Monthly burn is $12k.",
    mode="deep",  # fast / deep / exhaustive
)

print(f"Confidence: {answer.get('confidence')}")
print(f"Answer: {answer.get('answer')}")
print("\nReasoning trace:")
for step in answer.get("steps", []):
    print(f"  Step {step['step']}: {step['thought']}")
    if step.get("memory_consulted"):
        print(f"    Memory consulted: {step['memory_consulted']}")
```

### Verify a Claim

```python
# Before making a claim, verify it against memory
verdict = memory.verify(
    claim="Ed prefers email for urgent messages."
)

print(f"Verdict: {verdict['verdict']}")  # supported / contradicted / inconclusive
for entry in verdict.get("evidence", []):
    print(f"  Evidence: {entry['text']}")
    print(f"  Created: {entry['created_at']}")
```

### Self-Reflection Before Answering

```python
# Draft an answer, then have the agent critique itself
draft = "You should build the mobile app first because it's a growing market."

review = memory.reflect(
    draft_answer=draft,
    question="What should we prioritize first — mobile or web?",
    memory_query="Ed solo founder constraints",
)

print(f"Reflection score: {review['score']}/100")
print(f"Verdict: {review['verdict']}")  # needs_revision / accepted
print(f"Gaps: {review.get('gaps', [])}")
print(f"Suggestions: {review.get('suggestions', [])}")
```

### Confidence Scoring

```python
from logicmem import LogicMem
from logicmem.reasoning import ReasoningEngine

memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])
reasoner = ReasoningEngine(memory)

score = reasoner.confidence(
    question="What is Ed's preferred communication channel?",
    answer="Telegram, because Ed prefers urgent messages via Telegram.",
)

print(f"Confidence score: {score['score']}/100")
for factor in score.get("factors", []):
    print(f"  {factor['name']}: {factor['value']}")
```

---

## 3. A2A Multi-Agent Sharing

### Researcher → Executor Handoff

```python
# In the RESEARCHER agent:
from logicmem.a2a import A2AClient

researcher_a2a = A2AClient(
    api_key=os.environ["RESEARCHER_API_KEY"],
    agent_id="researcher-claude",
)

# Register first
researcher_a2a.register(
    name="Claude Researcher",
    agent_type="agent",
    client_id="project-x",
)

# When research is done, share findings
researcher_a2a.share_memory(
    target_agent_id="executor-claude",
    memory={
        "text": "Research complete. "
                "Competitor analysis: 3 players in target segment. "
                "Recommended positioning: mid-market SMB, "
                "lead with pricing transparency.",
        "category": "decision",
        "importance": 9,
    },
    client_id="project-x",
)
```

```python
# In the EXECUTOR agent:
from logicmem.a2a import A2AClient

executor_a2a = A2AClient(
    api_key=os.environ["EXECUTOR_API_KEY"],
    agent_id="executor-claude",
)

# Check for new context from the researcher
new_memories = executor_a2a.sync()
for entry in new_memories:
    print(f"From {entry['from_agent_id']}: {entry['text']}")
    # Store it in local memory for reference
    memory.log(
        text=f"[via A2A from {entry['from_agent_id']}]: {entry['text']}",
        category="context",
        source="a2a",
    )
```

### List Online Agents

```python
# Check who's available
a2a = A2AClient(api_key=os.environ["LOGICMEM_API_KEY"], agent_id="orchestrator")

agents = a2a.list_agents(client_id="project-x")
for agent in agents:
    status_emoji = {"online": "🟢", "busy": "🟡", "away": "⚫"}.get(
        agent.get("status"), "❓"
    )
    print(f"{status_emoji} {agent['agent_id']} ({agent.get('name', '')})")
```

---

## 4. Audit Chain Verification

```python
from logicmem.audit import AuditChain

audit = AuditChain(memory)

# Verify the full audit chain
result = audit.verify()
if result["valid"]:
    print(f"✅ Audit chain intact. {result['chain_length']} entries.")
    print(f"   Last hash: {result['last_hash'][:16]}...")
else:
    print("❌ Audit chain integrity violation detected!")

# Weekly automated audit
import schedule

def weekly_audit():
    result = audit.verify()
    if not result["valid"]:
        # Send alert
        print("ALERT: Audit chain integrity violation!")

# Note: schedule is a third-party lib, or use cron/APScheduler
```

---

## 5. Voice Agent Memory (VAPI)

### Store a Voice Call Summary

```python
# After a VAPI voice call ends, store the transcript summary
memory.log(
    text="Voice call with Ed (VAPI call_id: vc_abc123). "
         "Topic: Q3 proposal review. "
         "Ed confirmed Friday deadline. "
         "Ed wants cost breakdown before anything else. "
         "Ed sounded positive about the project direction.",
    category="voice_call",
    importance=8,
    source="voice_call",
    tags=["vapi", "q3", "proposal"],
    client_id="ed_creed",
)

# Retrieve recent call history
calls = memory.recall(
    query="Ed voice calls about Q3 proposal",
    limit=5,
    client_id="ed_creed",
)

for call in calls:
    if call.get("category") == "voice_call":
        print(f"Call: {call['text'][:100]}...")
```

---

## 6. Session Context Briefing

### Start of Session

```python
# At the start of every session, get full context
def start_session(client_id: str):
    memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

    brief = memory.session(client_id=client_id)

    print(f"Relationship trend: {brief.get('relationship_trend', 'unknown')}")
    print(f"Confidence: {brief.get('confidence', 0)}%")
    print()

    print("Active constraints:")
    for c in brief.get("active_constraints", []):
        print(f"  - {c}")

    print("\nSuggested conversation openers:")
    for opener in brief.get("conversation_openers", []):
        print(f"  → {opener}")

    print("\nCritical gaps (things we don't know about the user):")
    for gap in brief.get("critical_gaps", []):
        print(f"  ⚠ {gap}")

    return brief

# Run at session start
start_session("ed_creed")
```

---

## 7. DPO Correction Pipeline

### Log a Correction (Improves the Model)

```python
# When the agent makes a mistake, log the correction
audit = AuditChain(memory)

audit.log_correction(
    original="The user prefers email for urgent messages.",
    corrected="The user prefers Telegram for urgent messages, not email.",
    reason="User explicitly corrected this in the call on 2026-06-10. "
           "They said 'I never check email for urgent things — "
           "always Telegram.'",
)

# Check how many corrections are queued
stats = audit.dpo_stats()
print(f"Correction pairs ready for training: {stats.get('ready_count', 0)}")
```

---

## 8. Error Handling

```python
import os
from logicmem import LogicMem
from logicmem.exceptions import (
    LogicMemError,
    AuthenticationError,
    MemoryNotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    NetworkError,
)

memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

try:
    memory.log(text="Test memory", category="general")
except AuthenticationError as e:
    print(f"Invalid API key: {e.message}")
    # → Prompt user to check their key
except RateLimitError:
    print("Rate limited — backing off and retrying")
    # → Implement exponential backoff
except ServerError as e:
    print(f"Server error ({e.status_code}): {e.message}")
    # → Alert on-call, log for debugging
except NetworkError as e:
    print(f"Network issue: {e.message}")
    # → Check internet connection, retry
except ValidationError as e:
    print(f"Bad request: {e.message}")
    # → Fix the request parameters
except LogicMemError as e:
    # Catch-all for any other LogicMem error
    print(f"Unexpected error: {e.message}")
```

### Retry with Exponential Backoff

```python
import time
import random
from logicmem.exceptions import RateLimitError, ServerError, NetworkError

def log_with_retry(memory, text, max_retries=3):
    for attempt in range(max_retries):
        try:
            return memory.log(text=text)
        except RateLimitError:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited. Retrying in {wait:.1f}s...")
            time.sleep(wait)
        except (ServerError, NetworkError) as e:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Error: {e}. Retrying in {wait:.1f}s...")
            time.sleep(wait)
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    raise Exception(f"Failed after {max_retries} retries")

result = log_with_retry(memory, "Important memory that needs to be stored")
```

---

## 9. Full Agent Loop Example

```python
"""
Full agent loop that uses memory at every step.
This is what a production AI agent looks like with LogicMem.
"""

import os
from logicmem import LogicMem
from logicmem.exceptions import RateLimitError
import time

def agent_loop(user_id: str, initial_prompt: str):
    memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

    # ── Session start: Get full context ───────────────────────
    brief = memory.session(client_id=user_id)
    print(f"Session briefing: {brief.get('relationship_trend')} "
          f"relationship, {brief.get('confidence')}% confidence")

    # ── Check for shared context from other agents ───────────
    # (See A2A examples above for full sync code)
    # shared = a2a.sync()

    # ── Main conversation loop ────────────────────────────────
    messages = [{"role": "user", "content": initial_prompt}]

    for turn in range(10):  # max 10 turns
        # Build context from memory
        context_memories = memory.recall(
            query=initial_prompt,
            limit=3,
            client_id=user_id,
        )

        context_text = "\n".join(
            f"- {m['text']}" for m in context_memories
        )

        # Construct prompt with memory context
        prompt = f"""Previous relevant memories:
{context_text}

User: {initial_prompt}

Respond helpfully based on the user's history and the memories above."""

        # (In production: call your LLM here with `prompt`)
        # response = llm.generate(prompt)
        response = f"[Agent response to: {initial_prompt}]"

        messages.append({"role": "assistant", "content": response})
        print(f"Agent: {response}")

        # Store this exchange in memory
        memory.log(
            text=f"User said: {initial_prompt}. "
                 f"Agent responded about: {response[:100]}",
            category="interaction",
            importance=6,
            client_id=user_id,
        )

        # Check if we need to reason about a decision
        if "should we" in initial_prompt.lower() or "recommend" in initial_prompt.lower():
            reasoning = memory.reason(
                question=initial_prompt,
                context=f"User: {initial_prompt}",
                mode="deep",
            )
            print(f"🧠 Reasoning confidence: {reasoning.get('confidence')}")

        # Log corrections if we made a mistake
        # (In production: compare response to user feedback)
        # audit.log_correction(original=response, corrected=..., reason="...")

        break  # Single turn for this example

    # ── Session end: Store summary ──────────────────────────
    memory.log(
        text=f"Session summary: User asked about '{initial_prompt}'. "
             f"Agent provided response. "
             f"Confidence at session end: {brief.get('confidence')}",
        category="interaction",
        importance=5,
        client_id=user_id,
    )

# Run the agent
if __name__ == "__main__":
    agent_loop(
        user_id="ed_creed",
        initial_prompt="How's my Q3 proposal coming along?",
    )
```
