# Production Synthetic Monitoring

**Added:** 2026-06-22 (production readiness audit follow-up)
**Owner:** themis-synthetic-monitor

## What It Does

Probes every public LogicMem endpoint **the way real customer traffic hits it**, on a 60-second loop:

| Surface | Probes |
|---------|--------|
| **Memory HTTP server** (`:8421`) | `/memory/health`, `/memory/stats`, `/memory/audit/verify` |
| **Qdrant vector store** (`:6333`) | `/collections`, `/collections/{name}`, `/readyz` |
| **Customer-facing Cloudflare** | `https://api.logicmem.io/memory/health`, `/memory/stats` |
| **MCP JSON-RPC server** (`:8423`) | `initialize`, `tools/list`, `tools/call logicframe_health`, `tools/call logicframe_memory_recall` |

For each probe the monitor:
- Measures latency in ms
- Validates the response **shape** (not just HTTP 200 — proves the contract still works)
- Records the result to `/root/LogicFrame/logs/synthetic_monitor.jsonl`
- Compares against the last known-good baseline in `synthetic_monitor_state.json`
- Surfaces drift (state flip, latency > 2x, audit chain degradation)
- Writes alerts to memory server via `/memory/log` so the watchdog surfaces them

## What It Caught Already

During build-out on 2026-06-22, the synthetic monitor caught Qdrant
flapping between `up` → `down` between two consecutive probes — exactly
the failure mode the monitor was built to detect before customers see it.

## Running

Cron (Hetzner): every minute.

```cron
* * * * * /usr/bin/python3 /root/LogicFrame/scripts/synthetic_monitor.py >> /var/log/synthetic_monitor_cron.log 2>&1
```

Ad-hoc:
```bash
python3 /root/LogicFrame/scripts/synthetic_monitor.py
```

## Adding a New Probe

Append to one of the lists in `synthetic_monitor.py`:

- `INTERNAL_ENDPOINTS` — localhost probes
- `EXTERNAL_ENDPOINTS` — public Cloudflare-proxied endpoints
- `MCP_TOOL_PROBES` — JSON-RPC `tools/call` exercises

Each probe is a dict with: `name`, `url`, `method`, and either
`expected_keys` (for JSON) or `expected_text` (for plaintext like
qdrant's `/readyz`). `headers` for auth, `jsonrpc_body` for MCP.

## Files

| Path | Purpose |
|------|---------|
| `monitoring/synthetic_monitor.py` | The script |
| `/root/LogicFrame/logs/synthetic_monitor.jsonl` | Per-probe results (every minute) |
| `/root/LogicFrame/logs/synthetic_monitor_state.json` | Last known-good baseline (drift detection) |
| `/root/LogicFrame/logs/synthetic_monitor_alerts.jsonl` | Alert events |
| `/var/log/synthetic_monitor_cron.log` | Cron stdout/stderr |

## Authentication

Memory server probes use `X-Cron-Secret: themis-cron-2026` for admin
read access (memory/stats + memory/audit/verify). MCP `tools/call`
probes use `X-Agent-ID: themis-synthetic-monitor` so the server can
attribute and rate-limit synthetic traffic separately from real users.
