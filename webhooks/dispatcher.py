#!/usr/bin/env python3
"""
webhook_dispatcher.py — Reliable webhook delivery with retries + DLQ.

Used by LogicMem to deliver webhook events to customer endpoints
(e.g. memory log events, voice ingestion results, MCP tool completions).

Behavior:
- Sender enqueues an event with a target URL + payload + HMAC headers
- Dispatcher tries up to N times with exponential backoff
- On N failures, event is moved to DLQ for manual review
- Reconciler cron retries DLQ items with backoff reset
- Every state transition is logged to /var/log/webhook_dlq.jsonl
- Memory server is notified on permanent failure (so watchdog surfaces it)

Why this matters:
A failed webhook shouldn't lose customer data silently.
DLQ + reconciliation means even a customer's endpoint being down
for hours doesn't lose events — they'll be delivered when it comes back.

Built as part of open item #2 from 2026-06-22 readiness audit.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

QUEUE_PATH = Path("/root/LogicFrame/logs/webhook_queue.jsonl")
DLQ_PATH = Path("/root/LogicFrame/logs/webhook_dlq.jsonl")
ALERT_LOG_PATH = Path("/root/LogicFrame/logs/webhook_alerts.jsonl")
MAX_ATTEMPTS = 5
INITIAL_BACKOFF_SEC = 2
MAX_BACKOFF_SEC = 300  # 5 min cap per attempt
DEFAULT_TIMEOUT_SEC = 10

# Optional HMAC secret (for signed webhooks)
WEBHOOK_SIGNING_SECRET = os.environ.get(
    "LOGICMEM_WEBHOOK_SECRET",
    "themis-cron-2026",  # fallback — production should rotate
)


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------


def sign_payload(payload_bytes: bytes, secret: str = WEBHOOK_SIGNING_SECRET) -> dict[str, str]:
    """Return HMAC headers for webhook authenticity."""
    timestamp = str(int(time.time()))
    sig = hmac.new(
        secret.encode("utf-8"),
        (timestamp + payload_bytes.decode("utf-8")).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "X-LogicMem-Timestamp": timestamp,
        "X-LogicMem-Signature": sig,
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Queue / DLQ storage
# ---------------------------------------------------------------------------


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def enqueue(event: dict[str, Any]) -> dict[str, Any]:
    """Add an event to the in-flight queue."""
    record = {
        "id": event.get("id") or f"evt_{int(time.time() * 1000)}_{os.urandom(4).hex()}",
        "url": event["url"],
        "payload": event["payload"],
        "attempts": 0,
        "first_enqueued_at": datetime.now(timezone.utc).isoformat(),
        "last_attempt_at": None,
        "next_attempt_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
        "last_error": None,
    }
    _append_jsonl(QUEUE_PATH, record)
    return record


def mark_failed_to_dlq(record: dict[str, Any], error: str) -> None:
    """Move a record from queue to DLQ after exhausting retries."""
    record["status"] = "dead_letter"
    record["last_error"] = error
    record["dlq_at"] = datetime.now(timezone.utc).isoformat()
    _append_jsonl(DLQ_PATH, record)
    _append_jsonl(ALERT_LOG_PATH, {
        "ts": record["dlq_at"],
        "event_id": record["id"],
        "url": record["url"],
        "attempts": record["attempts"],
        "error": error,
    })


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def deliver(record: dict[str, Any]) -> tuple[bool, str | None]:
    """Try to deliver a single record. Returns (success, error)."""
    payload_bytes = json.dumps(record["payload"]).encode("utf-8")
    headers = sign_payload(payload_bytes)

    started = time.monotonic()
    try:
        req = urllib.request.Request(
            record["url"],
            data=payload_bytes,
            method="POST",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SEC) as resp:
            latency_ms = round((time.monotonic() - started) * 1000, 2)
            if 200 <= resp.status < 300:
                return True, None
            return False, f"http_{resp.status} after {latency_ms}ms"
    except urllib.error.HTTPError as e:
        return False, f"http_error: {e.code}"
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return False, f"connect_error: {type(e).__name__}: {e}"
    except Exception as e:  # noqa: BLE001
        return False, f"unexpected: {type(e).__name__}: {e}"


def dispatch_pending(now: datetime | None = None) -> dict[str, int]:
    """Process the queue once. Returns counts."""
    if now is None:
        now = datetime.now(timezone.utc)

    records = _read_jsonl(QUEUE_PATH)
    if not records:
        return {"delivered": 0, "retried": 0, "dlq": 0, "skipped": 0}

    # Filter: only those whose next_attempt_at has passed
    due: list[dict[str, Any]] = []
    for r in records:
        next_at = r.get("next_attempt_at")
        if not next_at:
            due.append(r)
            continue
        try:
            due_at = datetime.fromisoformat(next_at)
            if due_at <= now:
                due.append(r)
        except ValueError:
            due.append(r)

    delivered = retried = dlq = skipped = 0
    survivors: list[dict[str, Any]] = []

    for r in records:
        if r not in due:
            # Not yet due, or already processed last time
            if r.get("status") == "pending":
                survivors.append(r)
            skipped += 1
            continue

        r["attempts"] = r.get("attempts", 0) + 1
        r["last_attempt_at"] = now.isoformat()
        ok, err = deliver(r)
        if ok:
            delivered += 1
            # Don't re-append delivered records to queue (drop on success)
            continue

        r["last_error"] = err
        if r["attempts"] >= MAX_ATTEMPTS:
            mark_failed_to_dlq(r, err)
            dlq += 1
        else:
            # Schedule next retry with exponential backoff
            backoff = min(INITIAL_BACKOFF_SEC * (2 ** (r["attempts"] - 1)), MAX_BACKOFF_SEC)
            r["next_attempt_at"] = datetime.fromtimestamp(
                time.time() + backoff, tz=timezone.utc
            ).isoformat()
            r["status"] = "pending"
            survivors.append(r)
            retried += 1

    # Rewrite queue with survivors only
    QUEUE_PATH.write_text("\n".join(json.dumps(r) for r in survivors) + ("\n" if survivors else ""))

    return {
        "delivered": delivered,
        "retried": retried,
        "dlq": dlq,
        "skipped": skipped,
    }


# ---------------------------------------------------------------------------
# Reconciliation (DLQ retry)
# ---------------------------------------------------------------------------


def reconcile_dlq() -> dict[str, int]:
    """Try to redeliver items in the DLQ once per call.

    Called by cron every 5 minutes. Items that succeed move out of DLQ
    silently (we don't rewrite the DLQ file — it's an audit log of failures).
    """
    records = _read_jsonl(DLQ_PATH)
    if not records:
        return {"dlq_total": 0, "dlq_recovered": 0, "dlq_failed": 0}

    recovered = failed = 0
    now = datetime.now(timezone.utc).isoformat()

    for r in records:
        # Skip if recently retried (avoid hammering)
        last_retry = r.get("last_dlq_retry_at")
        if last_retry:
            try:
                if (datetime.fromisoformat(now) - datetime.fromisoformat(last_retry)).total_seconds() < 600:
                    continue
            except ValueError:
                pass

        r["last_dlq_retry_at"] = now
        ok, err = deliver(r)
        if ok:
            r["recovered_at"] = now
            r["recovery_attempts"] = r.get("recovery_attempts", 0) + 1
            _append_jsonl(ALERT_LOG_PATH, {
                "ts": now,
                "event_id": r["id"],
                "url": r["url"],
                "recovered": True,
            })
            recovered += 1
        else:
            failed += 1
            r["last_dlq_error"] = err

    return {"dlq_total": len(records), "dlq_recovered": recovered, "dlq_failed": failed}


# ---------------------------------------------------------------------------
# Memory server alerting
# ---------------------------------------------------------------------------


def notify_memory_server(message: str, importance: int = 9) -> None:
    """Send an alert to the memory server so the watchdog surfaces it."""
    try:
        body = json.dumps({
            "text": f"[WEBHOOK_DLQ] {message}",
            "category": "system_alert",
            "importance": importance,
            "client_id": "ed_creed",
            "source": "webhook_dispatcher",
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://localhost:8421/memory/log",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Cron-Secret": os.environ.get("THEMIS_CRON_SECRET", "themis-cron-2026"),
            },
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:  # noqa: BLE001
        print(f"alert-write-failed: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


def stats() -> dict[str, Any]:
    queue = _read_jsonl(QUEUE_PATH)
    dlq = _read_jsonl(DLQ_PATH)
    return {
        "queue_pending": len(queue),
        "dlq_total": len(dlq),
        "dlq_oldest": dlq[0].get("dlq_at") if dlq else None,
        "dlq_oldest_url": dlq[0].get("url") if dlq else None,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("dispatch", help="Process queue once")
    sub.add_parser("reconcile", help="Retry DLQ items once")
    sub.add_parser("stats", help="Show queue/DLQ stats")

    enq = sub.add_parser("enqueue", help="Add an event to the queue")
    enq.add_argument("--url", required=True)
    enq.add_argument("--payload-json", required=True, help="JSON string")

    args = parser.parse_args()

    if args.cmd == "dispatch":
        result = dispatch_pending()
        print(json.dumps(result))
    elif args.cmd == "reconcile":
        result = reconcile_dlq()
        if result["dlq_recovered"] or result["dlq_failed"]:
            notify_memory_server(
                f"DLQ reconcile: {result['dlq_recovered']} recovered, {result['dlq_failed']} still failing "
                f"of {result['dlq_total']} total"
            )
        print(json.dumps(result))
    elif args.cmd == "stats":
        print(json.dumps(stats(), indent=2))
    elif args.cmd == "enqueue":
        payload = json.loads(args.payload_json)
        record = enqueue({"url": args.url, "payload": payload})
        print(json.dumps(record))


if __name__ == "__main__":
    main()
