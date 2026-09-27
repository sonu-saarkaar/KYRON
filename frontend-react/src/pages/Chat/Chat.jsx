import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Send,
  Sparkles,
  Plus,
  Trash2,
  Play,
  Music,
  ExternalLink,
  Bot,
  User,
  Check,
  Copy,
  Terminal,
  Shield,
  Zap,
  Menu,
  X,
  Clock,
  Code2,
  Radio,
  FileCode,
  Layers,
  ChevronDown,
  ChevronUp,
  Globe,
  MessageSquare
} from 'lucide-react';
import toast from 'react-hot-toast';

import { useKyronVoice } from '../../hooks/useKyronVoice';
import api from '../../services/api';
import MunderDifflinPanel from '../../components/MunderDifflinPanel';
import BMGManagementPanel from '../../components/BMGManagementPanel';
import { DiffCard, ActionPreviewCard } from '../../components/Jarvis/MissionCards';

export default function Chat() {
  const { panel } = useParams();
  const navigate = useNavigate();

  // Active workspace: 'kyron' | 'munder' | 'bmg'
  const activePanel = panel || 'kyron';
  const handlePanelChange = (newPanel) => {
    navigate(`/chat/${newPanel}`);
  };

  // Sidebar toggle for mobile/desktop
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Chat message stream (ChatGPT / Claude style)
  const [messages, setMessages] = useState([
    {
      id: 'welcome-msg',
      sender: 'kyron',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: "Namaste Boss! I am KYRON, your hands-free AGI assistant. You can speak naturally, say **'Hey Kyron'**, or clap to wake me up. How can I assist you today?",
      action: null
    }
  ]);

  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [hasInteracted, setHasInteracted] = useState(false);

  // Persistent Sessions state (ChatGPT / Claude style)
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // Fetch all sessions from persistent backend
  const fetchSessions = async (autoSelect = true) => {
    try {
      setLoadingSessions(true);
      const res = await api.get('/api/kyron/sessions');
      if (res.data?.success && Array.isArray(res.data.sessions)) {
        const list = res.data.sessions;
        setSessions(list);
        if (autoSelect && list.length > 0 && !activeSessionId) {
          selectSession(list[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to load chat sessions:', e);
    } finally {
      setLoadingSessions(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  // Select an existing session and load its message history
  const selectSession = async (sessionId) => {
    if (!sessionId) return;
    try {
      setActiveSessionId(sessionId);
      const res = await api.get(`/api/kyron/sessions/${sessionId}`);
      if (res.data?.success && res.data.session) {
        const sess = res.data.session;
        if (sess.messages && sess.messages.length > 0) {
          const loadedMsgs = sess.messages.map((m) => ({
            id: m.id,
            sender: m.role === 'user' ? 'user' : 'kyron',
            timestamp: new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            text: m.content,
            action: m.metadata?.action || null
          }));
          setMessages(loadedMsgs);
        } else {
          setMessages([
            {
              id: 'welcome-msg',
              sender: 'kyron',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              text: "Namaste Boss! I am KYRON, your hands-free AGI assistant. How can I assist you today?",
              action: null
            }
          ]);
        }
      }
    } catch (err) {
      console.error('Failed to load session details:', err);
    }
  };

  // Create a new conversation session
  const handleNewConversation = async () => {
    stopSpeaking();
    try {
      const res = await api.post('/api/kyron/sessions', { title: 'New Conversation' });
      if (res.data?.success && res.data.session) {
        const newSess = res.data.session;
        setSessions((prev) => [newSess, ...prev]);
        setActiveSessionId(newSess.id);
        setMessages([
          {
            id: `welcome-${Date.now()}`,
            sender: 'kyron',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            text: "Namaste Boss! I am KYRON, ready for a new conversation. What's on your mind?",
            action: null
          }
        ]);
        toast.success('Started new conversation');
      }
    } catch (e) {
      const tempId = `sess_${Date.now()}`;
      setActiveSessionId(tempId);
      setMessages([
        {
          id: `welcome-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: "Namaste Boss! I am KYRON, ready for a new conversation. What's on your mind?",
          action: null
        }
      ]);
    }
  };

  // Delete a conversation session
  const handleDeleteSession = async (sessionId, e) => {
    if (e) e.stopPropagation();
    try {
      await api.delete(`/api/kyron/sessions/${sessionId}`);
      const updated = sessions.filter((s) => s.id !== sessionId);
      setSessions(updated);
      toast.success('Conversation removed');
      if (activeSessionId === sessionId) {
        if (updated.length > 0) {
          selectSession(updated[0].id);
        } else {
          handleNewConversation();
        }
      }
    } catch (err) {
      toast.error('Failed to delete session');
    }
  };

  // Single greeting lock per session to prevent repeated "Good morning" spam
  const hasGreetedSessionRef = useRef(sessionStorage.getItem('kyron_has_greeted') === 'true');

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom of chat
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isProcessing]);

  // Audio interaction trigger to satisfy browser Autoplay Policy
  const enableAudioGesture = () => {
    if (!hasInteracted) {
      setHasInteracted(true);
      if ('speechSynthesis' in window) {
        window.speechSynthesis.resume();
      }
    }
  };

  // Initialize Hands-Free Voice Engine
  const {
    isListening,
    isSpeaking,
    isMuted,
    isWakeWordActive,
    liveTranscript,
    audioLevel,
    selectedLanguage,
    setVoiceLanguage,
    speak,
    stopSpeaking,
    toggleListening,
    toggleMute,
    activateVoice,
    triggerWakeup
  } = useKyronVoice({
    onDirectiveSubmit: (directive) => handleSendMessage(directive),
    onTranscriptChange: (liveSpeech) => {
      if (!isProcessing) {
        setInputText(liveSpeech);
      }
    },
    onStatusChange: () => {},
    onWake: (speakFn) => {
      enableAudioGesture();

      // Only greet ONCE per entire session - never repeat 'Good morning' in loops!
      if (!hasGreetedSessionRef.current) {
        hasGreetedSessionRef.current = true;
        try {
          sessionStorage.setItem('kyron_has_greeted', 'true');
        } catch (_) {}

        const hour = new Date().getHours();
        let timeOfDay = 'Morning';
        if (hour >= 12 && hour < 17) timeOfDay = 'Afternoon';
        else if (hour >= 17) timeOfDay = 'Evening';

        const greeting = `Good ${timeOfDay} Boss, bataye kya karni hai?`;

        setMessages((prev) => [
          ...prev,
          {
            id: `wake-${Date.now()}`,
            sender: 'kyron',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            text: greeting,
            isWakeGreeting: true
          }
        ]);

        if (speakFn) {
          speakFn(greeting);
        } else {
          speak(greeting);
        }
      } else {
        // Subsequent wakes: never speak "Good morning" repeatedly! Just notify & listen
        toast('Kyron active & listening...', { id: 'kyron-awake', icon: '🎙️', duration: 1500 });
      }
    }
  });

  // Global ESC key listener to immediately stop Kyron speaking if desired
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isSpeaking) {
        stopSpeaking();
        toast('Speech stopped', { id: 'tts-stopped', duration: 1000 });
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isSpeaking, stopSpeaking]);

  // Main submission handler
  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputText).trim();
    if (!text || isProcessing) return;

    enableAudioGesture();
    stopSpeaking();
    setInputText('');

    // Append User Message
    const userMsgId = `user-${Date.now()}`;
    const userMsg = {
      id: userMsgId,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsProcessing(true);

    try {
      const lower = text.toLowerCase();

      // 1. YouTube & Song playback intent (Hindi, Hinglish & English)
      const hasSong =
        lower.includes('song') ||
        lower.includes('gana') ||
        lower.includes('gaana') ||
        lower.includes('music') ||
        lower.includes('गाना') ||
        lower.includes('सॉन्ग') ||
        lower.includes('म्यूजिक');

      const hasAction =
        lower.includes('banao') ||
        lower.includes('chalao') ||
        lower.includes('play') ||
        lower.includes('sunao') ||
        lower.includes('lagao') ||
        lower.includes('bajao') ||
        lower.includes('open') ||
        lower.includes('बनाओ') ||
        lower.includes('चलाओ') ||
        lower.includes('बजाओ') ||
        lower.includes('सुनाओ');

      if ((hasSong && hasAction) || (hasSong && lower.split(' ').length <= 4)) {
        const replyText = "Opening Chrome and playing a song for you on YouTube right now, Boss!";
        
        // Frontend backup open in case backend popup is blocked
        setTimeout(() => {
          try {
            window.open('https://www.youtube.com/watch?v=jfKfPfyJRdk', '_blank');
          } catch (_) {}
        }, 600);

        // Also notify backend
        try {
          await api.post('/api/kyron/chat', { message: text });
        } catch (_) {}

        setMessages((prev) => [
          ...prev,
          {
            id: `resp-${Date.now()}`,
            sender: 'kyron',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            text: replyText,
            action: {
              type: 'media_play',
              title: 'YouTube Music Stream',
              url: 'https://www.youtube.com/watch?v=jfKfPfyJRdk'
            }
          }
        ]);

        speak(replyText);
        return;
      }

      // 2. CodeAgent bug diagnosis intent
      if (
        lower.includes('pricing') ||
        lower.includes('flat deduction') ||
        (lower.includes('fix') && (lower.includes('bug') || lower.includes('code')))
      ) {
        toast.loading('Analyzing codebase in isolated sandbox...', { id: 'code-audit' });
        try {
          const res = await api.post('/api/kyron/code-agent/run', {
            instruction: text,
            target_file: 'services/pricing.py'
          });

          toast.dismiss('code-audit');
          const data = res.data;

          if (data && data.diff) {
            const replyMsg = `I have analyzed the pricing calculation bug in \`services/pricing.py\` and generated an autonomous dry-run fix. You can review the diff below and approve it to commit to disk.`;
            setMessages((prev) => [
              ...prev,
              {
                id: `resp-${Date.now()}`,
                sender: 'kyron',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                text: replyMsg,
                action: {
                  type: 'diff_review',
                  diffData: data
                }
              }
            ]);
            speak("I have analyzed the pricing bug and created a dry-run fix. Please review the diff in the chat.");
            return;
          }
        } catch (e) {
          toast.dismiss('code-audit');
        }
      }

      // 3. General conversational chat (routed through Hermes / Kyron backend)
      const chatRes = await api.post('/api/kyron/chat', {
        message: text,
        language: 'en',
        session_id: activeSessionId
      });

      const reply =
        chatRes.data?.reply ||
        chatRes.data?.text ||
        chatRes.data?.response ||
        'Directive acknowledged and processed by KYRON.';

      const actionData = chatRes.data?.action;

      if (chatRes.data?.session_id) {
        const returnedSid = chatRes.data.session_id;
        const returnedTitle = chatRes.data.session_title;
        setActiveSessionId(returnedSid);
        setSessions((prev) => {
          const idx = prev.findIndex((s) => s.id === returnedSid);
          if (idx >= 0) {
            const updated = [...prev];
            updated[idx] = {
              ...updated[idx],
              title: returnedTitle || updated[idx].title,
              updated_at: new Date().toISOString(),
              message_count: (updated[idx].message_count || 0) + 2
            };
            return updated;
          } else {
            return [
              {
                id: returnedSid,
                title: returnedTitle || 'New Conversation',
                updated_at: new Date().toISOString(),
                message_count: 2
              },
              ...prev
            ];
          }
        });
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `resp-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: reply,
          action: actionData
        }
      ]);

      const spokenText = chatRes.data?.voice_vocalization || reply;
      speak(spokenText);
    } catch (err) {
      console.error('Chat error:', err);
      const fallbackReply = `Haan Boss, '${text}' samajh gaya. Bataye ispe kya action execute karni hai?`;
      setMessages((prev) => [
        ...prev,
        {
          id: `resp-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: fallbackReply
        }
      ]);
      speak(fallbackReply);
    } finally {
      setIsProcessing(false);
    }
  };

  const copyMessage = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clearChat = () => {
    stopSpeaking();
    setMessages([
      {
        id: `sys-${Date.now()}`,
        sender: 'kyron',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: "Chat cleared. I'm listening Boss! Say 'Hey Kyron' or speak anytime."
      }
    ]);
    toast.success('Conversation cleared');
  };

  // Quick prompt suggestions
  const suggestions = [
    {
      title: "https://www.bookmygadi.app/ form bharo",
      desc: "Autonomously opens Chrome & fills cab booking forms",
      icon: <Globe className="w-4 h-4 text-cyan-400" />
    },
    {
      title: "Mere liye song banao",
      desc: "Opens Chrome and plays trending songs on YouTube",
      icon: <Music className="w-4 h-4 text-emerald-400" />
    },
    {
      title: "Diagnose BookMyGaadi pricing bug",
      desc: "Runs autonomous CodeAgent dry-run fix in sandbox",
      icon: <FileCode className="w-4 h-4 text-cyan-400" />
    },
    {
      title: "Remember my preferences",
      desc: "Stores context into Hermes episodic memory",
      icon: <Zap className="w-4 h-4 text-amber-400" />
    },
    {
      title: "What capabilities do you have?",
      desc: "Lists all registered skills & system integrations",
      icon: <Sparkles className="w-4 h-4 text-purple-400" />
    }
  ];

  return (
    <div
      onClick={enableAudioGesture}
      className="flex h-screen w-screen bg-[#0b0f17] text-slate-100 font-sans overflow-hidden select-none"
    >
      {/* ======================================================== */}
      {/* 1. CLAUDE / CHATGPT STYLE SIDEBAR                        */}
      {/* ======================================================== */}
      <AnimatePresence initial={false}>
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="h-full bg-[#0e131f] border-r border-slate-800/80 flex flex-col z-30 shrink-0 select-none overflow-hidden"
          >
            {/* Brand Logo & New Chat */}
            <div className="p-4 border-b border-slate-800/80 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-900/30">
                    <Sparkles className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h1 className="font-bold text-sm tracking-wide text-white">KYRON</h1>
                    <span className="text-[10px] text-cyan-400 font-medium">AGI Autonomous Voice</span>
                  </div>
                </div>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
                  title="Close sidebar"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* New Chat Button */}
              <button
                onClick={handleNewConversation}
                className="w-full flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl bg-gradient-to-r from-cyan-600/20 to-indigo-600/20 hover:from-cyan-600/30 hover:to-indigo-600/30 border border-cyan-500/30 text-cyan-200 text-xs font-medium transition shadow-sm"
              >
                <Plus className="w-4 h-4" />
                <span>New Conversation</span>
              </button>
            </div>

            {/* Workspace Switcher */}
            <div className="px-3 py-2.5 border-b border-slate-800/60 shrink-0">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-2 mb-1.5 block">
                Workspaces
              </span>
              <div className="space-y-1">
                {[
                  { id: 'kyron', label: 'Kyron Voice Chat', icon: <Bot className="w-4 h-4 text-cyan-400" /> },
                  { id: 'munder', label: 'Munder Difflin', icon: <Code2 className="w-4 h-4 text-indigo-400" /> },
                  { id: 'bmg', label: 'BMG Management', icon: <Layers className="w-4 h-4 text-emerald-400" /> }
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handlePanelChange(item.id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-1.5 rounded-xl text-xs font-medium transition ${
                      activePanel === item.id
                        ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* ChatGPT / Claude Style Persistent Sessions List */}
            <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 custom-scrollbar border-b border-slate-800/60 min-h-[140px]">
              <div className="flex items-center justify-between px-2 mb-1.5">
                <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                  Chats ({sessions.length})
                </span>
                <button
                  onClick={handleNewConversation}
                  className="p-1 rounded text-slate-400 hover:text-cyan-300 hover:bg-slate-800 transition"
                  title="New conversation"
                >
                  <Plus className="w-3.5 h-3.5" />
                </button>
              </div>

              {loadingSessions && sessions.length === 0 ? (
                <div className="px-3 py-4 text-center text-xs text-slate-500 animate-pulse">
                  Loading chats...
                </div>
              ) : sessions.length === 0 ? (
                <div className="px-3 py-3 text-center text-[11px] text-slate-500">
                  No previous conversations
                </div>
              ) : (
                sessions.map((sess) => {
                  const isActive = activeSessionId === sess.id;
                  return (
                    <div
                      key={sess.id}
                      onClick={() => selectSession(sess.id)}
                      className={`group relative flex items-center justify-between px-2.5 py-2 rounded-xl text-xs cursor-pointer transition ${
                        isActive
                          ? 'bg-gradient-to-r from-cyan-950/60 to-indigo-950/40 text-cyan-200 border border-cyan-500/40 shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                      }`}
                    >
                      <div className="flex items-center gap-2 overflow-hidden flex-1 mr-1">
                        <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-400'}`} />
                        <span className="truncate font-medium">{sess.title || 'New Conversation'}</span>
                      </div>
                      <button
                        onClick={(e) => handleDeleteSession(sess.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-rose-500/20 hover:text-rose-400 text-slate-500 transition shrink-0"
                        title="Delete conversation"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })
              )}
            </div>

            {/* Quick Voice Directives */}
            <div className="max-h-48 overflow-y-auto px-3 py-2 space-y-1 custom-scrollbar shrink-0">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-2 mb-1.5 block">
                Voice Prompts
              </span>
              {suggestions.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(item.title)}
                  className="w-full text-left p-2 rounded-xl border border-slate-800/40 bg-slate-900/30 hover:bg-slate-800/60 hover:border-slate-700 transition group"
                >
                  <div className="flex items-center gap-2 text-xs font-medium text-slate-300 group-hover:text-cyan-300">
                    {item.icon}
                    <span className="truncate">{item.title}</span>
                  </div>
                </button>
              ))}
            </div>

            {/* Status Footer */}
            <div className="p-3 border-t border-slate-800/80 bg-[#0b0f17]/60 flex items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-2">
                <span className="relative flex h-2 w-2">
                  <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isListening ? 'bg-rose-400' : 'bg-emerald-400'} opacity-75`}></span>
                  <span className={`relative inline-flex rounded-full h-2 w-2 ${isListening ? 'bg-rose-500' : 'bg-emerald-500'}`}></span>
                </span>
                <span className="text-[11px]">{isListening ? 'Voice Armed' : 'Voice Ready'}</span>
              </div>
              <button
                onClick={clearChat}
                className="p-1.5 rounded-lg hover:text-rose-400 hover:bg-slate-800 transition"
                title="Clear current chat"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* ======================================================== */}
      {/* 2. WORKSPACE PANEL (Munder Difflin or BMG)               */}
      {/* ======================================================== */}
      {activePanel === 'munder' ? (
        <div className="flex-1 h-full overflow-hidden">
          <MunderDifflinPanel />
        </div>
      ) : activePanel === 'bmg' ? (
        <div className="flex-1 h-full overflow-hidden">
          <BMGManagementPanel />
        </div>
      ) : (
        /* ======================================================== */
        /* 3. MAIN CHATGPT / CLAUDE CONVERSATIONAL CHAT CONTAINER   */
        /* ======================================================== */
        <main className="flex-1 flex flex-col h-full bg-[#0b0f17] relative overflow-hidden">
          {/* Top Header Bar */}
          <header className="h-14 border-b border-slate-800/60 bg-[#0e131f]/80 backdrop-blur-md flex items-center justify-between px-4 z-20 shrink-0">
            <div className="flex items-center gap-3">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
                  title="Open sidebar"
                >
                  <Menu className="w-5 h-5" />
                </button>
              )}

              {/* Model Badge */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-xs font-semibold text-slate-200">KYRON 2.0</span>
                <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                  Voice AGI
                </span>
              </div>
            </div>

            {/* Wake Status & Wispr Voice Pill Controls */}
            <div className="flex items-center gap-2 sm:gap-3">
              {/* Wispr Live Audio Energy Level Bar */}
              <div
                onClick={triggerWakeup}
                className="cursor-pointer flex items-center gap-2 px-3 py-1.5 rounded-xl bg-cyan-950/40 border border-cyan-500/40 text-cyan-300 text-xs transition hover:bg-cyan-900/50 shadow-sm"
                title="Wispr Flow Sensitivity Active. Click to wake or say 'Hey Kyron' / Clap"
              >
                {/* 4-bar dynamic audio equalizer */}
                <div className="flex items-end gap-0.5 h-3.5 w-4">
                  <span
                    className="w-1 bg-cyan-400 rounded-full transition-all duration-75"
                    style={{ height: `${Math.max(3, (audioLevel * 14) / 100)}px` }}
                  />
                  <span
                    className="w-1 bg-emerald-400 rounded-full transition-all duration-75"
                    style={{ height: `${Math.max(4, (audioLevel * 18) / 100)}px` }}
                  />
                  <span
                    className="w-1 bg-cyan-400 rounded-full transition-all duration-75"
                    style={{ height: `${Math.max(2, (audioLevel * 12) / 100)}px` }}
                  />
                </div>
                <span className="hidden md:inline font-mono text-[11px] font-medium">
                  {isWakeWordActive ? '🔥 Awake & Listening' : 'Wispr Mic: "Hey Kyron"'}
                </span>
              </div>

              {/* Mic Toggle Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleListening();
                }}
                className={`p-2 rounded-xl border text-xs flex items-center gap-1.5 transition ${
                  isListening
                    ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300 shadow-[0_0_12px_rgba(16,185,129,0.3)]'
                    : 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-slate-200'
                }`}
                title={isListening ? 'Click to Pause Mic' : 'Click to Turn Mic ON'}
              >
                {isListening ? (
                  <>
                    <Mic className="w-4 h-4 text-emerald-400 animate-pulse" />
                    <span className="hidden sm:inline text-xs font-semibold text-emerald-300">
                      Mic Active
                    </span>
                  </>
                ) : (
                  <>
                    <MicOff className="w-4 h-4 text-slate-400" />
                    <span className="hidden sm:inline text-xs font-medium text-slate-400">
                      Mic Off
                    </span>
                  </>
                )}
              </button>

              {/* Language Switcher */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  const nextLang = selectedLanguage === 'hi-IN' ? 'en-IN' : 'hi-IN';
                  setVoiceLanguage(nextLang);
                  toast.success(nextLang === 'hi-IN' ? 'Listening in 🇮🇳 Hindi / Hinglish' : 'Listening in 🌐 English');
                }}
                className="hidden sm:flex items-center gap-1.5 px-2.5 py-2 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs text-slate-300 hover:text-white transition"
                title="Toggle Speech Recognition language between Hindi/Hinglish and English"
              >
                <span>{selectedLanguage === 'hi-IN' ? '🇮🇳 Hindi' : '🌐 English'}</span>
              </button>

              {/* Speaker Test Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  enableAudioGesture();
                  speak("Namaste Boss! Kyron audio is working loud and clear.");
                  toast.success("Playing speaker test...");
                }}
                className="p-2 rounded-xl border bg-slate-800/80 border-slate-700/80 text-xs text-cyan-400 hover:text-cyan-300 hover:border-cyan-500/40 transition"
                title="Test Kyron Speaker Sound"
              >
                <Volume2 className="w-4 h-4 text-cyan-400" />
              </button>

              {/* Mute TTS Speaker Toggle */}
              <button
                onClick={toggleMute}
                className={`p-2 rounded-xl border transition ${
                  isMuted
                    ? 'bg-slate-800/50 border-slate-700 text-slate-500'
                    : 'bg-indigo-950/40 border-indigo-500/40 text-indigo-300 hover:text-white'
                }`}
                title={isMuted ? 'Voice is muted' : 'Voice is active'}
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>

              {/* Instant Stop Speaking Button (Active when Kyron is talking) */}
              {isSpeaking && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    stopSpeaking();
                    toast('Speech stopped', { id: 'tts-stopped', duration: 1000 });
                  }}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/20 border border-rose-500/50 text-rose-300 text-xs font-semibold hover:bg-rose-500/30 transition animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.3)]"
                  title="Click to stop Kyron speaking immediately (or press ESC)"
                >
                  <VolumeX className="w-4 h-4 text-rose-400" />
                  <span className="hidden sm:inline">Stop (ESC)</span>
                </button>
              )}
            </div>
          </header>

          {/* Messages Scroll Area */}
          <div className="flex-1 overflow-y-auto px-4 py-6 custom-scrollbar select-text">
            <div className="max-w-3xl mx-auto space-y-6">
              {/* Welcome Screen if only 1 message */}
              {messages.length === 1 && (
                <div className="py-12 flex flex-col items-center text-center">
                  <div
                    onClick={triggerWakeup}
                    className="relative cursor-pointer group mb-4"
                    title="Click to wake Kyron immediately!"
                  >
                    <div className="w-20 h-20 rounded-full bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-cyan-500/40 group-hover:scale-105 transition-all">
                      <Sparkles className="w-10 h-10 text-white animate-pulse" />
                    </div>
                    {isListening && (
                      <span className="absolute -inset-2 rounded-full border-2 border-cyan-400/40 animate-ping pointer-events-none"></span>
                    )}
                  </div>
                  <h2 className="text-xl sm:text-2xl font-bold text-white mb-2">
                    How can I assist you today, Boss?
                  </h2>
                  <p className="text-xs sm:text-sm text-slate-400 max-w-md mb-4">
                    Say <span className="text-cyan-300 font-semibold">"Hey Kyron"</span>, clap your hands, or speak your request directly. I can play songs on YouTube, fix code bugs, and manage your tasks.
                  </p>

                  {/* Immediate Action Buttons */}
                  <div className="flex items-center gap-3 mb-8">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleListening();
                      }}
                      className={`flex items-center gap-2 px-5 py-2.5 rounded-2xl font-bold text-xs shadow-lg transition ${
                        isListening
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 shadow-emerald-900/20'
                          : 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 shadow-emerald-500/30 animate-pulse'
                      }`}
                    >
                      {isListening ? (
                        <>
                          <Mic className="w-4 h-4 text-emerald-400 animate-pulse" />
                          <span>🟢 Mic Online (Say "Hey Kyron" or speak)</span>
                        </>
                      ) : (
                        <>
                          <MicOff className="w-4 h-4" />
                          <span>▶️ Click to Turn Mic ON</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        triggerWakeup();
                      }}
                      className="flex items-center gap-2 px-5 py-2.5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-cyan-300 font-semibold text-xs border border-slate-700 transition shadow-sm"
                    >
                      <Sparkles className="w-4 h-4 text-cyan-400" />
                      <span>Wake Kyron Now</span>
                    </button>
                  </div>

                  {/* Suggestion Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                    {suggestions.map((card, i) => (
                      <button
                        key={i}
                        onClick={() => handleSendMessage(card.title)}
                        className="text-left p-3.5 rounded-2xl bg-slate-900/60 hover:bg-slate-800/80 border border-slate-800 hover:border-cyan-500/40 transition group shadow-sm"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          {card.icon}
                          <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300">
                            {card.title}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">{card.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Message History List */}
              {messages.map((msg) => {
                const isUser = msg.sender === 'user';
                return (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                    className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    {/* Kyron Avatar on Left */}
                    {!isUser && (
                      <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md shadow-cyan-900/20 mt-0.5">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                    )}

                    {/* Message Bubble Container */}
                    <div className={`max-w-[85%] sm:max-w-[75%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                      {/* Message Content */}
                      <div
                        className={`rounded-2xl px-4 py-3 text-xs sm:text-sm leading-relaxed ${
                          isUser
                            ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-950/30'
                            : 'bg-[#141b2a] border border-slate-800 text-slate-200 shadow-md'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.text}</p>

                        {/* Interactive Media Action Card (YouTube) */}
                        {msg.action?.type === 'media_play' && (
                          <div className="mt-3 p-3 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex items-center justify-between gap-3">
                            <div className="flex items-center gap-2.5">
                              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                                <Music className="w-4 h-4 text-emerald-400 animate-bounce" />
                              </div>
                              <div>
                                <span className="text-xs font-semibold text-emerald-300 block">
                                  Playing on YouTube Chrome
                                </span>
                                <span className="text-[10px] text-slate-400">Stream opened in browser</span>
                              </div>
                            </div>
                            <a
                              href={msg.action.url}
                              target="_blank"
                              rel="noreferrer"
                              className="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-xs font-medium flex items-center gap-1 transition"
                            >
                              <span>Open YT</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        )}

                        {/* Interactive Chrome Browser Automation Card */}
                        {msg.action?.type === 'browser_open' && (
                          <div className="mt-3 p-3.5 rounded-xl bg-slate-900/90 border border-cyan-500/40 shadow-lg shadow-cyan-950/20">
                            <div className="flex items-center justify-between gap-3 mb-2">
                              <div className="flex items-center gap-2.5">
                                <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center border border-cyan-500/30">
                                  <Globe className="w-4 h-4 text-cyan-400 animate-pulse" />
                                </div>
                                <div>
                                  <span className="text-xs font-semibold text-cyan-300 block">
                                    {msg.action.title || 'Chrome Browser Automation Active'}
                                  </span>
                                  <span className="text-[10px] text-slate-400 font-mono">
                                    {msg.action.url}
                                  </span>
                                </div>
                              </div>
                              <a
                                href={msg.action.url}
                                target="_blank"
                                rel="noreferrer"
                                className="px-3 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 text-xs font-medium flex items-center gap-1.5 transition border border-cyan-500/30 hover:border-cyan-400/50"
                              >
                                <span>View Live Site</span>
                                <ExternalLink className="w-3 h-3" />
                              </a>
                            </div>
                            <div className="flex items-center gap-2 text-[10px] text-slate-400 pt-2 border-t border-slate-800">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                              <span>Playwright Agent active & ready to autofill form fields on directive.</span>
                            </div>
                          </div>
                        )}

                        {/* Interactive Code Diff Review Card */}
                        {msg.action?.type === 'diff_review' && (
                          <div className="mt-3">
                            <DiffCard
                              targetFile={msg.action.diffData.target_file || 'services/pricing.py'}
                              diff={msg.action.diffData.diff}
                              iteration={1}
                              applied={msg.action.diffData.applied}
                              onApply={async () => {
                                try {
                                  await api.post('/api/kyron/code-agent/run', {
                                    ...msg.action.diffData,
                                    apply: true
                                  });
                                  toast.success('Fix applied to disk!');
                                  speak('Fix successfully committed to disk, Boss!');
                                } catch (_) {
                                  toast.error('Failed to commit fix');
                                }
                              }}
                              onReject={() => toast('Fix discarded')}
                            />
                          </div>
                        )}
                      </div>

                      {/* Action Bar Below Message */}
                      <div className="flex items-center gap-2 mt-1 px-1 text-[10px] text-slate-400">
                        <span>{msg.timestamp}</span>
                        {!isUser && (
                          <>
                            <button
                              onClick={() => speak(msg.text)}
                              className="hover:text-cyan-400 transition flex items-center gap-0.5"
                              title="Listen to response"
                            >
                              <Volume2 className="w-3 h-3" />
                              <span>Listen</span>
                            </button>
                            <button
                              onClick={() => copyMessage(msg.id, msg.text)}
                              className="hover:text-cyan-400 transition flex items-center gap-0.5"
                              title="Copy text"
                            >
                              {copiedId === msg.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                              <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                            </button>
                          </>
                        )}
                      </div>
                    </div>

                    {/* User Avatar on Right */}
                    {isUser && (
                      <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                        <User className="w-4 h-4 text-slate-300" />
                      </div>
                    )}
                  </motion.div>
                );
              })}

              {/* Processing / Thinking State */}
              {isProcessing && (
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-cyan-600 flex items-center justify-center shrink-0 animate-pulse">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="p-3 rounded-2xl bg-[#141b2a] border border-slate-800 text-xs text-cyan-300 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    <span>KYRON is thinking & preparing action...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* ======================================================== */}
          {/* 4. LIVE TRANSCRIPT PILL (FLOATING ABOVE INPUT)            */}
          {/* ======================================================== */}
          <AnimatePresence>
            {liveTranscript && (
              <motion.div
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                className="max-w-xl mx-auto w-full px-4 mb-2 z-10"
              >
                <div className="p-3 rounded-2xl bg-cyan-950/80 border border-cyan-500/50 backdrop-blur-xl shadow-xl shadow-cyan-950/40 flex items-center gap-3">
                  {/* Soundwave animation */}
                  <div className="flex items-center gap-0.5 h-4">
                    <span className="w-1 bg-cyan-400 rounded-full animate-[bounce_0.8s_infinite_100ms] h-3"></span>
                    <span className="w-1 bg-cyan-400 rounded-full animate-[bounce_0.8s_infinite_200ms] h-4"></span>
                    <span className="w-1 bg-cyan-400 rounded-full animate-[bounce_0.8s_infinite_300ms] h-2"></span>
                    <span className="w-1 bg-cyan-400 rounded-full animate-[bounce_0.8s_infinite_400ms] h-4"></span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider block">
                      Live Voice Transcript (VAD Auto-Submit)
                    </span>
                    <p className="text-xs sm:text-sm font-medium text-white truncate">
                      "{liveTranscript}"
                    </p>
                  </div>
                  <button
                    onClick={() => handleSendMessage(liveTranscript)}
                    className="px-2.5 py-1 rounded-lg bg-cyan-500 text-slate-950 font-semibold text-xs hover:bg-cyan-400 transition shrink-0"
                  >
                    Send Now
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ======================================================== */}
          {/* 5. BOTTOM INPUT BAR (CHATGPT / CLAUDE STYLE)             */}
          {/* ======================================================== */}
          <div className="shrink-0 p-4 bg-gradient-to-t from-[#0b0f17] via-[#0b0f17] to-transparent">
            <div className="max-w-3xl mx-auto">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className={`relative flex items-center rounded-2xl bg-[#141b2a] border transition-all ${
                  isListening && inputText
                    ? 'border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.35)] ring-1 ring-cyan-400/50'
                    : 'border-slate-700/80 focus-within:border-cyan-500/60 shadow-xl'
                }`}
              >
                {/* Voice Listener Trigger */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleListening();
                  }}
                  className={`p-3 rounded-l-2xl transition ${
                    isListening
                      ? 'text-emerald-400 bg-emerald-500/10'
                      : 'text-slate-400 hover:text-cyan-400'
                  }`}
                  title={isListening ? 'Mic Active: Click to pause' : 'Click to turn mic ON or speak'}
                >
                  {isListening ? (
                    <Mic className="w-5 h-5 text-emerald-400 animate-pulse" />
                  ) : (
                    <MicOff className="w-5 h-5" />
                  )}
                </button>

                {/* Input Text Area */}
                <input
                  ref={inputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={
                    isListening
                      ? 'Boliye... jo bolenge yahan real-time type hoga aur silence pe auto-send ho jayega...'
                      : 'Ask Kyron anything or say "Hey Kyron"...'
                  }
                  disabled={isProcessing}
                  className="flex-1 bg-transparent py-3.5 px-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none"
                />

                {/* Live Dictation Auto-Send Badge */}
                {isListening && inputText && (
                  <span className="hidden sm:inline text-[10px] font-mono text-cyan-400 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30 animate-pulse mr-2">
                    Auto-send on silence
                  </span>
                )}

                {/* Submit Send Button */}
                <button
                  type="submit"
                  disabled={!inputText.trim() || isProcessing}
                  className={`p-2.5 mr-2 rounded-xl transition ${
                    inputText.trim() && !isProcessing
                      ? 'bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-900/40 hover:opacity-90'
                      : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>

              {/* Minimal Hint */}
              <div className="flex items-center justify-between mt-2 px-1 text-[11px] text-slate-400">
                <span>Wake: <strong className="text-cyan-300">"Hey Kyron"</strong> or 👏 <strong>Clap</strong></span>
                <span>Supports natural Hindi, Hinglish & English</span>
              </div>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
