import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Globe,
  RefreshCw,
  ExternalLink,
  MessageCircle,
  Instagram,
  Terminal,
  Shield,
  CheckCircle2,
  Clock,
  Sparkles,
  Play,
  Send,
  Zap,
  Layers,
  ChevronRight,
  UserCheck,
  Eye,
  Maximize2
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function MacScreenMirror({
  mirrorState,
  onSwitchMode,
  onPeekWhatsApp,
  onSmartReplyWhatsApp,
  onAutoReplyInstagram,
  isProcessing
}) {
  const [activeTab, setActiveTab] = useState(mirrorState?.mirror_mode || 'whatsapp');
  const [customReplyContact, setCustomReplyContact] = useState('');
  const [customReplyText, setCustomReplyText] = useState('');
  const [showReplyModal, setShowReplyModal] = useState(false);

  const defaultSteps = [
    { id: 'step_1', tool: 'chrome', time: 'Just now', text: 'Chrome Viewport initialized via Playwright automation engine' },
    { id: 'step_2', tool: 'memory', time: '1m ago', text: "Sonu's identity & business profile loaded from KYRON_MIND.md" },
    { id: 'step_3', tool: 'dograh', time: '2m ago', text: 'Wispr ultra-low latency audio listening pipeline active (sub-25ms)' },
    { id: 'step_4', tool: 'whatsapp', time: '3m ago', text: 'WhatsApp Peek service synchronized with macOS SQLite database' }
  ];

  const defaultChats = [
    { id: 'chat_1', sender: 'Rohit Kumar (Fleet Lead)', time: '10:42 AM', preview: 'Bhai kal ke Patna to Darbhanga fleet bookings ready hain, status update de do.', suggested_reply: 'Haan Rohit, sab verified hai. 7 AM cab locked.', status: 'unread' },
    { id: 'chat_2', sender: 'Dev Anand (Senior AI Engg)', time: '09:15 AM', preview: 'Sonu, sub-25ms speech pipeline benchmarks check kar lo PR #42 pe.', suggested_reply: 'PR dekh liya, latency solid hai. Merge kar do.', status: 'unread' },
    { id: 'chat_3', sender: 'Priya Sharma (Client Support)', time: 'Yesterday', preview: 'BookMyGaadi airport pickup booking confirmation link bhej dijiye.', suggested_reply: 'Confirmation dispatched to client WhatsApp.', status: 'replied', last_reply: 'Confirmation link sent.' }
  ];

  const defaultInstagramDms = [
    { id: 'ig_1', username: 'tech_founder_india', time: '12m ago', message: 'Hey Sonu, love the KYRON macOS AGI! Is it available for private beta testing?', reply_text: 'Haan bhai! Private beta access link DM me send kar raha hoon.', replied: true },
    { id: 'ig_2', username: 'ai_innovators_hub', time: '1h ago', message: 'Can BookMyGaadi API be integrated with corporate travel desks?', reply_text: 'Bilkul! API docs and corporate dashboard live hain.', replied: false }
  ];

  const steps = mirrorState?.steps_log && mirrorState.steps_log.length > 0 ? mirrorState.steps_log : defaultSteps;
  const ongoing = mirrorState?.ongoing_task || {
    title: 'Chrome / Screen Automation Standby',
    app: 'Chrome / macOS',
    step: 'Standing by for voice or chat directives',
    progress: 100,
    status: 'completed'
  };
  const whatsappChats = mirrorState?.whatsapp_chats && mirrorState.whatsapp_chats.length > 0 ? mirrorState.whatsapp_chats : defaultChats;
  const instagramDms = mirrorState?.instagram_dms && mirrorState.instagram_dms.length > 0 ? mirrorState.instagram_dms : defaultInstagramDms;

  const handleTabChange = (mode) => {
    setActiveTab(mode);
    if (onSwitchMode) onSwitchMode(mode);
  };

  return (
    <div className="flex flex-col h-full bg-[#0d121f]/90 backdrop-blur-2xl border-l border-white/10 select-none">
      {/* 1. TOP HEADER: ACTIVE TASK INDICATOR */}
      <div className="p-3 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
            </span>
            <span className="text-xs font-bold text-white tracking-wide uppercase font-mono">
              Live Screen Mirror
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-900/80 px-2 py-0.5 rounded-full border border-white/10 text-[10px] text-cyan-300 font-mono">
            <Globe className="w-3 h-3 text-cyan-400" />
            <span>Chrome Viewport</span>
          </div>
        </div>

        {/* Current task what Kyron is executing right now */}
        <div className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-950/40 via-indigo-950/30 to-purple-950/30 border border-cyan-500/30">
          <div className="flex items-center justify-between text-[11px] mb-1">
            <span className="text-slate-400 font-medium">Current Goal:</span>
            <span className="text-emerald-400 font-mono font-semibold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              {ongoing.status === 'completed' ? 'Executed' : 'In Progress'}
            </span>
          </div>
          <p className="text-xs font-semibold text-slate-100 truncate">
            {ongoing.title}
          </p>
          <p className="text-[10px] text-cyan-300/80 truncate mt-0.5">
            {ongoing.step}
          </p>
        </div>
      </div>

      {/* 2. CHROME BROWSER FRAME / LIVE MIRROR VIEWPORT */}
      <div className="p-3">
        <div className="rounded-2xl border border-white/15 bg-[#101726] shadow-2xl overflow-hidden flex flex-col">
          {/* Chrome Titlebar & Tabs */}
          <div className="h-9 bg-[#1a2338] border-b border-white/10 flex items-center justify-between px-3">
            {/* macOS Window Traffic Lights */}
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#ff5f56] inline-block shadow-sm"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-[#ffbd2e] inline-block shadow-sm"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-[#27c93f] inline-block shadow-sm"></span>
            </div>

            {/* Browser Tabs Switcher */}
            <div className="flex items-center gap-1 text-[11px]">
              <button
                onClick={() => handleTabChange('whatsapp')}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-t-lg transition ${
                  activeTab === 'whatsapp'
                    ? 'bg-[#101726] text-emerald-300 font-semibold border-t border-x border-white/10'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <MessageCircle className="w-3 h-3 text-emerald-400" />
                <span>WhatsApp Web</span>
              </button>

              <button
                onClick={() => handleTabChange('instagram')}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-t-lg transition ${
                  activeTab === 'instagram'
                    ? 'bg-[#101726] text-pink-300 font-semibold border-t border-x border-white/10'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <Instagram className="w-3 h-3 text-pink-400" />
                <span>Instagram DMs</span>
              </button>
            </div>

            <div className="text-[10px] text-slate-500 font-mono">1280x800</div>
          </div>

          {/* Chrome Address Bar */}
          <div className="h-8 bg-[#141b2d] border-b border-white/5 flex items-center gap-2 px-3 text-xs">
            <div className="flex items-center gap-1 text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <Shield className="w-3 h-3 text-emerald-400" />
            </div>
            <div className="flex-1 bg-black/40 px-2 py-0.5 rounded text-[11px] font-mono text-slate-300 truncate border border-white/5 flex items-center justify-between">
              <span>
                {activeTab === 'whatsapp'
                  ? 'https://web.whatsapp.com'
                  : 'https://www.instagram.com/direct/inbox/'}
              </span>
              <span className="text-[9px] text-emerald-400 bg-emerald-950/60 px-1 rounded">
                SECURE
              </span>
            </div>
            <button
              onClick={() => {
                toast.success('Mirror viewport reloaded');
                if (activeTab === 'whatsapp') onPeekWhatsApp?.();
                else onAutoReplyInstagram?.();
              }}
              className="p-1 rounded text-slate-400 hover:text-white hover:bg-white/5 transition"
              title="Refresh Viewport"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>

          {/* VIEWPORT CANVAS (LIVE SIMULATION) */}
          <div className="h-56 overflow-y-auto bg-[#0a0f18] p-2.5 relative custom-scrollbar">
            {/* Animated Virtual Automation Cursor */}
            <motion.div
              animate={{
                x: [20, 140, 80, 200, 40],
                y: [30, 80, 130, 60, 40]
              }}
              transition={{
                duration: 9,
                repeat: Infinity,
                ease: 'easeInOut'
              }}
              className="absolute z-30 pointer-events-none drop-shadow-md"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path
                  d="M3 3l7 18 3-7 7-3L3 3z"
                  fill="#06b6d4"
                  stroke="#ffffff"
                  strokeWidth="1.5"
                />
              </svg>
              <span className="ml-3 -mt-2 px-1.5 py-0.2 rounded bg-cyan-500 text-[8px] font-mono font-bold text-slate-950 block shadow">
                KYRON
              </span>
            </motion.div>

            {/* TAB CONTENT: WHATSAPP WEB */}
            {activeTab === 'whatsapp' ? (
              <div className="space-y-2 text-xs">
                {/* WhatsApp Peek Banner */}
                <div className="p-2 rounded-xl bg-emerald-950/40 border border-emerald-500/30 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Eye className="w-4 h-4 text-emerald-400" />
                    <div>
                      <span className="text-[11px] font-bold text-emerald-300 block">
                        WhatsApp Peek Mode Active
                      </span>
                      <span className="text-[9px] text-slate-400">
                        Reading previews without opening chat windows
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                    {whatsappChats.length} UNREAD
                  </span>
                </div>

                {/* WhatsApp Chats List */}
                <div className="space-y-1.5">
                  {whatsappChats.map((chat) => (
                    <div
                      key={chat.id}
                      className={`p-2 rounded-xl border transition ${
                        chat.status === 'replied'
                          ? 'bg-slate-900/60 border-slate-800 opacity-70'
                          : 'bg-[#152033] border-cyan-500/40 shadow-sm'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5">
                          <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center text-[10px] font-bold text-slate-950">
                            {chat.sender[0]}
                          </div>
                          <span className="font-semibold text-slate-200 text-xs">
                            {chat.sender}
                          </span>
                        </div>
                        <span className="text-[9px] text-slate-400">{chat.time}</span>
                      </div>

                      <p className="text-[11px] text-slate-300 leading-snug line-clamp-2 bg-black/30 p-1.5 rounded-lg border border-white/5">
                        "{chat.preview}"
                      </p>

                      {chat.status === 'replied' ? (
                        <div className="mt-1 flex items-center gap-1 text-[9px] text-emerald-400 font-mono">
                          <CheckCircle2 className="w-2.5 h-2.5" />
                          <span>Replied: "{chat.last_reply}"</span>
                        </div>
                      ) : (
                        <div className="mt-1.5 flex items-center justify-between gap-2">
                          <span className="text-[9px] text-cyan-400 font-mono truncate">
                            Auto: "{chat.suggested_reply}"
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              /* TAB CONTENT: INSTAGRAM DIRECT */
              <div className="space-y-2 text-xs">
                <div className="p-2 rounded-xl bg-pink-950/40 border border-pink-500/30 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Instagram className="w-4 h-4 text-pink-400" />
                    <div>
                      <span className="text-[11px] font-bold text-pink-300 block">
                        Instagram Direct Automation
                      </span>
                      <span className="text-[9px] text-slate-400">
                        Autonomous responses & live vocal broadcast
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-pink-500/20 text-pink-300 border border-pink-500/40">
                    3 DMs
                  </span>
                </div>

                <div className="space-y-1.5">
                  {instagramDms.map((dm) => (
                    <div
                      key={dm.id}
                      className="p-2 rounded-xl bg-[#171a2c] border border-pink-500/30"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-1.5">
                          <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-pink-500 to-purple-600 flex items-center justify-center text-[10px] font-bold text-white">
                            @
                          </div>
                          <span className="font-semibold text-slate-200 text-xs">
                            @{dm.username}
                          </span>
                        </div>
                        <span className="text-[9px] text-slate-400">{dm.time}</span>
                      </div>

                      <p className="text-[11px] text-slate-300 p-1.5 rounded-lg bg-black/30 border border-white/5">
                        "{dm.message}"
                      </p>

                      <div className="mt-1.5 p-1 rounded-lg bg-pink-950/50 border border-pink-500/20 flex items-center justify-between text-[9px]">
                        <span className="text-pink-300 font-mono">
                          Reply: "{dm.reply_text}"
                        </span>
                        <span className="text-emerald-400 font-bold">
                          {dm.replied ? '✓ Dispatched' : 'Pending'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 3. QUICK ACTION BAR FOR THE MIRROR */}
      <div className="px-3 pb-2 flex items-center gap-1.5">
        <button
          onClick={onPeekWhatsApp}
          disabled={isProcessing}
          className="flex-1 py-1.5 px-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 text-[11px] font-semibold flex items-center justify-center gap-1 transition"
          title="Inspect WhatsApp unread messages"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Peek WhatsApp</span>
        </button>

        <button
          onClick={() => onSmartReplyWhatsApp?.()}
          disabled={isProcessing}
          className="flex-1 py-1.5 px-2 rounded-xl bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 text-[11px] font-semibold flex items-center justify-center gap-1 transition"
          title="Auto-reply using Sonu's memory & style"
        >
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Memory Reply</span>
        </button>

        <button
          onClick={onAutoReplyInstagram}
          disabled={isProcessing}
          className="flex-1 py-1.5 px-2 rounded-xl bg-pink-500/20 hover:bg-pink-500/30 border border-pink-500/40 text-pink-300 text-[11px] font-semibold flex items-center justify-center gap-1 transition"
          title="Auto-reply to Instagram DMs with voice broadcast"
        >
          <Instagram className="w-3.5 h-3.5 text-pink-400" />
          <span>Auto Insta</span>
        </button>
      </div>

      {/* 4. NICHE: LIVE STEP-BY-STEP EXECUTION STREAM */}
      <div className="flex-1 min-h-[160px] p-3 border-t border-white/10 bg-black/20 flex flex-col overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
            <Terminal className="w-3.5 h-3.5 text-cyan-400" />
            <span>Execution Steps (Niche Stream)</span>
          </div>
          <span className="text-[10px] font-mono text-slate-500">
            {steps.length} actions
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 custom-scrollbar">
          {steps.map((step) => {
            const isChrome = step.tool === 'chrome';
            const isMemory = step.tool === 'memory';
            const isDograh = step.tool === 'dograh';

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: 6 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-2 rounded-xl bg-white/[0.03] border border-white/5 hover:border-cyan-500/30 transition text-xs flex items-start gap-2"
              >
                <div className="mt-0.5 shrink-0">
                  {isChrome ? (
                    <Globe className="w-3.5 h-3.5 text-cyan-400" />
                  ) : isMemory ? (
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                  ) : isDograh ? (
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                  ) : (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono mb-0.5">
                    <span className="uppercase text-slate-400 font-semibold">
                      {step.tool || 'Action'}
                    </span>
                    <span>{step.time}</span>
                  </div>
                  <p className="text-[11px] text-slate-200 leading-snug break-words">
                    {step.text}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
