import React from 'react';
import { motion } from 'framer-motion';
import {
  Zap,
  Play,
  Pause,
  RotateCw,
  CheckCircle2,
  AlertCircle,
  Eye,
  Sparkles,
  Instagram,
  Music,
  ExternalLink,
  MessageCircle,
  Search
} from 'lucide-react';

export default function MacOngoingTaskCard({
  ongoingTask,
  onOpenWhatsApp,
  onSearchAndSendSonu,
  onPeekWhatsApp,
  onSmartReplyWhatsApp,
  onAutoReplyInstagram,
  onPlaySong,
  isProcessing
}) {
  const task = ongoingTask || {
    id: 'onj_ready',
    title: 'Awaiting Directive',
    app: 'macOS Sequoia',
    target: 'System Ready',
    progress: 100,
    status: 'idle',
    step: 'Listening via Wispr Engine (Tara / Lekha voice active)',
    updated_at: 'Just now'
  };

  const isActive = task.status === 'active' || isProcessing;

  return (
    <div className="relative rounded-2xl bg-gradient-to-r from-[#0d1728]/95 via-[#111c33]/90 to-[#14142b]/95 border border-cyan-500/30 p-3.5 shadow-2xl backdrop-blur-2xl overflow-hidden">
      {/* Background Glow */}
      <div className="absolute -top-12 -right-12 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none"></div>

      <div className="relative z-10">
        {/* Top Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full ${
                  isActive ? 'bg-emerald-400' : 'bg-cyan-400'
                } opacity-75`}
              ></span>
              <span
                className={`relative inline-flex rounded-full h-3 w-3 ${
                  isActive ? 'bg-emerald-500' : 'bg-cyan-500'
                }`}
              ></span>
            </span>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-black tracking-wider uppercase text-white font-mono">
                ONJ: {isActive ? 'Ongoing Active Operation' : 'Autonomous Engine Armed'}
              </span>
              <span className="text-[10px] text-cyan-300 font-mono bg-cyan-950/70 px-1.5 py-0.5 rounded border border-cyan-500/30">
                {task.app}
              </span>
            </div>
          </div>

          <span className="text-[10px] font-mono text-slate-400">
            {task.updated_at}
          </span>
        </div>

        {/* Task Title & Sub-Step */}
        <div className="mb-2.5">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <span>{task.title}</span>
            {isActive && (
              <RotateCw className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
            )}
          </h3>
          <p className="text-xs text-cyan-300/80 mt-0.5 font-medium">
            {task.step}
          </p>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-800/80 rounded-full h-1.5 mb-3 overflow-hidden border border-white/5">
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: `${task.progress || 100}%` }}
            transition={{ duration: 0.5 }}
            className={`h-full rounded-full ${
              isActive
                ? 'bg-gradient-to-r from-cyan-400 via-teal-300 to-emerald-400 animate-pulse'
                : 'bg-gradient-to-r from-cyan-500 to-indigo-500'
            }`}
          />
        </div>

        {/* Action Directives Quick Toolbar */}
        <div className="flex items-center gap-2 overflow-x-auto pt-1 custom-scrollbar">
          <button
            onClick={onOpenWhatsApp}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-xs font-semibold transition shrink-0 shadow-sm"
            title="Launch WhatsApp application"
          >
            <MessageCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span>1. Open WhatsApp</span>
          </button>

          <button
            onClick={onSearchAndSendSonu}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-xs font-semibold transition shrink-0 shadow-sm"
            title="Search Sonu and send Hi Sonu"
          >
            <Search className="w-3.5 h-3.5 text-cyan-400" />
            <span>2. Search Sonu & Send "Hi Sonu"</span>
          </button>

          <button
            onClick={onPeekWhatsApp}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 text-xs font-semibold transition shrink-0 shadow-sm"
          >
            <Eye className="w-3.5 h-3.5 text-emerald-400" />
            <span>Peek WhatsApp</span>
          </button>

          <button
            onClick={onSmartReplyWhatsApp}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 text-cyan-300 text-xs font-semibold transition shrink-0 shadow-sm"
          >
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Smart Reply (Memory)</span>
          </button>

          <button
            onClick={onAutoReplyInstagram}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-pink-500/15 hover:bg-pink-500/25 border border-pink-500/30 text-pink-300 text-xs font-semibold transition shrink-0 shadow-sm"
          >
            <Instagram className="w-3.5 h-3.5 text-pink-400" />
            <span>Auto-Reply Instagram</span>
          </button>

          <button
            onClick={onPlaySong}
            disabled={isProcessing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-500/15 hover:bg-purple-500/25 border border-purple-500/30 text-purple-300 text-xs font-semibold transition shrink-0 shadow-sm"
          >
            <Music className="w-3.5 h-3.5 text-purple-400" />
            <span>Play Song</span>
          </button>
        </div>
      </div>
    </div>
  );
}
