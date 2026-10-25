import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic,
  MicOff,
  Volume2,
  Sparkles,
  Search,
  MessageCircle,
  CheckCircle2,
  Radio,
  ChevronUp,
  ChevronDown,
  Monitor,
  Zap,
  Globe,
  X,
  ExternalLink
} from 'lucide-react';

export default function MacOBGListener({
  visible = true,
  onClose,
  isListening,
  toggleListening,
  isSpeaking,
  audioLevel,
  liveTranscript,
  ongoingTask,
  activeApp,
  onOpenWhatsApp,
  onSearchAndSendSonu,
  isProcessing
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  const task = ongoingTask || {
    title: 'OBG Desktop HUD',
    step: 'Listening via Wispr Engine',
    app: activeApp || 'macOS Desktop',
    status: 'idle'
  };

  const appDisplayName = activeApp || task.app || 'macOS Desktop';

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 40, scale: 0.95 }}
          transition={{ type: 'spring', stiffness: 380, damping: 28 }}
          className="fixed bottom-5 left-1/2 -translate-x-1/2 z-50 select-none max-w-[92vw]"
        >
          <div
            className={`rounded-full border shadow-[0_12px_40px_rgba(0,0,0,0.8)] backdrop-blur-2xl transition-all duration-300 ${
              isSpeaking
                ? 'bg-gradient-to-r from-cyan-950/95 via-indigo-950/95 to-purple-950/95 border-cyan-400 shadow-[0_0_35px_rgba(6,182,212,0.4)]'
                : isListening
                ? 'bg-[#091122]/95 border-emerald-500/60 shadow-[0_0_30px_rgba(16,185,129,0.35)]'
                : 'bg-[#0b1325]/95 border-white/15 hover:border-white/25'
            }`}
          >
            {/* Dynamic Island Dock Pill */}
            <div className="px-4 py-2 flex items-center gap-3">
              {/* Glowing Orb / Status Beacon */}
              <div
                onClick={toggleListening}
                className="cursor-pointer relative flex items-center justify-center shrink-0"
                title={isListening ? 'OBG is Listening (Click to Pause)' : 'Click to Activate OBG'}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center transition ${
                    isSpeaking
                      ? 'bg-gradient-to-tr from-cyan-400 to-indigo-500 text-slate-950'
                      : isListening
                      ? 'bg-emerald-500 text-slate-950'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {isSpeaking ? (
                    <Volume2 className="w-4 h-4 animate-bounce" />
                  ) : isListening ? (
                    <Mic className="w-4 h-4 animate-pulse" />
                  ) : (
                    <MicOff className="w-3.5 h-3.5" />
                  )}
                </div>

                {/* Ripple Pulse Rings */}
                {isListening && (
                  <span className="absolute -inset-1 rounded-full border-2 border-emerald-400/50 animate-ping pointer-events-none"></span>
                )}
              </div>

              {/* Soundwave Energy Equalizer */}
              <div className="flex items-end gap-0.5 h-3.5 w-4 shrink-0">
                <span
                  className="w-1 bg-cyan-400 rounded-full transition-all duration-75"
                  style={{ height: `${Math.max(3, (audioLevel * 14) / 100)}px` }}
                />
                <span
                  className="w-1 bg-emerald-400 rounded-full transition-all duration-75"
                  style={{ height: `${Math.max(4, (audioLevel * 18) / 100)}px` }}
                />
                <span
                  className="w-1 bg-cyan-400 rounded-full transition-all duration-75"
                  style={{ height: `${Math.max(2, (audioLevel * 12) / 100)}px` }}
                />
              </div>

              {/* Center Info Text */}
              <div className="min-w-[190px] max-w-[340px]">
                <div className="flex items-center gap-1.5">
                  <span className="text-[10px] font-mono uppercase font-black tracking-wider text-cyan-300 truncate">
                    {appDisplayName}
                  </span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-white/10 text-slate-300 font-mono shrink-0">
                    {isSpeaking ? 'Speaking' : isListening ? 'Listening' : 'Desktop HUD'}
                  </span>
                </div>

                {/* Live speech transcription or current task status */}
                {liveTranscript ? (
                  <p className="text-xs font-semibold text-white truncate animate-pulse">
                    "{liveTranscript}"
                  </p>
                ) : (
                  <p className="text-xs font-medium text-slate-200 truncate">
                    {task.step || 'Say "Hey Kyron" or speak your directive...'}
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-1 shrink-0">
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="p-1 rounded-full hover:bg-white/10 text-slate-400 hover:text-white transition"
                  title={isExpanded ? 'Collapse Quick Actions' : 'Expand Quick Actions'}
                >
                  {isExpanded ? (
                    <ChevronDown className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronUp className="w-3.5 h-3.5" />
                  )}
                </button>

                {onClose && (
                  <button
                    onClick={onClose}
                    className="p-1 rounded-full hover:bg-white/10 text-slate-400 hover:text-rose-400 transition ml-0.5"
                    title="Hide Desktop HUD"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>
            </div>

            {/* Expanded Quick Action Chips (Desktop & Home Screen Synchronization) */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="px-4 pb-2.5 pt-1 border-t border-white/5 flex items-center gap-2 overflow-x-auto text-[11px]"
                >
                  <button
                    onClick={onOpenWhatsApp}
                    disabled={isProcessing}
                    className="px-2.5 py-1 rounded-full bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 font-semibold flex items-center gap-1 transition shrink-0"
                  >
                    <MessageCircle className="w-3 h-3 text-emerald-400" />
                    <span>Open WhatsApp</span>
                  </button>

                  <button
                    onClick={onSearchAndSendSonu}
                    disabled={isProcessing}
                    className="px-2.5 py-1 rounded-full bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 font-semibold flex items-center gap-1 transition shrink-0"
                  >
                    <Search className="w-3 h-3 text-cyan-400" />
                    <span>Search Sonu & Send "Hi Sonu"</span>
                  </button>

                  <div className="flex items-center gap-1 text-[10px] text-slate-400 font-mono pl-1 shrink-0">
                    <Monitor className="w-3 h-3 text-cyan-400" />
                    <span>macOS Desktop Synchronized</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
