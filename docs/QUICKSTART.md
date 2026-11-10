# LogicMem quickstart — share a note, check it in, re-check the record

> **Goal:** install the kit, confirm the local package responds with no network call, then (with an API key) have one declared agent id share a note, have another check in with `sync()`, and ask the server to re-check the record.

The hosted steps need a key. They were not run against `api.logicmem.io` in the audit that wrote this page. Anything in a block marked **illustrative fixture** was not returned by the server.

## Prerequisites

- Python 3.11 or later. This audit ran the local checks on Python 3.12.3. Python 3.13 is inside `requires-python` and was not executed here. The package classifiers list 3.11 and 3.12.
- `git`, because the install command clones the repository.
- A LogicMem API key (`lm_...`) for the hosted steps. Keys are issued to pilot teams while self-serve sign-up is being rebuilt: [request a pilot](https://logicmem.io/design-partner/). On 2026-11-09 a browser GET of `https://api.logicmem.io/` redirected to an account form. That form was not submitted. Do not assume it issues a key for this kit.

On Windows, create the venv with `py -3 -m venv .venv` and activate `.venv\Scripts\activate`. The `python3` lines below are for macOS and Linux.

## Step 1 — Install

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install "logicmem[cli] @ git+https://github.com/LogicMem/LogicMem-mcp-.git"
```

> Install from GitHub as shown. As of 2026-11-09, PyPI `logicmem` was still 0.1.1, with older links and with functionality, access, and security wording this repo does not stand behind. See the README. One PyPI sentence attributes a star count to OpenClaw, not to LogicMem.

The `cli` extra installs `httpx`. The console script is part of the base package. `logicmem-server --help` also works without that extra; the server uses `urllib` when `httpx` is not installed.

## Step 2 — Local check, no API key

These commands do not call LogicMem. On 2026-11-09, on Python 3.12.3, `pip install -e .` (no extras) and `pip install -e ".[dev]"` both imported version `0.1.2`, and `logicmem-server --help` and `python -m logicmem.cli --help` both exited 0. `--help` does not send HTTP. Hosted calls without `httpx` use urllib's default User-Agent. That path's acceptance at the edge was not verified. The `cli` extra is the conservative install for hosted calls, not a guarantee. See the README.

```bash
python -c "import logicmem; print(logicmem.__version__)"
logicmem-server --help
python -m logicmem.cli --help
```

That output is the package version and the local server's help text. It is not a hosted audit record and it does not show that a share was stored.

## Step 3 — Set your API key

```bash
export LOGICMEM_API_KEY="lm_your_api_key_here"
```

The script below reads the key from this environment variable. Never commit the key to git.

Use one synthetic client id in the script and, if you start the local bridge, in `LOGICMEM_CLIENT_ID`. The SDK and the bridge default to `default` when the id is omitted, so a script that writes to `quickstart-demo` and a bridge left on `default` are not looking at the same id. `quickstart-demo` is an example string. The SDK sends it. It does not mean the server will accept an arbitrary tenant id for your key. A Nov 9, 2026 check got HTTP 403 for a foreign `client_id` on that check's route. This audit did not repeat that call.

## Step 4 — Share, check in, ask for a re-check

Create `quickstart.py`:

```python
import os
from logicmem import LogicMem
from logicmem.a2a import A2AClient
from logicmem.audit import AuditChain

memory = LogicMem(api_key=os.environ["LOGICMEM_API_KEY"])
CLIENT = "quickstart-demo"

# Two labels in one process. They are not two authenticated identities,
# and they are not two vendors.
researcher = A2AClient(
    api_key=os.environ["LOGICMEM_API_KEY"],
    agent_id="agent-researcher",
)
executor = A2AClient(
    api_key=os.environ["LOGICMEM_API_KEY"],
    agent_id="agent-executor",
)
researcher.register(name="Researcher", client_id=CLIENT)
executor.register(name="Executor", client_id=CLIENT)

researcher.share_memory(
    target_agent_id="agent-executor",
    memory={"text": "Handoff test: the deploy freeze starts Friday."},
    category="task",
    importance=8,
    client_id=CLIENT,
)
print("share call returned")

# Check-in. This does not open a stream, and it does not prove the
# executor process acted. If the list is as long as limit (default 50),
# do not treat it as the whole backlog and do not advance a checkpoint.
# A shorter list is not proof that nothing older remains.
# See docs/A2A-PROTOCOL.md.
seen = executor.sync(client_id=CLIENT)
print(f"sync returned {len(seen)} entries")
for entry in seen:
    print(entry.get("text"))

# Server-side re-check. Print the dict. This client does not score it.
print(AuditChain(memory).verify())
```

## Step 5 — Run it

```bash
python quickstart.py
```

You should see `share call returned`, then however many texts `sync` returned for that client id, then the JSON from `verify()`. Counts and fields depend on the server and on data already stored for that key. This audit did not run the script.

**Illustrative fixture. Not captured from api.logicmem.io or mcp.logicmem.io.**

```text
share call returned
sync returned 1 entries
Handoff test: the deploy freeze starts Friday.
{'note': 'replace this brace with the dict your server actually returned'}
```

A chain report, even one the server describes as intact, does not prove the entries are true or complete, and it does not by itself show that the newest entries were not removed. Not every endpoint writes an audit entry. Details: [SECURITY.md](SECURITY.md).

## Step 6 — Connect via MCP

**Hosted server.** In the client's settings, add a streamable-HTTP server with URL `https://mcp.logicmem.io/mcp` and header `Authorization: Bearer lm_your_api_key`. Keyless `initialize` and `tools/list` returned HTTP 401 on 2026-11-09; see [MCP-PROTOCOL.md](MCP-PROTOCOL.md). The hosted URL does not read `LOGICMEM_CLIENT_ID`. Pass `client_id` in the tool arguments when that tool's schema has the field. The 2026-10-24 note for `logicframe_memory_recall` did not list `client_id`, and that schema was not re-listed on 2026-11-09.

**Local stdio server.** The JSON below is the `mcpServers` shape used by Claude Desktop's local config and by Cursor's MCP config. This audit did not start either application. Cursor was not in the operator's configured-client notes. Claude was reported as configured; which Claude app was not pinned down here.

```json
{
  "mcpServers": {
    "logicmem": {
      "command": "logicmem-server",
      "env": {
        "LOGICMEM_API_KEY": "lm_your_api_key",
        "LOGICMEM_CLIENT_ID": "quickstart-demo"
      }
    }
  }
}
```

If the client cannot find `logicmem-server`, use the full path from `which logicmem-server` (Windows: `where logicmem-server`), or `"command": "python3", "args": ["-m", "logicmem.cli"]` with the same `env`. On Windows, `py` may be the launcher instead of `python3`. Both `logicmem-server --help` and `python -m logicmem.cli --help` exited 0 in the local check above.

OpenClaw uses a different file shape (`mcp.servers` in `~/.openclaw/openclaw.json`). That example is in the README, labeled as OpenClaw.

## What's next?

- **[MCP-PROTOCOL.md](MCP-PROTOCOL.md)** — Hosted MCP server reference
- **[A2A-PROTOCOL.md](A2A-PROTOCOL.md)** — Sharing: SDK poll versus hosted listeners
- **[EXAMPLES.md](EXAMPLES.md)** — More examples (explicit voice notes, audit, errors)
- **[SECURITY.md](SECURITY.md)** — Records, auth, and data-handling gaps
