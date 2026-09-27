import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  FileCode2,
  Terminal,
  ChevronDown,
  ChevronUp,
  Brain,
  Sparkles,
  Zap,
  Lock,
  ArrowRight,
  Code2,
  Check,
  RotateCcw
} from 'lucide-react';

/**
 * DiffCard Component
 * Implements the CRITICAL safety gate:
 * Never auto-applies code to production files.
 * Only clicking the physical "Apply Fix" button sends apply=true to the backend.
 */
export function DiffCard({
  targetFile = 'services/pricing.py',
  diff = '',
  testResult = 'Passed',
  iteration = 1,
  onApply,
  onReject,
  isApplying = false,
  applied = false
}) {
  const [copied, setCopied] = useState(false);

  const copyDiff = () => {
    navigator.clipboard.writeText(diff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Parse diff lines into syntax styled elements
  const lines = diff ? diff.split('\n') : [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`rounded-xl border overflow-hidden backdrop-blur-md transition-all duration-300 shadow-xl ${
        applied
          ? 'bg-[#061e16]/80 border-emerald-500/40 shadow-emerald-950/30'
          : 'bg-[#090d16]/90 border-cyan-500/30 shadow-cyan-950/20'
      }`}
    >
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between px-4 py-3 border-b border-cyan-500/20 bg-slate-950/60 gap-2">
        <div className="flex items-center space-x-2.5 min-w-0">
          <div className={`p-1.5 rounded-lg ${applied ? 'bg-emerald-500/20 text-emerald-400' : 'bg-cyan-500/20 text-cyan-400'}`}>
            <FileCode2 className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-semibold text-slate-100 truncate">
                {targetFile}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                Iteration {iteration}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block"></span>
              Sandbox Verification: <span className="text-emerald-300 font-semibold">{testResult}</span>
            </p>
          </div>
        </div>

        {/* Copy and Mode Tag */}
        <div className="flex items-center space-x-2">
          <button
            onClick={copyDiff}
            className="text-[11px] font-mono px-2.5 py-1 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 transition-colors flex items-center gap-1 border border-slate-700/60"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Terminal className="w-3 h-3" />}
            {copied ? 'Copied' : 'Copy Diff'}
          </button>
          <div className="text-[10px] font-mono px-2 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 flex items-center gap-1">
            <Lock className="w-3 h-3 text-amber-400" />
            <span>DRY-RUN GATED</span>
          </div>
        </div>
      </div>

      {/* Code Unified Diff Viewer */}
      <div className="p-3 bg-black/60 font-mono text-[11px] leading-relaxed max-h-72 overflow-y-auto custom-scrollbar border-b border-cyan-500/10 select-text">
        {lines.length === 0 ? (
          <div className="text-slate-500 text-center py-4">No diff lines generated yet.</div>
        ) : (
          lines.map((line, idx) => {
            const isAdded = line.startsWith('+') && !line.startsWith('+++');
            const isRemoved = line.startsWith('-') && !line.startsWith('---');
            const isHeader = line.startsWith('@@') || line.startsWith('---') || line.startsWith('+++');

            let lineBg = 'transparent';
            let lineText = 'text-slate-300';

            if (isAdded) {
              lineBg = 'bg-emerald-500/15';
              lineText = 'text-emerald-300';
            } else if (isRemoved) {
              lineBg = 'bg-rose-500/15';
              lineText = 'text-rose-300 line-through opacity-85';
            } else if (isHeader) {
              lineBg = 'bg-cyan-950/30';
              lineText = 'text-cyan-400 font-semibold';
            }

            return (
              <div
                key={idx}
                className={`flex items-start px-2 py-0.5 rounded-sm hover:bg-white/5 transition-colors ${lineBg}`}
              >
                <span className="w-7 select-none text-[10px] text-slate-600 font-mono text-right pr-3">
                  {idx + 1}
                </span>
                <span className={`flex-1 break-all ${lineText}`}>
                  {line}
                </span>
              </div>
            );
          })
        )}
      </div>

      {/* Safety Gate Warning & Action Bar */}
      <div className="p-3.5 bg-slate-950/90 flex flex-col sm:flex-row items-center justify-between gap-3">
        {applied ? (
          <div className="flex items-center space-x-2 text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-xs font-mono font-medium">
              Applied successfully to disk. Production code updated.
            </span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 text-amber-300 text-xs font-mono">
            <ShieldAlert className="w-4 h-4 shrink-0 text-amber-400 animate-pulse" />
            <span>
              Dry-run preview. File has <strong>NOT</strong> been modified on disk.
            </span>
          </div>
        )}

        <div className="flex items-center space-x-2.5 w-full sm:w-auto justify-end">
          {!applied ? (
            <>
              {onReject && (
                <button
                  onClick={onReject}
                  className="px-3 py-1.5 rounded-lg border border-slate-700/80 bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-mono flex items-center space-x-1.5 transition-all"
                >
                  <XCircle className="w-3.5 h-3.5" />
                  <span>Reject</span>
                </button>
              )}
              {onApply && (
                <button
                  onClick={onApply}
                  disabled={isApplying}
                  className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-semibold text-xs font-mono flex items-center space-x-1.5 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Zap className="w-3.5 h-3.5" />
                  <span>{isApplying ? 'Applying to Disk...' : '⚡ Apply Fix (Commit)'}</span>
                </button>
              )}
            </>
          ) : (
            <div className="text-[11px] font-mono px-3 py-1 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>COMMIT VERIFIED</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

/**
 * ReasoningTrace Accordion Component
 * Shows step-by-step thinking of the AGI agent with expandable thoughts.
 */
export function ReasoningTrace({ thoughts = [], executionTime = '1.2s' }) {
  const [isOpen, setIsOpen] = useState(true);

  if (!thoughts || thoughts.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border border-cyan-500/25 bg-[#090e18]/80 backdrop-blur-md overflow-hidden shadow-lg shadow-cyan-950/10"
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-slate-900/60 hover:bg-slate-900/80 transition-colors text-left"
      >
        <div className="flex items-center space-x-2">
          <Brain className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-mono font-medium text-slate-200">
            KYRON Reasoning Trace ({thoughts.length} {thoughts.length === 1 ? 'step' : 'steps'})
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {executionTime}
          </span>
        </div>
        <div className="text-slate-400 hover:text-slate-200">
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="p-3 border-t border-cyan-500/10 space-y-2 bg-black/40 font-mono text-xs"
          >
            {thoughts.map((step, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-lg bg-slate-900/40 border border-slate-800 flex items-start space-x-2.5 text-slate-300"
              >
                <div className="w-5 h-5 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-[10px] text-cyan-300 font-bold shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-semibold text-cyan-200">
                      {step.title || `Phase ${idx + 1}: Thought Process`}
                    </span>
                    {step.time && <span className="text-[10px] text-slate-500">{step.time}</span>}
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed whitespace-pre-wrap">
                    {step.detail || step}
                  </p>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

/**
 * SkillLearnedCard
 * Informs the user when Hermes autonomously learned or matched a skill
 */
export function SkillLearnedCard({ skillName = 'bookmygaadi-bug-check', trigger = 'pricing flat discount error' }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-xl border border-violet-500/30 bg-gradient-to-r from-violet-950/30 to-purple-950/20 p-3.5 backdrop-blur-md flex items-center space-x-3 shadow-lg shadow-purple-950/20"
    >
      <div className="w-9 h-9 rounded-lg bg-violet-500/20 border border-violet-500/40 flex items-center justify-center text-violet-300 shrink-0">
        <Sparkles className="w-5 h-5 animate-pulse" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono font-bold text-violet-200">
            Autonomous Skill Activated
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30">
            Hermes Engine
          </span>
        </div>
        <p className="text-[11px] text-slate-300 font-mono mt-0.5 truncate">
          Matched: <span className="text-violet-300 font-semibold">{skillName}</span>
        </p>
      </div>
    </motion.div>
  );
}

/**
 * JarvisMessageCard
 * Renders standard assistant text messages with mission control telemetry badge
 */
export function JarvisMessageCard({
  message,
  timestamp = 'Just now',
  memoryRecalled = null
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 rounded-xl border border-cyan-500/20 bg-[#080d19]/90 backdrop-blur-md shadow-lg shadow-cyan-950/20 space-y-2.5"
    >
      <div className="flex items-center justify-between border-b border-cyan-500/10 pb-2">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></div>
          <span className="text-xs font-mono font-semibold text-cyan-300 tracking-wider">
            KYRON // TELEMETRY RESPONSE
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-500">{timestamp}</span>
      </div>

      <div className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">
        {message}
      </div>

      {memoryRecalled && (
        <div className="mt-2 pt-2 border-t border-cyan-500/10 flex items-center space-x-2 text-[10px] font-mono text-cyan-400">
          <Brain className="w-3.5 h-3.5" />
          <span>Hermes Memory Recall: {memoryRecalled}</span>
        </div>
      )}
    </motion.div>
  );
}

export { default as ActionPreviewCard } from './ActionPreviewCard';
