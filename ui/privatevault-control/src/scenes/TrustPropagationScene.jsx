import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { runtimeSimulator } from '../api';

const TrustPropagationScene = () => {
  const [trustData, setTrustData] = useState(null);
  const [pulses, setPulses] = useState([]);

  useEffect(() => {
    const data = runtimeSimulator.getNarrativeFlow();
    setTrustData(data);
    
    // Simulate trust decay pulses
    const pulseInterval = setInterval(() => {
      setPulses(prev => {
        const newPulses = [...prev, Date.now()];
        return newPulses.slice(-6); // limit visible pulses
      });
    }, 420);

    return () => clearInterval(pulseInterval);
  }, []);

  return (
    <div className="relative h-screen bg-[#050505] flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(at_center,#1a1a2e_0%,transparent_70%)]"></div>
      
      <div className="relative z-10 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.6 }}
        >
          <div className="font-mono text-xs tracking-[4px] text-emerald-400 mb-6">TRUST MESH</div>
          <h2 className="text-6xl font-light tracking-[-0.04em] text-white mb-6">Propagation</h2>
          <p className="max-w-xs mx-auto text-lg text-white/60">Authority flows. Decay is measured in real time. Lineage remains immutable.</p>
        </motion.div>
      </div>

      {/* Pure spatial trust — volumetric pulses, edge decay, propagation trails (no tables) */}
      {pulses.slice(0, 4).map((ts, i) => (
        <motion.div
          key={ts}
          className="absolute h-px bg-gradient-to-r from-transparent via-purple-400/70 via-50% to-transparent"
          style={{ 
            top: `${22 + (i * 14)}%`,
            left: `${15 + (i % 2) * 8}%`,
            width: `${65 - i * 4}%`
          }}
          initial={{ scaleX: 0.2, opacity: 0.4 }}
          animate={{ 
            scaleX: [0.2, 1.15, 0.3], 
            opacity: [0.4, 0.85, 0.3] 
          }}
          transition={{ duration: 3.8, delay: i * 0.45, ease: "easeInOut" }}
        />
      ))}

      <div className="absolute bottom-14 font-mono text-[10px] text-white/25 tracking-[1px]">SPATIAL TRUST PROPAGATION</div>
    </div>
  );
};

export default TrustPropagationScene;
