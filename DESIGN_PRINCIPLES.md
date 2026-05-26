# PrivateVault Cinematic Runtime Design Principles

**Mandatory reading for all contributors.** This document freezes the v0.2.0-runtime-experience baseline. All work must strictly preserve this identity. Deviation = rejection.

## Non-Negotiable Core Rules

- **runtime-as-interface**: The live replay DAG / execution topology *is* the interface. No separate "dashboard" or control layer.
- **no dashboard grammar**: Absolutely no admin panels, metric cards, status bars, data tables, sidebars, or enterprise workflow UI patterns.
- **replay DAG is the centerpiece**: The ReactFlow-powered (or equivalent) spatial graph of governed executions, delegation edges, trust propagation, checkpoints, and lineage must dominate the entire experience. All scenes, navigation, and interactions orbit this topology.
- **cinematic restraint**: Deep atmospheric darkness (#050505 void), minimal typography, low-opacity volumetric glows, precise pacing. Never visual noise or decorative flair.
- **semantic motion only**: Every animation (pulses, sweeps, illuminations, flows, reconstructions) must directly represent a runtime concept — trust decay, authority delegation, forensic replay, escalation, persistence. No gratuitous effects.
- **deterministic infrastructure feeling**: All simulations, mocks, and UI states must mirror backend determinism (fixed seeds, sorted keys, reproducible ExecutionLineage, cryptographic references, consistent replay).
- **no SaaS marketing patterns**: No hero conversion sections, pricing grids, feature cards, or marketing landing page language.
- **no CRUD/admin layouts**: No forms-for-forms-sake, no editable tables, no traditional enterprise admin interfaces. Governance must feel spatial/physical.
- **topology over tables**: Trust, lineage, and execution data must be expressed through spatial/volumetric visualization (trails, opacity decay, node awakening, edge flow), never tabular grids.
- **governance should feel spatial**: Authority, trust scores, policy enforcement, and replay reconstruction are physical phenomena within the runtime canvas.

## Contributor Guidelines (Interns & Beyond)

**Allowed & Encouraged:**
- Documentation and architecture walkthroughs
- Motion polish (semantic timing, easing, transitions)
- Mobile optimization and responsive topology
- Accessibility improvements
- Performance (ReactFlow rendering, bundle size, reduced motion)
- CLI demos and integration
- Topology refinement and replay reconstruction fidelity

**Strictly Prohibited:**
- Redesigning the homepage, hero, or core scene architecture
- Adding SaaS sections, marketing copy, or pricing grids
- Reintroducing dashboard elements, cards, tables, or CRUD patterns
- Any regression toward "finding identity" via iterative admin UI mutation

This file, the live deployment, built assets, screenshots, screen recordings, Lighthouse reports, and topology/replay demos form the **canonical reference baseline**.

Priority has shifted permanently from “finding identity” to **protecting and refining** the cinematic runtime identity.

**Baseline Tag:** v0.2.0-runtime-experience
**Status:** Frozen — protect at all costs.
