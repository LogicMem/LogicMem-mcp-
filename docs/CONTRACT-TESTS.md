# MCP Contract Tests

**Added:** 2026-06-22

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

## Running

Point the harness at a LogicMem server you run (it defaults to `localhost`):

```bash
python3 tests/contract_tests.py
```

Exit code 0 on all-pass, 1 on any failure.

## Adding a New Test

Tests are grouped by category in `test_*()` functions in
`tests/contract_tests.py`. Each test uses the `run_test(category, name)`
helper which records the result and exposes `t.pass_(**details)` or
`t.fail(error)`.
