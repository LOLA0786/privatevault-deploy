# PrivateVault Battle Cards

**PrivateVault is execution authority infrastructure.** It verifies whether an autonomous agent's cognitive state remains trustworthy *at the moment of execution* using pre-execution gates, approval binding, Merkle lineage, deterministic replay, and runtime trust decay.

Identity verifies **WHO**. PrivateVault verifies **WHETHER the mind is still trustworthy**.

## 1. vs Zenity (Runtime Protection for Agents)

| Feature                  | PrivateVault                          | Zenity                               | Winner + Why |
|--------------------------|---------------------------------------|--------------------------------------|--------------|
| Pre-Execution Gate       | ✅ Real validator + drift + binding   | Policy-based, post-prompt            | PrivateVault — stops execution, doesn't just filter prompts |
| Deterministic Replay     | ✅ Full forensic lineage from snapshots | Limited audit logs                   | PrivateVault — courtroom-grade replay of mutations |
| Merkle + Approval Binding| ✅ Cryptographic immutability         | No cryptographic lineage             | PrivateVault — tamper-proof authority chain |
| Trust Decay Model        | ✅ Dynamic (0.92 → 0.19 on drift)     | Static risk scores                   | PrivateVault — multiplicative decay on real runtime state |
| $2.5M Poisoning Demo     | ✅ Blocks live with replay            | Would allow after initial approval   | PrivateVault — proves governance that stops execution |

**Winner: PrivateVault**. Zenity is prompt filtering. PrivateVault is runtime execution authority.

## 2. vs Microsoft Agent Governance Toolkit (AGT)

| Feature                  | PrivateVault                          | Microsoft AGT                        | Winner + Why |
|--------------------------|---------------------------------------|--------------------------------------|--------------|
| Execution Authority      | ✅ Pre-execution gate with binding    | Policy enforcement after reasoning   | PrivateVault — true fail-closed before tool call |
| Deterministic Replay     | ✅ Runtime-derived timeline + trajectory | Basic logging                        | PrivateVault — reconstructs exact mutation path |
| Cryptographic Enforcement| ✅ Merkle snapshots + signed receipts | No Merkle or binding                 | PrivateVault — provable lineage for auditors |
| High-Risk Drift Handling | ✅ Risk-tiered thresholds ($1M = 0.08)| Generic content filters              | PrivateVault — financial-specific collapse to 0.19 |
| Forensic Receipts        | ✅ Chained, signed, immutable         | Basic audit trails                   | PrivateVault — enterprise compliance ready |

**Winner: PrivateVault**. AGT is governance theater. PrivateVault is cryptographic runtime enforcement.

## 3. vs Guardrails AI / NeMo Guardrails

| Feature                  | PrivateVault                          | Guardrails AI / NeMo                 | Winner + Why |
|--------------------------|---------------------------------------|--------------------------------------|--------------|
| Pre-Execution Enforcement| ✅ Cognitive validator gate           | Output/rail validation               | PrivateVault — blocks before execution, not after |
| Delegation Lineage       | ✅ Authority inheritance + replay     | No lineage                           | PrivateVault — CFO → procurement → payment with revocation |
| Deterministic Replay     | ✅ Full snapshot sequence replay      | Limited guardrail traces             | PrivateVault — adversarial branch simulation |
| Runtime Tamper Detection | ✅ Merkle divergence + self-verification | Prompt injection only               | PrivateVault — protects the protector |
| Enterprise Moat          | ✅ Execution authority infrastructure | Prompt/output rails                  | PrivateVault — "whether the mind is trustworthy" |

**Winner: PrivateVault**. Guardrails are output filters. PrivateVault is cognitive runtime security.

## 4. vs Obsidian Security / HiddenLayer (AI Security Platforms)

| Feature                  | PrivateVault                          | Obsidian / HiddenLayer               | Winner + Why |
|--------------------------|---------------------------------------|--------------------------------------|--------------|
| Focus                    | Execution authority + replay          | Threat detection / monitoring        | PrivateVault — prevents, doesn't just detect |
| Pre-Execution Gate       | ✅ Real validator with binding        | Post-execution alerts                | PrivateVault — fail-closed before irreversible action |
| Deterministic Replay     | ✅ Forensic OS with timeline          | Basic audit                          | PrivateVault — reconstructs exact cognitive mutation |
| Cryptographic Proofs     | ✅ Merkle + signed receipts           | No cryptographic lineage             | PrivateVault — auditor-proof evidence |
| $2.5M Fraud Demo         | ✅ Blocks live                        | Would alert after                    | PrivateVault — stops the wire, doesn't log it |

**Winner: PrivateVault**. Obsidian/HiddenLayer monitor threats. PrivateVault enforces authority at runtime.

**Strategic Positioning Summary**

PrivateVault is not another AI security tool.

It is the **Decision Security Control Plane** for autonomous execution.

- **CrowdStrike for AI agents** (prevents the breach)
- **Okta for autonomous authority** (verifies the mind)
- **Runtime trust infrastructure** (governance that can stop execution)

Use these cards in sales calls, founder meetings, and the README. They make the differentiation crystal clear.

**Next: Ship pvctl CLI polish, PyPI packaging, or Streamlit demo?** (Reply with choice or "ship everything".)
