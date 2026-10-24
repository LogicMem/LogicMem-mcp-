# Embedding Fallback Chain

> How the LogicMem server keeps memory writes working when an external
> embedding provider is down. This runs on the server, not in this SDK.

## The chain

When you call `memory.log()`, the server computes an embedding for the text.
It tries these providers in order and uses the first one that succeeds:

| Tier | Provider | Needs |
|------|----------|-------|
| 1 | Cohere `embed-v4.0` | Cohere API + network |
| 1b | Cohere `embed-english-v3.0` (padded to the same vector size) | Cohere API + network |
| 2 | Ollama `nomic-embed-text`, run locally on the server (padded) | Local Ollama service |
| 3 | Deterministic token-hash vector | Nothing external |

Tier 3 is the last resort. It is not semantic, but it has no external dependencies, so writes still succeed.

## What this means for you

- **Cohere up:** best recall quality.
- **Cohere down, Ollama up:** writes succeed; recall quality is lower, because padded vectors from a smaller model compare less well.
- **Cohere and Ollama down:** writes succeed; recall works mainly for exact or partial text matches.

You can see which embedding model the server is currently using in the public health check: `GET https://api.logicmem.io/memory/health` (the `embedding` field).

If recall quality looks degraded for a while, check the [Cohere status page](https://status.cohere.com/) and contact support@logicmem.io.
