import React, { useState } from 'react';
import {
  History,
  CheckCircle2,
  Clock,
  Calendar,
  ChevronDown,
  ChevronRight,
  Filter,
  Search,
  ExternalLink,
  MessageCircle,
  Instagram,
  Terminal,
  Cpu
} from 'lucide-react';

export default function MacTaskHistoryCard({ taskHistory, onSelectTask }) {
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedSessions, setExpandedSessions] = useState({
    sess_today_01: true,
    sess_yesterday_02: false
  });

  const toggleSession = (sessId) => {
    setExpandedSessions((prev) => ({
      ...prev,
      [sessId]: !prev[sessId]
    }));
  };

  const sessions = taskHistory || [];

  return (
    <div className="flex flex-col h-full rounded-2xl bg-[#0c121e]/80 border border-white/10 backdrop-blur-xl overflow-hidden shadow-xl">
      {/* Header */}
      <div className="p-3 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
              <History className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white tracking-wide">
                Task History (Session-Wise)
              </h4>
              <span className="text-[10px] text-slate-400 font-mono">
                Executed Workflows
              </span>
            </div>
          </div>

          <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded-full border border-cyan-500/30">
            {sessions.reduce((acc, s) => acc + (s.tasks?.length || 0), 0)} logged
          </span>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-1 overflow-x-auto custom-scrollbar pt-1">
          {['all', 'Social & Voice', 'Browser', 'Development', 'System Control'].map((cat) => (
            <button
              key={cat}
              onClick={() => setFilterCategory(cat)}
              className={`px-2 py-0.5 rounded-lg text-[10px] font-medium whitespace-nowrap transition ${
                filterCategory === cat
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'text-slate-400 hover:text-white bg-slate-800/40'
              }`}
            >
              {cat === 'all' ? 'All Tasks' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Sessions Accordion List */}
      <div className="flex-1 overflow-y-auto p-2.5 space-y-2.5 custom-scrollbar">
        {sessions.map((sess) => {
          const isExpanded = !!expandedSessions[sess.session_id];
          const filteredTasks = (sess.tasks || []).filter((t) => {
            const matchesCat = filterCategory === 'all' || t.category === filterCategory;
            const matchesQuery = !searchQuery || t.title.toLowerCase().includes(searchQuery.toLowerCase()) || t.detail.toLowerCase().includes(searchQuery.toLowerCase());
            return matchesCat && matchesQuery;
          });

          if (filteredTasks.length === 0 && filterCategory !== 'all') return null;

          return (
            <div
              key={sess.session_id}
              className="rounded-xl border border-white/5 bg-slate-900/40 overflow-hidden"
            >
              {/* Session Header */}
              <div
                onClick={() => toggleSession(sess.session_id)}
                className="p-2.5 flex items-center justify-between cursor-pointer hover:bg-white/[0.03] transition"
              >
                <div className="flex items-center gap-2">
                  {isExpanded ? (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                  )}
                  <div>
                    <h5 className="text-[11px] font-bold text-slate-200">
                      {sess.session_title}
                    </h5>
                    <span className="text-[9px] text-slate-400 font-mono">
                      {sess.date}
                    </span>
                  </div>
                </div>

                <span className="text-[10px] text-slate-400 font-mono">
                  {filteredTasks.length} tasks
                </span>
              </div>

              {/* Tasks in this Session */}
              {isExpanded && (
                <div className="p-2 pt-0 space-y-1.5 border-t border-white/5">
                  {filteredTasks.map((task) => {
                    const isWhatsApp = task.app?.toLowerCase().includes('whatsapp');
                    const isInsta = task.app?.toLowerCase().includes('instagram');
                    const isCode = task.app?.toLowerCase().includes('code');

                    return (
                      <div
                        key={task.id}
                        onClick={() => onSelectTask?.(task)}
                        className="p-2 rounded-lg bg-black/30 border border-white/5 hover:border-cyan-500/30 transition cursor-pointer group"
                      >
                        <div className="flex items-center justify-between mb-0.5">
                          <div className="flex items-center gap-1.5">
                            {isWhatsApp ? (
                              <MessageCircle className="w-3 h-3 text-emerald-400" />
                            ) : isInsta ? (
                              <Instagram className="w-3 h-3 text-pink-400" />
                            ) : isCode ? (
                              <Terminal className="w-3 h-3 text-indigo-400" />
                            ) : (
                              <CheckCircle2 className="w-3 h-3 text-cyan-400" />
                            )}
                            <span className="text-[11px] font-semibold text-slate-200 group-hover:text-cyan-300">
                              {task.title}
                            </span>
                          </div>

                          <span className="text-[9px] text-slate-500 font-mono">
                            {task.time}
                          </span>
                        </div>

                        <p className="text-[10px] text-slate-400 line-clamp-1 pl-4.5">
                          {task.detail}
                        </p>

                        <div className="flex items-center justify-between mt-1 pl-4.5 text-[9px] text-slate-500 font-mono">
                          <span className="text-cyan-400/80 bg-cyan-950/40 px-1 rounded">
                            {task.app}
                          </span>
                          <span className="text-emerald-400 font-bold">
                            ✓ {task.status}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
