import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Globe,
  Monitor,
  ExternalLink,
  Lock,
  ArrowRight,
  AlertTriangle,
  Loader2,
  Zap,
} from 'lucide-react';

/**
 * ActionPreviewCard Component
 * Generic, reusable Safety Gate modal/card for both:
 * 1. BROWSER Actions (e.g. checkout, payment submit, delete, publish)
 * 2. SYSTEM/OS Actions (e.g. WhatsApp message dispatch, OS commands)
 *
 * Implements the core KYRON safety invariant:
 * Irreversible actions NEVER fire automatically. Only a physical user click executes them.
 */
export default function ActionPreviewCard({
  actionId,
  type = 'browser', // 'browser' | 'system'
  app = 'Browser',
  target = '',
  description = 'Irreversible action requires approval',
  website = '',
  pageTitle = '',
  riskLevel = 'high',
  onConfirm,
  onReject,
  isConfirming = false,
  status = 'pending_confirmation', // 'pending_confirmation' | 'executed' | 'rejected'
}) {
  const [localStatus, setLocalStatus] = useState(status);
  const isBrowser = type === 'browser';
  const isExecuted = localStatus === 'executed';
  const isRejected = localStatus === 'rejected';

  const handleConfirm = async () => {
    if (onConfirm) {
      await onConfirm(actionId);
      setLocalStatus('executed');
    }
  };

  const handleReject = async () => {
    if (onReject) {
      await onReject(actionId);
      setLocalStatus('rejected');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`my-3 rounded-xl border overflow-hidden backdrop-blur-xl transition-all duration-300 shadow-2xl ${
        isExecuted
          ? 'bg-[#061e16]/90 border-emerald-500/50 shadow-emerald-950/40'
          : isRejected
          ? 'bg-[#1e0a0a]/90 border-rose-500/40 shadow-rose-950/30'
          : 'bg-[#0c101c]/95 border-amber-500/40 shadow-amber-950/20'
      }`}
    >
      {/* Top Banner */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-950/70 border-b border-white/5">
        <div className="flex items-center space-x-2">
          <div
            className={`p-1.5 rounded-lg ${
              isExecuted
                ? 'bg-emerald-500/20 text-emerald-400'
                : isRejected
                ? 'bg-rose-500/20 text-rose-400'
                : 'bg-amber-500/20 text-amber-400'
            }`}
          >
            {isExecuted ? (
              <CheckCircle2 className="w-4 h-4" />
            ) : isRejected ? (
              <XCircle className="w-4 h-4" />
            ) : (
              <ShieldAlert className="w-4 h-4 animate-pulse" />
            )}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-100">
                {isBrowser ? 'Browser Safety Gate' : 'System Safety Gate'}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300">
                DRY-RUN PAUSED
              </span>
            </div>
          </div>
        </div>

        {/* Action Type Badge */}
        <div className="flex items-center space-x-2">
          <div className="text-[10px] font-mono px-2.5 py-1 rounded bg-slate-800/80 text-slate-300 border border-slate-700/60 flex items-center gap-1.5">
            {isBrowser ? <Globe className="w-3 h-3 text-blue-400" /> : <Monitor className="w-3 h-3 text-teal-400" />}
            <span>{app}</span>
          </div>
        </div>
      </div>

      {/* Main Body */}
      <div className="p-4 space-y-3">
        <div className="space-y-1">
          <div className="text-xs font-mono text-slate-400">Target Destination / Context:</div>
          <div className="text-sm font-semibold text-cyan-200 font-mono break-all flex items-center gap-1.5">
            <span>{website || target || pageTitle || 'Active Target'}</span>
          </div>
        </div>

        <div className="p-3 rounded-lg bg-black/50 border border-amber-500/20 space-y-1.5">
          <div className="text-[11px] font-mono text-amber-300 flex items-center gap-1.5 font-medium">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>Pending Irreversible Operation:</span>
          </div>
          <div className="text-xs sm:text-sm text-slate-100 font-sans leading-relaxed">
            {description}
          </div>
        </div>

        {/* Status Messaging */}
        {isExecuted && (
          <div className="flex items-center space-x-2 text-emerald-400 text-xs font-mono pt-1">
            <CheckCircle2 className="w-4 h-4" />
            <span>Operation confirmed by operator. Action executed successfully.</span>
          </div>
        )}

        {isRejected && (
          <div className="flex items-center space-x-2 text-rose-400 text-xs font-mono pt-1">
            <XCircle className="w-4 h-4" />
            <span>Operation cancelled. No changes or submissions were made.</span>
          </div>
        )}
      </div>

      {/* Bottom Action Gate Controls */}
      {!isExecuted && !isRejected && (
        <div className="px-4 py-3 bg-slate-950/90 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-amber-400" />
            <span>Awaiting physical operator signature</span>
          </div>

          <div className="flex items-center space-x-2.5 w-full sm:w-auto justify-end">
            <button
              onClick={handleReject}
              disabled={isConfirming}
              className="px-3.5 py-1.5 rounded-lg border border-slate-700 bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-mono transition-all flex items-center gap-1.5 disabled:opacity-50"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Reject & Discard</span>
            </button>

            <button
              onClick={handleConfirm}
              disabled={isConfirming}
              className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-xs font-mono transition-all flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 active:scale-95 disabled:opacity-50"
            >
              {isConfirming ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Executing...</span>
                </>
              ) : (
                <>
                  <Zap className="w-3.5 h-3.5" />
                  <span>⚡ Confirm & Execute</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
}
