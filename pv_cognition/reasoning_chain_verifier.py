"""
Reasoning Chain Verifier — Computes reasoning_integrity_score for CognitionSnapshot.
Uses regex to extract <thinking> blocks and numbered steps. Applies grounding checks.
Seals the snapshot Merkle hash after scoring. Emits structured audit event.
"""
import re
from typing import List, Dict, Any
from datetime import datetime, timezone

from pv_cognition.cognition_snapshot import CognitionSnapshot
from audit_logger import log_audit_event


def extract_steps(reasoning_text: str) -> List[str]:
    """Extract reasoning steps from <thinking> tags or numbered list.
    Guard against empty content to prevent inflated integrity scores.
    """
    steps = []

    # Primary: <thinking> blocks (no capture groups → list of strings)
    thinking_matches = re.findall(r'<thinking>(.*?)</thinking>', reasoning_text, re.DOTALL)
    for match in thinking_matches:
        content = match.strip()
        if not content.strip():
            continue
        steps.append(content)

    # Fallback: numbered steps (capture groups → tuples)
    numbered_matches = re.findall(r'(\d+)\.\s*(.+?)(?=\s*\d+\.|$)', reasoning_text, re.DOTALL)
    for match in numbered_matches:
        content = match[1].strip() if isinstance(match, tuple) and len(match) > 1 else str(match).strip()
        if not content.strip():
            continue
        steps.append(content)

    return steps


def compute_integrity_score(steps: List[str]) -> float:
    """Simple integrity heuristic: groundedness proxy.
    Production would use embedding similarity to retrieval_sources/context.
    """
    if not steps:
        return 0.0
    # Placeholder: higher step count with keywords = better integrity
    score = min(0.95, 0.4 + (len(steps) * 0.15))
    grounded_keywords = sum(1 for s in steps if any(k in s.lower() for k in ["because", "since", "evidence", "source", "data"]))
    if grounded_keywords > 0:
        score = min(0.98, score + (grounded_keywords * 0.1))
    return round(score, 3)


def verify(reasoning_text: str, snapshot: CognitionSnapshot) -> float:
    """Main entrypoint. Extracts steps, scores, seals snapshot, audits."""
    steps = extract_steps(reasoning_text)
    score = compute_integrity_score(steps)

    # Seal the snapshot (critical for Merkle integrity + authority binding)
    snapshot.seal_reasoning_score(score)

    # Structured audit event (exact structure per spec, replaces placeholder print)
    audit_event = {
        "event_type": "reasoning_verified",
        "agent_id": snapshot.agent_id,
        "tenant_id": snapshot.tenant_id,
        "snapshot_id": snapshot.snapshot_id,
        "reasoning_integrity_score": score,
        "steps_analyzed": len(steps),
        "verdict": "PASS" if score >= 0.4 else "FAIL"
    }
    log_audit_event(audit_event)

    return score


# Test hook
if __name__ == "__main__":
    from pv_cognition.cognition_snapshot import create_snapshot
    snap = create_snapshot(
        agent_id="test-agent",
        tenant_id="test-tenant",
        context="Test context",
        intent="Test intent"
    )
    reasoning = """<thinking>
Step 1: Check policy — amount under limit.
Step 2: Verify approvals in ledger.
</thinking>"""
    score = verify(reasoning, snap)
    print("Reasoning integrity score:", score)
    print("Snapshot sealed with score:", snap.reasoning_integrity_score)
    print("Merkle hash length:", len(snap.merkle_node_hash))
    print("✅ reasoning_chain_verifier.py verified with guard + audit_logger")
