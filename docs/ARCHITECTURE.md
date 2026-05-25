PrivateVault Architecture
========================

## Execution Flow
User → SDK/CLI → GovernanceRuntime.decide_and_execute() → Policy + Trust + Tenant + Drift + Authority → Execute or Escalate → Lineage + Audit + Replay Reference

## Key Guarantees
- Fail-closed on missing tenant/authority
- Full lineage for every action
- Deterministic replay with Merkle evidence
- Scoped multi-agent delegation
- Tamper-resistant audit

See individual docs:
- runtime-flow.md
- replay-model.md
- authority-model.md
- multi-agent-governance.md

