import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { runtimeSimulator } from '../api';

const ReplayReconstructionScene = () => {
  const [isReconstructing, setIsReconstructing] = useState(false);
  const [replayData, setReplayData] = useState(null);

  const startReconstruction = () => {
    setIsReconstructing(true);
    const data = runtimeSimulator.getReplay('rv_8f3a9c2e');
    setReplayData(data);
    
    setTimeout(() => {
      setIsReconstructing(false);
    }, 4200);
  };

  return (
    <div className="relative h-screen bg-black flex items-center justify-center overflow-hidden">
      {/* Cryptographic grid for forensic inevitability */}
      <div className="absolute inset-0 bg-[repeating-linear-gradient(45deg,#111_0,#111_1px,transparent_1px,transparent_32px)] opacity-20"></div>
      
      <div className="relative z-10 text-center max-w-3xl px-8">
        <motion.div
          animate={isReconstructing ? { opacity: [0.6, 1] } : {}}
          className="mb-8"
        >
          <div className="text-rose-400/80 font-mono text-xs tracking-[3px] mb-6">MERKLE • LINEAGE • EVIDENCE</div>
          <h2 className="text-[4.8rem] leading-[0.92] font-light tracking-[-0.05em] text-white">REPLAY<br />RECONSTRUCTION</h2>
        </motion.div>

        <p className="text-lg text-white/60 max-w-md mx-auto mb-20">
          The sweep is deterministic.<br />Every edge, every decision, every trust score is recovered with cryptographic precision.
        </p>

        {!replayData ? (
          <motion.button
            onClick={startReconstruction}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className="px-14 py-5 border border-white/40 hover:border-white/80 text-sm font-mono tracking-[2.5px] rounded-3xl text-white/90 transition-all"
          >
            INITIATE FORENSIC SWEEP
          </motion.button>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-zinc-950 border border-purple-500/30 p-8 rounded-3xl text-left font-mono text-sm max-w-xl mx-auto"
          >
            <div className="text-emerald-400 mb-6">✓ RECONSTRUCTION COMPLETE — 4 STEPS RECOVERED</div>
            {replayData.lineage.map((step, i) => (
              <div key={i} className="flex justify-between py-3 border-b border-white/10 last:border-0">
                <span className="text-white/80">{step.agent}</span>
                <span className="text-purple-400">{step.trust}</span>
              </div>
            ))}
            <div className="mt-8 text-[10px] text-white/40">REPLAY REFERENCE: {replayData.replay_reference}<br />CORRELATION: {replayData.correlation_id}</div>
          </motion.div>
        )}
      </div>

      {/* Forensic sweep — cryptographic, inevitable, deterministic */}
      {isReconstructing && (
        <motion.div 
          className="absolute inset-0 bg-gradient-to-r from-transparent via-purple-500/10 to-transparent"
          animate={{ x: ['-120%', '320%'] }}
          transition={{ duration: 3.8, ease: "linear" }}
        />
      )}

      <div className="absolute bottom-14 font-mono text-[10px] text-white/25 tracking-widest">REPLAY LAYER • DETERMINISTIC LINEAGE RECONSTRUCTION</div>
    </div>
  );
};

export default ReplayReconstructionScene;
