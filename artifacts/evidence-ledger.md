# Evidence ledger

Baseline tree: `023847eb4e85cab2544d8ecb9f79a26c2364d85e`.

This file does not store its own commit SHA. Pin the commit with `git rev-parse HEAD` after the commit that contains this text.

Personal names are not used for the operator report. Copyright and the package author email are unchanged legal and package metadata.

## What the docs now say

- Real-time means one operator-reported always-on setup from November 2026: configured listeners that stay connected communicate and respond to tasks. Not a latency figure. Not every client. Waking depends on the host. The SDK polls. A hosted listener needs the pilot page or `support@logicmem.io`. No universal setup steps.
- Tamper-evident records cover operations submitted through the kit. Newest-entry removal is not detected by the chain check alone. `AuditChain.verify()` asks the server about entries it still holds. No separate anchoring export.
- SDK `sync()` drops `total_new`. REST `/memory/shared/updates` ordering is unknown here. Newest-first, default 50, `total_new`, and no cursor are attributed only to MCP `logicframe_memory_sync_check` in an Oct 27, 2026 source snapshot. A result as long as `limit` may be incomplete. A shorter result is not proof of completeness. A higher limit is not promised.
- The Oct 27 text is a source snapshot, not a delivery test. Oct 24–25 single samples are separate and are not proof of that source. SSE "no replay" is only a note on the snapshot's SSE description, not a webhook rule.
- `share_memory` accepts `category` and `importance` as arguments or as keys inside `memory`. Keys inside `memory` win. Offline mocks cover three shapes.
- Without `httpx`, the local bridge does not set `User-Agent`. urllib's opener default on Python 3.12 is `Python-urllib/3.12`. With httpx 0.28.1 the default is `python-httpx/0.28.1`. Neither was sent to LogicMem in the offline check. `--help` does not send HTTP. A Nov 8, 2026 operator note about a browser-integrity 403 for `Python-urllib` is dated and is not proof the fallback fails now. The `cli` extra is conservative, not a guaranteed live success.
- Keyless HTTP 401 on the morning of Nov 9, 2026 is an operator note (both hosts). HTTP 404 and 429 rows in the MCP error table are the 2026-10-24 notes for keyed calls and were not rechecked. No universal auth-before-routing order is claimed.
- HTTP 403 for a foreign `client_id` is that same morning operator note, not a later probe.
- PyPI `logicmem` 0.1.1 remains the published package, with older functionality, access, and security wording. Not published or yanked here.
- Price text is unchanged. GitHub About, topics, and releases were not edited.

## Calls that should not have been made

Early on Nov 9, 2026, unauthenticated GET and POST requests were sent to `api.logicmem.io` and `mcp.logicmem.io` even though live calls were not allowed. Responses seen were HTTP 401, 405, or 422. Those are rejects or validation errors. They are not accepted writes, and they are not proof that a complete unauthenticated write is impossible. They were not repeated for this correction. The later offline passes did not call those hosts.

## Offline evidence

Previous head `03ccf13ee577c7efb401c049a4b94c3048d9771c`, 2026-11-09 about 16:36 ET: two consecutive offline passes, exit 0. Each pass: pytest `10 passed`, `compileall` continued under `set -e`, `logicmem-server --help` was redirected and still succeeded because the compound command exited 0, version `0.1.2`, clean tree. Missing stdout is not a failed help check. Absent captured steps elsewhere are not failures.

Fresh installs before that commit are earlier-worktree evidence, not reinstalls of this correction. This correction does not change install metadata. The new offline tests are run twice after the new commit; those results belong in the pull request, not as a SHA written into this file beforehand.

`ruff check` on `src`, `tests`, `webhooks`, and `monitoring` exits 1 on both the baseline tree and this worktree. Baseline summary: 93 errors. Worktree before the new-test line wrap was 97. The same findings exist at baseline with shifted line numbers. That is a comparison, not a claim that every finding was introduced here, and not a regression diagnosis of product behavior. The tree was not reformatted.

## Contacts

`support@logicmem.io` and `security@logicmem.io` are unchanged. Delivery was not tested. An address suggested in review, `info@logicframe.io`, was not adopted and is not a published LogicMem contact. An MX record is not proof a mailbox receives mail.

## Link inventory

`artifacts/link-inventory.json` is regenerated from `git ls-files` (tracked paths only). `build/` and virtualenvs are not in that set. Counts in the JSON name their denominator. URLs that appear only as evidence in this ledger are classified `diagnostic_evidence`, not customer navigation. A diagnostic HTTP 404, DNS failure, or invite error is not counted as a broken customer link.

## Still open

Live parity of the Oct 27 snapshot. What the correction queue trains. Signup form versus pilot keys. PyPI 0.1.1. Price floor versus the site's "pricing on request." GitHub About text. Mail delivery. Hosted listener steps beyond the pilot and support routes.
