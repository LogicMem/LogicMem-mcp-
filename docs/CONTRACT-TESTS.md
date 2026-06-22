# MCP Contract Tests

**Added:** 2026-06-22
**Owner:** contract-test

## What They Catch

Real MCP clients (OpenClaw, Claude Desktop, stdio bridges) hit the
MCP server. If the contract drifts (tool renames, schema changes,
auth model breaks), their integrations break silently. Contract tests
catch this **before customers see it**.

## Tests Included

| Category | Tests |
|----------|-------|
| **MCP protocol** | `initialize` handshake, `tools/list` shape, unknown method → 404 |
| **Memory core** | `memory_log` ↔ `memory_recall` round-trip, `memory_stats` shape |
| **Voice platforms** | VAPI (8 required tools), Retell (7), Bland (6) — presence + schema validity |
| **Auth** | `tools/list` is public, `tools/call` requires auth, `X-Agent-ID` works |

## Bugs Caught Already

### 1. MCP spec violation: `input_schema` → `inputSchema`

**Found:** 2026-06-22 during initial run of `tools_list_shape` test.

90 of 108 MCP tools used `input_schema` (snake_case) instead of
`inputSchema` (camelCase). Per the MCP spec, the field is `inputSchema`.

**Impact:** Real MCP clients couldn't validate tool inputs because
the schema lookup was failing on every call.

**Fix:** Renamed `input_schema` → `inputSchema` in
`mcp_server_v2_full.py` (108 occurrences total). MCP server restarted.
All contract tests now pass on the `inputSchema` field.

**Action still needed:** Update SDK + README examples to use `inputSchema`.

### 2. `database is locked` errors under load

**Found:** 2026-06-22, caught by the synthetic monitor + contract
tests running concurrently.

The audit chain SQLite DB (268MB, 65K pages) is being written to on
every `memory_log` and read on every `/memory/health` call. Default
SQLite locking is "rollback journal" mode which doesn't allow
concurrent readers + writers.

**Impact:** Health endpoint returned 500 intermittently. MCP tools
that internally called `/memory/stats` failed. Customer-facing
endpoints saw timeouts.

**Fix:** Patched `memory_server_v2.py` to enable WAL mode +
`busy_timeout=30000` on every SQLite connection. **This patch is
risky and is being evaluated for revert** — see "Caveats" below.

### 3. 78.4% decryption failures on recall

**Found:** 2026-06-22 via contract test `log_recall_roundtrip`
returning `[decryption failed]` instead of newly logged text.

Pattern: failures cluster in `tier=episodic, category=general,
importance ≤ 5`. Spans April → June 2026. This is **NOT** related
to the contract tests themselves — it's a pre-existing encryption
layer issue uncovered when the test forced a recall round-trip.

**Status:** Root cause under investigation. Likely a key-derivation
or tier-specific encryption rotation that didn't re-encrypt existing
entries. See `decryption_failure_analysis.md` for the trace.

## Running

Cron (Hetzner): not yet wired (manual for now).

Ad-hoc:
```bash
python3 /root/LogicFrame/scripts/contract_tests.py
```

Output:
```
Contract Tests: 12/14 passed
  ✅ [mcp_protocol    ] initialize_handshake
  ✅ [mcp_protocol    ] tools_list_shape
  ✅ [mcp_protocol    ] unknown_method_404
  ❌ [memory_core     ] log_recall_roundtrip  — recall returned decryption failures
  ❌ [memory_core     ] stats_shape  — HTTP 500
  ✅ [vapi_contract   ] vapi_required_tools_present
  ✅ [vapi_contract   ] vapi_schema_validity
  ... (8 more)
```

Exit code 0 on all-pass, 1 on any failure.

## Files

| Path | Purpose |
|------|---------|
| `tests/contract_tests.py` | Test harness |
| `/root/LogicFrame/logs/contract_tests.jsonl` | Per-run results |
| `/root/LogicFrame/logs/contract_tests_latest.json` | Latest run (pretty) |

## Adding a New Test

Tests are grouped by category in `test_*()` functions in
`contract_tests.py`. Each test uses the `run_test(category, name)`
helper which records the result and exposes `t.pass_(**details)` or
`t.fail(error)`.

## Caveats

**The WAL patch (bug #2) is risky.** Under sustained load (synthetic
monitor probing every 60s + contract tests + any real traffic), the
memory server spiked to 14GB memory and stopped responding. It was
recovered via `kill -9` + restart. The patch may need to be reverted
pending a deeper refactor of the audit chain verifier.

**Decision pending:** keep WAL patch (current state, risky) vs.
revert (back to intermittent 500s under load) vs. refactor verifier
to not block (best long-term answer, not done yet).