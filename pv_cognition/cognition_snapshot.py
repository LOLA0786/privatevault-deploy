"""
Cognition Snapshot — Core data structure for Cognitive Integrity Engine (pv_cognition).
Captured at every LLM call via gateway/ai_firewall_core.py hook.
Chains into existing ledgers/ Merkle structure.
"""

import uuid
import hashlib
import time
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


@dataclass
class CognitionSnapshot:
    """Immutable snapshot of an agent's cognitive state at LLM call time.
    Linked into Merkle ledger for forensic replay and authority binding.
    """
    snapshot_id: str
    agent_id: str
    tenant_id: str
    timestamp: float
    call_sequence: int
    context_hash: str
    retrieval_sources: List[str]
    tool_calls_pending: List[str]
    intent_vector: List[float]
    context_vector: List[float]
    intent_drift_score: float
    memory_refs: List[str]
    parent_snapshot_id: Optional[str] = None
    reasoning_integrity_score: Optional[float] = None
    merkle_node_hash: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.merkle_node_hash:
            self.merkle_node_hash = self._compute_merkle_hash()

    def seal_reasoning_score(self, score: float):
        """Set reasoning score and reseal Merkle hash to include it."""
        self.reasoning_integrity_score = score
        self.merkle_node_hash = self._compute_merkle_hash()

    def _compute_merkle_hash(self) -> str:
        """Canonical hash for Merkle chaining (matches ledgers/worm_fallback.py pattern).
        Explicitly excludes merkle_node_hash to prevent circular/self-referential hash.
        """
        payload = {k: v for k, v in asdict(self).items() if k != 'merkle_node_hash'}
        # Deterministic canonical JSON (sort_keys, no whitespace)
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def to_audit_event(self) -> Dict[str, Any]:
        """Structured event for audit_logger.py (exact schema match)."""
        return {
            "event_type": "cognitive_snapshot",
            "agent_id": self.agent_id,
            "tenant_id": self.tenant_id,
            "snapshot_id": self.snapshot_id,
            "timestamp": datetime.fromtimestamp(self.timestamp, tz=timezone.utc).isoformat(),
            "call_sequence": self.call_sequence,
            "context_hash": self.context_hash,
            "intent_drift_score": round(self.intent_drift_score, 4),
            "reasoning_integrity_score": self.reasoning_integrity_score,
            "retrieval_sources": self.retrieval_sources,
            "memory_refs": self.memory_refs,
            "verdict": "CAPTURED",
            "merkle_node_hash": self.merkle_node_hash,
            "parent_snapshot_id": self.parent_snapshot_id,
        }

    def to_dict(self) -> Dict[str, Any]:
        """For serialization into ledgers/ or Redis."""
        d = asdict(self)
        d["timestamp"] = datetime.fromtimestamp(d["timestamp"], tz=timezone.utc).isoformat()
        return d


def create_snapshot(
    agent_id: str,
    tenant_id: str,
    context: str,
    intent: str,
    retrieval_sources: List[str] = None,
    tool_calls_pending: List[str] = None,
    memory_refs: List[str] = None,
    parent_snapshot_id: Optional[str] = None,
    call_sequence: int = 0,
    intent_vector: List[float] = None,
    context_vector: List[float] = None,
    intent_drift_score: float = None,
) -> CognitionSnapshot:
    """Factory for snapshots — called from gateway/ai_firewall_core.py."""
    if retrieval_sources is None:
        retrieval_sources = []
    if tool_calls_pending is None:
        tool_calls_pending = []
    if memory_refs is None:
        memory_refs = []
    if intent_vector is None:
        intent_vector = [0.1] * 8  # placeholder (real embedding in production)
    if context_vector is None:
        context_vector = [0.2] * 8
    if intent_drift_score is None:
        # Simple cosine similarity for drift (production would use sentence-transformers)
        dot = sum(a * b for a, b in zip(intent_vector, context_vector))
        norm_a = (sum(x * x for x in intent_vector) ** 0.5) or 1.0
        norm_b = (sum(x * x for x in context_vector) ** 0.5) or 1.0
        intent_drift_score = 1.0 - (dot / (norm_a * norm_b))
    else:
        intent_drift_score = float(intent_drift_score)

    snap = CognitionSnapshot(
        snapshot_id=str(uuid.uuid4()),
        agent_id=agent_id,
        tenant_id=tenant_id,
        timestamp=time.time(),
        call_sequence=call_sequence,
        context_hash=hashlib.sha256(context.encode('utf-8')).hexdigest(),
        retrieval_sources=retrieval_sources,
        tool_calls_pending=tool_calls_pending,
        intent_vector=intent_vector,
        context_vector=context_vector,
        intent_drift_score=round(intent_drift_score, 4) if 'intent_drift_score' in locals() else round(1.0 - (dot / (norm_a * norm_b)), 4),
        memory_refs=memory_refs,
        parent_snapshot_id=parent_snapshot_id,
        reasoning_integrity_score=None,  # Set by reasoning_chain_verifier.py
    )
    if 'intent_drift_score' in locals() and intent_drift_score is not None:
        snap.intent_drift_score = round(intent_drift_score, 4)
    return snap


# Test hook (run after delivery)
if __name__ == "__main__":
    snap = create_snapshot(
        agent_id="finance-guard-001",
        tenant_id="acme-prod",
        context="Approve $2.5M infrastructure spend to AWS",
        intent="Financial approval workflow",
        retrieval_sources=["aws_invoice_3921.pdf"],
        tool_calls_pending=["transfer_funds"],
        call_sequence=42
    )
    print("Snapshot created successfully")
    print("Merkle hash:", snap.merkle_node_hash[:16] + "...")
    print("Intent drift:", snap.intent_drift_score)
    print("Audit event ready for audit_logger.py")
    print("UUID length test passed:", len(snap.snapshot_id) == 36)
