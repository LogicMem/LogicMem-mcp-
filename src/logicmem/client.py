"""
LogicMem Client
================
Main entry point for the LogicMem SDK.
"""

from __future__ import annotations

import requests
from typing import Any

from logicmem.exceptions import (
    LogicMemError,
    AuthenticationError,
    MemoryNotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    NetworkError,
)


class LogicMem:
    """
    Main client for LogicMem — AI agent memory infrastructure.

    Connect to the LogicMem memory server and store, search, and reason
    over persistent agent memories.

    Args:
        api_key: Your LogicMem API key.
        base_url: Base URL of the LogicMem server.
                  Defaults to the production Hetzner server.
        timeout: Request timeout in seconds. Defaults to 30.

    Example:
        >>> from logicmem import LogicMem
        >>> memory = LogicMem(api_key="lm_your_api_key")
        >>> memory.log("User prefers urgent messages via Telegram", category="preference")
        >>> results = memory.recall("user communication preferences")
    """

    DEFAULT_BASE_URL = "http://5.78.202.35:8421"
    DEFAULT_TIMEOUT = 30

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        if not api_key:
            raise ValidationError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-Cron-Secret": self.api_key,
        })

    # -------------------------------------------------------------------------
    # Core Memory Operations
    # -------------------------------------------------------------------------

    def log(
        self,
        text: str,
        category: str = "general",
        importance: int = 7,
        client_id: str = "default",
        tags: list[str] | None = None,
        source: str = "sdk",
    ) -> dict[str, Any]:
        """
        Store a new memory entry.

        Args:
            text: The memory content to store. Be specific — include who,
                  what, when, and why.
            category: Category for the memory. Options: general, preference,
                      task, decision, contract, correction, interaction,
                      complaint. Defaults to "general".
            importance: Importance on a scale of 1-10. Higher values are
                        stored with stronger embeddings. Defaults to 7.
            client_id: Client/agent identifier for multi-tenant isolation.
                       Defaults to "default".
            tags: Optional list of string tags for the memory.
            source: Source of the memory (e.g., "voice_call", "chat",
                    "email", "manual"). Defaults to "sdk".

        Returns:
            dict with at least ``entry_id`` and ``created_at`` fields.

        Raises:
            AuthenticationError: If the API key is invalid.
            ValidationError: If parameters fail validation.
            RateLimitError: If the rate limit is exceeded.
            ServerError: If the server returns a 5xx error.
        """
        payload: dict[str, Any] = {
            "text": text,
            "category": category,
            "importance": importance,
            "client_id": client_id,
            "source": source,
        }
        if tags:
            payload["tags"] = tags

        return self._post("/memory/log", payload)

    def recall(
        self,
        query: str,
        limit: int = 5,
        client_id: str = "default",
    ) -> list[dict[str, Any]]:
        """
        Search for relevant memories using natural language.

        Uses vector similarity search to find memories related to the query.

        Args:
            query: Natural language search query.
            limit: Maximum number of results to return. Defaults to 5.
            client_id: Client/agent identifier. Defaults to "default".

        Returns:
            List of memory entries, each containing ``entry_id``, ``text``,
            ``category``, ``importance``, ``score`` (relevance 0-1),
            ``created_at``, and optionally ``tags``.

        Raises:
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
            ServerError: If the server returns a 5xx error.
        """
        payload = {
            "query": query,
            "limit": limit,
            "client_id": client_id,
        }
        result = self._post("/memory/recall", payload)
        # Normalize response: server may return {"entries": [...]} or a list
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            if "entries" in result:
                return result["entries"]
            if "results" in result:
                return result["results"]
        return []

    def session(self, client_id: str = "default") -> dict[str, Any]:
        """
        Get a full context briefing for the current session.

        Fires recall + sentiment + constraints + intelligence + gaps
        in parallel and returns a comprehensive context summary.

        Args:
            client_id: Client/agent identifier. Defaults to "default".

        Returns:
            dict containing ``relationship_trend``, ``confidence``,
            ``conversation_openers``, ``active_constraints``, and
            ``critical_gaps``.
        """
        payload = {"client_id": client_id}
        return self._post("/memory/session", payload)

    def health(self) -> dict[str, Any]:
        """
        Check the health of the LogicMem server.

        Returns:
            dict with ``status``, ``version``, and optionally ``latency_ms``.
        """
        return self._post("/memory/health", {})

    # -------------------------------------------------------------------------
    # Reasoning Engine
    # -------------------------------------------------------------------------

    def reason(
        self,
        question: str,
        context: str = "",
        mode: str = "deep",
        max_steps: int = 5,
    ) -> dict[str, Any]:
        """
        Multi-step reasoning that consults memory at each step.

        Reasons step-by-step, storing the trace for future reference.

        Args:
            question: The question or problem to reason about.
            context: Additional context to include in reasoning.
            mode: Reasoning depth — "fast" (2 steps), "deep" (5 steps),
                  "exhaustive" (10 steps). Defaults to "deep".
            max_steps: Override for number of reasoning steps.

        Returns:
            dict with ``answer``, ``steps`` (list of reasoning traces),
            and ``confidence``.
        """
        payload = {
            "question": question,
            "context": context,
            "mode": mode,
            "max_steps": max_steps,
        }
        return self._post("/memory/reason", payload)

    def verify(self, claim: str) -> dict[str, Any]:
        """
        Verify a claim against stored facts.

        Returns whether the claim is supported, contradicted, or
        inconclusive based on memory.

        Args:
            claim: The statement to verify.

        Returns:
            dict with ``verdict`` ("supported", "contradicted",
            "inconclusive"), ``evidence`` (list of supporting
            or contradicting entries), and ``confidence``.
        """
        payload = {"claim": claim}
        return self._post("/memory/verify", payload)

    def reflect(
        self,
        draft_answer: str,
        question: str,
        memory_query: str = "",
    ) -> dict[str, Any]:
        """
        Self-critique: evaluate a draft answer against retrieved facts.

        Identifies weaknesses, gaps, and suggests improvements before
        committing to an answer.

        Args:
            draft_answer: The proposed answer to evaluate.
            question: The original user question.
            memory_query: Query used to retrieve supporting memories.

        Returns:
            dict with ``score`` (0-100), ``gaps`` (list of weaknesses),
            ``suggestions`` (list of improvements), and ``verdict``.
        """
        payload = {
            "draft_answer": draft_answer,
            "question": question,
            "memory_query": memory_query,
        }
        return self._post("/memory/reflect", payload)

    def intelligence(self, client_id: str = "default") -> dict[str, Any]:
        """
        Run proactive intelligence analysis.

        Detects patterns, overdue items, and contradictions in memory.

        Args:
            client_id: Client/agent identifier. Defaults to "default".

        Returns:
            dict with ``patterns``, ``overdue_items``,
            ``contradictions``, and ``recommendations``.
        """
        payload = {"client_id": client_id}
        return self._post("/memory/intelligence", payload)

    # -------------------------------------------------------------------------
    # Internal HTTP helpers
    # -------------------------------------------------------------------------

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Make a POST request to the LogicMem server.

        Handles error mapping and response normalization.
        """
        url = f"{self.base_url}{path}"
        try:
            resp = self._session.post(
                url,
                json=payload,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out after {self.timeout}s: {e}")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {e}")

        if resp.status_code == 401:
            raise AuthenticationError("Invalid or missing API key", status_code=401)
        if resp.status_code == 404:
            raise MemoryNotFoundError(f"Resource not found: {path}", status_code=404)
        if resp.status_code == 429:
            raise RateLimitError("Rate limit exceeded", status_code=429)
        if resp.status_code >= 500:
            raise ServerError(
                f"Server error: {resp.status_code}", status_code=resp.status_code
            )
        if resp.status_code >= 400:
            try:
                body = resp.json()
                msg = body.get("error", body.get("message", resp.text))
            except Exception:
                msg = resp.text
            raise ValidationError(msg, status_code=resp.status_code)

        try:
            return resp.json()
        except Exception as e:
            raise LogicMemError(f"Failed to parse server response: {e}")

    def __repr__(self) -> str:
        return f"LogicMem(base_url={self.base_url!r})"
