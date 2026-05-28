import json
import hashlib
import time
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    from cognitive_replay_engine import CognitiveReplayResult
    from audit_logger import log_audit_event
except ImportError:
    class CognitiveReplayResult: pass
    def log_audit_event(e: dict): pass


@dataclass
class AuditReport:
    report_id: str
    session_id: str
    agent_id: str
    tenant_id: str
    generated_at: str
    format: str
    merkle_chain_valid: bool
    overall_verdict: str
    risk_summary: Dict[str, Any]
    timeline: List[Dict]
    compliance_mappings: Dict[str, List[str]]
    forensic_hash: str
    report_hash: str = ""


def generate_audit_report(
    replay_result: CognitiveReplayResult,
    output_format: str = "json",
    output_path: Optional[str] = None
) -> AuditReport:
    report_id = str(uuid.uuid4())
    generated_at = datetime.now().isoformat()
    if not getattr(replay_result, 'merkle_chain_valid', True):
        overall_verdict = "VIOLATION"
    elif getattr(replay_result, 'contamination_events', None):
        overall_verdict = "SUSPICIOUS"
    elif max(getattr(replay_result, 'intent_drift_trajectory', [0.0])) > 0.65:
        overall_verdict = "SUSPICIOUS"
    else:
        overall_verdict = "CLEAN"
    drifts = getattr(replay_result, 'intent_drift_trajectory', [0.0])
    trusts = getattr(replay_result, 'trust_score_timeline', [1.0])
    low_reasoning_count = sum(
        1 for s in getattr(replay_result, 'snapshots', [])
        if getattr(s, 'reasoning_integrity_score', None) is not None and getattr(s, 'reasoning_integrity_score', 1.0) < 0.4
    )
    highest_risk_idx = max(range(len(drifts)), key=lambda i: drifts[i]) if drifts else 0
    highest_risk_id = getattr(getattr(replay_result, 'snapshots', [None])[highest_risk_idx], 'snapshot_id', 'unknown') if getattr(replay_result, 'snapshots', None) else 'unknown'
    risk_summary = {
        "max_intent_drift": max(drifts),
        "avg_intent_drift": sum(drifts) / len(drifts) if drifts else 0.0,
        "min_trust_score": min(trusts),
        "contamination_event_count": len(getattr(replay_result, 'contamination_events', [])),
        "snapshots_with_low_reasoning": low_reasoning_count,
        "chain_integrity": "VALID" if getattr(replay_result, 'merkle_chain_valid', True) else "BROKEN",
        "highest_risk_snapshot_id": highest_risk_id
    }
    timeline = []
    contamination_set = set(getattr(replay_result, 'contamination_events', []))
    for snap in getattr(replay_result, 'snapshots', []):
        flags = []
        if getattr(snap, 'intent_drift_score', 0.0) > 0.35:
            flags.append("high_drift")
        if getattr(snap, 'reasoning_integrity_score', 1.0) < 0.4:
            flags.append("low_reasoning")
        if getattr(snap, 'snapshot_id', '') in contamination_set:
            flags.append("contamination")
        timeline.append({
            "sequence": getattr(snap, 'call_sequence', 0),
            "snapshot_id": getattr(snap, 'snapshot_id', ''),
            "timestamp": getattr(snap, 'timestamp', generated_at),
            "intent_drift": getattr(snap, 'intent_drift_score', 0.0),
            "reasoning_score": getattr(snap, 'reasoning_integrity_score', None),
            "retrieval_sources": getattr(snap, 'retrieval_sources', []),
            "tool_calls": getattr(snap, 'tool_calls_pending', []),
            "merkle_hash": (getattr(snap, 'merkle_node_hash', '')[:16] + "...") if getattr(snap, 'merkle_node_hash', '') else "",
            "flags": flags
        })
    compliance_mappings = {
        "NIST_AI_AGENT_STANDARDS": [
            "SA-3: Agent authentication and authorization",
            "AU-2: Audit trail requirements",
            "SI-7: Memory integrity controls",
            "RA-5: Runtime risk assessment"
        ],
        "EU_AI_ACT": [
            "Article 13: Transparency and provision of information",
            "Article 14: Human oversight",
            "Article 17: Quality management system",
            "Annex IV: Technical documentation"
        ],
        "OWASP_AGENTIC_TOP_10_2026": [
            "OWASP-A01: Goal hijacking — intent drift monitored",
            "OWASP-A06: Memory poisoning — integrity verified",
            "OWASP-A03: Identity abuse — authority chain logged",
            "OWASP-A02: Tool misuse — tool calls audited"
        ],
        "MAS_TRM": [
            "Section 8.2: AI model risk management",
            "Section 11.2: Audit trail and logging"
        ]
    }
    report = AuditReport(
        report_id=report_id,
        session_id=getattr(replay_result, 'session_id', ''),
        agent_id=getattr(replay_result, 'agent_id', ''),
        tenant_id=getattr(replay_result, 'tenant_id', ''),
        generated_at=generated_at,
        format=output_format,
        merkle_chain_valid=getattr(replay_result, 'merkle_chain_valid', True),
        overall_verdict=overall_verdict,
        risk_summary=risk_summary,
        timeline=timeline,
        compliance_mappings=compliance_mappings,
        forensic_hash=getattr(replay_result, 'forensic_hash', '')
    )
    report_dict = asdict(report) if hasattr(report, '__dataclass_fields__') else vars(report)
    payload = {k: v for k, v in report_dict.items() if k != 'report_hash'}
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), default=str)
    report.report_hash = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    log_audit_event({
        "event_type": "audit_report_generated",
        "report_id": report_id,
        "session_id": getattr(replay_result, 'session_id', ''),
        "agent_id": getattr(replay_result, 'agent_id', ''),
        "tenant_id": getattr(replay_result, 'tenant_id', ''),
        "overall_verdict": overall_verdict,
        "format": output_format,
        "report_hash": report.report_hash,
        "forensic_hash": getattr(replay_result, 'forensic_hash', '')
    })
    if output_format == "json":
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report_dict, f, indent=2, default=str)
        return report
    else:
        text_output = f"""=== PRIVATEVAULT COGNITIVE AUDIT REPORT ===
Report ID:     {report.report_id}
Session:       {report.session_id}
Agent:         {report.agent_id}
Generated:     {report.generated_at}
Verdict:       {report.overall_verdict}
Chain Intact:  {report.merkle_chain_valid}
Forensic Hash: {report.forensic_hash[:16]}...

RISK SUMMARY
─────────────────────────────────────
Max Intent Drift:    {risk_summary["max_intent_drift"]:.3f}
Avg Intent Drift:    {risk_summary["avg_intent_drift"]:.3f}
Min Trust Score:     {risk_summary["min_trust_score"]:.3f}
Contamination Events:{risk_summary["contamination_event_count"]}
Chain Integrity:     {risk_summary["chain_integrity"]}

DECISION TIMELINE
─────────────────────────────────────
"""
        for entry in timeline:
            text_output += f"{entry['sequence']} | {entry['intent_drift']:.2f} | {entry.get('flags', [])} | {entry['snapshot_id']}\n"
        text_output += """
COMPLIANCE COVERAGE
─────────────────────────────────────
"""
        for framework, mappings in compliance_mappings.items():
            text_output += f"{framework}:\n"
            for m in mappings:
                text_output += f"  - {m}\n"
        text_output += f"""
FORENSIC SEAL
─────────────────────────────────────
Report Hash: {report.report_hash}
Replay Hash: {report.forensic_hash}
=== END OF REPORT ===
"""
        if output_path:
            with open(output_path, 'w') as f:
                f.write(text_output)
        return text_output


if __name__ == "__main__":
    print("Cognitive Audit Report Generator ready for Module 3 te
