# Decryption Failure Root Cause Analysis

**Investigation:** 2026-06-22 18:30 CDT
**Scope:** 78.4% of recalled memories (3,855 of 4,915 sampled) return `"[decryption failed]"`
**Severity:** 🔴 **CRITICAL** — customer-facing data integrity issue

## TL;DR

The failing entries were encrypted with a scheme that the **current
memory server code cannot decrypt**. None of the 7 keys in the key
registry can decrypt these entries. The encrypted_text bytes start
with `0x03` (not `0x80` which is Fernet's version byte), and the
length (54 bytes) is too short for Fernet (which produces ~150 bytes
even for "hello world").

The current server code ONLY uses `cryptography.fernet.Fernet` for
encryption (verified via `grep`). So the failing entries were
created by **a different version of the code that no longer exists
in the repo or backups** — likely lost in a refactor before
2026-06-21 (the date of the oldest backup).

## What I Verified

| Check | Result |
|-------|--------|
| Current code imports | ONLY `from cryptography.fernet import Fernet` |
| Current encryption calls | 9 `fernet.encrypt()` call sites, no other crypto |
| Key registry size | 7 keys (incl. auto-added 2026-06-21) |
| Try all 7 keys via Fernet on a failing entry | ❌ ALL FAIL |
| `fix_decryption.py` (existing tool) | Only knows 4 keys, same result |
| Git history of memory_server_v2.py | Single initial commit 2026-06-21, always Fernet |
| `encrypted_text` byte pattern | Starts with `0x03`, NOT Fernet's `0x80` |
| `encrypted_text` length | 54 bytes (too short for Fernet ~150+ bytes) |

## Pattern of Failures

All 378 sampled failures share these traits:
- `tier = "episodic"`
- `category = "general"` (mostly)
- `importance ≤ 5` (mostly 1-3)
- Timestamps: April 4 → June 8, 2026
- `model_used = "ollama-gemma3"` (in some samples)

This looks like a **batch write that went through a different code path**
— possibly an early "verbatim" or "fast_write" path that used
a hand-rolled AES-GCM or simpler scheme to avoid the Fernet overhead.
The code path was refactored away (or never made it into git) and the
entries are now stranded.

## What I Tried

1. ✅ Listed every key in `~/.config/logicframe/key_registry.json`
2. ✅ Tried decrypting sample entries with each key directly via `Fernet(key).decrypt(...)` — all failed
3. ✅ Verified the encrypted bytes are not valid Fernet tokens (wrong version byte, too short)
4. ✅ Verified git history of `memory_server_v2.py` shows only Fernet was ever used in tracked code
5. ❌ Did not find any other encryption helper in `/root/LogicFrame/*.py` or backups
6. ❌ Did not find any backup of the encryption code that produced `0x03` prefix

## What Would Recover the Data

**None of these are available without Ed's input:**

1. **Find the original encryption code** — if it exists anywhere outside `/root/LogicFrame/`. Could be in a different repo, on a different machine, in a code archive, or in someone's head.
2. **Restore from a pre-refactor Qdrant snapshot** — Hostinger has daily snapshots. If we find one from before the schema migration that introduced this different encryption, we can replay the missing entries.
3. **Re-derive the missing key** — if the encryption was actually a known scheme (e.g., AES-GCM with a key derived from the current Fernet key) and we can find the derivation function, we could reconstruct.
4. **Accept the loss** — 78% of memories are unrecoverable. Mark them as `[decryption failed]` permanently in recall responses and surface this to customers as known data loss.

## Recommended Next Step

**Treat as data loss and notify affected customers.** Until we find the
original encryption code (option 1) or a pre-refactor snapshot
(option 2), these memories cannot be recovered.

**Important:** do NOT silently re-encrypt or delete these entries —
they may be the only record of important customer interactions.
A `/memory/recall` should return the literal `"[decryption failed]"`
text (current behavior) so customers can see what's lost.

## What I Added to Detect This Automatically

The synthetic monitor now includes a `decryptability_rate` probe that:

1. Runs a recall query with a fixed test term
2. Counts how many results are `"[decryption failed]"`
3. Alerts if the failure rate exceeds 10%

This will catch any future drift where the decryption rate
drops (e.g., if more keys get rotated, if a new bug introduces
failures, etc).

## Files

- `/Users/themis/.openclaw/workspace/docs/DECRYPTION-FAILURE-ANALYSIS.md` — this document
- `/Users/themis/.openclaw/workspace/scripts/decrypt_diagnose.py` — diagnostic tool used
- `/tmp/key_inspect.py` — key registry inspection tool

## Honest Assessment

I can't fix this without more context from Ed:
- Where did the original encryption code live?
- Do we have Qdrant snapshots from before April 4, 2026?
- Is there a different machine/repo where the encryption helper exists?

If the answer to all three is "no," this is permanent data loss and we
need to figure out customer comms.