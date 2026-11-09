# LogicMem: real-time sharing in one reported setup, and a record you can re-check

Agents share through LogicMem, and LogicMem keeps a tamper-evident, hash-linked record of operations submitted through this kit. **Real-time**, on this page, means only this: an operator reported in November 2026 that configured listeners, kept on, communicate and respond to tasks. That report was not independently reproduced. It is one always-on setup, not a latency figure, not support for every client, and not proof that an idle host wakes. Waking depends on the host. The Python SDK in this repository does not open that listener. `sync()` and `receive_memory()` poll.

A hosted listener is not a set of universal steps in this kit. It needs pilot-assisted configuration: [request a pilot](https://logicmem.io/design-partner/) or write to [support@logicmem.io](mailto:support@logicmem.io). Mail delivery to that address was not tested.

The record is what was submitted under an API key, with the agent id the caller declared. It is not everything an agent did. Not every endpoint writes an audit entry. Chain checks run on the server, on entries the server still holds. A check described as intact does not prove those entries are true or complete, and it does not by itself show that the newest entries were not removed. See [SECURITY.md](docs/SECURITY.md). This is not a compliance certificate.

> The record shows what was submitted through LogicMem, and whether those stored entries still link. It does not show everything an agent did.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP server](https://img.shields.io/badge/MCP-server-blueviolet)](https://modelcontextprotocol.io)

The MCP badge is a label for the local server in this repo. It is not a third-party compatibility certification.

---

## The problem

An auditor can ask what an agent submitted, and ordinary logs can be edited without a visible trace. Separately, one agent often cannot see what another agent just wrote down.

## What LogicMem gives you

Two different things:

1. **Sharing.** An agent can write a memory for other agents that use the same LogicMem workspace. Hearing about that write is a second step, described under [How a share is delivered](#how-a-share-is-delivered).
2. **A tamper-evident record** of operations the server chooses to log. There are two records in an Oct 27, 2026 server snapshot that is not in this repository; live parity was not re-checked here. See [Which record](#which-record).

---

## How a share is delivered

These are different events. A notification is not proof the other agent received the payload or ran the task.

| Event | What it means here |
| --- | --- |
| **Stored** | The write call was accepted and the share is in the shared pool. |
| **Notified** | Some other path tells a listener. This SDK does not do that. |
| **Checked in** | `A2AClient.sync()` and `receive_memory()` poll. They do not open a stream. |
| **Acted on** | Whatever the receiving agent and its host decide to do. This kit does not record that decision. |

**This SDK polls.** `sync()` calls `GET /memory/shared/updates`, requests at most `limit` entries (default 50), and returns a list. It has no offset. If the JSON also has `total_new`, this client drops that field, so you cannot compare it from `sync()` alone. Ordering, a default slice, and whether a cursor exists for this REST path are **not** known from code in this repository. Do not treat a list shorter than `limit` as proof the backlog is finished. If `len(result) == limit`, the backlog may be incomplete: do not advance a checkpoint. Do not assume a higher `limit` is accepted. Those rules are the conservative reading of this client only.

Newest-first order, a default of 50, a `total_new` count, and no cursor are attributes of the MCP tool `logicframe_memory_sync_check` in an Oct 27, 2026 source snapshot. They are not transferred here onto `GET /memory/shared/updates`.

**Hosted listeners are a different path.** The November 2026 operator report above is the real-time claim: configured listeners kept on, in that one setup. It is not a product-wide latency or compatibility claim. An Oct 27, 2026 **source snapshot** (not a delivery test, and not in this repository) described an MCP SSE path and, separately, signed webhooks that can retry or dead-letter. A review note attached to that SSE description said that SSE path had no replay. That note is not a webhook guarantee and not a test result. Separate single-sample delivery notes from Oct 24–25, 2026 are not proof of the source snapshot, and they are not repeated here as a speed claim. Stream behavior and webhook behavior are different channels. This kit does not document a universal listener setup. Use the pilot or support route above.

The file `webhooks/dispatcher.py` is a local queue in this repo (5 attempts, then a dead-letter file). It is not the hosted webhook service. The Oct 27 snapshot's outbox used different limits (12 attempts or 7 days). Do not treat them as one contract. See [A2A-PROTOCOL.md](docs/A2A-PROTOCOL.md).

"LogicMem A2A" in this repo is LogicMem's own sharing API. It is not an implementation of the [Agent2Agent protocol](https://a2a-protocol.org/).

---

## Which record

`AuditChain.verify()` sends `GET /memory/audit/verify` and returns the server's JSON. It does not recompute hashes in this process.

An Oct 27, 2026 server snapshot (not in this repository; the server repo was not readable with the Nov 9, 2026 review credential) kept two hash-linked records:

- An audit log that included operational rows such as `RECALL`, and a correction write.
- A selected-write chain whose operation set was `LOG`, `SHARE`, `BROADCAST`, `SUPERSEDE`, `ARCHIVE`, and `MEMORY_MERGE`. That set did not include `RECALL`.

Recall in that snapshot could be on the audit log and off the selected-write chain. Do not read the selected-write list as "recall is unaudited." Whether `logicframe_correction_log` is that correction write, and whether production still matches the snapshot, were not established. A Nov 9, 2026 health read reported both a hash chain and an audit chain as valid; that is a status string, not a map of which operations were included.

---

## What is in this repo

- **Python SDK** (`logicmem`, MIT licensed): a client for the LogicMem REST API at `https://api.logicmem.io`.
- **Local MCP server** (`logicmem-server`): a stdio bridge that serves `logicmem_*` tools to MCP clients.
- **Docs** for the hosted MCP server at `https://mcp.logicmem.io/mcp`, which serves `logicframe_*` tools. LogicFrame LLC holds the copyright in this repo. The prefix is the hosted tool namespace, not a second package to install.

The LogicMem server itself (storage, reasoning engine, audit chain) is not in this repo; it runs in LogicMem's cloud.

**Access:** API keys are issued to pilot teams. Pilots run 30 days, from $500/mo: [logicmem.io/design-partner](https://logicmem.io/design-partner/).

As of 2026-11-09, a browser open of `https://api.logicmem.io/` redirected to `/mem/signup`, which shows an account form. The form was not submitted. It is not known whether that form issues keys for this kit. The access path these docs describe is the pilot page above.

Code and documentation in this repository are under the MIT license. Using the hosted service needs an API key. This repo does not include a terms-of-service or privacy-policy link for that service.

---

## Install

You need Python 3.11 or later and `git`. The install command clones this repository. On Windows, `py -3` is the usual launcher (`py -3 -m venv .venv`, then `.venv\Scripts\activate`). The `python3` examples below are for macOS and Linux.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# SDK only
pip install git+https://github.com/LogicMem/LogicMem-mcp-.git

# SDK + local MCP server (logicmem-server)
pip install "logicmem[cli] @ git+https://github.com/LogicMem/LogicMem-mcp-.git"
```

> Install from GitHub as shown. As of 2026-11-09 the `logicmem` package on PyPI was still 0.1.1 and had not been replaced. Its description and project URLs are older than this repo: they point at the archived `CreedLab/logicmem-mcp` repository and at `docs.logicmem.io`, and they make functionality, access, and security claims this README does not stand behind (including "immutable", "every operation", encryption and compliance phrases, and a self-serve key path). One sentence there attributes a star count to OpenClaw, not to LogicMem. Do not treat the PyPI page as the current kit. Publishing a corrected package is a separate release, not done from this repository's docs.

---

## Quick start

The short path that shares, checks in, and asks the server to re-check the record is [docs/QUICKSTART.md](docs/QUICKSTART.md). It needs an API key for the hosted calls. Importing the package and running `logicmem-server --help` do not.

### 1. Get an API key

Keys start with `lm_`. They are issued to pilot teams while self-serve sign-up is being rebuilt: request one at **[logicmem.io/design-partner](https://logicmem.io/design-partner/)**. Treat the key like a password. The signup form mentioned above was not tested.

Requests over your rate limit return HTTP 429 (`RateLimitError` in the SDK).

### 2. Use the Python SDK

`LogicMem.log`, `recall`, and `session` default `client_id` to `"default"` when you omit it. Pass the id your key is for. The SDK sends that string. It does not decide which ids the server will accept. A Nov 9, 2026 morning operator note recorded HTTP 403 for a foreign `client_id` on that check's route. That is counterevidence to a general cross-tenant bypass, not a full access policy, and not a new probe from the later offline pass.

```python
import os
from logicmem import LogicMem

memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])

# Store a memory you explicitly record
memory.log(
    text="User prefers urgent messages via Telegram, not email.",
    category="preference",
    importance=8,
    client_id="demo-tenant",
)

# Search memories
results = memory.recall(
    query="user communication preferences",
    client_id="demo-tenant",
)
for r in results:
    print(r.get("text"))

# Session briefing (a context summary from the server)
brief = memory.session(client_id="demo-tenant")
print(brief)
```

### 3. Reasoning engine

```python
answer = memory.reason(
    question="Should we prioritize the mobile app or web dashboard first?",
    context="Example only: a small team with a fixed weekly time budget.",
    mode="deep",  # sent as the string fast, deep, or exhaustive
)
print(answer.get("answer"))
print(answer.get("confidence"))
```

`mode` does not change the `max_steps` value this client sends (the default is 5). `verify()`, `reflect()` and `intelligence()` exist on the client but always raise `NotImplementedError`: those names are hosted MCP tools (`logicframe_verify`, `logicframe_reflect`, `logicframe_intelligence`). Call them from an MCP client. The hosted tool list was not re-read on Nov 9, 2026, because a keyless `tools/list` returned HTTP 401.

### 4. Share memory between agents

LogicMem's own sharing API, not the Agent2Agent open protocol. The calls below poll. They do not open a listener.

```python
import os
from logicmem.a2a import A2AClient

a2a = A2AClient(api_key=os.environ["LOGICMEM_API_KEY"], agent_id="agent-researcher")

# Register this process under a label you declare. The label is not a credential.
a2a.register(name="Researcher Agent", agent_type="agent", client_id="demo-tenant")

# Store a share for another declared agent id
a2a.share_memory(
    target_agent_id="agent-executor",
    memory={"text": "User needs Q3 report by Friday. High priority."},
    category="task",
    importance=9,
    client_id="demo-tenant",
)

# In the other process: check in. This does not prove that process ran the task.
executor = A2AClient(api_key=os.environ["LOGICMEM_API_KEY"], agent_id="agent-executor")
for entry in executor.sync(client_id="demo-tenant"):
    print(entry.get("text"))
```

`agent_id` is a string you supply. Supplying it does not prove that another caller in the same workspace cannot read the entry. `is_private` is forwarded on the write; this SDK does not enforce it.

### 5. Ask the server to re-check the record

```python
from logicmem.audit import AuditChain

audit = AuditChain(memory)  # pass a LogicMem client

# The server re-checks. This process does not recompute the chain.
print(audit.verify())

# Store a correction. The client describes this as queued for the server's
# DPO training pipeline. What that queue trains, on whose data, for how long,
# and whether you can opt out, is not in this repo. See docs/SECURITY.md.
audit.log_correction(
    original="The user prefers email for urgent messages.",
    corrected="The user prefers Telegram for urgent messages, not email.",
    reason="User explicitly stated Telegram in a call.",
)
print(audit.dpo_stats())
```

There is no sample `verify()` body in this README. This audit did not call the hosted verify endpoint. Print the dict you get. Read [SECURITY.md](docs/SECURITY.md) for what a chain check does not prove. An illustrative sketch that is **not** server output lives in [QUICKSTART.md](docs/QUICKSTART.md).

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Your MCP client                         │
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
              sharing · records · reasoning · audit checks
```

---

## Connect an MCP client

OpenClaw below is a worked example because OpenClaw's own docs use this config shape (read 2026-11-09). A November 2026 operator note also named OpenClaw among configured clients. Cursor was not in that note. A Codex connection was mentioned there with the method unresolved, so it is not documented here as a supported client, and nothing here is ChatGPT app support. These checks did not launch the applications.

### Option A: hosted URL, OpenClaw config shape

OpenClaw documents remote servers under `mcp.servers` in `~/.openclaw/openclaw.json`, with `transport` `streamable-http` and optional `headers` (OpenClaw docs read 2026-11-09). `openclaw` was not run from this repository.

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

`transport: streamable-http` is the client config key. It is not a claim that the hosted server's `protocolVersion` string was re-read. The local bridge answers `initialize` with `2024-11-05`. A keyless hosted `initialize` on 2026-11-09 returned HTTP 401, so the hosted version string was not reconfirmed.

Other clients that can set a streamable-HTTP URL and an `Authorization` header are not certified here. Claude Desktop's local config file and Cursor's MCP file use a different shape (`mcpServers`); see Option B for stdio. Cursor was not part of the November 2026 operator note.

### Option B: local stdio server

The console script is part of the base package. `logicmem-server --help` does not send HTTP. It exited 0 on Python 3.12.3 on 2026-11-09 with and without `httpx`. When `httpx` is missing, tool calls use `urllib` and do not set `User-Agent`. Python's urllib then supplies its default, `Python-urllib/<version>` (offline check on 3.12: `Python-urllib/3.12`). With `httpx` installed, the client sends httpx's own default unless you override it (offline check: `python-httpx/0.28.1`). Neither default was sent to LogicMem in that check. A Nov 8, 2026 operator note said a browser-integrity check returned 403 to a `Python-urllib` agent on some paths, and that an exception existed for certain MCP paths. That note was not rechecked and is not proof the fallback fails now. Installing the `cli` extra (httpx) is the conservative choice for hosted calls. It is not a guarantee the edge accepts httpx.

```bash
pip install "logicmem[cli] @ git+https://github.com/LogicMem/LogicMem-mcp-.git"
logicmem-server --help
```

Stdio clients that use a top-level `mcpServers` object (the shape in Claude Desktop's `claude_desktop_config.json`, and in Cursor's MCP config) can launch the command. Set `LOGICMEM_CLIENT_ID` to the same id your SDK calls use. If you omit it, the bridge defaults to `default`, and a script that wrote to another id will not be what the bridge reads.

```json
{
  "mcpServers": {
    "logicmem": {
      "command": "logicmem-server",
      "env": {
        "LOGICMEM_API_KEY": "lm_YOUR_API_KEY",
        "LOGICMEM_CLIENT_ID": "demo-tenant"
      }
    }
  }
}
```

### Check your setup (OpenClaw)

```bash
openclaw mcp list
```

OpenClaw's own docs say `mcp list` reads the configured server block and does not connect to the server. A listing is not a live call. The command was not run from this repository.

Then ask the agent to store a note with `logicframe_memory_log` (hosted) or `logicmem_memory_log` (local) and recall it, using the same `client_id` you wrote with. Hosted `logicframe_memory_recall`, as documented from a `tools/list` on 2026-10-24, did not list `client_id`. That schema was not re-listed on 2026-11-09.

### Environment variables (for `logicmem-server`)

The Python SDK does not read these; pass `api_key` and `base_url` to `LogicMem(...)` instead.

| Variable | Default | Description |
|----------|---------|-------------|
| `LOGICMEM_API_KEY` | — | Your API key (`lm_...`), issued to [pilot teams](https://logicmem.io/design-partner/) |
| `LOGICMEM_SERVER_URL` | `https://api.logicmem.io` | Override the LogicMem REST API URL |
| `LOGICMEM_CLIENT_ID` | `default` | Default client_id for memory operations on the local bridge |
| `LOGICMEM_TIMEOUT` | `30` | HTTP request timeout in seconds |

---

## MCP reference

**Hosted MCP endpoint:** `https://mcp.logicmem.io/mcp`

**REST API base URL:** `https://api.logicmem.io`

**Keyless requests:** A Nov 9, 2026 morning operator note recorded HTTP 401 for keyless GET of `/sse`, `/mcp/sse`, and `/mcp`, and for keyless POST `initialize` and `tools/list`, on both hosts. That note is about those requests. It is not a map of every later edge or session rule, and it is not an authenticated call. The local stdio server still answers `initialize` and `tools/list` on stdin without a key. The REST call behind a tool still needs one. Error rows that mention HTTP 404 or 429 are from the 2026-10-24 notes for calls that presented a key. They were not rechecked. See [MCP-PROTOCOL.md](docs/MCP-PROTOCOL.md).

**Direct HTTP, from an operator runbook dated Nov 8, 2026 (not replayed):** `Authorization: Bearer lm_...`, `Accept: application/json, text/event-stream`, a descriptive `User-Agent`, and `X-Agent-ID`. After `initialize`, send `Mcp-Session-Id` if the server returned one. No authenticated session id was recorded for these docs. A keyless 401 does not prove that header is optional once a key is sent.

The cURL sample in [MCP-PROTOCOL.md](docs/MCP-PROTOCOL.md) includes the bearer token. It is not a completed session transcript.

> **Tool name prefix:** the hosted server's documented names use `logicframe_*`. The local pip server (`logicmem-server`) serves `logicmem_*`. They are not one-to-one. Names below for the hosted server come from the doc's 2026-10-24 `tools/list` note, except where marked. A public re-list on 2026-11-09 was blocked by HTTP 401.

| SDK | Local tool | Hosted name in the 2026-10-24 note |
| --- | --- | --- |
| `LogicMem.log` | `logicmem_memory_log` | `logicframe_memory_log` |
| `LogicMem.recall` | `logicmem_memory_recall` | `logicframe_memory_recall` |
| `LogicMem.session` | `logicmem_memory_session` | not the same as `logicframe_memory_context` |
| `LogicMem.health` | `logicmem_memory_health` | `logicframe_health` (listed under other tools) |
| `MemoryTools.stats` | `logicmem_memory_stats` | `logicframe_memory_stats` |
| `A2AClient.register` | `logicmem_a2a_register` | no matching name in that note |
| `A2AClient.heartbeat` | `logicmem_a2a_heartbeat` | no matching name in that note |
| `A2AClient.list_agents` | `logicmem_a2a_list_agents` | no matching name in that note |
| `share_memory` / `write_shared` | `logicmem_a2a_write_shared` | `logicframe_memory_share` shares an existing entry by id; different call shape |
| `sync` / `receive_memory` | `logicmem_a2a_sync` | `logicframe_memory_sync_check` |
| `verify` / `reflect` / `intelligence` | not local tools (`NotImplementedError`) | `logicframe_verify`, `logicframe_reflect`, `logicframe_intelligence` |
| `AuditChain.verify` | no local tool; REST `GET /memory/audit/verify` | `logicframe_audit_verify` |
| `AuditChain.log_correction` | no local tool; REST `POST /memory/correction/log` | `logicframe_correction_log` (whether that is the snapshot's correction audit row is unknown) |

### Commonly used hosted tools

The hosted server lists many more tools. `tools/list` with a key is the source of truth. The table dated 2026-10-24 was not reconfirmed on 2026-11-09.

| Tool | Description |
|------|-------------|
| `logicframe_memory_log` | Store a new memory with category, importance, tags |
| `logicframe_memory_recall` | Search memories with natural language |
| `logicframe_memory_context` | Get context about a client, project, or person |
| `logicframe_memory_share` | Share an existing memory with another declared agent id |
| `logicframe_memory_sync_check` | Check in for memories stored by other agents since a timestamp |
| `logicframe_reason` | Multi-step reasoning that consults memory |
| `logicframe_verify` | Check a claim against stored memories |
| `logicframe_reflect` | Critique a draft answer against memory |
| `logicframe_intelligence` | Look for patterns and overdue items |
| `logicframe_audit_verify` | Ask the server to re-check the audit chain and the hash chain |
| `logicframe_correction_log` | Log a correction (the client docs describe a DPO queue; see Security) |
| `logicframe_conversations_store` | Store conversation state for auto-resume |
| `logicframe_conversations_resume` | Retrieve stored conversation state |

See [MCP-PROTOCOL.md](docs/MCP-PROTOCOL.md) for details.

---

## Security

- **In transit:** HTTPS. One client handshake on 2026-11-09 negotiated TLS 1.3. That does not prove older TLS versions are disabled. Details are in [SECURITY.md](docs/SECURITY.md).
- **Records:** see [Which record](#which-record). Not every endpoint writes an audit entry. Re-check with `logicframe_audit_verify` or `AuditChain.verify()`.
- **API keys:** sent as a Bearer token; keep them out of code and git.
- **Corrections:** `log_correction` posts the text you supply. The client describes a DPO training queue. The consumer of that queue is not in this repo.

See [SECURITY.md](docs/SECURITY.md).

---

## Documentation

| Doc | What you need |
|-----|--------------|
| **[Start here](docs/QUICKSTART.md)** | Install, local no-key check, share then check in then verify |
| **[MCP protocol](docs/MCP-PROTOCOL.md)** | Hosted MCP server reference |
| **[A2A sharing](docs/A2A-PROTOCOL.md)** | LogicMem's sharing API (not the Agent2Agent protocol) |
| **[Security](docs/SECURITY.md)** | Transport, auth, records, data-handling gaps |
| **[Code examples](docs/EXAMPLES.md)** | Examples with synthetic ids |
| **[Embedding fallback](docs/EMBEDDING-FALLBACK.md)** | Documented server embedding order; not re-traced live |
| **[Doc index](docs/INDEX.md)** | The rest, including internal ops scripts |

## Links

- 🌐 [logicmem.io](https://logicmem.io) — Product
- 🚀 [Quickstart](https://logicmem.io/quickstart/) — Product quickstart page
- 🧪 [Pilots](https://logicmem.io/design-partner/) — 30-day pilots from $500/mo
- 📜 [EU AI Act Article 12](https://logicmem.io/eu-ai-act-article-12/) — LogicMem is designed to support record-keeping such as EU AI Act Article 12 (not legal advice)
- 📧 [support@logicmem.io](mailto:support@logicmem.io)

Mailbox delivery for `support@logicmem.io` was not tested. Nothing was sent.

---

## Contributing

Contributions welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md). We especially welcome MCP client examples, framework integrations (LangChain, CrewAI, etc.), sharing examples, and SDKs in other languages.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT License. The license covers the software and documentation in this repository. See [LICENSE](LICENSE).
