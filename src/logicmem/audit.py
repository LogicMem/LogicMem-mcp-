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
        # /memory/audit/verify is a GET endpoint on the server.
        return self._client._get("/memory/audit/verify", {})

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
        return self._client._post("/memory/correction/log", payload)

    def dpo_stats(self) -> dict[str, Any]:
        """
        Get DPO training statistics.

        Returns how many correction pairs are ready for training
        and the health of the training pipeline.

        Note: As of v0.1.1 the production server reports 0 pairs ready
        until enough corrections are logged. The endpoint is live;
        the data accumulates with usage.
        """
        return self._client._post("/memory/dpo/stats", {})

    def run_dpo(self) -> dict[str, Any]:
        """
        Trigger a DPO training run.

        Requires a minimum number of correction pairs (configurable on the
        server). Returns a status dict indicating whether training started.
        """
        return self._client._post("/memory/dpo/run", {})

    def health(self) -> dict[str, Any]:
        """
        Check the health of the audit chain subsystem.

        Returns:
            dict with ``status``, ``chain_height``, ``last_append``.
        """
        return self._client._post("/memory/audit", {})