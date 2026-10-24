# Changelog

## 0.1.2 — 2026-10-24

Fixes
- `LogicMem.health()` now uses GET (the server rejects POST with 405).
- `AuditChain.health()` now uses GET `/memory/audit` (POST returned 405).
- `A2AClient.sync()` now reads `/memory/shared/updates` and filters out your own entries; it previously called an endpoint that always returned 422. Added `client_id` and `limit` arguments.
- `A2AClient.share_memory()` now uses `category` / `importance` from the `memory` dict when present.
- `ReasoningEngine.confidence()` and `.trace()` now raise `NotImplementedError` pointing to the hosted MCP tools (the REST endpoints they called do not exist and returned 404).
- `logicmem-server`: added `--help`, `--version`, `--api-key`, `--server-url`, `--client-id` (previously `--help` was ignored and the server started); `python -m logicmem.cli` now works; fixed tools that lost `client_id` (list agents and sync crashed), heartbeat now sends fields in the query string, stats uses GET, list agents uses `/memory/org/agents`, outcome takes `entry_id` + `score`; removed `logicmem_memory_reflect` (its endpoint does not exist); server version now matches the package.
- Removed dead duplicate HTTP helper code in `client.py`.
- `ValidationError` and `NetworkError` are now exported from `logicmem`.
- Contract tests: server URLs and log directory can be set by environment variables.

Docs
- Corrected install steps, API-key instructions (keys are issued to pilot teams), tool lists, A2A endpoints and examples to match the code and the live server; removed unverifiable claims.

## 0.1.1

- Initial public release.
