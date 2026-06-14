"""
Reasoning Engine
================
Multi-step reasoning, verification, and self-reflection tools.
"""

from __future__ import annotations

from typing import Any


class ReasoningEngine:
    """
    High-level reasoning tools that consult memory during thought.

    In most cases, use the methods on :class:`logicmem.LogicMem` directly.
    """

    def __init__(self, client: Any):
        self._client = client

    def reason(
        self,
        question: str,
        context: str = "",
        mode: str = "deep",
        max_steps: int = 5,
    ) -> dict[str, Any]:
        """
        Multi-step reasoning. Alias for :meth:`LogicMem.reason`.
        """
        return self._client.reason(
            question=question,
            context=context,
            mode=mode,
            max_steps=max_steps,
        )

    def verify(self, claim: str) -> dict[str, Any]:
        """
        Verify a claim against stored facts.
        Alias for :meth:`LogicMem.verify`.
        """
        return self._client.verify(claim=claim)

    def reflect(
        self,
        draft_answer: str,
        question: str,
        memory_query: str = "",
    ) -> dict[str, Any]:
        """
        Self-critique a draft answer against memory.
        Alias for :meth:`LogicMem.reflect`.
        """
        return self._client.reflect(
            draft_answer=draft_answer,
            question=question,
            memory_query=memory_query,
        )

    def confidence(
        self,
        question: str,
        answer: str,
    ) -> dict[str, Any]:
        """
        Compute a confidence score (0-100) for an answer,
        based on memory coverage, evidence strength, and reasoning depth.

        Args:
            question: The original question.
            answer: The proposed answer.

        Returns:
            dict with ``score`` (0-100) and ``factors`` breakdown.
        """
        return self._client._post("/memory/confidence", {
            "question": question,
            "answer": answer,
        })

    def trace(self, session_id: str = "") -> dict[str, Any]:
        """
        Retrieve a previous reasoning trace by session ID.

        Useful for auditing AI reasoning steps.
        """
        return self._client._post("/memory/trace", {"session_id": session_id})
