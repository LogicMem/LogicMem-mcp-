# Embedding Fallback Chain

> How LogicMem keeps your memory writes working even when external embedding
> providers go down.

## The 3-Tier Chain

When you call `memory.log()`, the server runs an embedding against the text.
The chain below is tried in order — the first one to succeed wins.

| Tier | Provider | Output Dim | Time | Dependencies |
|------|----------|------------|------|-------------|
| 1 | Cohere `embed-v4.0` | 1536 | ~0.3s | API key + network |
| 1b | Cohere `embed-english-v3.0` | 1024 → padded to 1536 | 1.5s timeout | API key + network |
| 2 | Ollama `nomic-embed-text` (local) | 768 → padded to 1536 | ~0.07s | Ollama running on Hetzner |
| 3 | TF-IDF hash-based (deterministic) | 1536 | ~0.04s | None (Python stdlib only) |

**Tier 3 is the absolute fallback.** It produces a deterministic 1536-dim
vector based on token hashing. Not semantic — but never fails.

## What This Means For You

- **Cohere is up**: best quality, 1536-dim native, ~0.3s latency.
- **Cohere is down, Ollama is up**: ~30% reduced semantic recall quality
  (because the 768-dim embedding is zero-padded to 1536, which artificially
  boosts cosine scores between Ollama-padded entries). All writes succeed.
- **Cohere AND Ollama are down**: writes succeed with token-matching only.
  Recall quality degrades but is functional for exact/partial text matches.

## Inspecting What Tier Served

Every fallback chain decision is logged. To see what tier served your last
request, you can check the model field in the response:

```python
r = memory.log(text="hello world", client_id="my_app")
print(r.get("model_used"))
# "cohere-embed-v4.0" — tier 1
# "ollama-nomic-embed-text-padded" — tier 2
# "tfidf-hash-v1" — tier 3
```

## Resolving Tier-Degraded Recall

If you see lots of `ollama-nomic-embed-text-padded` or `tfidf-hash-v1` in your
audit logs, your customers are getting degraded recall quality. To recover:

1. Check Cohere status: `curl https://status.cohere.com/`
2. Check Hetzner Ollama service: `ssh root@5.78.202.35 'systemctl status ollama'`
3. If Cohere is permanently down for you, contact LogicFrame to migrate to
   a fully self-hosted embedding stack (deferred v2 feature).

## Why This Matters

Voice agent customers running VAPI/Retell/Bland make 3-10 memory ops per
active call. Without tier 2/3 fallbacks, a single Cohere outage would
immediately fail every customer voice session. With this chain, a single
provider outage degrades quality but never breaks the customer experience.

## Related

- `RUNBOOK.md` (internal) — operational procedures for fixing each tier
- `MEMORY.md` — see "Production Readiness Audit 2026-06-21" for the audit
  that motivated this design
