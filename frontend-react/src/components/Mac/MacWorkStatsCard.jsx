import React from 'react';
import {
  Activity,
  CheckCircle,
  Clock,
  Zap,
  TrendingUp,
  Cpu,
  Layers,
  ShieldCheck,
  Bot
} from 'lucide-react';

export default function MacWorkStatsCard({ stats }) {
  const data = stats || {
    total_tasks_completed: 156,
    actions_automated: 642,
    hours_saved: '21.8 hrs',
    system_uptime: '99.9%',
    average_voice_latency: '18ms',
    active_integrations: ['Chrome', 'WhatsApp Web', 'Instagram Direct', 'macOS Sequoia', 'Hermes Memory'],
    messages_processed_today: 34
  };

  return (
    <div className="p-3.5 rounded-2xl bg-gradient-to-br from-slate-900/80 via-slate-900/60 to-[#0d1424]/90 border border-white/10 shadow-xl backdrop-blur-xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
            <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white tracking-wide">
              KYRON Work Overview
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">
              Autonomous Execution Log
            </span>
          </div>
        </div>

        <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold border border-emerald-500/30">
          99.9% Uptime
        </span>
      </div>

      {/* Grid of 4 Key Stats */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        {/* Stat 1: Tasks Done */}
        <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/5 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <CheckCircle className="w-3 h-3 text-cyan-400" />
            <span>Tasks Done</span>
          </div>
          <span className="text-base font-extrabold text-white font-mono">
            {data.total_tasks_completed}+
          </span>
          <span className="text-[9px] text-cyan-300/80 mt-0.5">
            Today: {data.messages_processed_today} actions
          </span>
        </div>

        {/* Stat 2: Hours Saved */}
        <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/5 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <Clock className="w-3 h-3 text-emerald-400" />
            <span>Time Saved</span>
          </div>
          <span className="text-base font-extrabold text-emerald-300 font-mono">
            {data.hours_saved}
          </span>
          <span className="text-[9px] text-slate-400 mt-0.5">
            Productivity gain
          </span>
        </div>

        {/* Stat 3: Actions Automated */}
        <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/5 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <Zap className="w-3 h-3 text-amber-400" />
            <span>Automations</span>
          </div>
          <span className="text-base font-extrabold text-amber-300 font-mono">
            {data.actions_automated}
          </span>
          <span className="text-[9px] text-slate-400 mt-0.5">
            Clicks & Directives
          </span>
        </div>

        {/* Stat 4: Response Latency */}
        <div className="p-2.5 rounded-xl bg-white/[0.03] border border-white/5 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[10px] mb-1">
            <Cpu className="w-3 h-3 text-purple-400" />
            <span>Voice Latency</span>
          </div>
          <span className="text-base font-extrabold text-purple-300 font-mono">
            {data.average_voice_latency}
          </span>
          <span className="text-[9px] text-slate-400 mt-0.5">
            Dograh Native TTS
          </span>
        </div>
      </div>

      {/* Active Integrations Badges */}
      <div>
        <span className="text-[10px] font-semibold text-slate-400 block mb-1.5 uppercase tracking-wider">
          Connected Ecosystem
        </span>
        <div className="flex flex-wrap gap-1">
          {data.active_integrations.map((item, idx) => (
            <span
              key={idx}
              className="px-2 py-0.5 rounded-lg bg-slate-800/80 border border-slate-700 text-[10px] text-slate-300 font-medium"
            >
              {item}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
