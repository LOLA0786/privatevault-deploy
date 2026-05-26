import React from 'react';
import { motion } from 'framer-motion';

const HeroScene = () => {
  return (
    <div className="relative h-screen bg-[#050505] flex items-center justify-center overflow-hidden">
      {/* Atmospheric depth layers */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(59,130,246,0.12)_0%,transparent_60%)]"></div>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_70%,rgba(168,85,247,0.08)_0%,transparent_70%)]"></div>
      
      {/* Extremely restrained spatial reference — supports topology without competing */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.018)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.018)_1px,transparent_1px)] bg-[size:64px_64px]"></div>

      <div className="relative z-10 text-center px-6">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.8, ease: [0.23, 1, 0.32, 1] }}
        >
          <div className="font-mono text-xs tracking-[3px] text-sky-400/90 mb-8">PRIVATEVAULT</div>
          
          <h1 className="text-[clamp(3.2rem,8vw,5.2rem)] font-light tracking-[-0.04em] leading-none text-white mb-6">
            DECISION SECURITY<br />CONTROL PLANE
          </h1>
          
          <p className="max-w-md mx-auto text-lg text-white/70 tracking-tight mb-8">
            Runtime governance for autonomous systems
          </p>
          
          <div className="flex flex-wrap justify-center gap-x-8 gap-y-1 text-[13px] text-white/50 font-mono tracking-widest">
            <div>DETERMINISTIC REPLAY</div>
            <div>TRUST PROPAGATION</div>
            <div>AUTHORITY-AWARE EXECUTION</div>
            <div>CRYPTGRAPHIC LINEAGE</div>
          </div>
        </motion.div>
      </div>

      {/* Single semantic intent pulse — origin of execution, no decorative layers */}
      <motion.div
        className="absolute left-1/2 top-1/2 w-5 h-5 border border-sky-400/80 rounded-full"
        animate={{ scale: [0.8, 3.2, 0.8], opacity: [0.7, 0.15, 0.7] }}
        transition={{ duration: 5.5, repeat: Infinity, ease: "easeInOut" }}
      />

      <div className="absolute bottom-16 left-1/2 -translate-x-1/2 text-xs font-mono text-white/30 tracking-[2px]">
        THE REPLAY TOPOLOGY IS THE INTERFACE
      </div>
    </div>
  );
};

export default HeroScene;
