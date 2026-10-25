import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  Sparkles,
  ShieldCheck,
  User,
  Users,
  Compass,
  CheckCircle2,
  ChevronRight,
  ChevronDown,
  Layers,
  Zap,
  Cpu
} from 'lucide-react';

export default function MacBossProfileCard({ bossProfile, onOpenPersonalize }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState('framework'); // 'framework' | 'relationships' | 'studies'

  const profile = bossProfile || {
    name: 'Asif Aslam (Sonu Sarkar)',
    full_name: 'Asif Aslam',
    alias: 'Sonu Sarkar',
    title: 'Founder & Chief AI Systems Architect',
    ecosystem: 'KYRON AGI • BookMyGaadi',
    thinking_philosophy: {
      style: 'High-Agency & First Principles',
      rules: [
        'Speed over bureaucracy: execute immediately, verify in sandbox',
        'Direct & polite communication: zero fluff, clear timelines',
        'Continuous automation: if done twice, automate with Kyron'
      ]
    },
    education_and_studies: [
      'Agentic AI/ML & LLM Reasoning Research',
      'Distributed Systems & Microservices',
      'Apple Silicon internals & macOS CoreAudio'
    ],
    hobbies: [
      'Late-night autonomous agent coding marathons',
      'High-tempo Lofi and EDM music while programming',
      'Frosted-glass Apple-grade UI design'
    ],
    relationship_rules: [
      {
        group: 'Developers & Engineers',
        examples: 'Rahul, Dev Anand',
        handling: 'Direct, collaborative, motivating, technical reviews ("PR solid hai, merge karo")'
      },
      {
        group: 'Team Leads & Operations',
        examples: 'Rohit',
        handling: 'Punctual, clear directives, supportive, crisp time commitments ("Meeting 11 baje final hai")'
      },
      {
        group: 'Close Circle & Friends',
        examples: 'Sonu',
        handling: 'Warm, authentic Hinglish, high energy, fast response ("Hi Sonu", "Haan bhai sab ready hai")'
      },
      {
        group: 'Designers & Creatives',
        examples: 'Priya Sharma, Neha',
        handling: 'Appreciative of aesthetics, constructive design critique, dark glass polish'
      }
    ],
    total_memories_recalled: 64,
    status: 'Active & Synchronized • Profile-First Verified'
  };

  return (
    <div className="rounded-2xl bg-gradient-to-br from-[#0c1424]/95 via-[#0e172e]/90 to-[#12132a]/95 border border-cyan-500/30 shadow-2xl backdrop-blur-2xl overflow-hidden select-none">
      {/* Header Banner */}
      <div className="p-3.5 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center text-white font-black text-sm shadow-md shadow-cyan-900/40">
                S
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#0c1424] animate-pulse"></span>
            </div>

            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="text-xs font-bold text-white tracking-wide">
                  {profile.name}
                </h3>
                <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/30 font-bold">
                  BOSS
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono">
                {profile.title}
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition flex items-center gap-1 text-[10px] font-mono"
            title="Toggle details"
          >
            <span>{isExpanded ? 'Less' : 'Details'}</span>
            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          </button>
        </div>

        {/* Cognitive Status Pill */}
        <div className="flex items-center justify-between p-2 rounded-xl bg-cyan-950/40 border border-cyan-500/20 text-[10px]">
          <div className="flex items-center gap-1.5 text-cyan-300 font-medium">
            <Brain className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span>Persona Memory: Synchronized</span>
          </div>
          <span className="text-emerald-400 font-mono font-bold">
            {profile.total_memories_recalled} Neurals Recalled
          </span>
        </div>
      </div>

      {/* Expanded Persona & Relationship Matrix */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-3 border-t border-white/5 text-xs space-y-2.5"
          >
            {/* Tabs */}
            <div className="flex items-center gap-1 bg-black/40 p-1 rounded-xl border border-white/5">
              <button
                onClick={() => setActiveTab('framework')}
                className={`flex-1 py-1 rounded-lg text-[10px] font-semibold transition ${
                  activeTab === 'framework'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Thinking
              </button>
              <button
                onClick={() => setActiveTab('relationships')}
                className={`flex-1 py-1 rounded-lg text-[10px] font-semibold transition ${
                  activeTab === 'relationships'
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Handling
              </button>
              <button
                onClick={() => setActiveTab('studies')}
                className={`flex-1 py-1 rounded-lg text-[10px] font-semibold transition ${
                  activeTab === 'studies'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Studies
              </button>
            </div>

            {/* Tab 1: Thinking Framework */}
            {activeTab === 'framework' && (
              <div className="space-y-1.5">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                  Sonu's Decision Matrix ("Think se le ke sab")
                </span>
                {profile.thinking_philosophy.rules.map((rule, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded-xl bg-black/30 border border-white/5 flex items-start gap-2"
                  >
                    <Zap className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0" />
                    <p className="text-[11px] text-slate-300 leading-snug">
                      {rule}
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 2: Relationship Handling Rules */}
            {activeTab === 'relationships' && (
              <div className="space-y-1.5 max-h-48 overflow-y-auto custom-scrollbar pr-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                  How Sonu Handles People ("Kaise kisi ko handle karna")
                </span>
                {profile.relationship_rules.map((rule, idx) => (
                  <div
                    key={idx}
                    className="p-2 rounded-xl bg-black/30 border border-white/5 space-y-1"
                  >
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="font-bold text-purple-300">
                        {rule.group}
                      </span>
                      <span className="text-slate-500 font-mono">
                        {rule.examples}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 italic">
                      "{rule.handling}"
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 3: Studies & Hobbies */}
            {activeTab === 'studies' && (
              <div className="space-y-2 text-xs">
                <div>
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block font-mono mb-1">
                    What He Studies Daily ("Kya Padhta Hu")
                  </span>
                  <div className="space-y-1">
                    {(profile.education_and_studies || [
                      'AI/ML Agentic research papers',
                      'Distributed microservices & low-latency backends',
                      'macOS CoreAudio and Apple Silicon internals'
                    ]).map((s, idx) => (
                      <div key={idx} className="p-1.5 rounded-lg bg-black/30 border border-white/5 text-[11px] text-slate-300 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        <span className="truncate">{s}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider block font-mono mb-1">
                    Hobbies & Passions ("Meri Hobby")
                  </span>
                  <div className="space-y-1">
                    {(profile.hobbies || [
                      'Late-night deep work coding marathons',
                      'High-tempo Lofi and EDM music while programming',
                      'Frosted-glass Apple UI design'
                    ]).map((h, idx) => (
                      <div key={idx} className="p-1.5 rounded-lg bg-black/30 border border-white/5 text-[11px] text-slate-300 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                        <span className="truncate">{h}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Direct Link to Personalize Panel */}
            {onOpenPersonalize && (
              <div className="pt-2 border-t border-white/10 flex items-center gap-2">
                <button
                  onClick={onOpenPersonalize}
                  className="flex-1 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-bold text-[10px] flex items-center justify-center gap-1 transition shadow-md shadow-cyan-950/40"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Open Mind & Vault</span>
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
