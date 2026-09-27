import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Sparkles, Activity, ShieldCheck, AlertCircle, Volume2 } from 'lucide-react';

/**
 * JarvisCore Component
 * Central animated holographic orb representing KYRON's AGI consciousness and processing state.
 *
 * States:
 * - 'idle': Ambient, calm cyan breathing pulse
 * - 'speaking': Electric violet/magenta audio soundwave pulse (KYRON speaking aloud)
 * - 'thinking': High-speed counter-rotating rings with electric plasma burst
 * - 'executing': Emerald green / cyan speed surge
 * - 'review': Amber halo warning for safety-gate confirmation
 */
export default function JarvisCore({ status = 'idle', statusText = 'KYRON CORE ONLINE // AWAITING COMMAND' }) {
  const isSpeaking = status === 'speaking';
  const isThinking = status === 'thinking';
  const isExecuting = status === 'executing';
  const isReview = status === 'review';

  const primaryGlow = isSpeaking
    ? 'rgba(168, 85, 247, 0.65)'
    : isReview
    ? 'rgba(245, 158, 11, 0.4)'
    : isExecuting
    ? 'rgba(16, 185, 129, 0.45)'
    : isThinking
    ? 'rgba(0, 240, 255, 0.65)'
    : 'rgba(0, 220, 255, 0.25)';

  const ringColor = isSpeaking
    ? '#c084fc'
    : isReview
    ? '#f59e0b'
    : isExecuting
    ? '#10b981'
    : isThinking
    ? '#00f0ff'
    : '#0284c7';

  return (
    <div className="relative flex flex-col items-center justify-center py-3 select-none">
      {/* Ambient background glow aura */}
      <motion.div
        className="absolute w-44 h-44 rounded-full pointer-events-none blur-3xl"
        animate={{
          scale: isSpeaking ? [1, 1.35, 1] : isThinking ? [1, 1.25, 1] : isExecuting ? [1, 1.15, 1] : [1, 1.08, 1],
          opacity: isSpeaking ? [0.75, 1, 0.75] : isThinking ? [0.6, 0.9, 0.6] : [0.35, 0.5, 0.35],
        }}
        transition={{
          duration: isSpeaking ? 0.8 : isThinking ? 1.4 : 3.5,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        style={{ background: primaryGlow }}
      />

      {/* Holographic Concentric Rings Assembly */}
      <div className="relative w-28 h-28 flex items-center justify-center">
        {/* Outer Ring 1 */}
        <motion.div
          className="absolute inset-0 rounded-full border border-dashed"
          style={{ borderColor: ringColor, opacity: 0.6 }}
          animate={{ rotate: 360 }}
          transition={{
            duration: isSpeaking ? 2 : isThinking ? 4 : isExecuting ? 5 : 20,
            repeat: Infinity,
            ease: 'linear',
          }}
        />

        {/* Mid Ring 2 (Counter-Rotating) */}
        <motion.div
          className="absolute inset-2 rounded-full border border-cyan-400/40"
          style={{ borderTopColor: ringColor, borderBottomColor: 'transparent' }}
          animate={{ rotate: -360 }}
          transition={{
            duration: isSpeaking ? 1.8 : isThinking ? 3 : isExecuting ? 3.5 : 14,
            repeat: Infinity,
            ease: 'linear',
          }}
        />

        {/* Inner Ring 3 (Segmented) */}
        <motion.div
          className="absolute inset-4 rounded-full border-2"
          style={{
            borderColor: 'transparent',
            borderLeftColor: ringColor,
            borderRightColor: ringColor,
            boxShadow: `0 0 15px ${primaryGlow}`,
          }}
          animate={{
            rotate: 360,
            scale: isSpeaking ? [0.92, 1.1, 0.92] : isThinking ? [0.95, 1.05, 0.95] : [1, 1.02, 1],
          }}
          transition={{
            rotate: { duration: isSpeaking ? 1.2 : isThinking ? 2 : 10, repeat: Infinity, ease: 'linear' },
            scale: { duration: isSpeaking ? 0.6 : 1.5, repeat: Infinity, ease: 'easeInOut' },
          }}
        />

        {/* Center Nucleus Orb with Audio Soundwave Equalizer when Speaking */}
        <motion.div
          className="relative z-10 w-12 h-12 rounded-full flex items-center justify-center bg-slate-950/80 backdrop-blur-md border border-cyan-400/50"
          style={{ boxShadow: `0 0 20px ${primaryGlow}` }}
          animate={{
            scale: isSpeaking ? [1, 1.2, 1] : isThinking ? [1, 1.15, 1] : [1, 1.04, 1],
          }}
          transition={{
            duration: isSpeaking ? 0.5 : isThinking ? 0.8 : 2.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          {isSpeaking ? (
            <div className="flex items-center justify-center space-x-0.5 h-5 px-1">
              {[0.2, 0.6, 1.0, 0.7, 0.4].map((delay, i) => (
                <motion.div
                  key={i}
                  className="w-1 bg-violet-400 rounded-full"
                  animate={{ height: ['4px', '22px', '4px'] }}
                  transition={{
                    duration: 0.45,
                    repeat: Infinity,
                    delay: delay * 0.15,
                    ease: 'easeInOut',
                  }}
                />
              ))}
            </div>
          ) : isReview ? (
            <AlertCircle className="w-5 h-5 text-amber-400 animate-pulse" />
          ) : isExecuting ? (
            <ShieldCheck className="w-5 h-5 text-emerald-400 animate-pulse" />
          ) : isThinking ? (
            <Sparkles className="w-5 h-5 text-cyan-300 animate-spin" />
          ) : (
            <Cpu className="w-5 h-5 text-cyan-400" />
          )}
        </motion.div>
      </div>

      {/* Holographic Status Ticker */}
      <motion.div
        className="mt-3 flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-cyan-500/20 backdrop-blur-md"
        animate={{ opacity: [0.85, 1, 0.85] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <span
          className={`w-2 h-2 rounded-full ${
            isSpeaking
              ? 'bg-violet-400 shadow-[0_0_8px_#c084fc] animate-ping'
              : isReview
              ? 'bg-amber-400 shadow-[0_0_8px_#f59e0b]'
              : isExecuting
              ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]'
              : isThinking
              ? 'bg-cyan-400 shadow-[0_0_8px_#00f0ff] animate-ping'
              : 'bg-cyan-500 shadow-[0_0_6px_#0284c7]'
          }`}
        />
        <span className="font-mono text-[11px] tracking-wider uppercase text-cyan-200/90 font-medium flex items-center gap-1.5">
          {isSpeaking && <Volume2 className="w-3.5 h-3.5 text-violet-400 animate-pulse" />}
          <span>{statusText}</span>
        </span>
      </motion.div>
    </div>
  );
}
