// Enhanced deterministic runtime simulator for cinematic immersive experience
// All data is static, narrative-driven, matching GovernanceRuntime, ExecutionLineage,
// TrustPropagator (decay ~0.11), ReplayReconstructor. No network calls.

export const runtimeSimulator = {
  // Narrative sequence for runtime story
  getNarrativeFlow: () => ({
    stages: [
      { id: 'intent', label: 'Intent Begins', agents: ['user-proxy'], trust: 1.0, status: 'init' },
      { id: 'coordination', label: 'Multi-Agent Coordination', agents: ['risk-engine', 'audit-agent'], trust: 0.96, status: 'propagating' },
      { id: 'trust', label: 'Trust Propagation', agents: ['risk-engine', 'finance-approver'], trust: 0.89, status: 'evaluating' },
      { id: 'governance', label: 'Governance Evaluation', agents: ['policy-engine'], trust: 0.87, status: 'checkpoint' },
      { id: 'validation', label: 'Policy Validation', agents: ['canonical-policy'], trust: 0.94, status: 'deciding' },
      { id: 'execution', label: 'Authority-Aware Execution', agents: ['finance-approver'], trust: 0.82, status: 'executing' },
      { id: 'replay', label: 'Replay Reconstruction', agents: ['audit-lineage'], trust: 0.91, status: 'reconstructed' }
    ],
    correlationId: 'corr_7b1d4f6a9e2b',
    replayRef: 'rv_8f3a9c2e7b1d'
  }),

  // Deterministic replay lineage with illumination data
  getReplay: (id = 'default') => ({
    intent_hash: id,
    decision: 'APPROVED',
    lineage: [
      { agent: 'risk-engine', trust: 0.98, timestamp: '2026-05-25T18:42:15Z', action: 'validate_policy', evidence: 'pol_3928f1' },
      { agent: 'multi-agent-mesh', trust: 0.93, timestamp: '2026-05-25T18:42:16Z', action: 'propagate_context', evidence: 'ctx_a3f9d2' },
      { agent: 'finance-approver', trust: 0.87, timestamp: '2026-05-25T18:42:17Z', action: 'execute_transfer', evidence: 'tx_7c4e91' },
      { agent: 'audit-lineage', trust: 0.91, timestamp: '2026-05-25T18:42:18Z', action: 'reconstruct_dag', evidence: 'merkle_9e2b4f' }
    ],
    replay_reference: 'rv_8f3a9c2e',
    correlation_id: 'corr_7b1d4f6a',
    evidence_hash: 'sha256:9c2e7b1d4f6a9e2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b',
    trust_propagation: {
      initial: 0.98,
      propagated: 0.87,
      decay: 0.11,
      drift_detected: false,
      pulses: [0.98, 0.94, 0.89, 0.87]
    },
    reconstruction_steps: 4
  }),

  // Drift simulation scenarios for cinematic escalation
  simulateDrift: (params = {}) => {
    const decay = params.decay || 0.22;
    const depth = params.depth || 4;
    const trustFinal = Math.max(0.45, 0.96 - decay * depth);
    
    return {
      initialTrust: 0.96,
      finalTrust: parseFloat(trustFinal.toFixed(2)),
      decayRate: decay,
      delegationDepth: depth,
      status: trustFinal < 0.65 ? 'BLOCKED' : (trustFinal < 0.8 ? 'ESCALATED' : 'REPLAY_RECONSTRUCTED'),
      visualization: {
        pulses: Array.from({length: 5}, (_, i) => Math.max(0.4, 0.96 - (decay * i * 0.6))),
        lineageIllumination: trustFinal > 0.7,
        escalationFlash: trustFinal < 0.8,
        blockBarrier: trustFinal < 0.65
      },
      message: trustFinal < 0.65 
        ? 'Governance block enforced. Replay lineage reconstructed for forensic audit.' 
        : 'Escalation triggered. Trust propagated through canonical policy engine.',
      replayRef: 'rv_drift_' + Math.floor(Math.random()*10000)
    };
  },

  // pvctl CLI output sequences (deterministic)
  getCLIOutput: (command) => {
    const outputs = {
      'execute': `✓ Executed under authority chain [risk-engine → finance-approver]
  Replay Reference: rv_8f3a9c2e
  Correlation ID: corr_7b1d4f6a
  Trust Score: 0.87 (decay: 0.11)
  Regulated Mode: ENABLED
  Evidence Hash: sha256:9c2e7b1d...`,
      'replay': `Replaying rv_8f3a9c2e...
  [✓] Lineage reconstructed (4 steps)
  [✓] Trust propagation validated (0.98 → 0.87)
  [✓] Policy decisions match canonical engine
  [✓] No drift detected
  Full DAG rendered in runtime visualizer.`,
      'lineage': `Authority Lineage for corr_7b1d4f6a:
  • risk-engine (trust=0.98, depth=0)
  → multi-agent-mesh (trust=0.93, delegated)
    → finance-approver (trust=0.87, executed)
  Governance Checkpoint: PASSED
  Merkle Root: merkle_9e2b4f`,
      'authorize': `Delegation Authorized.
  SignedEnvelope: [sig:0x...]
  TTL: 24h | MaxDepth: 5 | TrustFloor: 0.75
  Propagation complete. Trust Mesh updated.`
    };
    return outputs[command] || 'Deterministic governance output streamed from runtime simulator.';
  },

  getStatus: () => ({
    node: "sovereign-runtime-01",
    mode: "governed+replay+audit+mesh",
    policy_version: "v0.2.1-cinematic",
    trust_score: 0.94,
    regulated_mode: true,
    narrative_phase: "propagation"
  })
};

// Backward compatible API wrapper
export const api = {
  get: (endpoint) => {
    return new Promise((resolve) => {
      const delay = 80 + Math.random() * 120; // Fast for cinematic feel
      setTimeout(() => {
        if (endpoint === '/status') {
          resolve({ data: runtimeSimulator.getStatus() });
        } else if (endpoint.startsWith('/replay/')) {
          resolve({ data: runtimeSimulator.getReplay(endpoint.split('/')[2]) });
        } else if (endpoint.includes('drift')) {
          resolve({ data: runtimeSimulator.simulateDrift() });
        } else {
          resolve({ 
            data: runtimeSimulator.getNarrativeFlow() 
          });
        }
      }, delay);
    });
  }
};
