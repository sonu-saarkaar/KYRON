import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Sparkles,
  Clock,
  ShieldCheck,
  Cpu,
  RefreshCw,
  Play,
  CheckCircle2,
  AlertTriangle,
  FolderGit2,
  Database,
  ExternalLink,
  ChevronRight,
  Zap,
  Info
} from 'lucide-react';
import api from '../../services/api';

export default function SystemDashboard({ onTriggerCron, onTelemetryLog }) {
  const [loading, setLoading] = useState(false);
  const [memories, setMemories] = useState([]);
  const [skills, setSkills] = useState([]);
  const [cronJobs, setCronJobs] = useState([]);
  const [codeAgentStatus, setCodeAgentStatus] = useState(null);
  const [triggeringJobId, setTriggeringJobId] = useState(null);
  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'memory' | 'skills' | 'cron'

  const fetchSystemTelemetry = async () => {
    setLoading(true);
    try {
      const [memRes, skillRes, cronRes, caRes] = await Promise.allSettled([
        api.get('/api/hermes/memory'),
        api.get('/api/hermes/skills'),
        api.get('/api/hermes/cron'),
        api.get('/api/kyron/code-agent/status')
      ]);

      if (memRes.status === 'fulfilled' && memRes.value?.data?.memories) {
        setMemories(memRes.value.data.memories);
      }
      if (skillRes.status === 'fulfilled' && skillRes.value?.data?.skills) {
        setSkills(skillRes.value.data.skills);
      }
      if (cronRes.status === 'fulfilled' && cronRes.value?.data?.jobs) {
        setCronJobs(cronRes.value.data.jobs);
      }
      if (caRes.status === 'fulfilled' && caRes.value?.data) {
        setCodeAgentStatus(caRes.value.data);
      }
    } catch (err) {
      console.warn('System telemetry fetch partial fallback:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemTelemetry();
    const interval = setInterval(fetchSystemTelemetry, 25000);
    return () => clearInterval(interval);
  }, []);

  const handleTriggerJob = async (jobId, jobName) => {
    setTriggeringJobId(jobId);
    if (onTelemetryLog) {
      onTelemetryLog({
        source: 'Cron',
        title: `Manual Trigger: ${jobName}`,
        detail: `Autonomous cycle launched for job ID: ${jobId}`,
        category: 'cron'
      });
    }

    try {
      const res = await api.post(`/api/hermes/cron/${jobId}/trigger`);
      if (res.data?.success) {
        if (onTelemetryLog) {
          onTelemetryLog({
            source: 'Cron',
            title: `Job Succeeded: ${jobName}`,
            detail: `Autonomous task executed successfully. Result status: OK`,
            category: 'cron'
          });
        }
        await fetchSystemTelemetry();
      }
    } catch (err) {
      console.error('Failed to trigger job:', err);
      if (onTelemetryLog) {
        onTelemetryLog({
          source: 'Cron',
          title: `Trigger Error: ${jobName}`,
          detail: err?.response?.data?.detail || err.message,
          category: 'cron'
        });
      }
    } finally {
      setTriggeringJobId(null);
    }
  };

  return (
    <aside className="w-80 lg:w-88 flex flex-col h-full bg-[#050811]/95 border-l border-cyan-500/20 backdrop-blur-xl relative overflow-hidden select-none">
      {/* Decorative cyber grid lines */}
      <div className="absolute inset-0 bg-[linear-gradient(to_bottom,rgba(0,240,255,0.02)_1px,transparent_1px)] bg-[size:100%_24px] pointer-events-none" />

      {/* Header */}
      <div className="p-4 border-b border-cyan-500/20 flex items-center justify-between bg-black/40">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h2 className="text-xs font-mono font-bold tracking-wider text-slate-100 uppercase">
            SYSTEM TELEMETRY
          </h2>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={fetchSystemTelemetry}
            disabled={loading}
            className="p-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-400 hover:text-cyan-400 transition-colors border border-slate-800"
            title="Refresh Telemetry"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Mini Tabs */}
      <div className="flex border-b border-cyan-500/10 bg-slate-950/60 p-1 gap-1 text-[11px] font-mono">
        <button
          onClick={() => setActiveTab('overview')}
          className={`flex-1 py-1 px-2 rounded text-center transition-all ${
            activeTab === 'overview'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab('memory')}
          className={`flex-1 py-1 px-2 rounded text-center transition-all ${
            activeTab === 'memory'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Memory ({memories.length})
        </button>
        <button
          onClick={() => setActiveTab('skills')}
          className={`flex-1 py-1 px-2 rounded text-center transition-all ${
            activeTab === 'skills'
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Skills ({skills.length})
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-3.5 custom-scrollbar">
        {activeTab === 'overview' && (
          <>
            {/* 1. Hermes Memory Card */}
            <div className="p-3 rounded-xl bg-slate-900/50 border border-cyan-500/20 backdrop-blur-sm space-y-2 hover:border-cyan-500/40 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-cyan-500/10 text-cyan-400">
                    <Brain className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-200">
                    Hermes Memory
                  </span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/25">
                  {memories.length} Cards
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                Fenced episodic & operational memory loaded for real-time prompt injection.
              </p>
              {memories.slice(0, 2).map((m, idx) => (
                <div
                  key={idx}
                  className="p-2 rounded bg-black/40 border border-slate-800 text-[10px] font-mono text-slate-300 truncate"
                >
                  • {m.content}
                </div>
              ))}
            </div>

            {/* 2. Skills Engine Card */}
            <div className="p-3 rounded-xl bg-slate-900/50 border border-violet-500/20 backdrop-blur-sm space-y-2 hover:border-violet-500/40 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-violet-500/10 text-violet-400">
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-200">
                    Skills Engine
                  </span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/25">
                  {skills.length} Loaded
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-snug">
                Autonomous self-learning engine enabled. Persisted as markdown specs.
              </p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {skills.map((s, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] font-mono px-2 py-0.5 rounded bg-violet-950/40 text-violet-300 border border-violet-800/40"
                  >
                    {s.name}
                  </span>
                ))}
              </div>
            </div>

            {/* 3. Cron Task Scheduler Card */}
            <div className="p-3 rounded-xl bg-slate-900/50 border border-emerald-500/20 backdrop-blur-sm space-y-2 hover:border-emerald-500/40 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-emerald-500/10 text-emerald-400">
                    <Clock className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-200">
                    Autonomous Cron
                  </span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/25">
                  Active (09:00 AM)
                </span>
              </div>
              {cronJobs.map((job) => (
                <div
                  key={job.id}
                  className="p-2.5 rounded-lg bg-black/50 border border-slate-800/80 space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-medium text-slate-100">
                      {job.name}
                    </span>
                    <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">
                      {job.schedule}
                    </span>
                  </div>
                  <div className="text-[10px] font-mono text-slate-400">
                    Next Run: <span className="text-slate-200">{job.next_run_iso ? new Date(job.next_run_iso).toLocaleTimeString() : '09:00 AM Daily'}</span>
                  </div>
                  <button
                    onClick={() => handleTriggerJob(job.id, job.name)}
                    disabled={triggeringJobId === job.id}
                    className="w-full py-1.5 px-2 rounded bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-[11px] font-mono font-medium flex items-center justify-center space-x-1.5 transition-all active:scale-95 disabled:opacity-50"
                  >
                    <Play className={`w-3 h-3 ${triggeringJobId === job.id ? 'animate-spin' : ''}`} />
                    <span>{triggeringJobId === job.id ? 'Executing Cycle...' : 'Run Autonomous Cycle Now'}</span>
                  </button>
                </div>
              ))}
            </div>

            {/* 4. CodeAgent Sandbox & Safety Lock */}
            <div className="p-3 rounded-xl bg-slate-900/50 border border-cyan-500/20 backdrop-blur-sm space-y-2 hover:border-cyan-500/40 transition-all">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-1 rounded bg-cyan-500/10 text-cyan-400">
                    <ShieldCheck className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-200">
                    CodeAgent Sandbox
                  </span>
                </div>
                <div className="flex items-center space-x-1 text-[10px] font-mono text-emerald-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>ONLINE</span>
                </div>
              </div>

              <div className="space-y-1.5 text-[11px] font-mono">
                <div className="flex justify-between text-slate-400">
                  <span>Runtime Isolation:</span>
                  <span className="text-slate-200 font-semibold">
                    {codeAgentStatus?.default_mode || 'Local Isolated Sandbox'}
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Safety Gate:</span>
                  <span className="text-amber-400 font-semibold">
                    Dry-Run Lock Active
                  </span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>LLM Core Provider:</span>
                  <span className="text-cyan-300 font-semibold">
                    {codeAgentStatus?.llm_provider || 'NVIDIA NIM (Free)'}
                  </span>
                </div>
              </div>

              <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-[10px] font-mono text-amber-300 flex items-start space-x-1.5 mt-2">
                <Info className="w-3.5 h-3.5 shrink-0 mt-0.5 text-amber-400" />
                <span>
                  All code tasks run dry-run with test verification. Physical button click required to write disk.
                </span>
              </div>
            </div>
          </>
        )}

        {activeTab === 'memory' && (
          <div className="space-y-2">
            <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider px-1">
              Active Memory Cards ({memories.length})
            </div>
            {memories.map((m) => (
              <div
                key={m.id}
                className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono space-y-1"
              >
                <div className="flex items-center justify-between text-[10px] text-cyan-400">
                  <span className="capitalize">{m.category}</span>
                  <span className="text-slate-500">ID: {m.id?.slice(0, 8)}</span>
                </div>
                <p className="text-slate-200 text-[11px] leading-relaxed">{m.content}</p>
                {m.tags && m.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {m.tags.map((t, i) => (
                      <span key={i} className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                        #{t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="space-y-2">
            <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider px-1">
              Learned & Persisted Skills ({skills.length})
            </div>
            {skills.map((s, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-xs font-mono space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-violet-300">{s.name}</span>
                  <span className="text-[10px] text-slate-500">{s.tags?.[0] || 'skill'}</span>
                </div>
                <p className="text-slate-300 text-[11px] leading-relaxed">{s.description}</p>
                {s.trigger_phrases && (
                  <div className="text-[10px] text-slate-400 pt-1">
                    <span className="text-slate-500">Triggers: </span>
                    {s.trigger_phrases.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer System Status */}
      <div className="p-3 border-t border-cyan-500/20 bg-black/60 flex items-center justify-between text-[11px] font-mono text-slate-400">
        <div className="flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="text-slate-200">KYRON AGI DAEMON</span>
        </div>
        <span className="text-cyan-400">PORT 8000</span>
      </div>
    </aside>
  );
}
