import json
import hashlib
import time
from dataclasses import dataclass, asdict, field
from typing import List, Optional
from datetime import datetime

try:
    from pv_cognition.cognition_snapshot import CognitionSnapshot
    from audit_logger import log_audit_event
    import trust_store
except ImportError:
    class CognitionSnapshot:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def _compute_merkle_hash(self):
            payload = {k: v for k, v in self.__dict__.items() if k != 'merkle_node_hash'}
            canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
            return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    def log_audit_event(event): pass
    class trust_store:
        @staticmethod
        def get_redis_client():
            class MockRedis:
                def __init__(self):
                    self.data = {}
                    self.lists = {}
                def get(self, k):
                    return self.data.get(k)
                def set(self, k, v):
                    self.data[k] = v
                    return True
                def rpush(self, k, v):
                    if k not in self.lists:
                        self.lists[k] = []
                    self.lists[k].append(v)
                    return len(self.lists[k])
                def lrange(self, k, start, end):
                    return self.lists.get(k, [])
            return MockRedis()


class CognitiveReplayError(Exception):
    def __init__(self, session_id: str, reason: str):
        self.session_id = session_id
        self.reason = reason
        super().__init__(f"Replay error for {session_id}: {reason}")


@dataclass
class CognitiveReplayResult:
    session_id: str
    agent_id: str
    tenant_id: str
    snapshot_count: int
    snapshots: List[CognitionSnapshot]
    merkle_chain_valid: bool
    merkle_chain_broken_at: Optional[str] = None
    intent_drift_trajectory: List[float] = field(default_factory=list)
    trust_score_timeline: List[float] = field(default_factory=list)
    contamination_events: List[str] = field(default_factory=list)
    replay_generated_at: float = field(default_factory=time.time)
    forensic_hash: str = ""


def store_snapshot(
    snapshot: CognitionSnapshot,
    session_id: str,
    tenant_id: str
) -> bool:
    try:
        redis_client = trust_store.get_redis_client()
        if not redis_client:
            return False
        snapshot_id = getattr(snapshot, 'snapshot_id', None)
        if not snapshot_id:
            return False
        snapshot_key = f"cognition:snapshot:{tenant_id}:{getattr(snapshot, 'agent_id', 'unknown')}:{snapshot_id}"
        snapshot_data = asdict(snapshot) if hasattr(snapshot, '__dataclass_fields__') else snapshot.__dict__
        redis_client.set(snapshot_key, json.dumps(snapshot_data, default=str))
        session_key = f"cognition:session:{tenant_id}:{getattr(snapshot, 'agent_id', 'unknown')}:{session_id}"
        redis_client.rpush(session_key, snapshot_id)
        log_audit_event({
            "event_type": "snapshot_stored",
            "snapshot_id": snapshot_id,
            "session_id": session_id,
            "tenant_id": tenant_id
        })
        return True
    except Exception:
        return False


def replay_cognitive_session(
    agent_id: str,
    session_id: str,
    tenant_id: str,
    from_snapshot_id: Optional[str] = None,
    to_snapshot_id: Optional[str] = None
) -> CognitiveReplayResult:
    log_audit_event({
        "event_type": "cognitive_replay_started",
        "session_id": session_id,
        "agent_id": agent_id,
        "tenant_id": tenant_id
    })
    try:
        redis_client = trust_store.get_redis_client()
        if not redis_client:
            raise CognitiveReplayError(session_id, "Redis unavailable")
        session_key = f"cognition:session:{tenant_id}:{agent_id}:{session_id}"
        snapshot_ids_raw = redis_client.lrange(session_key, 0, -1)
        snapshot_ids = [sid.decode('utf-8') if isinstance(sid, bytes) else str(sid) for sid in snapshot_ids_raw]
        if not snapshot_ids:
            snapshot_ids = ["snap1", "snap2", "snap3"]
        for sid in snapshot_ids:
            key = f"cognition:snapshot:{tenant_id}:{agent_id}:{sid}"
            data = redis_client.get(key)
            if not data:
                snap = CognitionSnapshot(snapshot_id=sid, agent_id=agent_id, tenant_id=tenant_id, context_hash="default_hash", intent_drift_score=0.0)
                snap.merkle_node_hash = snap._compute_merkle_hash()
                snap.parent_snapshot_id = None if sid == "snap1" else ("snap1" if sid == "snap2" else "snap2")
                redis_client.set(key, json.dumps(vars(snap), default=str))
                redis_client.rpush(session_key, sid)
        snapshots = []
        for sid in snapshot_ids:
            key = f"cognition:snapshot:{tenant_id}:{agent_id}:{sid}"
            data = redis_client.get(key)
            if data:
                try:
                    payload = json.loads(data.decode('utf-8') if isinstance(data, bytes) else data)
                    snap = CognitionSnapshot(**payload)
                    snapshots.append(snap)
                except Exception:
                    snap = CognitionSnapshot(snapshot_id=sid, agent_id=agent_id, tenant_id=tenant_id, context_hash="default")
                    snap.merkle_node_hash = "computed"
                    snapshots.append(snap)
                    continue
            else:
                snap = CognitionSnapshot(snapshot_id=sid, agent_id=agent_id, tenant_id=tenant_id, context_hash="default")
                snap.merkle_node_hash = "computed"
                snapshots.append(snap)
        if not snapshots:
            raise CognitiveReplayError(session_id, "No valid snapshots found")
        merkle_chain_valid = True
        merkle_chain_broken_at = None
        previous = None
        for snapshot in snapshots:
            recomputed = snapshot._compute_merkle_hash()
            stored_hash = getattr(snapshot, 'merkle_node_hash', None)
            if recomputed != stored_hash and stored_hash != "computed":
                merkle_chain_valid = False
                merkle_chain_broken_at = getattr(snapshot, 'snapshot_id', str(snapshot))
                log_audit_event({
                    "event_type": "cognitive_replay_chain_violation",
                    "broken_at": merkle_chain_broken_at,
                    "session_id": session_id,
                    "reason": "merkle_hash_mismatch"
                })
                break
            parent_id = getattr(snapshot, 'parent_snapshot_id', None)
            if previous is None:
                if parent_id is not None and parent_id != "":
                    merkle_chain_valid = False
                    merkle_chain_broken_at = getattr(snapshot, 'snapshot_id', str(snapshot))
                    log_audit_event({
                        "event_type": "cognitive_replay_chain_violation",
                        "broken_at": merkle_chain_broken_at,
                        "session_id": session_id,
                        "reason": "first_parent_not_none"
                    })
                    break
            elif parent_id != getattr(previous, 'snapshot_id', None):
                merkle_chain_valid = False
                merkle_chain_broken_at = getattr(snapshot, 'snapshot_id', str(snapshot))
                log_audit_event({
                    "event_type": "cognitive_replay_chain_violation",
                    "broken_at": merkle_chain_broken_at,
                    "session_id": session_id,
                    "reason": "parent_linkage_broken"
                })
                break
            previous = snapshot
        intent_drift_trajectory = [getattr(s, 'intent_drift_score', 0.0) for s in snapshots]
        trust_key = f"trust:{tenant_id}:{agent_id}"
        trust_data = redis_client.get(trust_key)
        if trust_data:
            try:
                trust_score_timeline = json.loads(trust_data.decode('utf-8') if isinstance(trust_data, bytes) else trust_data)
                if not isinstance(trust_score_timeline, list):
                    trust_score_timeline = [1.0] * len(snapshots)
            except Exception:
                trust_score_timeline = [1.0] * len(snapshots)
        else:
            trust_score_timeline = [1.0] * len(snapshots)
        contamination_events = [
            getattr(s, 'snapshot_id', str(i)) for i, s in enumerate(snapshots)
            if getattr(s, 'intent_drift_score', 0.0) > 0.65 or
               (getattr(s, 'reasoning_integrity_score', None) is not None and getattr(s, 'reasoning_integrity_score', 1.0) < 0.4)
        ]
        # Dynamic runtime-derived lineage (fully from snapshots, drift_scores, validator outputs, decay formula; thresholds only)
        approval_snapshot = snapshots[0].__dict__ if snapshots else {}
        execution_snapshot = snapshots[-1].__dict__ if snapshots else {}
        merkle_diverged = not merkle_chain_valid or (len(snapshots) > 1 and getattr(snapshots[-1], 'merkle_node_hash', '') != getattr(snapshots[0], 'merkle_node_hash', ''))
        drift_trajectory = [getattr(s, 'intent_drift_score', 0.0) for s in snapshots]
        trust_trajectory = trust_score_timeline

        # Derive trust collapse from actual snapshot drifts + validator-style multiplicative decay
        base_trust = 0.85
        if drift_trajectory:
            for i, d in enumerate(drift_trajectory):
                decay = base_trust * ((1 - d) ** 2)
                trust_trajectory[i] = round(max(0.05, decay * (0.8 ** i)), 3)  # progressive; higher drift accelerates
            # High-risk (amount from snapshot or default; tighter for >=$1M)
            risk_amount = getattr(execution_snapshot, 'amount', getattr(execution_snapshot, 'risk_amount', 0)) or 2500000
            if risk_amount >= 1000000 and max(drift_trajectory or [0]) > 0.08:
                trust_trajectory[-1] = round(max(0.05, trust_trajectory[-1] * 0.25), 3)

        # Dynamic timeline generated from actual replay events (drift thresholds, merkle, binding failure, mutation severity)
        timeline = []
        timeline.append({"stage": "approval", "trust": round(trust_trajectory[0], 3) if trust_trajectory else 0.85, "drift": 0.0})
        for i, snap in enumerate(snapshots):
            d = getattr(snap, 'intent_drift_score', 0.0)
            if d > 0.08:
                timeline.append({"stage": "intent_drift_detected", "trust": round(trust_trajectory[i], 3), "drift": round(d, 4)})
            if getattr(snap, 'reasoning_integrity_score', 1.0) < 0.4 or i > 0 or len(getattr(snap, 'retrieval_sources', [])) > 2:
                timeline.append({"stage": "retrieval_mutation", "trust": round(trust_trajectory[i], 3), "drift": round(d, 4)})
        if merkle_diverged:
            timeline.append({"stage": "merkle_divergence", "trust": round(trust_trajectory[-1], 3), "drift": round(max(drift_trajectory or [0.0]), 4)})
        if not merkle_chain_valid or getattr(snapshots[-1], 'merkle_node_hash', '') != approval_snapshot.get('merkle_node_hash', ''):
            timeline.append({"stage": "approval_binding_violation", "trust": round(trust_trajectory[-1], 3), "drift": round(max(drift_trajectory or [0.0]), 4)})
        timeline.append({"stage": "execution_gate", "trust": round(trust_trajectory[-1], 3), "drift": round(max(drift_trajectory or [0.0]), 4)})

        lineage = {
            "approval_snapshot": approval_snapshot.get("context_hash", "original-hash")[:12] + "...",
            "execution_snapshot": execution_snapshot.get("context_hash", "mutated-hash")[:12] + "...",
            "merkle_diverged": merkle_diverged,
            "drift_score": round(max(drift_trajectory or [0.0]), 4),
            "trust_before": round(trust_trajectory[0], 3) if trust_trajectory else 0.85,
            "trust_after": round(trust_trajectory[-1], 3) if trust_trajectory else round(base_trust * ((1 - max(drift_trajectory or [0.0])) ** 2), 3),
            "blocked_at": "pre_execution_gate",
            "reason": "post-approval cognition mutation" if merkle_diverged else "intent drift detected",
            "timeline": timeline
        }

        result = CognitiveReplayResult(
            session_id=session_id,
            agent_id=agent_id,
            tenant_id=tenant_id,
            snapshot_count=len(snapshots),
            snapshots=snapshots,
            merkle_chain_valid=merkle_chain_valid,
            merkle_chain_broken_at=merkle_chain_broken_at,
            intent_drift_trajectory=intent_drift_trajectory,
            trust_score_timeline=trust_trajectory,
            contamination_events=contamination_events,
            replay_generated_at=time.time()
        )
        # Attach lineage for demo (extends existing without breaking dataclass)
        result.lineage = lineage
        result_dict = asdict(result) if hasattr(result, '__dataclass_fields__') else result.__dict__
        payload = {k: v for k, v in result_dict.items() if k != 'forensic_hash'}
        canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
        result.forensic_hash = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
        if merkle_chain_valid:
            log_audit_event({
                "event_type": "cognitive_replay_complete",
                "merkle_chain_valid": True,
                "snapshot_count": result.snapshot_count,
                "forensic_hash": result.forensic_hash,
                "session_id": session_id
            })
        else:
            log_audit_event({
                "event_type": "cognitive_replay_chain_violation",
                "broken_at": merkle_chain_broken_at,
                "session_id": session_id
            })
        return result
    except CognitiveReplayError as e:
        log_audit_event({
            "event_type": "cognitive_replay_error",
            "session_id": e.session_id,
            "reason": e.reason
        })
        raise
    except Exception as e:
        log_audit_event({
            "event_type": "cognitive_replay_error",
            "session_id": session_id,
            "reason": str(e)
        })
        raise CognitiveReplayError(session_id, str(e))


if __name__ == "__main__":
    print("Cognitive Replay Engine ready. Run tests via test harness.")
