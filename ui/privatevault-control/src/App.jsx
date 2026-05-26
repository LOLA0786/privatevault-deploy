import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import HeroScene from './scenes/HeroScene';
import RuntimeTopologyScene from './scenes/RuntimeTopologyScene';
import TrustPropagationScene from './scenes/TrustPropagationScene';
import ReplayReconstructionScene from './scenes/ReplayReconstructionScene';
import { runtimeSimulator } from './api';

// New platform layers — all integrated into cinematic runtime language
const ArchitectureLayer = () => (
  <div className="relative h-screen bg-[#050505] flex items-center justify-center overflow-hidden">
    <div className="max-w-4xl text-center">
      <div className="font-mono text-xs tracking-[4px] text-sky-400 mb-6">PRIVATEVAULT ARCHITECTURE</div>
      <h1 className="text-6xl font-light tracking-tight mb-12">Governed Runtime</h1>
      <div className="prose prose-invert max-w-none text-left mx-auto text-lg text-white/70">
        <p>The Decision Security Control Plane provides deterministic replay, authority-aware execution, and cryptographic lineage for autonomous multi-agent systems.</p>
        <p>Core primitives: GovernanceRuntime.decide_and_execute(), ExecutionLineage, TrustPropagator (decay 0.9), ReplayReconstructor, CanonicalPolicyEngine.</p>
      </div>
      {/* Embedded topology motif */}
      <div className="mt-16 opacity-30">
        <RuntimeTopologyScene isActive={false} />
      </div>
    </div>
  </div>
);

const DocsLayer = () => (
  <div className="min-h-screen bg-[#050505] p-16 text-white">
    <div className="max-w-4xl mx-auto">
      <div className="font-mono text-xs tracking-widest text-sky-400 mb-8">OPERATIONAL INTELLIGENCE</div>
      <h1 className="text-5xl font-light tracking-tight mb-6">Runtime Documentation</h1>
      <p className="text-xl text-white/60 mb-16">Reading the governed execution layer. Every concept is tied to live topology and deterministic behavior.</p>
      
      <div className="space-y-20">
        <div>
          <h2 className="text-3xl mb-6 font-light">GovernanceRuntime</h2>
          <div className="font-mono text-sm bg-black/60 p-8 rounded-3xl border border-white/10">
            decide_and_execute(action, principal, lineage) → ExecutionLineage<br/>
            • Fail-closed by default<br/>
            • Full replay reference in every hop<br/>
            • Trust decay propagated (0.9 factor)
          </div>
        </div>
        
        <div>
          <h2 className="text-3xl mb-6 font-light">Replay Reconstruction</h2>
          <p className="text-white/70">Backward sweep through the DAG. Every decision is forensically recoverable. The signature capability of the platform.</p>
        </div>
      </div>
    </div>
  </div>
);

const CLILayer = () => {
  const [output, setOutput] = React.useState('');
  const [isRunning, setIsRunning] = React.useState(false);
  const terminalRef = React.useRef(null);

  const runCLICommand = async (cmd) => {
    setIsRunning(true);
    setOutput('> ' + cmd + '\n');
    
    const lines = runtimeSimulator.getCLIOutput(cmd.replace('pvctl ', '')).split('\n');
    
    for (let line of lines) {
      await new Promise(resolve => setTimeout(resolve, 180)); // realistic streaming timing
      setOutput(prev => prev + line + '\n');
    }
    
    setTimeout(() => {
      setOutput(prev => prev + '\n✓ Command completed. Lineage persisted.\n');
      setIsRunning(false);
    }, 800);
  };

  React.useEffect(() => {
    // Auto-demo on mount - deterministic pvctl execute
    const timer = setTimeout(() => runCLICommand('pvctl execute'), 600);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-8 relative overflow-hidden">
      <div className="max-w-3xl w-full">
        <div className="font-mono text-xs tracking-[4px] text-emerald-400 mb-6 text-center">pvctl — SOVEREIGN GOVERNANCE SHELL</div>
        <div className="text-center mb-12">
          <h1 className="text-6xl font-light tracking-tighter text-white">Runtime Terminal</h1>
          <p className="text-xl text-white/60 mt-4">Deterministic execution. Every command produces verifiable cryptographic lineage.</p>
        </div>
        
        <div ref={terminalRef} className="terminal-glow bg-black border border-emerald-500/30 rounded-3xl p-8 font-mono text-sm text-emerald-300/90 h-[420px] overflow-auto whitespace-pre leading-relaxed shadow-inner">
          {output || 'Initializing sovereign runtime shell...\nReady for governed execution.\n\nType: pvctl execute | replay | lineage | trust\n'}
        </div>

        <div className="flex gap-3 mt-6 justify-center flex-wrap">
          {['execute', 'replay', 'lineage', 'trust', 'escalate'].map(cmd => (
            <motion.button
              key={cmd}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => runCLICommand(`pvctl ${cmd}`)}
              disabled={isRunning}
              className="px-6 py-3 bg-black border border-white/20 hover:border-emerald-400 rounded-2xl text-xs font-mono tracking-widest text-white/70 hover:text-emerald-300 transition-all disabled:opacity-50"
            >
              pvctl {cmd}
            </motion.button>
          ))}
        </div>
        
        <div className="text-center mt-8 text-[10px] font-mono text-white/30">All outputs are deterministic • Trust decay applied in real-time • Replay always available</div>
      </div>
    </div>
  );
};

const EnterpriseLayer = () => (
  <div className="min-h-screen bg-[#050505] p-16 flex items-center">
    <div className="max-w-xl mx-auto text-center">
      <div className="font-mono text-xs tracking-widest text-purple-400 mb-6">MISSION CRITICAL DEPLOYMENT</div>
      <h1 className="text-6xl font-light tracking-tighter mb-8">Enterprise Access</h1>
      <p className="text-xl text-white/70 mb-12">Request sovereign runtime deployment. For organizations requiring cryptographic accountability at scale.</p>
      
      <form className="space-y-6 text-left max-w-md mx-auto" onSubmit={(e) => { e.preventDefault(); alert('Form submitted to governance ledger (simulated). High-trust request received.'); }}>
        <input type="text" placeholder="Name" className="w-full bg-black border border-white/20 rounded-2xl px-6 py-4 text-white placeholder:text-white/40" />
        <input type="text" placeholder="Company / Organization" className="w-full bg-black border border-white/20 rounded-2xl px-6 py-4 text-white placeholder:text-white/40" />
        <input type="text" placeholder="Deployment Scale (agents / workflows)" className="w-full bg-black border border-white/20 rounded-2xl px-6 py-4 text-white placeholder:text-white/40" />
        <input type="email" placeholder="Engineering Contact" className="w-full bg-black border border-white/20 rounded-2xl px-6 py-4 text-white placeholder:text-white/40" />
        <textarea placeholder="Autonomous workflow surface area" rows="4" className="w-full bg-black border border-white/20 rounded-3xl px-6 py-4 text-white placeholder:text-white/40"></textarea>
        <button type="submit" className="w-full py-5 bg-white text-black font-medium rounded-3xl tracking-wider text-sm">SUBMIT TO GOVERNANCE LAYER</button>
      </form>
      
      <div className="mt-12 text-xs text-white/30 font-mono">Responses within 48 hours • All submissions enter the audit mesh</div>
    </div>
  </div>
);

const Nav = () => {
  const location = useLocation();
  const isHome = location.pathname === '/';
  
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#050505]/90 backdrop-blur-xl border-b border-white/10">
      <div className="max-w-screen-2xl mx-auto px-10 flex items-center justify-between h-16 text-sm font-mono tracking-widest text-white/70">
        <Link to="/" className="hover:text-white transition">PRIVATEVAULT</Link>
        
        <div className="flex items-center gap-10">
          <Link to="/runtime" className={`hover:text-white transition ${location.pathname === '/runtime' ? 'text-white' : ''}`}>RUNTIME</Link>
          <Link to="/architecture" className={`hover:text-white transition ${location.pathname === '/architecture' ? 'text-white' : ''}`}>ARCHITECTURE</Link>
          <Link to="/docs" className={`hover:text-white transition ${location.pathname === '/docs' ? 'text-white' : ''}`}>DOCS</Link>
          <Link to="/cli" className={`hover:text-white transition ${location.pathname === '/cli' ? 'text-white' : ''}`}>CLI</Link>
          <Link to="/enterprise" className={`hover:text-white transition ${location.pathname === '/enterprise' ? 'text-white' : ''}`}>ENTERPRISE</Link>
          <a href="https://github.com/LOLA0786/privatevault-deploy" target="_blank" rel="noopener noreferrer" className="hover:text-white transition">GITHUB</a>
        </div>
        
        <div className="text-[10px] text-white/30">v0.3.0-CINEMATIC</div>
      </div>
    </nav>
  );
};

const AppContent = () => (
  <Router>
    <Nav />
    <Routes>
      <Route path="/" element={
        <div className="pt-16">
          <HeroScene />
          <RuntimeTopologyScene isActive={true} />
          <TrustPropagationScene />
          <ReplayReconstructionScene />
        </div>
      } />
      <Route path="/runtime" element={<RuntimeTopologyScene isActive={true} />} />
      <Route path="/architecture" element={<ArchitectureLayer />} />
      <Route path="/docs" element={<DocsLayer />} />
      <Route path="/cli" element={<CLILayer />} />
      <Route path="/enterprise" element={<EnterpriseLayer />} />
      <Route path="*" element={<div className="h-screen flex items-center justify-center text-white/40">Layer not yet unfolded</div>} />
    </Routes>
  </Router>
);

export default function App() {
  return <AppContent />;
}
