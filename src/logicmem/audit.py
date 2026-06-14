"""
Audit Chain Tools
=================
Immutable audit trail verification for LogicMem.
Every operation is logged to a cryptographically linked hash chain.
"""

from __future__ import annotations

from typing import Any


class AuditChain:
    """
    Tools for verifying the integrity of the LogicMem audit chain.

    The audit chain is an immutable, hash-linked ledger of all memory
    operations. Use these tools to verify that no memory has been
    tampered with.
    """

    def __init__(self, client: Any):
        self._client = client

    def verify(self) -> dict[str, Any]:
        """
        Verify the integrity of the entire audit chain.

        Confirms that no memory entries have been tampered with or deleted
        since they were logged.

        Returns:
            dict with ``valid`` (bool), ``chain_length``,
            ``last_hash``, and ``verified_at``.
        """
        return self._client._post("/audit/verify", {})

    def log_correction(
        self,
        original: str,
        corrected: str,
        reason: str = "",
    ) -> dict[str, Any]:
        """
        Log a correction — feeds the DPO training pipeline.

        Every correction improves the underlying model. Use this when
        the agent makes a mistake and you want to prevent it in future.

        Args:
            original: The incorrect statement or action.
            corrected: The correct statement or action.
            reason: Why the correction was made.

        Returns:
            dict with ``correction_id``, ``logged_at``.
        """
        payload = {
            "original": original,
            "corrected": corrected,
            "reason": reason,
        }
        return self._client._post("/audit/correction", payload)

    def dpo_stats(self) -> dict[str, Any]:
        """
        Get DPO training statistics.

        Returns how many correction pairs are ready for training
        and the health of the training pipeline.
        """
        return self._client._post("/audit/dpo_stats", {})

    def self_heal(self) -> dict[str, Any]:
        """
        Run system diagnostics on the LogicMem memory server.

        Detects and attempts to repair common issues with memory
        storage, retrieval, and the audit chain.
        """
        return self._client._post("/audit/self_heal", {})

    def health(self) -> dict[str, Any]:
        """
        Check the health of the audit chain subsystem.

        Returns:
            dict with ``status``, ``chain_height``, ``last_append``.
        """
        return self._client._post("/audit/health", {})
