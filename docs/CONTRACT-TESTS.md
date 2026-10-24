# MCP Contract Tests

**Added:** 2026-06-22

## What They Catch

Real MCP clients (OpenClaw, Claude Desktop, stdio bridges) hit the
MCP server. If the contract drifts (tool renames, schema changes,
auth model breaks), their integrations break silently. Contract tests
catch this drift when you run them.

## Tests Included

| Category | Tests |
|----------|-------|
| **MCP protocol** | `initialize` handshake, `tools/list` shape, unknown method → 404 |
| **Memory core** | `memory_log` ↔ `memory_recall` round-trip, `memory_stats` shape |
| **Voice platforms** | VAPI (9 required tools), Retell (7), Bland (6) — presence + schema validity |
| **Auth** | `tools/list` is public, `tools/call` requires auth, `X-Agent-ID` works |

## Running

The harness defaults to a LogicMem server on `localhost` (MCP on port 8423,
memory API on 8421) and writes results under `/root/LogicFrame/logs`.
Override with environment variables:

```bash
LOGICMEM_MCP_URL=http://localhost:8423/mcp \
LOGICMEM_MEMORY_URL=http://localhost:8421 \
LOGICMEM_TEST_LOG_DIR=./test-logs \
python3 tests/contract_tests.py
```

This is a standalone script, not a pytest suite, and the memory round-trip
needs a server that accepts unauthenticated local calls, so it is meant for
LogicMem's own servers.

Exit code 0 on all-pass, 1 on any failure.

## Adding a New Test

Tests are grouped by category in `test_*()` functions in
`tests/contract_tests.py`. Each test uses the `run_test(category, name)`
helper which records the result and exposes `t.pass_(**details)` or
`t.fail(error)`.
