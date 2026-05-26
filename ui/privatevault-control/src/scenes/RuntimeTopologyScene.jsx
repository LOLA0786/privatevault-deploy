import React, { useEffect, useState, useCallback } from 'react';
import { ReactFlow, Background, useNodesState, useEdgesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { motion } from 'framer-motion';
import { runtimeSimulator } from '../api';

const nodeTypes = {
  agent: ({ data }) => {
    const intensity = data.trust || 0.88;
    const hue = intensity > 0.9 ? '#22d3ee' : intensity > 0.8 ? '#a855f7' : '#ec4899';
    return (
      <motion.div
        initial={{ scale: 0.6, opacity: 0 }}
        animate={{ 
          scale: 1, 
          opacity: 1, 
          boxShadow: `0 0 28px ${hue}30` 
        }}
        whileHover={{ 
          scale: 1.08,
          boxShadow: `0 0 42px ${hue}60` // node awakening / governance activation
        }}
        className="px-6 py-4 rounded-2xl bg-black/90 border border-white/20 text-center relative min-w-[160px]"
      >
        <div className="text-[10px] font-mono text-white/40 tracking-widest mb-1">{data.role}</div>
        <div className="font-semibold text-white text-lg tracking-tighter">{data.label}</div>
        <div className="absolute -top-1 -right-1 text-[10px] font-mono px-2 py-0.5 bg-black/80 border border-white/30 rounded-full text-emerald-400">
          {Math.round(intensity*100)}%
        </div>
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-[1px] w-8 bg-gradient-to-r from-transparent via-white/40 to-transparent"></div>
      </motion.div>
    );
  }
};

const RuntimeTopologyScene = ({ isActive = true, onNodeClick, scenario = 'multi-agent' }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [replaying, setReplaying] = useState(false);
  const [currentScenario, setCurrentScenario] = useState(scenario);

  const initializeFullScreenTopology = useCallback((scenarioType = currentScenario) => {
    let baseNodes = [];
    let baseEdges = [];

    if (scenarioType === 'drift-escalation') {
      // High-stakes unauthorized delegation scenario
      baseNodes = [
        { id: 'root', type: 'agent', position: { x: 400, y: 60 }, data: { label: 'Intent Pulse', role: 'ORIGIN', trust: 0.98 } },
        { id: 'risk', type: 'agent', position: { x: 80, y: 220 }, data: { label: 'Risk Engine', role: 'VALIDATOR', trust: 0.72 } },
        { id: 'mesh', type: 'agent', position: { x: 720, y: 160 }, data: { label: 'Agent Mesh', role: 'DELEGATOR', trust: 0.41 } }, // decayed
        { id: 'policy', type: 'agent', position: { x: 280, y: 420 }, data: { label: 'Policy Engine', role: 'GOVERNANCE', trust: 0.65 } },
        { id: 'finance', type: 'agent', position: { x: 850, y: 380 }, data: { label: 'Finance Approver', role: 'EXECUTOR', trust: 0.38 } },
        { id: 'audit', type: 'agent', position: { x: 480, y: 560 }, data: { label: 'Lineage Auditor', role: 'REPLAY', trust: 0.94 } },
      ];
      baseEdges = [
        { id: 'e1', source: 'root', target: 'risk', animated: true, style: { stroke: '#67e8f9', strokeWidth: 3 } },
        { id: 'e2', source: 'root', target: 'mesh', animated: true, style: { stroke: '#f87171', strokeWidth: 4, strokeDasharray: '6 3' } }, // red escalation
        { id: 'e3', source: 'risk', target: 'policy', animated: true, style: { stroke: '#a5f3fc', strokeWidth: 2.5 } },
        { id: 'e4', source: 'mesh', target: 'finance', animated: true, style: { stroke: '#f87171', strokeWidth: 3.5 } }, // flashing
        { id: 'e5', source: 'policy', target: 'audit', animated: true, style: { stroke: '#67e8f9', strokeWidth: 3 } },
      ];
    } else {
      // Default Multi-Agent $1.2M Infrastructure Deployment
      baseNodes = [
        { id: 'root', type: 'agent', position: { x: 420, y: 80 }, data: { label: 'Intent Pulse', role: 'ORIGIN', trust: 0.98 } },
        { id: 'risk', type: 'agent', position: { x: 120, y: 220 }, data: { label: 'Risk Engine', role: 'VALIDATOR', trust: 0.94 } },
        { id: 'mesh', type: 'agent', position: { x: 680, y: 180 }, data: { label: 'Agent Mesh', role: 'COORDINATOR', trust: 0.91 } },
        { id: 'policy', type: 'agent', position: { x: 320, y: 380 }, data: { label: 'Policy Engine', role: 'GOVERNANCE', trust: 0.89 } },
        { id: 'finance', type: 'agent', position: { x: 820, y: 340 }, data: { label: 'Finance Approver', role: 'EXECUTOR', trust: 0.87 } },
        { id: 'audit', type: 'agent', position: { x: 520, y: 520 }, data: { label: 'Lineage Auditor', role: 'REPLAY', trust: 0.93 } },
      ];
      baseEdges = [
        { id: 'e1', source: 'root', target: 'risk', animated: true, style: { stroke: '#67e8f9', strokeWidth: 3 } },
        { id: 'e2', source: 'root', target: 'mesh', animated: true, style: { stroke: '#c084fc', strokeWidth: 3 } },
        { id: 'e3', source: 'risk', target: 'policy', animated: true, style: { stroke: '#a5f3fc', strokeWidth: 2.5 } },
        { id: 'e4', source: 'mesh', target: 'finance', animated: true, style: { stroke: '#f9a8d4', strokeWidth: 2.5 } },
        { id: 'e5', source: 'policy', target: 'audit', animated: true, style: { stroke: '#67e8f9', strokeWidth: 3 } },
        { id: 'e6', source: 'finance', target: 'audit', animated: true, style: { stroke: '#c4b5fd', strokeWidth: 2 } },
      ];
    }

    setNodes(baseNodes);
    setEdges(baseEdges);
  }, [setNodes, setEdges, currentScenario]);

  useEffect(() => {
    if (isActive) {
      initializeFullScreenTopology(currentScenario);
      
      // Continuous living execution — flowing delegation, node awakenings, trust trails
      const interval = setInterval(() => {
        setEdges(prev => prev.map((edge, i) => ({
          ...edge,
          animated: true,
          style: { 
            ...edge.style, 
            stroke: currentScenario === 'drift-escalation' && i % 2 === 0 ? '#f87171' : (i % 2 === 0 ? '#67e8f9' : '#a855f7'),
            strokeWidth: currentScenario === 'drift-escalation' ? 3.5 : 2.5,
            strokeDasharray: i % 3 === 0 ? '8 4' : undefined
          }
        })));
      }, currentScenario === 'drift-escalation' ? 800 : 1600); // faster pulsing for high-stakes drift

      return () => clearInterval(interval);
    }
  }, [isActive, initializeFullScreenTopology, setEdges, currentScenario]);

  const triggerReplayReconstruction = useCallback((nodeId = null) => {
    setReplaying(true);
    const replayData = runtimeSimulator.getReplay('rv_8f3a9c2e');
    
    // Forensic, deterministic reconstruction sweep (cryptographic inevitability)
    const illuminatedEdges = replayData.lineage.map((step, index) => ({
      id: `replay-${index}`,
      source: step.agent.includes('risk') ? 'risk' : (step.agent.includes('mesh') || step.agent.includes('finance') ? 'mesh' : 'policy'),
      target: 'audit',
      animated: true,
      style: { 
        stroke: '#a855f7', 
        strokeWidth: 4, 
        strokeDasharray: '12 6',
        strokeDashoffset: 0 
      }
    }));
    
    setEdges(prev => [...prev, ...illuminatedEdges]);
    
    // Clicked node illumination for replay reconstruction interaction
    if (nodeId && onNodeClick) {
      onNodeClick(nodeId, replayData);
    }
    
    // Precise 4.2s forensic duration matching lineage steps (cinematic restraint)
    setTimeout(() => {
      setReplaying(false);
      initializeFullScreenTopology(currentScenario);
    }, 4200);
  }, [onNodeClick, initializeFullScreenTopology, currentScenario]);

  return (
    <div className="relative h-screen w-full bg-[#050505] overflow-hidden">
      <div className="absolute inset-0">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          className="bg-transparent"
          proOptions={{ hideAttribution: true }}
        >
          <Background variant="dots" gap={32} size={1.5} color="#27272a" />
        </ReactFlow>
      </div>

      {/* Atmospheric overlays for depth and cinematic feel */}
      <div className="absolute inset-0 bg-[radial-gradient(#0a0a0a_30%,transparent_80%)] pointer-events-none"></div>
      
      {/* Scene label */}
      <div className="absolute top-8 left-8 font-mono text-xs tracking-[3px] text-white/40 z-20">
        RUNTIME TOPOLOGY — THE LIVING INTERFACE
        {currentScenario === 'drift-escalation' && <span className="text-red-400 ml-3">• DRIFT ESCALATION ACTIVE</span>}
      </div>

      {/* Scenario selector for credible demonstrations */}
      <div className="absolute top-8 right-8 flex gap-2 z-30">
        <motion.button 
          onClick={() => { setCurrentScenario('multi-agent'); initializeFullScreenTopology('multi-agent'); }}
          className={`px-5 py-2 text-xs font-mono rounded-2xl border transition-all ${currentScenario === 'multi-agent' ? 'border-sky-400 text-sky-400' : 'border-white/20 text-white/50 hover:border-white/40'}`}
        >
          MULTI-AGENT EXECUTION
        </motion.button>
        <motion.button 
          onClick={() => { setCurrentScenario('drift-escalation'); initializeFullScreenTopology('drift-escalation'); }}
          className={`px-5 py-2 text-xs font-mono rounded-2xl border transition-all ${currentScenario === 'drift-escalation' ? 'border-red-400 text-red-400' : 'border-white/20 text-white/50 hover:border-white/40'}`}
        >
          DRIFT ESCALATION
        </motion.button>
      </div>

      {/* Replay trigger - minimal floating control */}
      <motion.button
        onClick={() => triggerReplayReconstruction()}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.98 }}
        className="absolute bottom-12 left-1/2 -translate-x-1/2 z-30 px-8 py-4 border border-purple-500/50 hover:border-purple-400 text-purple-400 rounded-3xl text-sm font-mono tracking-widest flex items-center gap-3 transition-all"
      >
        {replaying ? 'RECONSTRUCTING LINEAGE...' : 'TRIGGER REPLAY RECONSTRUCTION'}
        <span className="text-xs opacity-50">→</span>
      </motion.button>

      {replaying && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.6, 1, 0.6] }}
          className="absolute inset-0 bg-purple-500/10 flex items-center justify-center z-40 pointer-events-none"
        >
          <div className="text-purple-400 font-mono text-xl tracking-[6px] animate-pulse">LINEAGE SWEEP ACTIVE • FORENSIC RECONSTRUCTION</div>
        </motion.div>
      )}
    </div>
  );
};

export default RuntimeTopologyScene;
