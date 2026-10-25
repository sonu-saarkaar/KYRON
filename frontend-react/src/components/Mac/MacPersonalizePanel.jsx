import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain,
  FileText,
  ShieldCheck,
  User,
  BookOpen,
  Cpu,
  Heart,
  Save,
  Upload,
  Crop,
  CheckCircle2,
  Sparkles,
  Building2,
  Share2,
  Send,
  Download,
  AlertCircle,
  Code2,
  RefreshCw,
  PhoneCall,
  Briefcase,
  CreditCard,
  Plane,
  Ticket,
  FileCheck,
  ExternalLink,
  X,
  Check,
  Loader2,
  ArrowRight
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';
import MacAutonomousActionCard from './MacAutonomousActionCard';

export default function MacPersonalizePanel({ onClose }) {
  const [activeTab, setActiveTab] = useState('mind'); // 'mind' | 'vault' | 'business'

  // Autonomous Super-Actions execution
  const [executingAction, setExecutingAction] = useState(null);
  const [actionResult, setActionResult] = useState(null);
  const [showActionModal, setShowActionModal] = useState(false);

  // Profile data
  const [profile, setProfile] = useState(null);
  const [loadingProfile, setLoadingProfile] = useState(true);

  // Markdown Mind
  const [mindMarkdown, setMindMarkdown] = useState('');
  const [savingMind, setSavingMind] = useState(false);

  // Profile check test query
  const [testQuery, setTestQuery] = useState('mai koun hu aur mera kya business hai?');
  const [testResult, setTestResult] = useState(null);
  const [checkingQuery, setCheckingQuery] = useState(false);

  // Document Vault data
  const [vaultData, setVaultData] = useState(null);
  const [loadingVault, setLoadingVault] = useState(false);

  // Form Resizer state
  const [selectedDocType, setSelectedDocType] = useState('photo');
  const [targetWidth, setTargetWidth] = useState(200);
  const [targetHeight, setTargetHeight] = useState(230);
  const [maxSizeKB, setMaxSizeKB] = useState(50);
  const [outputFormat, setOutputFormat] = useState('jpeg');
  const [processingDoc, setProcessingDoc] = useState(false);
  const [processedResult, setProcessedResult] = useState(null);

  // Business Suite state
  const [businessData, setBusinessData] = useState(null);
  const [campaignTopic, setCampaignTopic] = useState('BookMyGaadi Outstation Ride WhatsApp Booking');
  const [campaignPlatform, setCampaignPlatform] = useState('LinkedIn');
  const [generatingCampaign, setGeneratingCampaign] = useState(false);
  const [generatedCampaign, setGeneratedCampaign] = useState(null);

  // Fetch Profile & Mind
  const fetchProfileAndMind = async () => {
    try {
      setLoadingProfile(true);
      const resProfile = await api.get('/api/kyron/profile/mind');
      if (resProfile.data?.success) {
        setProfile(resProfile.data.profile);
      }
      const resMind = await api.get('/api/kyron/profile/mind/readme');
      if (resMind.data?.success) {
        setMindMarkdown(resMind.data.markdown);
      }
    } catch (e) {
      console.debug('Failed to fetch profile/mind:', e);
    } finally {
      setLoadingProfile(false);
    }
  };

  // Fetch Vault Data
  const fetchVaultData = async () => {
    try {
      setLoadingVault(true);
      const res = await api.get('/api/kyron/vault/documents');
      if (res.data?.success) {
        setVaultData(res.data.vault);
      }
    } catch (e) {
      console.debug('Failed to fetch vault data:', e);
    } finally {
      setLoadingVault(false);
    }
  };

  // Fetch Business Data
  const fetchBusinessData = async () => {
    try {
      const res = await api.get('/api/kyron/business/summary');
      if (res.data?.success) {
        setBusinessData(res.data.business);
      }
    } catch (e) {
      console.debug('Failed to fetch business data:', e);
    }
  };

  useEffect(() => {
    fetchProfileAndMind();
    fetchVaultData();
    fetchBusinessData();
  }, []);

  // Save updated KYRON_MIND.md
  const handleSaveMind = async () => {
    try {
      setSavingMind(true);
      const res = await api.post('/api/kyron/profile/mind/readme', { markdown: mindMarkdown });
      if (res.data?.success) {
        toast.success('KYRON_MIND.md saved and active in Kyron Cognitive Memory!');
      } else {
        toast.error('Failed to save KYRON_MIND.md');
      }
    } catch (e) {
      toast.error('Error saving KYRON_MIND.md');
    } finally {
      setSavingMind(false);
    }
  };

  // Execute Autonomous Super Action
  const handleExecuteAction = async (actionType, params = {}) => {
    try {
      setExecutingAction(actionType);
      const res = await api.post('/api/kyron/actions/execute', { action_type: actionType, params });
      if (res.data?.success) {
        setActionResult(res.data);
        setShowActionModal(true);
        toast.success(res.data.voice_vocalization || 'Action executed successfully!');
      } else {
        toast.error('Failed to execute action');
      }
    } catch (e) {
      toast.error('Error executing autonomous action');
    } finally {
      setExecutingAction(null);
    }
  };

  // Upload custom personal .md file and sync immediately
  const handleUploadReadme = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (e) => {
      const content = e.target?.result;
      if (typeof content === 'string') {
        setMindMarkdown(content);
        try {
          setSavingMind(true);
          const res = await api.post('/api/kyron/profile/mind/readme', { markdown: content });
          if (res.data?.success) {
            toast.success(`Uploaded ${file.name} and synchronized with Kyron Cognitive Mind!`);
            fetchProfileAndMind();
          } else {
            toast.error('Failed to synchronize markdown');
          }
        } catch (err) {
          toast.error('Error synchronizing markdown');
        } finally {
          setSavingMind(false);
        }
      }
    };
    reader.readAsText(file);
  };

  // Test Profile-First check
  const handleTestProfileCheck = async () => {
    if (!testQuery.trim()) return;
    try {
      setCheckingQuery(true);
      const res = await api.post('/api/kyron/profile/check', { query: testQuery });
      if (res.data?.success) {
        setTestResult(res.data.result);
      }
    } catch (e) {
      toast.error('Profile check error');
    } finally {
      setCheckingQuery(false);
    }
  };

  // Process Document for Web Form
  const handleProcessDoc = async () => {
    try {
      setProcessingDoc(true);
      const res = await api.post('/api/kyron/vault/format-doc', {
        doc_type: selectedDocType,
        target_width: Number(targetWidth),
        target_height: Number(targetHeight),
        max_size_kb: Number(maxSizeKB),
        output_format: outputFormat
      });
      if (res.data?.success) {
        setProcessedResult(res.data);
        toast.success(res.data.voice_vocalization || 'Document formatted to exact specifications!');
      }
    } catch (e) {
      toast.error('Error processing document for form');
    } finally {
      setProcessingDoc(false);
    }
  };

  // Generate Branding Campaign
  const handleGenerateCampaign = async () => {
    if (!campaignTopic.trim()) return;
    try {
      setGeneratingCampaign(true);
      const res = await api.post('/api/kyron/business/generate-campaign', {
        venture_name: 'BookMyGaadi',
        topic: campaignTopic,
        platform: campaignPlatform
      });
      if (res.data?.success) {
        setGeneratedCampaign(res.data.campaign);
        toast.success('Campaign generated successfully!');
      }
    } catch (e) {
      toast.error('Error generating campaign');
    } finally {
      setGeneratingCampaign(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#0a0f1d] text-slate-200 select-none overflow-hidden">
      {/* Top Navigation Bar */}
      <div className="p-4 border-b border-white/10 bg-slate-900/60 backdrop-blur-xl flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center text-white font-black text-lg shadow-lg shadow-cyan-900/40">
              A
            </div>
            <span className="absolute -bottom-1 -right-1 w-3.5 h-3.5 bg-emerald-500 rounded-full border-2 border-[#0a0f1d] animate-pulse"></span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white tracking-wide">
                Asif Aslam <span className="text-cyan-400 font-semibold">(Sonu Sarkar)</span>
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-500/40 font-bold">
                PERSONALIZED AGI MIND
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Founder & Chief AI Systems Architect • KYRON AGI & BookMyGaadi
            </p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-white/10 text-xs">
          {[
            { id: 'mind', label: 'Cognitive Mind & README', icon: <Brain className="w-3.5 h-3.5 text-cyan-400" /> },
            { id: 'vault', label: 'Document Vault & Form Resizer', icon: <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> },
            { id: 'business', label: 'Business Suite & Branding', icon: <Briefcase className="w-3.5 h-3.5 text-purple-400" /> }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
        {/* ============================================================== */}
        {/* TAB 1: COGNITIVE MIND & README                                 */}
        {/* ============================================================== */}
        {activeTab === 'mind' && (
          <div className="space-y-4">
            {/* AUTONOMOUS SUPER-ACTIONS BAR */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-cyan-950/40 via-indigo-950/30 to-purple-950/40 border border-cyan-500/30 shadow-2xl backdrop-blur-xl">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400">
                    <Sparkles className="w-4 h-4 animate-pulse" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                      <span>Autonomous Super-Power Actions</span>
                      <span className="text-[9px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-semibold">
                        ZERO MANUAL FORM-FILLING
                      </span>
                    </h3>
                    <p className="text-[11px] text-slate-400">
                      Kyron autonomously executes real tasks using your uploaded profile, auto-formatting photos and signatures.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
                {[
                  {
                    id: 'pan_card',
                    title: 'PAN Card (Form 49A)',
                    cmd: '"mera pan card bana do"',
                    desc: 'Auto-fill Form 49A, photo (200x230) & sign (140x60) auto-crop',
                    icon: <CreditCard className="w-4 h-4 text-amber-400" />,
                    bg: 'hover:border-amber-500/50'
                  },
                  {
                    id: 'passport',
                    title: 'Passport Seva Form 1',
                    cmd: '"passport bana do"',
                    desc: 'Auto-fill Form 1, photo (413x531 px), maps RPO Patna & Motihari',
                    icon: <Plane className="w-4 h-4 text-cyan-400" />,
                    bg: 'hover:border-cyan-500/50'
                  },
                  {
                    id: 'ticket_booking',
                    title: 'Ticket Reservation',
                    cmd: '"ticket kato"',
                    desc: 'Train & flight booking with Lower Berth preference & HDFC UPI',
                    icon: <Ticket className="w-4 h-4 text-emerald-400" />,
                    bg: 'hover:border-emerald-500/50'
                  },
                  {
                    id: 'universal_form',
                    title: 'Universal Form Filler',
                    cmd: '"form auto-fill"',
                    desc: 'Maps 10+ core personal, address & banking details to web forms',
                    icon: <FileCheck className="w-4 h-4 text-purple-400" />,
                    bg: 'hover:border-purple-500/50'
                  }
                ].map((act) => (
                  <button
                    key={act.id}
                    onClick={() => handleExecuteAction(act.id)}
                    disabled={executingAction === act.id}
                    className={`flex flex-col text-left p-3 rounded-xl bg-black/40 border border-white/10 ${act.bg} hover:bg-white/[0.04] transition group disabled:opacity-50`}
                  >
                    <div className="flex items-center justify-between w-full mb-1">
                      <div className="flex items-center gap-1.5 font-bold text-white text-xs">
                        {act.icon}
                        <span>{act.title}</span>
                      </div>
                      {executingAction === act.id ? (
                        <Loader2 className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
                      ) : (
                        <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-0.5 transition" />
                      )}
                    </div>
                    <span className="text-[10px] text-cyan-300 font-mono mb-1">{act.cmd}</span>
                    <p className="text-[10px] text-slate-400 line-clamp-2 leading-tight">
                      {act.desc}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left 1 Col: Persona Summary & What He Studies */}
            <div className="space-y-4">
              {/* Who Am I Card */}
              <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/10 shadow-xl backdrop-blur-xl">
                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
                  <User className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                    Identity & Background
                  </h3>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  {profile?.personal_life?.who_am_i ||
                    'Founder and Chief Architect of KYRON AGI and BookMyGaadi. Focuses on extreme automation, high-speed agency, and first-principles software design.'}
                </p>
                <div className="space-y-1.5 text-xs">
                  <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block font-mono">
                    Core Values
                  </span>
                  {(profile?.personal_life?.values || [
                    'Speed over bureaucracy',
                    'High agency ownership',
                    'Aesthetic & lightning-fast software'
                  ]).map((val, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-slate-300">
                      <span className="text-cyan-400 font-bold">•</span>
                      <span>{val}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* What I Study Daily */}
              <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/10 shadow-xl backdrop-blur-xl">
                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
                  <BookOpen className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                    What I Study & Read
                  </h3>
                </div>
                <div className="space-y-1.5 text-xs">
                  {(profile?.education_and_studies?.what_i_study_daily || [
                    'AI/ML Agentic research papers',
                    'Distributed Systems Architecture',
                    'macOS internals & CoreAudio',
                    'Glassmorphic spatial interface design'
                  ]).map((item, idx) => (
                    <div key={idx} className="p-2 rounded-xl bg-black/30 border border-white/5 flex items-center gap-2 text-slate-300">
                      <Cpu className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Hobbies & Passions */}
              <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/10 shadow-xl backdrop-blur-xl">
                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
                  <Heart className="w-4 h-4 text-rose-400" />
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                    Hobbies & Passions
                  </h3>
                </div>
                <div className="space-y-1 text-xs">
                  {(profile?.hobbies_and_passions || [
                    'Late-night autonomous agent coding marathons',
                    'Lofi and EDM music while programming',
                    'Designing frosted-glass Apple interfaces',
                    'Apple Silicon hardware benchmarking'
                  ]).map((hob, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-slate-300 py-0.5">
                      <span className="text-rose-400 font-bold">•</span>
                      <span>{hob}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right 2 Cols: Interactive KYRON_MIND.md Editor & Profile Check Tester */}
            <div className="lg:col-span-2 space-y-4">
              {/* Markdown Editor & Upload */}
              <div className="p-4 rounded-2xl bg-slate-900/70 border border-cyan-500/30 shadow-2xl backdrop-blur-xl flex flex-col h-[520px]">
                <div className="flex items-center justify-between pb-3 mb-2 border-b border-white/10">
                  <div className="flex items-center gap-2">
                    <Code2 className="w-4 h-4 text-cyan-400" />
                    <div>
                      <h4 className="text-xs font-bold text-cyan-300 flex items-center gap-1.5">
                        <span>KYRON_MIND.md</span>
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/30 font-mono">
                          Live Active Mind
                        </span>
                      </h4>
                      <p className="text-[10px] text-slate-400">
                        Kyron checks this file FIRST before generating any reply or executing tasks.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <label className="cursor-pointer px-2.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-medium border border-white/10 flex items-center gap-1.5 transition">
                      <Upload className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Upload README</span>
                      <input
                        type="file"
                        accept=".md,.txt"
                        onChange={handleUploadReadme}
                        className="hidden"
                      />
                    </label>

                    <button
                      onClick={handleSaveMind}
                      disabled={savingMind}
                      className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-cyan-950/40 flex items-center gap-1.5 transition disabled:opacity-50"
                    >
                      <Save className="w-3.5 h-3.5" />
                      <span>{savingMind ? 'Saving...' : 'Save Kyron Mind'}</span>
                    </button>
                  </div>
                </div>

                {/* Drag & Drop .md File Banner */}
                <div className="mb-2 p-2.5 rounded-xl bg-gradient-to-r from-cyan-950/40 to-black/40 border border-dashed border-cyan-500/40 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                    <div>
                      <h5 className="text-[11px] font-bold text-white">Upload Your Personal .md File</h5>
                      <p className="text-[10px] text-slate-400">
                        Upload your Markdown profile once. Kyron learns personal life, business, tech skills & documents automatically.
                      </p>
                    </div>
                  </div>
                  <label className="cursor-pointer shrink-0 px-2.5 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-[11px] font-bold shadow-md transition flex items-center gap-1.5">
                    <Upload className="w-3 h-3" />
                    <span>Select .md</span>
                    <input
                      type="file"
                      accept=".md,.markdown,.txt"
                      onChange={handleUploadReadme}
                      className="hidden"
                    />
                  </label>
                </div>

                {/* Editor Textarea */}
                <textarea
                  value={mindMarkdown}
                  onChange={(e) => setMindMarkdown(e.target.value)}
                  placeholder="Paste or write your custom Kyron Mind markdown instructions..."
                  className="flex-1 w-full bg-black/40 border border-white/10 rounded-xl p-3 text-xs font-mono text-cyan-200 leading-relaxed resize-none focus:outline-none focus:border-cyan-500/50 custom-scrollbar"
                />
                <span className="text-[10px] text-slate-500 font-mono mt-2">
                  Tip: You can customize directives, response rules, and persona facts here. Changes persist automatically.
                </span>
              </div>

              {/* Profile-First Verification Sandbox */}
              <div className="p-4 rounded-2xl bg-gradient-to-br from-[#0c1424] to-[#121c32] border border-cyan-500/30 shadow-xl">
                <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <h4 className="text-xs font-bold text-emerald-300 font-mono uppercase tracking-wider">
                    Profile-First Check Simulator
                  </h4>
                </div>
                <p className="text-[11px] text-slate-400 mb-3">
                  Test how Kyron checks your master profile before answering questions about who you are, what you study, or what you do:
                </p>

                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={testQuery}
                    onChange={(e) => setTestQuery(e.target.value)}
                    placeholder="Enter test query (e.g. mai koun hu, meri knowledge, kya padhta hu)..."
                    className="flex-1 bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 font-mono"
                  />
                  <button
                    onClick={handleTestProfileCheck}
                    disabled={checkingQuery}
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition flex items-center gap-1.5 shrink-0"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{checkingQuery ? 'Checking...' : 'Check Profile'}</span>
                  </button>
                </div>

                {testResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-3 p-3 rounded-xl bg-black/50 border border-emerald-500/40 text-xs space-y-2"
                  >
                    <div className="flex items-center justify-between text-[10px] font-mono">
                      <span className="text-emerald-400 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" />
                        Verified: {testResult.checked_profile}
                      </span>
                      <span className="text-slate-400">
                        Topics: {testResult.triggered_topics?.join(', ') || 'General Identity'}
                      </span>
                    </div>
                    <p className="text-slate-200 leading-relaxed font-sans bg-slate-900/60 p-2.5 rounded-lg border border-white/5">
                      {testResult.synthesized_answer}
                    </p>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        </div>
        )}

        {/* ============================================================== */}
        {/* TAB 2: DOCUMENT VAULT & FORM-FILLER RESIZER                    */}
        {/* ============================================================== */}
        {activeTab === 'vault' && (
          <div className="space-y-4">
            {/* Vault Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
              {[
                {
                  id: 'photo',
                  title: 'Passport Photo',
                  number: '413 x 531 px',
                  detail: 'Clean white background, 4:5 ratio',
                  badge: 'Photo Asset',
                  color: 'cyan'
                },
                {
                  id: 'signature',
                  title: 'Digital Signature',
                  number: 'Specimen Active',
                  detail: 'Dark ink on transparent PNG',
                  badge: 'Signature Asset',
                  color: 'purple'
                },
                {
                  id: 'aadhaar',
                  title: 'Aadhaar Card',
                  number: vaultData?.documents?.aadhaar?.number || 'XXXX-XXXX-9942',
                  detail: 'UIDAI Verified • Motihari, Bihar',
                  badge: 'Identity',
                  color: 'emerald'
                },
                {
                  id: 'pan',
                  title: 'PAN Card',
                  number: vaultData?.documents?.pan?.number || 'BXXXX8849F',
                  detail: 'Income Tax Dept of India',
                  badge: 'Tax ID',
                  color: 'amber'
                },
                {
                  id: 'bank_account',
                  title: 'Primary Bank Account',
                  number: 'HDFC •••• 7892',
                  detail: 'IFSC: HDFC0001234 • Motihari',
                  badge: 'Settlement',
                  color: 'blue'
                }
              ].map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => setSelectedDocType(doc.id)}
                  className={`p-3.5 rounded-2xl border cursor-pointer transition select-none ${
                    selectedDocType === doc.id
                      ? 'bg-cyan-950/40 border-cyan-400 shadow-lg shadow-cyan-950/50'
                      : 'bg-slate-900/50 border-white/10 hover:border-white/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-white/5 text-slate-300 border border-white/10">
                      {doc.badge}
                    </span>
                    {selectedDocType === doc.id && (
                      <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
                    )}
                  </div>
                  <h4 className="text-xs font-bold text-white mb-1 truncate">{doc.title}</h4>
                  <p className="text-xs font-mono font-bold text-cyan-300 mb-1">{doc.number}</p>
                  <span className="text-[10px] text-slate-400 block truncate">{doc.detail}</span>
                </div>
              ))}
            </div>

            {/* Smart Crop, Fit & Resize Engine */}
            <div className="p-4 rounded-2xl bg-gradient-to-br from-[#0e172a] via-[#101b33] to-[#0a1122] border border-cyan-500/30 shadow-2xl">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <Crop className="w-5 h-5 text-cyan-400" />
                  <div>
                    <h3 className="text-xs font-bold text-white flex items-center gap-2">
                      <span>Smart Form Resizer & Auto-Crop Engine</span>
                      <span className="text-[9px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-500/40 font-mono font-bold">
                        macOS Native sips Engine
                      </span>
                    </h3>
                    <p className="text-[10px] text-slate-400">
                      Website jo format aur dimension maange, Kyron use exact size me crop, fit aur compress kar dega.
                    </p>
                  </div>
                </div>
              </div>

              {/* Controls */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono mb-1">
                    Document
                  </label>
                  <select
                    value={selectedDocType}
                    onChange={(e) => setSelectedDocType(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="photo">Passport Photo</option>
                    <option value="signature">Digital Signature</option>
                    <option value="pan">PAN Card</option>
                    <option value="aadhaar">Aadhaar Card</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono mb-1">
                    Width (px)
                  </label>
                  <input
                    type="number"
                    value={targetWidth}
                    onChange={(e) => setTargetWidth(Number(e.target.value))}
                    className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono mb-1">
                    Height (px)
                  </label>
                  <input
                    type="number"
                    value={targetHeight}
                    onChange={(e) => setTargetHeight(Number(e.target.value))}
                    className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono mb-1">
                    Max Size (KB)
                  </label>
                  <input
                    type="number"
                    value={maxSizeKB}
                    onChange={(e) => setMaxSizeKB(Number(e.target.value))}
                    className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                  />
                </div>

                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono mb-1">
                    Format
                  </label>
                  <select
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                    className="w-full bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="jpeg">JPEG / JPG</option>
                    <option value="png">PNG</option>
                    <option value="pdf">PDF</option>
                  </select>
                </div>
              </div>

              {/* Action Button */}
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-slate-400 font-mono">
                  Target: {targetWidth}x{targetHeight}px • Max {maxSizeKB}KB • {outputFormat.toUpperCase()}
                </span>

                <button
                  onClick={handleProcessDoc}
                  disabled={processingDoc}
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-purple-600 hover:from-cyan-500 hover:to-purple-500 text-white text-xs font-bold shadow-lg shadow-cyan-950/40 flex items-center gap-2 transition disabled:opacity-50"
                >
                  <Crop className="w-3.5 h-3.5" />
                  <span>{processingDoc ? 'Processing with sips...' : 'Crop & Fit Document'}</span>
                </button>
              </div>

              {/* Processed Result Banner */}
              {processedResult && (
                <motion.div
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-3.5 rounded-xl bg-black/60 border border-emerald-500/40 text-xs flex flex-wrap items-center justify-between gap-3"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span className="font-bold text-emerald-300">
                        {processedResult.output_file?.file_name}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 font-bold border border-emerald-500/30">
                        {processedResult.output_file?.file_size}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300">
                      {processedResult.voice_vocalization}
                    </p>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => toast.success('Document copied to clipboard for direct web upload!')}
                      className="px-3 py-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/30 text-xs font-semibold flex items-center gap-1.5 transition"
                    >
                      <Share2 className="w-3.5 h-3.5" />
                      <span>Ready for Form Upload</span>
                    </button>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Standard Autofill Reference */}
            <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/10">
              <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono mb-2">
                Autofill Presets (Ready for Autonomous Form-Filling)
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs font-mono">
                {Object.entries(vaultData?.autofill_preset || {
                  fullName: 'Asif Aslam',
                  alias: 'Sonu Sarkar',
                  fatherName: 'Md Aslam',
                  dob: '15/08/2000',
                  phone: '+91 92979 89994',
                  aadhaar: 'XXXX-XXXX-9942',
                  pan: 'BXXXX8849F',
                  bank: 'HDFC Bank Ltd.'
                }).map(([k, v]) => (
                  <div key={k} className="p-2 rounded-xl bg-black/30 border border-white/5">
                    <span className="text-[10px] text-slate-500 block">{k}</span>
                    <span className="text-cyan-300 font-bold truncate block">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ============================================================== */}
        {/* TAB 3: BUSINESS SUITE & BRANDING                               */}
        {/* ============================================================== */}
        {activeTab === 'business' && (
          <div className="space-y-4">
            {/* Top Ventures Banner */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-2xl bg-gradient-to-br from-cyan-950/50 via-slate-900 to-indigo-950/40 border border-cyan-500/30 shadow-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold text-cyan-300 bg-cyan-950 px-2 py-0.5 rounded border border-cyan-500/30">
                    VENTURE 1
                  </span>
                  <span className="text-xs font-bold text-emerald-400">● Live Operations</span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">KYRON AGI</h3>
                <p className="text-xs text-slate-300 mb-3">
                  Autonomous Agentic OS & Personal Workstation with hands-free voice and desktop execution.
                </p>
                <div className="flex items-center gap-3 text-xs font-mono text-cyan-300">
                  <span>Users: 2,400+</span>
                  <span>•</span>
                  <span>Automated Tasks: 148,000+</span>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-gradient-to-br from-indigo-950/50 via-slate-900 to-purple-950/40 border border-purple-500/30 shadow-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-bold text-purple-300 bg-purple-950 px-2 py-0.5 rounded border border-purple-500/30">
                    VENTURE 2
                  </span>
                  <span className="text-xs font-bold text-emerald-400">● Live in Bihar</span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">BookMyGaadi</h3>
                <p className="text-xs text-slate-300 mb-3">
                  Intercity & Outstation cab booking fleet across Bihar & Eastern India via instant WhatsApp.
                </p>
                <div className="flex items-center gap-3 text-xs font-mono text-purple-300">
                  <span>Completed Rides: 12,500+</span>
                  <span>•</span>
                  <span>Drivers: 450+ Verified</span>
                </div>
              </div>
            </div>

            {/* Inbound Client Leads Pipeline */}
            <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/10">
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/10">
                <div className="flex items-center gap-2">
                  <Building2 className="w-4 h-4 text-cyan-400" />
                  <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                    Active Client Leads & Partnerships
                  </h4>
                </div>
                <span className="text-xs font-mono font-bold text-cyan-300">
                  3 Inbound Leads
                </span>
              </div>

              <div className="space-y-2">
                {[
                  {
                    name: 'Apex Logistics Ltd.',
                    contact: 'Vikram Malhotra',
                    service: 'Autonomous Fleet Tracking & WhatsApp Dispatch Agent',
                    val: '₹4,50,000',
                    status: 'Proposal Sent'
                  },
                  {
                    name: 'Zenith FinTech Solutions',
                    contact: 'Pooja Singhania',
                    service: 'Document Vault & KYC Autofill Engine Integration',
                    val: '₹3,20,000',
                    status: 'In Negotiation'
                  },
                  {
                    name: 'Bihar Tourism & Travel Corp',
                    contact: 'Rameshwar Prasad',
                    service: 'BookMyGaadi Outstation API Partnership',
                    val: '₹8,00,000',
                    status: 'Contract Drafted'
                  }
                ].map((lead, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-black/30 border border-white/5 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-white">{lead.name}</span>
                        <span className="text-slate-400 text-[10px]">({lead.contact})</span>
                      </div>
                      <p className="text-[11px] text-slate-300 mt-0.5">{lead.service}</p>
                    </div>

                    <div className="flex items-center gap-3 font-mono">
                      <span className="text-emerald-400 font-bold">{lead.val}</span>
                      <span className="px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 text-[10px] font-bold border border-cyan-500/30">
                        {lead.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Instant Promotion & Branding Generator */}
            <div className="p-4 rounded-2xl bg-gradient-to-br from-[#0c1424] to-[#121c32] border border-cyan-500/30 shadow-xl">
              <div className="flex items-center gap-2 mb-2 pb-2 border-b border-white/10">
                <Share2 className="w-4 h-4 text-purple-400" />
                <h4 className="text-xs font-bold text-purple-300 font-mono uppercase tracking-wider">
                  Promotion & Branding Generator (Sonu's Brand Voice)
                </h4>
              </div>
              <p className="text-[11px] text-slate-400 mb-3">
                Generate high-energy marketing campaigns for LinkedIn, Twitter, and WhatsApp broadcasting in your exact voice:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-3">
                <input
                  type="text"
                  value={campaignTopic}
                  onChange={(e) => setCampaignTopic(e.target.value)}
                  placeholder="Campaign Topic (e.g. KYRON v2.0 Launch, Cab booking discounts)..."
                  className="md:col-span-2 bg-black/40 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 font-mono"
                />

                <div className="flex items-center gap-2">
                  <select
                    value={campaignPlatform}
                    onChange={(e) => setCampaignPlatform(e.target.value)}
                    className="flex-1 bg-black/40 border border-white/10 rounded-xl p-2 text-xs text-white focus:outline-none focus:border-cyan-500 font-mono"
                  >
                    <option value="LinkedIn">LinkedIn</option>
                    <option value="Twitter">Twitter / X</option>
                    <option value="WhatsApp">WhatsApp Broadcast</option>
                  </select>

                  <button
                    onClick={handleGenerateCampaign}
                    disabled={generatingCampaign}
                    className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition flex items-center gap-1.5 shrink-0"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{generatingCampaign ? 'Writing...' : 'Generate'}</span>
                  </button>
                </div>
              </div>

              {generatedCampaign && (
                <div className="p-3 rounded-xl bg-black/60 border border-purple-500/40 text-xs space-y-2">
                  <div className="flex items-center justify-between text-[10px] font-mono">
                    <span className="text-purple-300 font-bold">
                      Platform: {generatedCampaign.platform} • {generatedCampaign.venture}
                    </span>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(generatedCampaign.generated_copy);
                        toast.success('Post copy copied to clipboard!');
                      }}
                      className="text-cyan-400 hover:text-cyan-300 font-bold"
                    >
                      Copy to Clipboard
                    </button>
                  </div>
                  <p className="text-slate-200 whitespace-pre-wrap font-sans bg-slate-900/60 p-3 rounded-lg border border-white/5 leading-relaxed">
                    {generatedCampaign.generated_copy}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Autonomous Action Result Modal */}
      <AnimatePresence>
        {showActionModal && actionResult && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-2xl bg-[#0c1424] border border-cyan-500/40 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
            >
              <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Autonomous Super-Power Execution</h3>
                </div>
                <button
                  onClick={() => setShowActionModal(false)}
                  className="p-1 rounded-lg text-slate-400 hover:text-white transition"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="p-4 overflow-y-auto custom-scrollbar">
                <MacAutonomousActionCard action={actionResult} />
              </div>

              <div className="p-3 border-t border-white/10 bg-black/40 flex items-center justify-end gap-2">
                <button
                  onClick={() => setShowActionModal(false)}
                  className="px-4 py-1.5 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-semibold transition"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
