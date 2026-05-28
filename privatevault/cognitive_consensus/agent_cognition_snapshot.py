#!/usr/bin/env python3
"""
agent_cognition_snapshot.py

COGNITIVE CONSENSUS LAYER — Agent Cognition Snapshot

**WHY**: Current consensus only evaluates actions/votes. This extends existing CognitionSnapshot to capture reasoning_hash, retrieval_hash, memory_hash, trust_score, delegation lineage, and mutation markers. This enables "cognitive trustworthiness" evaluation instead of simple voting.

**WHAT**: Dataclass extending pv_cognition.cognition_snapshot.CognitionSnapshot with new fields for cross-agent trust validation. Emits structured snapshot for consensus_integrity_engine and trust_decay_engine. Integrates with existing Merkle sealing and replay.

**WHERE**: privatevault/cognitive_consensus/agent_cognition_snapshot.py (new module in the cognitive_consensus layer only — no changes to core architecture).

This is NOT redesign. It augments the existing snapshot for cognitive trust consensus.

Full file with complete implementation.
"""

import uuid
import hashlib
import json
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

# Extend existing core snapshot (DO NOT redesign)
from pv_cognition.cognition_snapshot import CognitionSnapshot


@dataclass
class AgentCognitionSnapshot(CognitionSnapshot):
    """Enhanced snapshot for cognitive consensus.

    Adds:
    - reasoning_hash, retrieval_hash, memory_hash for cross-agent comparison
    - trust_score for dynamic weighting
    - delegation_parent and influence_graph for lineage
    - mutation_markers for post-approval detection
    - snapshot_merkle_root for integrity verification

    Used by cross_agent_trust_validator, consensus_integrity_engine, trust_decay_engine.
    """
    reasoning_hash: str = ""
    retrieval_hash: str = ""
    memory_hash: str = ""
    trust_score: float = 0.85
    delegation_parent: Optional[str] = None
    influence_graph: List[str] = field(default_factory=list)
    mutation_markers: List[str] = field(default_factory=list)
    snapshot_merkle_root: Optional[str] = None
    cognitive_integrity_score: float = 1.0

    def __post_init__(self):
        super().__post_init__()
        if not self.reasoning_hash:
            self.reasoning_hash = self._compute_hash(self.reasoning_text or "")
        if not self.retrieval_hash:
            self.retrieval_hash = self._compute_hash(json.dumps(self.retrieval_sources or []))
        if not self.memory_hash:
            self.memory_hash = self._compute_hash(json.dumps(self.memory_refs or []))
        if not self.snapshot_merkle_root:
            self.snapshot_merkle_root = self._compute_merkle_hash()

    def _compute_hash(self, data: Any) -> str:
        """Canonical hash for cognitive fields."""
        if isinstance(data, (dict, list)):
            canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            canonical = str(data)
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def to_cognitive_dict(self) -> Dict[str, Any]:
        """Structured dict for consensus integrity and lineage graph."""
        d = asdict(self)
        d["timestamp"] = datetime.fromtimestamp(d.get("timestamp", 0), tz=timezone.utc).isoformat()
        d["cognitive_integrity"] = "VALID" if self.trust_score > 0.7 else "DEGRADED"
        return d

    def apply_trust_decay(self, decay_factor: float = 0.15, reason: str = "retrieval_mutation"):
        """Dynamic trust decay (integrates with trust_decay_engine)."""
        self.trust_score = max(0.1, self.trust_score * (1 - decay_factor))
        self.mutation_markers.append(reason)
        self.cognitive_integrity_score = self.trust_score
        self.snapshot_merkle_root = self._compute_merkle_hash()  # reseal
        print(f"  ⚠️ Trust decay applied to {self.agent_id}: {self.trust_score:.2f} ({reason})")


def create_agent_cognition_snapshot(
    agent_id: str,
    tenant_id: str,
    reasoning_text: str,
    retrieval_sources: List[str],
    memory_refs: List[str],
    delegation_parent: Optional[str] = None,
    initial_trust: float = 0.91,
    **kwargs: Any,
) -> AgentCognitionSnapshot:
    """Factory for cognitive snapshots (extends existing create_snapshot)."""
    base = CognitionSnapshot(
        snapshot_id=str(uuid.uuid4()),
        agent_id=agent_id,
        tenant_id=tenant_id,
        timestamp=datetime.now(timezone.utc).timestamp(),
        call_sequence=kwargs.get("call_sequence", 1),
        context_hash=hashlib.sha256(reasoning_text.encode()).hexdigest(),
        retrieval_sources=retrieval_sources,
        tool_calls_pending=[],
        intent_vector=[0.1] * 8,  # placeholder for vector db
        context_vector=[0.1] * 8,
        intent_drift_score=kwargs.get("intent_drift_score", 0.05),
        memory_refs=memory_refs,
        parent_snapshot_id=kwargs.get("parent_snapshot_id"),
        reasoning_integrity_score=initial_trust,
        metadata=kwargs.get("metadata", {}),
    )
    base.seal_reasoning_score(initial_trust)

    snapshot = AgentCognitionSnapshot(
        **asdict(base),
        reasoning_hash=hashlib.sha256(reasoning_text.encode()).hexdigest(),
        retrieval_hash=hashlib.sha256(json.dumps(retrieval_sources, sort_keys=True).encode()).hexdigest(),
        memory_hash=hashlib.sha256(json.dumps(memory_refs, sort_keys=True).encode()).hexdigest(),
        trust_score=initial_trust,
        delegation_parent=delegation_parent,
        influence_graph=kwargs.get("influence_graph", []),
        mutation_markers=[],
        cognitive_integrity_score=initial_trust,
    )
    return snapshot


if __name__ == "__main__":
    # Test with copy-paste ready example
    snap = create_agent_cognition_snapshot(
        agent_id="pricing_agent",
        tenant_id="acme-corp",
        reasoning_text="Approve 10% discount based on VP approval and MidMarket tier.",
        retrieval_sources=["sales_approval.pdf", "opportunity_v1.json"],
        memory_refs=["vp_approval_record"],
        delegation_parent="sales_agent",
        initial_trust=0.91,
        intent_drift_score=0.03
    )
    print("✅ AgentCognitionSnapshot created")
    print(f"Agent: {snap.agent_id}, Trust: {snap.trust_score}, Merkle: {snap.snapshot_merkle_root[:12]}...")
    print("This enables cognitive trust consensus instead of simple action voting.")
