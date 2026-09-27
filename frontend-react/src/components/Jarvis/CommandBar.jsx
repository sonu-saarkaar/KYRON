import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Sparkles,
  Terminal,
  Bug,
  Brain,
  Clock,
  ShieldAlert,
  ArrowUp,
  Radio
} from 'lucide-react';

export default function CommandBar({
  onCommandSubmit,
  disabled = false,
  status = 'idle',
  isListening = false,
  isSpeaking = false,
  isMuted = false,
  liveTranscript = '',
  onToggleMic,
  onToggleMute
}) {
  const [input, setInput] = useState('');
  const inputRef = useRef(null);

  const suggestionChips = [
    {
      id: 'diagnose-bug',
      label: 'Diagnose BookMyGaadi pricing bug',
      icon: Bug,
      category: 'code',
      prompt: 'Diagnose and fix the BookMyGaadi flat deduction bug in services/pricing.py using CodeAgent (Dry Run)',
      isCodeAgent: true
    },
    {
      id: 'hermes-skills',
      label: 'Inspect learned skills',
      icon: Sparkles,
      category: 'skills',
      prompt: 'List all autonomous skills learned by KYRON and display their procedures'
    },
    {
      id: 'trigger-cron',
      label: 'Trigger morning autonomous health check',
      icon: Clock,
      category: 'cron',
      prompt: 'Run the scheduled BookMyGaadi health check cycle now'
    },
    {
      id: 'store-memory',
      label: 'Remember: DB is Postgres & BookMyGaadi port is 5000',
      icon: Brain,
      category: 'memory',
      prompt: 'Yaad rakhna: BookMyGaadi runs on port 5000 and uses PostgreSQL with isolated sandbox'
    }
  ];

  const handleSubmit = (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    const trimmed = (input || liveTranscript).trim();
    if (!trimmed || disabled) return;
    setInput('');
    onCommandSubmit(trimmed);
  };

  const handleChipClick = (chip) => {
    if (disabled) return;
    onCommandSubmit(chip.prompt, { isCodeAgent: chip.isCodeAgent });
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 py-2 select-none">
      {/* Live Voice Speech Transcript Preview Banner (When User Speaks) */}
      <AnimatePresence>
        {(isListening || liveTranscript) && (
          <motion.div
            initial={{ opacity: 0, y: 8, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: 8, height: 0 }}
            className="mb-2 px-3 py-2 rounded-xl bg-violet-950/40 border border-violet-500/40 backdrop-blur-md flex items-center justify-between text-xs font-mono"
          >
            <div className="flex items-center space-x-2 text-violet-300 min-w-0 flex-1">
              <Radio className="w-4 h-4 text-violet-400 animate-pulse shrink-0" />
              <span className="text-[11px] text-violet-400 font-semibold uppercase tracking-wider shrink-0">
                VOICE DETECTED:
              </span>
              <span className="text-slate-100 italic truncate font-sans text-xs">
                "{liveTranscript || 'Listening for directive... (Stops auto-submits)'}"
              </span>
            </div>
            <div className="text-[10px] text-violet-300/80 bg-violet-500/20 px-2 py-0.5 rounded border border-violet-500/30 shrink-0 ml-2">
              Auto-Execute on Pause
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Suggestion Chips */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 mb-1 scrollbar-none">
        <div className="text-[10px] font-mono text-cyan-500/70 uppercase tracking-widest shrink-0 flex items-center gap-1">
          <Terminal className="w-3 h-3" />
          <span>Directives:</span>
        </div>
        {suggestionChips.map((chip) => {
          const Icon = chip.icon;
          return (
            <motion.button
              key={chip.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => handleChipClick(chip)}
              disabled={disabled}
              className="shrink-0 text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-800 hover:border-cyan-500/40 transition-all flex items-center space-x-1.5 shadow-sm disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Icon className="w-3.5 h-3.5 text-cyan-400" />
              <span>{chip.label}</span>
            </motion.button>
          );
        })}
      </div>

      {/* Main Command Input Bar */}
      <form
        onSubmit={handleSubmit}
        className={`relative flex items-center rounded-2xl bg-[#070b14]/90 border transition-all duration-300 overflow-hidden shadow-2xl backdrop-blur-xl ${
          isListening
            ? 'border-violet-500/70 ring-2 ring-violet-500/30 shadow-violet-950/40'
            : 'border-cyan-500/30 hover:border-cyan-400/60 focus-within:border-cyan-400 focus-within:ring-2 focus-within:ring-cyan-500/20 shadow-cyan-950/30'
        }`}
      >
        {/* Terminal Prefix Indicator */}
        <div className="pl-4 pr-2 flex items-center space-x-1.5 text-cyan-400">
          <Terminal className="w-4 h-4" />
          <span className="text-xs font-mono font-bold text-cyan-500/80">KYRON&gt;</span>
        </div>

        {/* Input */}
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder={
            disabled
              ? 'Agent processing autonomous cycle...'
              : isListening
              ? 'Voice active: Speak directive or say "Hey Kyron"...'
              : 'Speak or type directive ("Hey Kyron", "Fix pricing bug", "Check health")...'
          }
          disabled={disabled}
          className="flex-1 bg-transparent py-3.5 px-2 text-sm text-slate-100 placeholder-slate-500 font-sans focus:outline-none disabled:opacity-50"
        />

        {/* Action Controls */}
        <div className="pr-3 flex items-center space-x-2">
          {/* Audio Speaker Mute Toggle */}
          {onToggleMute && (
            <button
              type="button"
              onClick={onToggleMute}
              className={`p-2 rounded-xl border transition-all ${
                isMuted
                  ? 'bg-slate-900 border-slate-800 text-slate-500 hover:text-slate-300'
                  : 'bg-violet-950/40 border-violet-500/30 text-violet-300 hover:text-violet-200'
              }`}
              title={isMuted ? 'Voice Vocalization Muted (Click to Unmute)' : 'Voice Vocalization Active (Click to Mute)'}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
          )}

          {/* Voice Microphone Toggle */}
          <button
            type="button"
            onClick={onToggleMic}
            className={`p-2 rounded-xl border transition-all ${
              isListening
                ? 'bg-rose-500/25 border-rose-500/60 text-rose-400 shadow-[0_0_12px_rgba(244,63,94,0.35)] animate-pulse'
                : 'bg-slate-900/80 border-slate-800 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30'
            }`}
            title={isListening ? 'Hands-Free Active: Click to Pause Mic' : 'Click to Activate Voice / Wake Word ("Hey Kyron")'}
          >
            {isListening ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
          </button>

          {/* Submit Button */}
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={(!input.trim() && !liveTranscript) || disabled}
            className="p-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/25 active:scale-95 transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
          >
            <ArrowUp className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>
      </form>

      {/* Safety Notice Subtext */}
      <div className="flex items-center justify-between px-2 pt-1.5 text-[10px] font-mono text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 rounded-full ${isListening ? 'bg-violet-400 animate-ping' : 'bg-cyan-400'}`}></span>
          <span>{isListening ? 'Wake Word Active ("Hey Kyron") // Hands-Free Audio' : 'Wake Word Standby'}</span>
        </span>
        <span className="text-amber-400/80 flex items-center gap-1">
          <ShieldAlert className="w-3 h-3" />
          Strict Dry-Run Gated (Production Protected)
        </span>
      </div>
    </div>
  );
}
