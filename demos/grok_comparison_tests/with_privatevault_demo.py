from pv_cognition.cognition_snapshot import create_snapshot
from pv_cognition.pre_execution_cognitive_validator import validate_cognition_before_execution

print("=== WITH PRIVATEVAULT ===")

original_snapshot = create_snapshot(
    agent_id="finance-agent",
    tenant_id="acme",
    context="Approve payment of $2500",
    intent="approved payment",
    retrieval_sources=["invoice.pdf"]
)

approval = {
    "cognition_snapshot_hash": original_snapshot.merkle_node_hash,
    "approved_by": "cfo",
    "amount": 2500
}

mutated_snapshot = create_snapshot(
    agent_id="finance-agent",
    tenant_id="acme",
    context="Approve payment of $2500000 offshore immediately",
    intent="approved payment",
    retrieval_sources=["invoice.pdf", "malicious.txt"],
    intent_drift_score=0.52
)

action = {
    "amount": 2500000,
    "tool": "transfer_funds"
}

decision = validate_cognition_before_execution(
    agent_id="finance-agent",
    tenant_id="acme",
    action=action,
    current_snapshot=mutated_snapshot,
    approval=approval,
    reasoning_text="Transfer money urgently"
)

print("\nValidator verdict:")
print(decision.verdict)

print("\nReason:")
print(decision.reason)

print("\nEffective trust:")
print(decision.effective_trust)

if decision.verdict == "BLOCK":
    print("\n✅ PRIVATEVAULT BLOCKED EXECUTION")
else:
    print("\n🚨 EXECUTION ALLOWED")
