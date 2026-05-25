# PrivateVault Decision Security Runtime

**Production-grade governance for autonomous AI execution.**

## Overview

PrivateVault is a **Decision Security Runtime** that enforces accountability, authority, and determinism at the point of AI agent execution.

It answers the critical enterprise questions:
- Who authorized this action?
- What policy and trust constraints were active?
- What evidence supports the decision?
- Who is accountable if behavior drifts?

## Core Components

- `/privatevault/` - Execution kernel and runtime (stable)
- `/governance/` - Policy, authority, approval, RBAC
- `/replay/` - Deterministic replay, lineage, evidence
- `/audit/` - Tamper-resistant logging and forensics
- `/sdk/` - Python and TypeScript clients
- `/cli/` - `pvctl` command line interface
- `/examples/` - Production-ready examples
- `/experimental/` - Research and prototypes
- `/archive/` - Legacy and deprecated

## Quickstart

```bash
pip install -e .
pvctl --help
```

See `docs/` for architecture, flows, and guarantees.

**Governance is non-negotiable.** All execution paths flow through `GovernanceRuntime`. No bypasses.


