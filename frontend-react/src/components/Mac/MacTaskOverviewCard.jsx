import React from 'react';
import {
  CheckCircle2,
  Activity,
  Clock,
  Zap,
  TrendingUp,
  MessageCircle,
  Globe,
  Code2,
  Cpu,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function MacTaskOverviewCard({ stats, taskHistory, onSelectTask }) {
  const data = stats || {
    total_tasks_completed: 158,
    actions_automated: 646,
    hours_saved: '21.8 hrs',
    system_uptime: '99.9%',
    messages_processed_today: 34
  };

  // Extract flat list of top 4 most recent completed tasks
  const recentTasks = [];
  if (taskHistory && Array.isArray(taskHistory)) {
    for (const session of taskHistory) {
      if (session.tasks && Array.isArray(session.tasks)) {
        for (const t of session.tasks) {
          recentTasks.push(t);
          if (recentTasks.length >= 4) break;
        }
      }
      if (recentTasks.length >= 4) break;
    }
  }

  // Fallback if no task history
  const displayTasks = recentTasks.length > 0 ? recentTasks : [
    {
      id: 'rt_1',
      title: 'WhatsApp Multi-Response',
      detail: "Sonu ko 'Hi' aur Rohit ko 'Hello' dispatched",
      app: 'WhatsApp',
      time: 'Just now',
      category: 'Social & Voice'
    },
    {
      id: 'rt_2',
      title: 'Aadhaar / Photo Form Resizer',
      detail: 'Auto-cropped to 200x230px, 34.2 KB (sips engine)',
      app: 'Vault Agent',
      time: '01:34 AM',
      category: 'Document Vault'
    },
    {
      id: 'rt_3',
      title: 'Pricing Calculation Bug Audit',
      detail: 'Analyzed pricing.py & dry-run sandbox diff ready',
      app: 'CodeAgent',
      time: 'Yesterday',
      category: 'Development'
    }
  ];

  const getAppIcon = (app) => {
    const a = (app || '').toLowerCase();
    if (a.includes('whatsapp')) return <MessageCircle className="w-3.5 h-3.5 text-emerald-400" />;
    if (a.includes('chrome') || a.includes('browser')) return <Globe className="w-3.5 h-3.5 text-cyan-400" />;
    if (a.includes('code') || a.includes('dev')) return <Code2 className="w-3.5 h-3.5 text-indigo-400" />;
    if (a.includes('vault') || a.includes('doc')) return <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />;
    return <Zap className="w-3.5 h-3.5 text-cyan-400" />;
  };

  return (
    <div className="p-3.5 rounded-2xl bg-gradient-to-br from-[#0c1424]/90 via-[#0e172a]/80 to-[#121c30]/90 border border-white/10 shadow-xl backdrop-blur-xl select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 mb-2.5 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
            <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white tracking-wide">
              Tasks Overview & Recent Work
            </h4>
            <span className="text-[10px] text-slate-400 font-mono">
              Autonomous Execution Log
            </span>
          </div>
        </div>

        <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold border border-emerald-500/30">
          {data.total_tasks_completed}+ Done
        </span>
      </div>

      {/* Overview Stat Strip */}
      <div className="grid grid-cols-3 gap-1.5 mb-3 text-center">
        <div className="p-2 rounded-xl bg-black/30 border border-white/5">
          <span className="text-[9px] text-slate-400 block font-mono uppercase">Tasks</span>
          <span className="text-xs font-bold text-white font-mono">{data.total_tasks_completed}</span>
        </div>
        <div className="p-2 rounded-xl bg-black/30 border border-white/5">
          <span className="text-[9px] text-slate-400 block font-mono uppercase">Automated</span>
          <span className="text-xs font-bold text-cyan-300 font-mono">{data.actions_automated}</span>
        </div>
        <div className="p-2 rounded-xl bg-black/30 border border-white/5">
          <span className="text-[9px] text-slate-400 block font-mono uppercase">Saved</span>
          <span className="text-xs font-bold text-emerald-300 font-mono">{data.hours_saved}</span>
        </div>
      </div>

      {/* Recent Tasks List */}
      <div className="space-y-1.5">
        <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block font-mono mb-1">
          Recent Completed Tasks ("Kya Complete Kia")
        </span>

        <div className="space-y-1.5 max-h-44 overflow-y-auto custom-scrollbar pr-1">
          {displayTasks.map((task) => (
            <div
              key={task.id}
              onClick={() => onSelectTask && onSelectTask(task)}
              className="p-2 rounded-xl bg-black/30 border border-white/5 hover:border-cyan-500/30 transition cursor-pointer flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-2 truncate mr-2">
                <div className="w-6 h-6 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                  {getAppIcon(task.app)}
                </div>
                <div className="truncate">
                  <span className="font-semibold text-white block text-[11px] truncate">
                    {task.title}
                  </span>
                  <span className="text-[9px] text-slate-400 truncate block">
                    {task.detail}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1.5 shrink-0 font-mono text-[9px]">
                <span className="text-slate-500">{task.time}</span>
                <span className="text-emerald-400 font-bold flex items-center gap-0.5">
                  <CheckCircle2 className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
