# Evidence ledger — LogicMem public client kit

Baseline `main` SHA: `023847eb4e85cab2544d8ecb9f79a26c2364d85e` (2026-10-24, merge of PR 6).

This file is part of the corrective worktree. The final commit SHA is `git rev-parse HEAD` after that commit. It is not on `main` until a human merges it.

Scope: the public repository only. No private server source is copied here. No package was published. No GitHub setting, topic, description, or credential was changed. No tenant, staging, or production write was made for the patched checks. Reads cited below are earlier the same day or from the named reviewer notes.

## What this branch changes

- Public wording so agent-to-agent sharing and the tamper-evident record are both in the lead, scoped to operations submitted through the kit.
- SDK polling versus hosted listeners, with Ed Creed's Leonard, Linus, and Claude report kept as one operator's setup and not as a latency benchmark.
- Two hash-linked records from an Oct 27, 2026 snapshot, without calling recall unaudited and without claiming live parity.
- Keyless MCP `initialize` / `tools/list` no longer described as public.
- Quickstart `client_id` aligned. Synthetic ids replace `ed_creed` in examples and in the internal harness defaults.
- `MemoryTools.stats()` uses GET.
- Dispatcher docstring matches this file's 5-attempt queue and is not equated with a different hosted outbox.
- CONTRIBUTING install steps match a local run. Issues URL is linked.
- PyPI 0.1.1 warning widened. The package on PyPI is unchanged.

## Runnable checks in this VM

| Check | Result |
| --- | --- |
| `pip install -e ".[dev]"` then `logicmem-server --help`, `python -m logicmem.cli --help` | Exit 0. `httpx` present because the dev extra depends on it. Python 3.12.3. Version 0.1.2. |
| `pip install -e .` (no extras) then the same help commands | Exit 0. `httpx` absent. Server still printed help. |
| `pip install /workspace` in a fresh venv | Imports 0.1.2. `logicmem-server --version` prints `logicmem 0.1.2`. |
| `pip install logicmem @ git+https://github.com/LogicMem/LogicMem-mcp-.git` | Succeeds and imports 0.1.2 from GitHub `main`, which does **not** include this branch. |
| `pytest tests/test_local_kit.py` | 10 passed after the fixes in this worktree (see the commit's post-check note if a later run differs). |
| `compileall` of `src`, `tests`, `webhooks`, `monitoring` | Exit 0. |
| `tests/contract_tests.py` against localhost or the public host | **Not run.** The harness writes. Default target is localhost, which is not running here. Public URL returned keyless HTTP 401 and must not be used as the target. |
| `monitoring/synthetic_monitor.py` | **Not run.** It probes production URLs and can POST an alert. |
| Hosted `verify`, share, sync, webhook delivery, authenticated MCP session | **Not run.** No key was used. No tenant call. |

`ruff 0.17.4` reports many existing style findings in files this branch did not reformat. That is pre-existing lint debt, not a clean bill of health, and not a gate this branch claimed to clear.

## Link inventory

`artifacts/link-inventory.json` lists every `http`, `mailto`, and Markdown link in `*.md`, `*.py`, and `*.toml`, excluding `.git`, virtualenvs, and pytest cache.

Regenerated from this worktree: see the JSON `count` field. Relative targets in that file resolved to existing files, and fragments resolved to heading slugs. Localhost URLs in the ops scripts were not probed. Mailto delivery was not tested.

Public GETs on 2026-11-09 (about 21:15–21:28 UTC) that this audit made itself:

- `https://logicmem.io/`, `/quickstart/`, `/design-partner/`, `/eu-ai-act-article-12/`: HTTP 200. Design-partner title is a 30-day pilot page and the visible price line is "pricing on request."
- `https://api.logicmem.io/` followed a redirect to `/mem/signup` (account form). Not submitted.
- `GET /memory/health`: HTTP 200, `embedding` `embed-v4.0`.
- `GET /memory/stats`: HTTP 401. `POST /memory/stats`: HTTP 405.
- `https://mcp.logicmem.io/mcp` keyless GET and keyless POST `initialize`, `tools/list`, and an unknown method: HTTP 401.
- `https://pypi.org/pypi/logicmem/json`: version 0.1.1 only (plus 0.1.0). URLs point at archived `CreedLab/logicmem-mcp` (HTTP 200, archived) and `docs.logicmem.io`.
- `docs.logicmem.io` from this host: DNS failure (`curl` exit 6, "Could not resolve host"). Not recorded as HTTP 404. Other reviewers, via a proxy, reported TLS EOF or HTTP 500. Treat the host as unavailable from the machines that checked, not as a single global status code.
- `https://discord.com/api/v9/invites/logicmem`: HTTP 404 body `Unknown Invite` code 10006. `https://discord.com/invite/logicmem`: HTTP 200 generic shell. The invite is not linked from this repo. Not added.
- `https://a2a-protocol.org/`: HTTP 200, Agent2Agent protocol. `https://google.github.io/A2A/`: HTTP 404.
- Shields badges, including the replacement `MCP-server` badge: HTTP 200 SVG.
- `openssl s_client` to `api.logicmem.io`, `mcp.logicmem.io`, `logicmem.io`: TLS 1.3, `TLS_AES_256_GCM_SHA384`, verify return code 0.

## GitHub surfaces at the baseline (read-only)

| Surface | Result |
| --- | --- |
| About description | "Python SDK and MCP connector for LogicMem: tamper-evident records of what your AI agents did." **Not edited.** A scoped description is a proposal only. |
| Homepage | `https://logicmem.io` |
| Topics | `ai-agents`, `audit-log`, `mcp`, `python-sdk`, `tamper-evident`. Not edited. Trailing hyphen in the repo name is not treated as a defect. |
| License | MIT. `LICENSE` copyright 2026 LogicFrame LLC. |
| Security policy | Enabled. Renders `docs/SECURITY.md`. Root `SECURITY.md` is absent. |
| Issues | Enabled. No open issues were listed. |
| Discussions | Enabled. Zero threads. Not a broken route. No discussion was created. |
| Wiki | Feature enabled. REST wiki API HTTP 404 (no pages). Browser `/wiki` redirects to the repository home. |
| GitHub Pages | `has_pages` false. Pages API HTTP 404. |
| Releases and tags | Empty. Version 0.1.2 in `pyproject.toml` has no tag. Tagging is not done here. |
| Code scanning alerts | HTTP 403 for this token. Not a pass. |
| Code of conduct, issue templates, PR template | Absent. Not added. Absence is not a broken contact route. |

## Reviewer dispositions

Severities in the reviews are triage labels. They are not, by themselves, product defects. Shared items are listed once, with the other reviewers named.

| Topic | Reviewers | Disposition |
| --- | --- | --- |
| Opening over-claims "what your AI did" | Maggie F1, F9; Nigel F2, F3; Victor H3; Piper v3 #2; Rex F7 | **Changed.** Lead is sharing plus a re-checkable record of submitted operations. Newest-entry and partial-coverage caveats stay. "Prove what your AI did" is not the headline. Piper's suggested headline still said "what your AI agents did" and was not copied verbatim. |
| Quickstart has no share, check-in, and verify, and no inspectable output | Maggie F2; Piper D4; Rex F11 | **Changed.** Script shares, `sync`s, and calls `verify()`. Stdio example sets `LOGICMEM_CLIENT_ID` to the same synthetic id. The sample block is labeled an illustrative fixture. It was not returned by the server. Local `--help` output was produced on this VM. |
| "Nothing is pushed" | Maggie F3; Victor H1; Rex F4 | **Changed.** SDK polls. Hosted listeners are separate and dated. Ed's always-on listeners stay in the text. No "instant", no wake-all, no delivery guarantee, no published latency. |
| Which operations are on a hash chain; recall | Nigel F4; Rex F3 | **Scoped.** Two records from the Oct 27 snapshot. Recall is in the audit-log side of that snapshot and not in `HASH_CHAIN_OPS`. Not re-read here (server repo HTTP 404 to this credential). Not stated as current production fact. MCP two-chain wording kept. |
| Catch-up newest 50 and checkpoints | Rex F5; original audit hint | **Documented for the client and attributed for the snapshot.** No cursor invented. |
| Webhook "won't lose events" | Victor H2; Rex F4 | **Docstring corrected to this file.** 5 attempts plus a dead-letter file. Hosted 12 attempts / 7 days kept as a different snapshot. Not equated. No delivery test. |
| DPO / training disclosure | Maggie F7; Nigel F7; Victor M2; Rex F9 | **Kept the queue wording.** SECURITY states the gap. No retention, opt-out, or tenant-training policy invented. |
| Keyless initialize/tools/list called public | Rex F8; this audit's 401s | **Removed.** Morning both-host note and this audit's later `mcp.logicmem.io` check are both cited. Authenticated session and Nov 8 header list are labeled not replayed. Contract harness text no longer pretends the public host matched the localhost expectation. |
| `client_id` / agent id / `is_private` | Rex F1, F2, F6 | **Clarified without a bypass claim.** Examples use `demo-tenant` and `quickstart-demo`. Dated 403 kept. One-key two-tenant example removed. |
| PyPI 0.1.1 stale claims and links | Sage F1; Victor C1; Kelli R12, R13; Piper v3 #1 | **Warning strengthened.** Publish, yank, and metadata edits are **not** done. External follow-up only. |
| Price "$500/mo" vs "on request" | Nigel F1; Piper v3 #4; Victor M1; Sage | **Not changed.** Uneven disclosure. Owner question. |
| Named clients and "any MCP client" / GPT | Maggie F5; Nigel F8; Victor M4; Piper v3 #5; Rex F12 | **Scoped.** OpenClaw JSON labeled and matched to OpenClaw's public config docs (fetched, not executed). Cursor marked untested. Claude reported as configured, app variant unresolved. Codex not treated as ChatGPT. |
| Tool prefix map and share/sync names | Maggie F4; Nigel F6; Sage F3 | **Table added** from this repo's tools plus the 2026-10-24 hosted note. Public re-list blocked by HTTP 401. No renames. |
| No-key path | Maggie F6 | **Local import and `--help` documented** as the no-key check. Signup form not offered as a working eval. No hosted demo was captured. |
| CONTRIBUTING extras and Issues link | Piper v3 #3; Kelli R5 | **Fixed and tested.** |
| TLS 1.3 | Nigel F11; Rex F16; Piper D11 | **Dated** with this audit's handshake. Not a proof that TLS 1.2 is rejected. |
| Ordinary-logs absolute | Nigel F9; Maggie F9 | **Softened.** |
| Internal ops paths and env-var names | Victor M3; Piper v3 #7; Rex F10; Sage | **Labeled internal.** Paths and names kept. Not treated as vulnerabilities. "Proves" in MONITORING changed to a shape check. |
| A2A vs Agent2Agent | Nigel F5; Victor M5; Rex F14 | **Disambiguated** after GET of a2a-protocol.org. |
| Contacts, `info@logicframe.io`, author email | Kelli; Piper v3 (withdrawn) | **Unchanged.** Delivery untested, not a pass. |
| Discord | Kelli R13; Sage | **Not in this repo.** API 10006 vs HTML 200 recorded. No new invite. |
| Signup page vs pilot copy | Sage F2; Kelli R8 | **Described, not resolved.** No form post. |
| Missing CoC, templates, Discussions, wiki, releases, trailing hyphen, topics | Kelli R14–R15; Piper v3 #6 and #8; Sage F4; Victor L1 | **Not changed.** Proposals only. Star count left as GitHub's. |
| License / hosted terms | Victor L3 | **One sentence:** MIT covers this repo; hosted terms are not in the repo. No fake terms URL. |
| Embedding chain and Cohere | Rex F9; health GET | **Pointed at from SECURITY.** Health field matches the tier-1 name only. Fallback not re-traced. TF-IDF removed from the monitor docstring because it contradicted EMBEDDING-FALLBACK and was not verified. |

## Open risks (not cleared)

- Live parity of the Oct 27, 2026 server snapshot (both records, SSE without replay, catch-up shape, webhook outbox).
- Whether `logicframe_correction_log` is the correction audit row, and what the DPO queue trains.
- Authenticated MCP session behavior and the Nov 8 direct-HTTP header list.
- Whether a key may use more than one `client_id`. The 403 is one route on one morning.
- PyPI 0.1.1 still serves the old text until a separate approved release.
- `https://api.logicmem.io/` still shows a signup form. Policy not chosen here.
- Pilot price floor versus the site's "pricing on request."
- Mailbox delivery for `support@` and `security@`.
- `docs.logicmem.io` unavailable from the checkers above, by different failure modes.
- No hosted share/sync/verify transcript. The quickstart fixture is not one.
- GitHub About text still uses the broader "what your AI agents did" line.
- `ruff` is not clean on the existing tree.
- Contract harness and synthetic monitor were not executed.

## Readiness

The branch is a reviewable documentation and small client correction. It is not a claim that every public sentence is now true, and it is not a star-outreach clearance. Independent rechecks should use the final commit SHA, not this baseline.
