import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Globe,
  Shield,
  RotateCw,
  CheckCircle2,
  Play,
  Pause,
  ExternalLink,
  ChevronUp,
  ChevronDown,
  X,
  Maximize2,
  Sparkles,
  MousePointer,
  FormInput,
  Terminal,
  Layers,
  ArrowRight
} from 'lucide-react';

export default function MacChromeFooterHUD({
  visible = true,
  task,
  activeApp = 'Google Chrome',
  steps = [],
  isProcessing = false,
  onClose,
  onOpenFullMirror
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [simulatedProgress, setSimulatedProgress] = useState(65);
  const [cursorPos, setCursorPos] = useState({ x: 540, y: 320 });

  // Determine current active URL & Action
  const activeTask = task || {
    title: 'Autonomous Form & Browser Navigation',
    step: 'Automating DOM inputs & submitting form fields',
    app: activeApp || 'Google Chrome',
    url: 'https://forms.google.com/kyron-autonomous-entry',
    progress: 75
  };

  const currentUrl =
    activeTask.url ||
    (activeTask.title?.toLowerCase().includes('whatsapp')
      ? 'https://web.whatsapp.com'
      : activeTask.title?.toLowerCase().includes('instagram')
      ? 'https://www.instagram.com/direct/inbox/'
      : activeTask.title?.toLowerCase().includes('song') || activeTask.title?.toLowerCase().includes('youtube')
      ? 'https://www.youtube.com/watch?v=autonomous'
      : 'https://google.com/search?q=Kyron+AGI');

  // Simulate cursor movement and form field typing effect when active
  useEffect(() => {
    if (!visible) return;
    const interval = setInterval(() => {
      setCursorPos({
        x: Math.floor(Math.random() * 240) + 400,
        y: Math.floor(Math.random() * 160) + 240
      });
      setSimulatedProgress((prev) => (prev >= 95 ? 60 : prev + 5));
    }, 2400);
    return () => clearInterval(interval);
  }, [visible]);

  if (!visible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50, scale: 0.94 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 50, scale: 0.94 }}
        transition={{ type: 'spring', stiffness: 350, damping: 26 }}
        className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 select-none max-w-[94vw] w-[620px]"
      >
        <div className="rounded-2xl bg-[#0b1325]/95 border border-cyan-400/40 shadow-[0_16px_50px_rgba(0,0,0,0.85)] backdrop-blur-2xl overflow-hidden flex flex-col transition-all">
          {/* 1. CHROME BROWSER TOP BAR (macOS Traffic lights + Tab) */}
          <div className="px-3.5 py-2 bg-[#121c33]/90 border-b border-white/10 flex items-center justify-between gap-3">
            {/* macOS Window Controls + Chrome Logo */}
            <div className="flex items-center gap-2.5">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56] inline-block shadow-sm"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e] inline-block shadow-sm"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-[#27c93f] inline-block shadow-sm"></span>
              </div>

              {/* Chrome Multi-color Icon Indicator */}
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-lg bg-black/40 border border-white/5">
                <div className="relative w-4 h-4 flex items-center justify-center">
                  <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="#4285F4" strokeWidth="2" />
                    <circle cx="12" cy="12" r="4" fill="#4285F4" />
                    <path d="M12 2a10 10 0 0 1 8.66 5H12" stroke="#EA4335" strokeWidth="2" />
                    <path d="M20.66 7a10 10 0 0 1-5 13.66L12 16" stroke="#FBBC05" strokeWidth="2" />
                    <path d="M7 16a10 10 0 0 1-5-6.66L7 12" stroke="#34A853" strokeWidth="2" />
                  </svg>
                </div>
                <span className="text-[11px] font-bold text-slate-200 font-mono tracking-tight">
                  Google Chrome
                </span>
                <span className="text-[9px] font-mono text-cyan-300 bg-cyan-950/80 px-1 rounded border border-cyan-500/30">
                  Autonomous HUD
                </span>
              </div>
            </div>

            {/* Live Controller Status Badge */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-[10px] text-emerald-300 font-mono font-semibold">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
                </span>
                <span>KYRON CONTROLLING</span>
              </div>

              {/* Expand / Collapse Button */}
              <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition"
                title={isExpanded ? 'Collapse Viewport' : 'Expand Live Viewport'}
              >
                {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
              </button>

              {/* Close HUD */}
              {onClose && (
                <button
                  onClick={onClose}
                  className="p-1 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-950/30 transition"
                  title="Hide Chrome HUD"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          </div>

          {/* 2. CHROME OMNIBOX & LIVE URL ADDRESS BAR */}
          <div className="px-3.5 py-1.5 bg-[#0e1628] border-b border-white/5 flex items-center gap-2 text-xs">
            <div className="flex items-center gap-1 text-emerald-400 shrink-0">
              <Shield className="w-3.5 h-3.5" />
            </div>

            {/* Address Bar Pill */}
            <div className="flex-1 bg-black/50 border border-white/10 rounded-xl px-2.5 py-1 flex items-center justify-between text-[11px] font-mono text-slate-300 overflow-hidden">
              <div className="flex items-center gap-1.5 truncate">
                <span className="text-slate-500">https://</span>
                <span className="text-cyan-300 font-semibold truncate">
                  {currentUrl.replace('https://', '')}
                </span>
              </div>
              <span className="text-[9px] uppercase tracking-wider text-emerald-400 bg-emerald-950/90 px-1.5 py-0.2 rounded font-bold border border-emerald-500/30 shrink-0 ml-1">
                Playwright Connected
              </span>
            </div>

            {/* Coordinates / DOM Pointer Badge */}
            <div className="hidden sm:flex items-center gap-1 text-[10px] text-slate-400 font-mono bg-white/[0.03] px-2 py-1 rounded-lg border border-white/5 shrink-0">
              <MousePointer className="w-3 h-3 text-cyan-400 animate-pulse" />
              <span>X:{cursorPos.x} Y:{cursorPos.y}</span>
            </div>
          </div>

          {/* 3. ACTIVE TASK & FORM FILLING ACTION ROW */}
          <div className="px-3.5 py-2.5 bg-gradient-to-r from-cyan-950/20 via-slate-900/40 to-indigo-950/20 flex items-center justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs font-bold text-white truncate">
                  {activeTask.title || 'Automating Browser Action'}
                </span>
                <RotateCw className="w-3 h-3 text-cyan-400 animate-spin shrink-0" />
              </div>
              <p className="text-[11px] text-cyan-300/90 font-mono truncate">
                {activeTask.step || 'Target selector located: Injecting verified form data...'}
              </p>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-1.5 shrink-0">
              <button
                onClick={() => setIsPaused(!isPaused)}
                className="px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-[10px] text-slate-300 font-medium flex items-center gap-1 transition"
                title={isPaused ? 'Resume Automation' : 'Pause Automation'}
              >
                {isPaused ? <Play className="w-3 h-3 text-emerald-400" /> : <Pause className="w-3 h-3 text-amber-400" />}
                <span>{isPaused ? 'Resume' : 'Pause'}</span>
              </button>

              {onOpenFullMirror && (
                <button
                  onClick={onOpenFullMirror}
                  className="px-2 py-1 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-[10px] text-cyan-200 font-semibold flex items-center gap-1 transition"
                  title="Open Full Screen Mirror"
                >
                  <Maximize2 className="w-3 h-3" />
                  <span className="hidden sm:inline">Inspect</span>
                </button>
              )}
            </div>
          </div>

          {/* 4. PROGRESS BAR */}
          <div className="w-full bg-slate-900 h-1 overflow-hidden">
            <motion.div
              initial={{ width: '40%' }}
              animate={{ width: `${activeTask.progress || simulatedProgress}%` }}
              transition={{ duration: 0.4 }}
              className="h-full bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 animate-pulse"
            ></motion.div>
          </div>

          {/* 5. COLLAPSIBLE EXPANDED MINI VIEWPORT & STEP LOGS */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.25 }}
                className="border-t border-white/10 bg-[#080d19] p-3 space-y-2.5 overflow-hidden"
              >
                {/* Simulated Interactive Chrome Screen Viewport */}
                <div className="relative rounded-xl border border-cyan-500/30 bg-black/80 h-36 overflow-hidden flex flex-col justify-between p-3">
                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400 border-b border-white/10 pb-1.5">
                    <span className="flex items-center gap-1 text-cyan-300">
                      <FormInput className="w-3.5 h-3.5 text-cyan-400" />
                      Playwright Form Autofill Simulation
                    </span>
                    <span className="text-emerald-400">100% Native Playwright Sandbox</span>
                  </div>

                  {/* Visual simulated DOM form elements being filled */}
                  <div className="space-y-1.5 py-1">
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-slate-400 w-24 truncate text-right font-mono">Full Name:</span>
                      <div className="flex-1 bg-white/5 border border-cyan-500/40 rounded px-2 py-0.5 text-cyan-200 font-mono text-[10px] flex items-center justify-between">
                        <span>Asif Aslam (Sonu Sarkar)</span>
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-slate-400 w-24 truncate text-right font-mono">Mobile / UID:</span>
                      <div className="flex-1 bg-white/5 border border-cyan-500/40 rounded px-2 py-0.5 text-cyan-200 font-mono text-[10px] flex items-center justify-between">
                        <span>+91 98350 78219 • Verified Vault</span>
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      </div>
                    </div>
                  </div>

                  {/* Simulated Animated Cursor Indicator */}
                  <div
                    className="absolute pointer-events-none transition-all duration-300"
                    style={{ left: `${(cursorPos.x % 300) + 40}px`, top: `${(cursorPos.y % 70) + 40}px` }}
                  >
                    <div className="relative flex items-center gap-1 bg-cyan-500 text-black px-1.5 py-0.5 rounded text-[9px] font-black shadow-lg shadow-cyan-500/50">
                      <MousePointer className="w-2.5 h-2.5 fill-black" />
                      <span>Kyron Typing</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[9px] font-mono text-slate-500 border-t border-white/5 pt-1">
                    <span>Target DOM Node: &lt;input name="candidate_name" /&gt;</span>
                    <span className="text-cyan-400">Latency: 14ms</span>
                  </div>
                </div>

                {/* Recent Playwright Steps */}
                <div className="space-y-1">
                  <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider flex items-center gap-1">
                    <Terminal className="w-3 h-3 text-cyan-400" />
                    <span>Recent Chrome Automation Operations</span>
                  </div>
                  <div className="space-y-1 max-h-20 overflow-y-auto custom-scrollbar font-mono text-[10px]">
                    <div className="flex items-center gap-1.5 text-emerald-300 bg-emerald-950/30 px-2 py-0.5 rounded">
                      <CheckCircle2 className="w-3 h-3 shrink-0" />
                      <span className="truncate">Page loaded: {currentUrl}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-cyan-300 bg-cyan-950/30 px-2 py-0.5 rounded">
                      <ArrowRight className="w-3 h-3 shrink-0" />
                      <span className="truncate">Injected Document Vault credentials into target form inputs</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
