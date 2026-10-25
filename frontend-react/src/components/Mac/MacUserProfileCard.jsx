import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  User,
  Brain,
  ShieldCheck,
  Zap,
  Sparkles,
  FileText,
  FileCode,
  BookOpen,
  Heart,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Cpu,
  Layers,
  CreditCard,
  Briefcase,
  CheckCircle2
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function MacUserProfileCard({ bossProfile, onOpenPersonalize, onOpenVault }) {
  // 3 Modes: 'profile' (My Profile & MD) | 'document' (Document Vault) | 'skill' (Skills & Business)
  const [activeMode, setActiveMode] = useState('profile');
  const [isExpanded, setIsExpanded] = useState(false);
  const [showMdPreview, setShowMdPreview] = useState(false);
  const [mindMarkdown, setMindMarkdown] = useState('');
  const [vaultSummary, setVaultSummary] = useState(null);

  const profile = bossProfile || {
    name: 'Asif Aslam (Sonu Sarkar)',
    full_name: 'Asif Aslam',
    alias: 'Sonu Sarkar',
    title: 'Founder & Chief AI Systems Architect',
    ecosystem: 'KYRON AGI • BookMyGaadi',
    location: 'Motihari / Patna, Bihar',
    thinking_philosophy: {
      style: 'High-Agency & First Principles',
      rules: [
        'Speed over bureaucracy: execute immediately, verify in sandbox',
        'Direct & polite communication: zero fluff, clear timelines',
        'Continuous automation: if done twice, automate with Kyron'
      ]
    },
    education_and_studies: [
      'Advanced AI/ML Agentic research papers',
      'Distributed Systems & Low-latency microservices',
      'Apple Silicon internals & macOS CoreAudio pipelines'
    ],
    hobbies: [
      'Late-night autonomous agent coding marathons',
      'Lofi and EDM music while programming',
      'Frosted-glass Apple-grade UI design'
    ]
  };

  // Fetch KYRON_MIND.md & Vault on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const resMind = await api.get('/api/kyron/profile/mind/readme');
        if (resMind.data?.success) {
          setMindMarkdown(resMind.data.markdown);
        }
      } catch (_) {}

      try {
        const resVault = await api.get('/api/kyron/vault/documents');
        if (resVault.data?.success) {
          setVaultSummary(resVault.data.vault);
        }
      } catch (_) {}
    };
    fetchData();
  }, []);

  return (
    <div className="rounded-2xl bg-gradient-to-br from-[#0b1220]/95 via-[#0e172e]/90 to-[#12132a]/95 border border-cyan-500/30 shadow-2xl backdrop-blur-2xl overflow-hidden select-none">
      {/* 1. Header Banner: Avatar + Name + Title */}
      <div className="p-3.5 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2.5">
            <div className="relative">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center text-white font-black text-sm shadow-md shadow-cyan-900/40">
                A
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#0b1220] animate-pulse"></span>
            </div>

            <div>
              <div className="flex items-center gap-1.5">
                <h3 className="text-xs font-bold text-white tracking-wide">
                  {profile.full_name || 'Asif Aslam'}{' '}
                  <span className="text-cyan-400 font-semibold">({profile.alias || 'Sonu Sarkar'})</span>
                </h3>
              </div>
              <p className="text-[10px] text-slate-400 font-mono truncate max-w-[170px]">
                {profile.title || 'Founder & Chief AI Systems Architect'}
              </p>
            </div>
          </div>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition flex items-center gap-1 text-[10px] font-mono"
            title="Toggle card details"
          >
            <span>{isExpanded ? 'Less' : 'Details'}</span>
            {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
          </button>
        </div>

        {/* Cognitive Mind Verification Beacon */}
        <div className="flex items-center justify-between p-2 rounded-xl bg-cyan-950/40 border border-cyan-500/20 text-[10px]">
          <div className="flex items-center gap-1.5 text-cyan-300 font-medium">
            <Brain className="w-3.5 h-3.5 text-cyan-400 animate-pulse shrink-0" />
            <span className="truncate">KYRON_MIND.md: Synchronized</span>
          </div>
          <span className="text-emerald-400 font-mono font-bold text-[9px] px-1.5 py-0.2 rounded bg-emerald-950/80 border border-emerald-500/30 shrink-0">
            Profile-First
          </span>
        </div>
      </div>

      {/* 2. Three Internal Modes Switcher: My Profile | Document | Skill */}
      <div className="p-2 border-b border-white/5 bg-black/30">
        <div className="grid grid-cols-3 gap-1 p-0.5 rounded-xl bg-black/40 border border-white/5 text-[10px]">
          <button
            onClick={() => {
              setActiveMode('profile');
              setIsExpanded(true);
            }}
            className={`py-1.5 rounded-lg font-bold flex items-center justify-center gap-1 transition ${
              activeMode === 'profile'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <User className="w-3 h-3" />
            <span>My Profile</span>
          </button>

          <button
            onClick={() => {
              setActiveMode('document');
              setIsExpanded(true);
            }}
            className={`py-1.5 rounded-lg font-bold flex items-center justify-center gap-1 transition ${
              activeMode === 'document'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <CreditCard className="w-3 h-3" />
            <span>Document</span>
          </button>

          <button
            onClick={() => {
              setActiveMode('skill');
              setIsExpanded(true);
            }}
            className={`py-1.5 rounded-lg font-bold flex items-center justify-center gap-1 transition ${
              activeMode === 'skill'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <Briefcase className="w-3 h-3" />
            <span>Skill</span>
          </button>
        </div>
      </div>

      {/* 3. Mode Content Viewport */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-3 text-xs space-y-2.5 overflow-hidden"
          >
            {/* ======================================================== */}
            {/* MODE 1: MY PROFILE & PERSONALIZED MD FILE                */}
            {/* ======================================================== */}
            {activeMode === 'profile' && (
              <div className="space-y-2">
                {/* Personalized MD File Section */}
                <div className="p-2.5 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-cyan-300 flex items-center gap-1">
                      <FileCode className="w-3.5 h-3.5 text-cyan-400" />
                      KYRON_MIND.md
                    </span>
                    <button
                      onClick={() => setShowMdPreview(!showMdPreview)}
                      className="text-[10px] text-cyan-400 hover:text-cyan-300 font-mono font-bold"
                    >
                      {showMdPreview ? 'Hide File' : 'View MD File'}
                    </button>
                  </div>

                  <p className="text-[10px] text-slate-300 leading-snug">
                    Kyron answers queries using this personalized markdown file. Profile checked before responding.
                  </p>

                  {/* Expandable Markdown Preview */}
                  {showMdPreview && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="p-2 bg-black/60 rounded-lg border border-white/5 max-h-36 overflow-y-auto custom-scrollbar font-mono text-[9px] text-cyan-200 whitespace-pre-wrap leading-relaxed"
                    >
                      {mindMarkdown || '# KYRON_MIND — Asif Aslam (Sonu Sarkar)\nLoading mind context...'}
                    </motion.div>
                  )}
                </div>

                {/* What He Studies Daily */}
                <div className="space-y-1">
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                    What He Studies ("Kya Padhta Hu")
                  </span>
                  {(profile.education_and_studies || [
                    'Advanced AI/ML Agentic research papers',
                    'Distributed Systems Architecture',
                    'Apple Silicon macOS CoreAudio pipelines'
                  ]).slice(0, 2).map((item, idx) => (
                    <div key={idx} className="p-1.5 rounded-lg bg-black/30 border border-white/5 flex items-center gap-1.5 text-[10px] text-slate-300">
                      <BookOpen className="w-3 h-3 text-indigo-400 shrink-0" />
                      <span className="truncate">{item}</span>
                    </div>
                  ))}
                </div>

                {/* Hobbies & Passions */}
                <div className="space-y-1">
                  <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                    Hobbies ("Meri Hobby")
                  </span>
                  {(profile.hobbies || [
                    'Late-night deep work coding marathons',
                    'High-tempo Lofi and EDM music'
                  ]).slice(0, 2).map((hob, idx) => (
                    <div key={idx} className="p-1.5 rounded-lg bg-black/30 border border-white/5 flex items-center gap-1.5 text-[10px] text-slate-300">
                      <Heart className="w-3 h-3 text-rose-400 shrink-0" />
                      <span className="truncate">{hob}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ======================================================== */}
            {/* MODE 2: DOCUMENT VAULT & FORM AUTO-FIT                   */}
            {/* ======================================================== */}
            {activeMode === 'document' && (
              <div className="space-y-2">
                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                  Stored KYC Documents & Credentials
                </span>

                <div className="space-y-1.5 max-h-48 overflow-y-auto custom-scrollbar pr-1">
                  {[
                    { label: 'Aadhaar Card', val: 'XXXX-XXXX-9942', type: 'UIDAI Masked', icon: '🆔' },
                    { label: 'PAN Card', val: 'BXXXX8849F', type: 'Tax ID', icon: '📄' },
                    { label: 'Passport Photo', val: '413 x 531 px • White BG', type: 'Photo Specimen', icon: '📷' },
                    { label: 'Digital Signature', val: 'Dark Ink PNG Specimen', type: 'Signature', icon: '✍️' },
                    { label: 'Bank Account', val: 'HDFC •••• 7892 (IFSC: HDFC0001234)', type: 'Settlement', icon: '🏦' }
                  ].map((doc, idx) => (
                    <div
                      key={idx}
                      className="p-2 rounded-xl bg-black/30 border border-white/5 flex items-center justify-between text-[10px]"
                    >
                      <div className="flex items-center gap-1.5 truncate mr-2">
                        <span>{doc.icon}</span>
                        <div className="truncate">
                          <span className="font-bold text-white block truncate">{doc.label}</span>
                          <span className="text-slate-400 font-mono text-[9px] block truncate">{doc.val}</span>
                        </div>
                      </div>
                      <span className="text-[9px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-500/20 shrink-0">
                        {doc.type}
                      </span>
                    </div>
                  ))}
                </div>

                <p className="text-[9px] text-slate-400 italic">
                  💡 Website jo dimension maange, Kyron use auto-crop aur fit karke upload karta hai.
                </p>
              </div>
            )}

            {/* ======================================================== */}
            {/* MODE 3: SKILL & BUSINESS AUTOMATION                      */}
            {/* ======================================================== */}
            {activeMode === 'skill' && (
              <div className="space-y-2 text-xs">
                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                  Active Ventures & Autonomous Skills
                </span>

                <div className="space-y-1.5">
                  <div className="p-2 rounded-xl bg-black/30 border border-white/5 space-y-1">
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="font-bold text-cyan-300">KYRON AGI</span>
                      <span className="text-emerald-400 font-mono font-bold">Live v2.0</span>
                    </div>
                    <p className="text-[10px] text-slate-300">
                      Personal Autonomous Agentic OS • Hands-free Voice & Desktop Control
                    </p>
                  </div>

                  <div className="p-2 rounded-xl bg-black/30 border border-white/5 space-y-1">
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="font-bold text-purple-300">BookMyGaadi</span>
                      <span className="text-emerald-400 font-mono font-bold">Bihar Operations</span>
                    </div>
                    <p className="text-[10px] text-slate-300">
                      Intercity Outstation Fleet Network • Instant WhatsApp Cab Bookings
                    </p>
                  </div>

                  <div className="p-2 rounded-xl bg-black/30 border border-white/5 space-y-1">
                    <span className="text-[10px] font-bold text-white block">Execution Capabilities</span>
                    <div className="flex flex-wrap gap-1 text-[9px] font-mono text-cyan-300">
                      <span className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">Playwright Web</span>
                      <span className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">macOS System Control</span>
                      <span className="px-1.5 py-0.5 rounded bg-white/5 border border-white/10">Client CRM & Lead Proposals</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Bottom Quick Action: Switch to Full Studio */}
            {onOpenPersonalize && (
              <div className="pt-2 border-t border-white/10">
                <button
                  onClick={onOpenPersonalize}
                  className="w-full py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-purple-600 hover:opacity-90 text-white font-bold text-[10px] flex items-center justify-center gap-1.5 transition shadow-md shadow-cyan-950/40"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Open Full Personalize Studio</span>
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
