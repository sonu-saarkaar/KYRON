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
  MessageSquare,
  MessageCircle,
  Eye,
  Instagram,
  Monitor,
  Sidebar,
  CloudLightning,
  PhoneCall,
  Brain
} from 'lucide-react';
import toast from 'react-hot-toast';

import { useKyronVoice } from '../../hooks/useKyronVoice';
import api, { socialAPI } from '../../services/api';
import MunderDifflinPanel from '../../components/MunderDifflinPanel';
import BMGManagementPanel from '../../components/BMGManagementPanel';
import { DiffCard, ActionPreviewCard } from '../../components/Jarvis/MissionCards';

// Mac Components
import MacMenuBar from '../../components/Mac/MacMenuBar';
import MacScreenMirror from '../../components/Mac/MacScreenMirror';
import MacUserProfileCard from '../../components/Mac/MacUserProfileCard';
import MacTaskOverviewCard from '../../components/Mac/MacTaskOverviewCard';
import MacSystemHealthCard from '../../components/Mac/MacSystemHealthCard';
import MacBossProfileCard from '../../components/Mac/MacBossProfileCard';
import MacWorkStatsCard from '../../components/Mac/MacWorkStatsCard';
import MacTaskHistoryCard from '../../components/Mac/MacTaskHistoryCard';
import MacSocialCard from '../../components/Mac/MacSocialCard';
import MacOBGListener from '../../components/Mac/MacOBGListener';
import NvidiaBrevCard from '../../components/Mac/NvidiaBrevCard';
import MacSystemStatusCard from '../../components/Mac/MacSystemStatusCard';
import MacPersonalizePanel from '../../components/Mac/MacPersonalizePanel';
import MacCallSupportPanel from '../../components/Mac/MacCallSupportPanel';
import MacCallingSetupSidebar from '../../components/Mac/MacCallingSetupSidebar';
import MacChromeFooterHUD from '../../components/Mac/MacChromeFooterHUD';

export default function Chat() {
  const { panel } = useParams();
  const navigate = useNavigate();

  // Active workspace: 'kyron' (Kyron AGI Workshop) | 'munder' (Best Coding Agent) | 'call_support' (Real Calling Agent)
  const activePanel = panel || 'kyron';
  const handlePanelChange = (newPanel) => {
    navigate(`/chat/${newPanel}`);
  };

  const [showPersonalizeModal, setShowPersonalizeModal] = useState(false);

  // macOS Workstation panels visibility
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mirrorOpen, setMirrorOpen] = useState(true);
  const [showNvidiaBrev, setShowNvidiaBrev] = useState(false);

  // Window focus & Desktop external app tracking
  const [isWindowFocused, setIsWindowFocused] = useState(true);
  const [hudDismissed, setHudDismissed] = useState(false);
  const [hudForceVisible, setHudForceVisible] = useState(false);

  // Autonomous Google Chrome Footer HUD state
  const [chromeHudDismissed, setChromeHudDismissed] = useState(false);
  const [chromeHudForceVisible, setChromeHudForceVisible] = useState(false);

  useEffect(() => {
    const handleFocus = () => setIsWindowFocused(true);
    const handleBlur = () => {
      setIsWindowFocused(false);
      setHudDismissed(false);
      setChromeHudDismissed(false);
    };
    const handleVisibility = () => {
      const isVisible = !document.hidden;
      setIsWindowFocused(isVisible);
      if (!isVisible) {
        setHudDismissed(false);
        setChromeHudDismissed(false);
      }
    };

    window.addEventListener('focus', handleFocus);
    window.addEventListener('blur', handleBlur);
    document.addEventListener('visibilitychange', handleVisibility);

    return () => {
      window.removeEventListener('focus', handleFocus);
      window.removeEventListener('blur', handleBlur);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, []);

  // Social & Mirror State (kitna kaam kia, steps, ONJ, chats, dms)
  const [mirrorState, setMirrorState] = useState(null);

  // Fetch live mirror state periodically and on mount
  const refreshMirrorState = async () => {
    try {
      const data = await socialAPI.getState();
      if (data && data.success) {
        setMirrorState(data);
      }
    } catch (e) {
      console.debug('Error refreshing mirror state:', e);
    }
  };

  useEffect(() => {
    refreshMirrorState();
    const interval = setInterval(refreshMirrorState, 5000);
    return () => clearInterval(interval);
  }, []);

  // Chat message stream
  const [messages, setMessages] = useState([
    {
      id: 'welcome-msg',
      sender: 'kyron',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text: "Namaste Boss! I am KYRON, your hands-free macOS AGI assistant. Speak naturally or say **'Hey Kyron'** / Clap. WhatsApp peeking, smart memory replies, Instagram auto-responses, and Chrome mirror are all active.",
      action: null
    }
  ]);

  const [inputText, setInputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const isProcessingRef = useRef(false);
  const [copiedId, setCopiedId] = useState(null);
  const [hasInteracted, setHasInteracted] = useState(false);

  // Persistent Sessions state
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loadingSessions, setLoadingSessions] = useState(false);

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

  const parseMessageAction = (m) => {
    if (!m.metadata) return null;
    if (typeof m.metadata.action === 'object' && m.metadata.action !== null) {
      return m.metadata.action;
    }
    if (typeof m.metadata.action === 'string') {
      return {
        action: m.metadata.action,
        actionName: m.metadata.actionName || m.metadata.action,
        result: m.metadata.result || {},
        type: m.metadata.action.toLowerCase()
      };
    }
    if (m.metadata.action_data) {
      return m.metadata.action_data;
    }
    return null;
  };

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
            action: parseMessageAction(m)
          }));
          setMessages(loadedMsgs);
        } else {
          setMessages([
            {
              id: 'welcome-msg',
              sender: 'kyron',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              text: "Namaste Boss! I am KYRON, ready to assist you. What shall we automate today?",
              action: null
            }
          ]);
        }
      }
    } catch (err) {
      console.error('Failed to load session details:', err);
    }
  };

  // Live Chat & Voice Activity Sync (mirrors background speech, terminal runs, hardware voice into Chat room in real time)
  const syncSessionMessages = async () => {
    let targetSessionId = activeSessionId;
    if (!targetSessionId) {
      try {
        const activeRes = await api.get('/api/kyron/sessions/active');
        if (activeRes.data?.success && activeRes.data.active_session_id) {
          targetSessionId = activeRes.data.active_session_id;
          setActiveSessionId(targetSessionId);
        }
      } catch (_) {
        return;
      }
    }
    if (!targetSessionId) return;

    try {
      const res = await api.get(`/api/kyron/sessions/${targetSessionId}`);
      if (res.data?.success && res.data.session) {
        const sess = res.data.session;
        if (sess.messages && sess.messages.length > 0) {
          setMessages((prev) => {
            const existingIds = new Set(prev.map((m) => m.id));
            const existingContentKeys = new Set(prev.map((m) => `${m.sender}:::${m.text.trim()}`));

            const newFromDb = sess.messages.filter((m) => {
              if (existingIds.has(m.id)) return false;
              const senderKey = m.role === 'user' ? 'user' : 'kyron';
              if (existingContentKeys.has(`${senderKey}:::${m.content.trim()}`)) return false;
              return true;
            });

            if (newFromDb.length === 0) return prev;

            const formattedNew = newFromDb.map((m) => ({
              id: m.id,
              sender: m.role === 'user' ? 'user' : 'kyron',
              timestamp: new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              text: m.content,
              action: parseMessageAction(m)
            }));

            return [...prev, ...formattedNew];
          });
        }
      }
    } catch (_) {}
  };

  useEffect(() => {
    const syncInterval = setInterval(syncSessionMessages, 1500);
    return () => clearInterval(syncInterval);
  }, [activeSessionId]);

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
            text: "Namaste Boss! Started a fresh conversation. How can I assist you?",
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
          text: "Namaste Boss! Started a fresh conversation. How can I assist you?",
          action: null
        }
      ]);
    }
  };

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

  const hasGreetedSessionRef = useRef(sessionStorage.getItem('kyron_has_greeted') === 'true');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isProcessing]);

  const enableAudioGesture = () => {
    if (!hasInteracted) {
      setHasInteracted(true);
      if ('speechSynthesis' in window) {
        window.speechSynthesis.resume();
      }
    }
  };

  // Hands-Free Voice Engine
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
    triggerWakeup,
    notifyAssistantSpeaking
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
      const hour = new Date().getHours();
      let timeOfDay = 'Morning';
      if (hour >= 12 && hour < 17) timeOfDay = 'Afternoon';
      else if (hour >= 17) timeOfDay = 'Evening';

      const greeting = `Good ${timeOfDay} Boss, bataye kya karni hai?`;

      if (!hasGreetedSessionRef.current) {
        hasGreetedSessionRef.current = true;
        try {
          sessionStorage.setItem('kyron_has_greeted', 'true');
        } catch (_) {}

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

        notifyAssistantSpeaking(greeting, 2800);
        api.post('/api/dograh/speak', { text: greeting }).catch(() => {
          if (speakFn) speakFn(greeting);
          else speak(greeting);
        });
      } else {
        const ack = "Haan Boss, bataye kya karni hai?";
        setMessages((prev) => [
          ...prev,
          {
            id: `wake-${Date.now()}`,
            sender: 'kyron',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            text: ack,
            isWakeGreeting: true
          }
        ]);
        notifyAssistantSpeaking(ack, 2200);
        api.post('/api/dograh/speak', { text: ack }).catch(() => {
          if (speakFn) speakFn(ack);
          else speak(ack);
        });
      }
    }
  });

  // ESC key listener to immediately stop Kyron speaking
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        stopSpeaking();
        api.post('/api/dograh/stop').catch(() => {});
        toast('Speech stopped', { id: 'tts-stopped', duration: 1000 });
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [stopSpeaking]);

  // Social direct triggers
  const handleOpenWhatsApp = async () => {
    enableAudioGesture();
    setIsProcessing(true);
    toast.loading('Launching WhatsApp on macOS desktop...', { id: 'social-run' });
    try {
      const res = await socialAPI.openWhatsApp();
      toast.dismiss('social-run');
      setMirrorState(res.mirror_state || mirrorState);
      
      setMessages((prev) => [
        ...prev,
        {
          id: `wa-open-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: res.voice_vocalization,
          action: {
            action: 'WHATSAPP_OPENED',
            type: 'whatsapp_opened',
            result: res
          }
        }
      ]);
      notifyAssistantSpeaking(res.voice_vocalization);
    } catch (e) {
      toast.dismiss('social-run');
      toast.error('Failed to open WhatsApp');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSearchAndSendWhatsApp = async (contact = 'Sonu', message = 'Hi Sonu') => {
    enableAudioGesture();
    setIsProcessing(true);
    toast.loading(`Searching ${contact} in WhatsApp & dispatching message...`, { id: 'social-run' });
    try {
      const res = await socialAPI.searchAndSendWhatsApp(contact, message);
      toast.dismiss('social-run');
      setMirrorState(res.mirror_state || mirrorState);
      
      setMessages((prev) => [
        ...prev,
        {
          id: `wa-search-send-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: res.voice_vocalization,
          action: {
            action: 'WHATSAPP_SEARCH_AND_SEND',
            type: 'whatsapp_search_and_send',
            contact,
            message,
            result: res
          }
        }
      ]);
      notifyAssistantSpeaking(res.voice_vocalization);
      toast.success(`Message "${message}" dispatched to ${contact}!`);
    } catch (e) {
      toast.dismiss('social-run');
      toast.error('Failed to search and send message');
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePeekWhatsApp = async () => {
    enableAudioGesture();
    setIsProcessing(true);
    toast.loading('Peeking WhatsApp unread messages...', { id: 'social-run' });
    try {
      const res = await socialAPI.peekWhatsApp();
      toast.dismiss('social-run');
      setMirrorState(res.mirror_state || mirrorState);
      
      setMessages((prev) => [
        ...prev,
        {
          id: `wa-peek-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: res.voice_vocalization,
          action: {
            action: 'WHATSAPP_PEEK',
            type: 'whatsapp_peek',
            result: res
          }
        }
      ]);
      notifyAssistantSpeaking(res.voice_vocalization);
    } catch (e) {
      toast.dismiss('social-run');
      toast.error('Failed to peek WhatsApp');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSmartReplyWhatsApp = async (contact = null) => {
    enableAudioGesture();
    setIsProcessing(true);
    toast.loading("Querying Sonu's memory for personalized reply...", { id: 'social-run' });
    try {
      const res = await socialAPI.smartReplyWhatsApp(contact);
      toast.dismiss('social-run');
      setMirrorState(res.mirror_state || mirrorState);
      
      setMessages((prev) => [
        ...prev,
        {
          id: `wa-smart-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: res.voice_vocalization,
          action: {
            action: 'WHATSAPP_SMART_REPLY',
            type: 'whatsapp_smart_reply',
            result: res
          }
        }
      ]);
      notifyAssistantSpeaking(res.voice_vocalization);
    } catch (e) {
      toast.dismiss('social-run');
      toast.error('Failed to send smart reply');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReplyCustom = async (contact, message) => {
    enableAudioGesture();
    setIsProcessing(true);
    try {
      const res = await socialAPI.replyWhatsApp(contact, message);
      setMirrorState(res.mirror_state || mirrorState);
      
      setMessages((prev) => [
        ...prev,
        {
          id: `wa-custom-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: res.voice_vocalization,
          action: {
            action: 'WHATSAPP_CUSTOM_REPLY',
            type: 'whatsapp_custom_reply',
            contact,
            message,
            result: res
          }
        }
      ]);
      notifyAssistantSpeaking(res.voice_vocalization);
      toast.success(`Message dispatched to ${contact}`);
    } catch (e) {
      toast.error('Failed to send custom reply');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAutoReplyInstagram = async () => {
    enableAudioGesture();
    setIsProcessing(true);
    toast.loading('Processing Instagram DMs & broadcasting...', { id: 'social-run' });
    try {
      const res = await socialAPI.autoReplyInstagram();
      toast.dismiss('social-run');
      setMirrorState(res.mirror_state || mirrorState);
      
      setMessages((prev) => [
        ...prev,
        {
          id: `ig-auto-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: res.voice_vocalization,
          action: {
            action: 'INSTAGRAM_AUTO_REPLY',
            type: 'instagram_auto_reply',
            result: res
          }
        }
      ]);
      notifyAssistantSpeaking(res.voice_vocalization);
    } catch (e) {
      toast.dismiss('social-run');
      toast.error('Failed to auto-reply to Instagram');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSwitchMirror = async (mode) => {
    try {
      const res = await socialAPI.switchMirror(mode);
      setMirrorState(res);
      toast.success(`Switched mirror to ${mode.toUpperCase()}`);
    } catch (_) {}
  };

  const handlePlaySong = () => {
    handleSendMessage("Mere liye gana chalao");
  };

  // Main submission handler
  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputText).trim();
    if (!text || isProcessingRef.current) return;
    isProcessingRef.current = true;
    setIsProcessing(true);

    enableAudioGesture();
    stopSpeaking();
    setInputText('');
    notifyAssistantSpeaking(null, 4000);

    const userMsgId = `user-${Date.now()}`;
    const userMsg = {
      id: userMsgId,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      text
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const lower = text.toLowerCase();

      // 0. Dograh Ultra-Low Latency Voice & Mac Control Fast-Path
      try {
        const dograhRes = await api.post('/api/dograh/command', {
          directive: text,
          session_id: activeSessionId
        });
        const dData = dograhRes.data;
        if (dData && dData.success && dData.voice_vocalization) {
          const replyText = dData.voice_vocalization;

          // Social actions mapping
          const isSocialAction = [
            'WHATSAPP_OPENED',
            'WHATSAPP_SEARCH_AND_SEND',
            'WHATSAPP_MULTI_REPLY',
            'WHATSAPP_PEEK',
            'WHATSAPP_UNREAD_SUMMARY',
            'WHATSAPP_DISAMBIGUATION',
            'WHATSAPP_AWAITING_MESSAGE',
            'WHATSAPP_MESSAGE_SENT',
            'WHATSAPP_CONTACT_NOT_FOUND',
            'WHATSAPP_SMART_REPLY',
            'WHATSAPP_CUSTOM_REPLY',
            'INSTAGRAM_AUTO_REPLY'
          ].includes(dData.action);

          setMessages((prev) => [
            ...prev,
            {
              id: `resp-${Date.now()}`,
              sender: 'kyron',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              text: replyText,
              action: isSocialAction
                ? {
                    action: dData.action,
                    actionName: dData.action,
                    result: dData.result,
                    type: dData.action.toLowerCase()
                  }
                : {
                    type: dData.requires_confirmation
                      ? 'action_preview'
                      : dData.action === 'GREETING' || dData.action === 'LISTENING' || dData.action === 'CAPABILITIES'
                      ? 'greeting'
                      : 'mac_control',
                    action: dData.action,
                    actionName: dData.action,
                    latency_ms: dData.latency_ms,
                    result: dData.result,
                    pendingAction: dData.pending_action
                  }
            }
          ]);

          notifyAssistantSpeaking(replyText);
          if (!dData.spoken_by_dograh) {
            speak(replyText);
          }

          // Refresh mirror state immediately to reflect steps
          refreshMirrorState();

          isProcessingRef.current = false;
          setIsProcessing(false);
          return;
        }
      } catch (err) {
        console.debug('Dograh fast-path pass-through:', err);
      }

      // 1. YouTube Song intent
      const hasSong =
        lower.includes('song') || lower.includes('gana') || lower.includes('gaana') || lower.includes('music');
      const hasAction =
        lower.includes('banao') || lower.includes('chalao') || lower.includes('play') || lower.includes('sunao') || lower.includes('bajao');

      if ((hasSong && hasAction) || (hasSong && lower.split(' ').length <= 4)) {
        const replyText = "Opening Chrome and playing a song for you on YouTube right now, Boss!";
        setTimeout(() => {
          try {
            window.open('https://www.youtube.com/watch?v=jfKfPfyJRdk', '_blank');
          } catch (_) {}
        }, 600);

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
        isProcessingRef.current = false;
        setIsProcessing(false);
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
            isProcessingRef.current = false;
            setIsProcessing(false);
            return;
          }
        } catch (e) {
          toast.dismiss('code-audit');
        }
      }

      // 3. Fallback conversational chat
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

      setMessages((prev) => [
        ...prev,
        {
          id: `resp-${Date.now()}`,
          sender: 'kyron',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          text: reply,
          action: chatRes.data?.action || null
        }
      ]);
      speak(reply);
    } catch (error) {
      console.error('Submission failed:', error);
      toast.error('Failed to process directive');
    } finally {
      isProcessingRef.current = false;
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
    setMessages([
      {
        id: 'welcome-msg',
        sender: 'kyron',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        text: "Namaste Boss! Chat cleared. Ready for your next command.",
        action: null
      }
    ]);
  };

  // Prompt suggestions
  const suggestions = [
    {
      title: "mai koun hu aur mera kya business hai?",
      desc: "Profile-first check of Asif Aslam (Sonu Sarkar)'s master mind",
      icon: <User className="w-4 h-4 text-cyan-400" />
    },
    {
      title: "meri knowledge aur kya padhta hu batao",
      desc: "Verified technical expertise, systems knowledge & daily studies",
      icon: <Sparkles className="w-4 h-4 text-indigo-400" />
    },
    {
      title: "kyron whatsapp open kroo",
      desc: "Launches WhatsApp on macOS desktop & arms OBG listener",
      icon: <MessageCircle className="w-4 h-4 text-emerald-400" />
    },
    {
      title: "kyron sonu search kro aur usko msg kro hi sonu",
      desc: "Searches Sonu via Cmd+F, dispatches 'Hi Sonu' & speaks confirmation",
      icon: <Send className="w-4 h-4 text-cyan-400" />
    },
    {
      title: "kyron whatsapp open kr ke dekho kitna msg aya",
      desc: "Peek unread messages from previews & speak who sent what",
      icon: <Eye className="w-4 h-4 text-emerald-400" />
    },
    {
      title: "Rahul ko reply karo ki kal 2 baje deliver ho jayega",
      desc: "Dispatches user-dictated message via WhatsApp Web",
      icon: <Send className="w-4 h-4 text-cyan-400" />
    },
    {
      title: "khud se reply kr do mera memory check karke",
      desc: "Smart autonomous reply using Sonu's persona & project knowledge",
      icon: <Sparkles className="w-4 h-4 text-purple-400" />
    },
    {
      title: "mera insta pe jaa ke reply kro jiska msg aya",
      desc: "Auto-replies to all Instagram DMs and speaks confirmation",
      icon: <Instagram className="w-4 h-4 text-pink-400" />
    },
    {
      title: "Mere liye gana chalao",
      desc: "Opens Chrome and plays YouTube trending songs",
      icon: <Music className="w-4 h-4 text-emerald-400" />
    },
    {
      title: "Volume badhao",
      desc: "Native macOS hardware volume boost via AppleScript",
      icon: <Volume2 className="w-4 h-4 text-amber-400" />
    }
  ];

  return (
    <div
      onClick={enableAudioGesture}
      className="flex flex-col h-screen w-screen bg-[#070b12] text-slate-100 font-sans overflow-hidden select-none"
    >
      {/* ======================================================== */}
      {/* 1. TOP macOS MENUBAR                                     */}
      {/* ======================================================== */}
      <MacMenuBar
        isListening={isListening}
        toggleListening={toggleListening}
        isSpeaking={isSpeaking}
        stopSpeaking={stopSpeaking}
        isMuted={isMuted}
        toggleMute={toggleMute}
        audioLevel={audioLevel}
        selectedLanguage={selectedLanguage}
        setVoiceLanguage={setVoiceLanguage}
        triggerWakeup={triggerWakeup}
      />

      {/* ======================================================== */}
      {/* AUTONOMOUS GOOGLE CHROME FOOTER HUD & OBG LISTENER        */}
      {/* ======================================================== */}
      {(() => {
        const isExternalTaskRunning =
          mirrorState?.ongoing_task?.status === 'active' ||
          (mirrorState?.active_app &&
            mirrorState.active_app !== 'KYRON Workstation' &&
            mirrorState.active_app !== 'macOS Sequoia' &&
            mirrorState.active_app !== 'None' &&
            mirrorState.active_app !== '') ||
          isProcessing;

        // STRICT REQUIREMENT: Completely remove Google Chrome HUD box from Kyron AGI chat box!
        // It must NEVER show while user is inside the Kyron AGI chat window (isWindowFocused === true)
        const isChromeControlling =
          !isWindowFocused &&
          (isExternalTaskRunning ||
            mirrorState?.active_app?.toLowerCase().includes('chrome') ||
            mirrorState?.active_app?.toLowerCase().includes('browser') ||
            mirrorState?.ongoing_task?.status === 'active');

        const showChromeFooterHUD =
          !isWindowFocused && isChromeControlling && !chromeHudDismissed;

        // OBG Dynamic Island pill is shown when on desktop and Chrome HUD is not overriding
        const showOBGFooter =
          !isWindowFocused && isExternalTaskRunning && !hudDismissed && !showChromeFooterHUD;

        return (
          <>
            <MacChromeFooterHUD
              visible={showChromeFooterHUD}
              task={mirrorState?.ongoing_task}
              activeApp={mirrorState?.active_app || 'Google Chrome'}
              steps={mirrorState?.steps_log}
              isProcessing={isProcessing}
              onClose={() => {
                setChromeHudDismissed(true);
                setChromeHudForceVisible(false);
              }}
              onOpenFullMirror={() => {
                setMirrorOpen(true);
              }}
            />

            <MacOBGListener
              visible={showOBGFooter}
              onClose={() => {
                setHudDismissed(true);
                setHudForceVisible(false);
              }}
              isListening={isListening}
              toggleListening={toggleListening}
              isSpeaking={isSpeaking}
              audioLevel={audioLevel}
              liveTranscript={liveTranscript}
              ongoingTask={mirrorState?.ongoing_task}
              activeApp={mirrorState?.active_app}
              onOpenWhatsApp={handleOpenWhatsApp}
              onSearchAndSendSonu={() => handleSearchAndSendWhatsApp('Sonu', 'Hi Sonu')}
              isProcessing={isProcessing}
            />
          </>
        );
      })()}

      {/* ======================================================== */}
      {/* 2. MAIN WORKSPACE CONTAINER                              */}
      {/* ======================================================== */}
      <div className="flex flex-1 w-full overflow-hidden">
        {/* ======================================================== */}
        {/* LEFT COLUMN: WORK STATS + TASK HISTORY + SESSIONS        */}
        {/* ======================================================== */}
        <AnimatePresence initial={false}>
          {sidebarOpen && (
            <motion.aside
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 340, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="h-full bg-[#0a0f19]/90 border-r border-white/10 flex flex-col z-20 shrink-0 select-none overflow-hidden backdrop-blur-2xl"
            >
              {/* Workspace Mode Selector */}
              <div className="p-3 border-b border-white/10 bg-white/[0.02]">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider font-mono">
                    Workspace Mode
                  </span>
                  <button
                    onClick={() => setSidebarOpen(false)}
                    className="p-1 rounded text-slate-400 hover:text-white transition"
                    title="Hide sidebar"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>
                </div>
                <div className="grid grid-cols-3 gap-1">
                  {[
                    { id: 'kyron', label: 'Kyron AGI', icon: <Bot className="w-3.5 h-3.5 text-cyan-400" /> },
                    { id: 'munder', label: 'Munder', icon: <Code2 className="w-3.5 h-3.5 text-indigo-400" /> },
                    { id: 'call_support', label: 'Call Support', icon: <PhoneCall className="w-3.5 h-3.5 text-emerald-400" /> }
                  ].map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handlePanelChange(item.id)}
                      className={`flex flex-col items-center justify-center p-2 rounded-xl text-xs font-medium transition ${
                        activePanel === item.id
                          ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.03]'
                      }`}
                    >
                      {item.icon}
                      <span className="text-[10px] mt-1 font-semibold">{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Scrollable Side Content */}
              <div className="flex-1 overflow-y-auto p-3 space-y-3 custom-scrollbar">
                {activePanel === 'call_support' ? (
                  /* Dedicated Calling Setup when in Call Support Mode */
                  <MacCallingSetupSidebar />
                ) : (
                  <>
                    {/* 1. Box 1: Profile & Mind Card (with 3 Modes: My Profile & MD file, Document, Skill) */}
                    <MacUserProfileCard
                      bossProfile={mirrorState?.boss_profile}
                      onOpenPersonalize={() => setShowPersonalizeModal(true)}
                      onOpenVault={() => setShowPersonalizeModal(true)}
                    />

                    {/* 2. Box 2: Tasks Overview & Recent Completed Tasks ("Overview & Recent Task") */}
                    <MacTaskOverviewCard
                      stats={mirrorState?.work_stats}
                      taskHistory={mirrorState?.task_history}
                      onSelectTask={(task) => {
                        toast(`Inspecting task: ${task.title}`);
                      }}
                    />

                    {/* 3. Box 3: System Health ("System Health & Diagnostics") */}
                    <MacSystemHealthCard />
                  </>
                )}

                {/* 4. Persistent Chat Sessions List */}
                <div className="rounded-2xl border border-white/10 bg-slate-900/40 p-2.5">
                  <div className="flex items-center justify-between mb-2 px-1">
                    <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wider font-mono">
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

                  <div className="space-y-1 max-h-40 overflow-y-auto custom-scrollbar">
                    {sessions.map((sess) => {
                      const isActive = activeSessionId === sess.id;
                      return (
                        <div
                          key={sess.id}
                          onClick={() => selectSession(sess.id)}
                          className={`group relative flex items-center justify-between px-2.5 py-1.5 rounded-xl text-xs cursor-pointer transition ${
                            isActive
                              ? 'bg-gradient-to-r from-cyan-950/60 to-indigo-950/40 text-cyan-200 border border-cyan-500/40'
                              : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                          }`}
                        >
                          <div className="flex items-center gap-2 overflow-hidden flex-1 mr-1">
                            <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
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
                    })}
                  </div>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* ======================================================== */}
        {/* CENTER COLUMN: MAIN MAC WORKSTATION VIEW                 */}
        {/* ======================================================== */}
        <main className="flex-1 flex flex-col h-full bg-[#0b101c]/95 relative overflow-hidden">
          {/* macOS Window Title Bar Header */}
          <div className="h-10 border-b border-white/10 bg-[#0f1626]/80 backdrop-blur-md flex items-center justify-between px-4 z-20 shrink-0">
            {/* macOS Window Traffic Lights */}
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <span className="w-3 h-3 rounded-full bg-[#ff5f56] inline-block shadow-sm"></span>
                <span className="w-3 h-3 rounded-full bg-[#ffbd2e] inline-block shadow-sm"></span>
                <span className="w-3 h-3 rounded-full bg-[#27c93f] inline-block shadow-sm"></span>
              </div>

              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="ml-2 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition"
                  title="Open sidebar"
                >
                  <Sidebar className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Window Center Title & Status Badge */}
            <div className="flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-xs font-bold text-slate-200 tracking-wide">
                KYRON AGI 2.0 • macOS Tahoe Workstation
              </span>
              <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 font-bold">
                🟢 Live Voice Armed
              </span>
            </div>

            {/* Right Toggle Buttons for Screen Mirror, Footer HUD & NVIDIA Brev */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setHudForceVisible(!hudForceVisible);
                  if (hudDismissed) setHudDismissed(false);
                }}
                className={`p-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${
                  hudForceVisible
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-sm'
                    : 'bg-white/5 text-slate-400 border-white/10 hover:text-emerald-300'
                }`}
                title="Toggle OBG Dynamic Island Footer HUD"
              >
                <Radio className="w-3.5 h-3.5 text-emerald-400" />
                <span className="hidden sm:inline text-[11px] font-semibold">
                  {hudForceVisible ? 'Footer HUD ON' : 'Footer HUD'}
                </span>
              </button>

              <button
                onClick={() => setShowNvidiaBrev(!showNvidiaBrev)}
                className={`p-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${
                  showNvidiaBrev
                    ? 'bg-[#76B900]/20 text-[#76B900] border-[#76B900]/40'
                    : 'bg-white/5 text-slate-400 border-white/10 hover:text-[#76B900]'
                }`}
                title="Toggle NVIDIA Brev Cloud GPU Stack"
              >
                <CloudLightning className="w-3.5 h-3.5 text-[#76B900]" />
                <span className="hidden sm:inline text-[11px] font-semibold">
                  {showNvidiaBrev ? 'Brev Active' : 'NVIDIA Brev'}
                </span>
              </button>

              {activePanel === 'kyron' && (
                <button
                  onClick={() => setMirrorOpen(!mirrorOpen)}
                  className={`p-1.5 rounded-xl border text-xs flex items-center gap-1.5 transition ${
                    mirrorOpen
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                      : 'bg-white/5 text-slate-400 border-white/10 hover:text-white'
                  }`}
                  title="Toggle Live Screen Mirror"
                >
                  <Monitor className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline text-[11px] font-semibold">
                    {mirrorOpen ? 'Mirror Active' : 'Show Mirror'}
                  </span>
                </button>
              )}
            </div>
          </div>

          {/* Collapsible NVIDIA Brev Cloud GPU Dashboard */}
          {showNvidiaBrev && (
            <div className="p-3 pb-0 shrink-0">
              <NvidiaBrevCard onClose={() => setShowNvidiaBrev(false)} />
            </div>
          )}

          {/* Conditional Workstation Panels */}
          {activePanel === 'call_support' ? (
            <div className="flex-1 overflow-hidden">
              <MacCallSupportPanel />
            </div>
          ) : activePanel === 'munder' ? (
            <div className="flex-1 overflow-hidden">
              <MunderDifflinPanel />
            </div>
          ) : (
            <>
          {/* SCROLLABLE CONVERSATIONAL MESSAGE STREAM */}
          <div className="flex-1 overflow-y-auto px-4 py-4 custom-scrollbar select-text">
            <div className="max-w-3xl mx-auto space-y-4">
              {/* Welcome Screen Cards if only 1 message */}
              {messages.length === 1 && (
                <div className="py-6 flex flex-col items-center text-center">
                  <div
                    onClick={triggerWakeup}
                    className="relative cursor-pointer group mb-3"
                    title="Click to wake Kyron immediately!"
                  >
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-cyan-500/30 group-hover:scale-105 transition-all">
                      <Sparkles className="w-8 h-8 text-white animate-pulse" />
                    </div>
                  </div>
                  <h2 className="text-xl font-bold text-white mb-1">
                    How can I assist you today, Boss?
                  </h2>
                  <p className="text-xs text-slate-400 max-w-md mb-4">
                    Say <span className="text-cyan-300 font-semibold">"Hey Kyron"</span>, speak in natural Hindi/Hinglish, or click any workflow card below.
                  </p>

                  {/* Suggestion Cards */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
                    {suggestions.map((card, i) => (
                      <button
                        key={i}
                        onClick={() => handleSendMessage(card.title)}
                        className="text-left p-3 rounded-2xl bg-[#111726]/80 hover:bg-[#152033] border border-white/10 hover:border-cyan-500/40 transition group shadow-sm flex items-start gap-2.5"
                      >
                        <div className="mt-0.5 p-1.5 rounded-lg bg-white/5 group-hover:bg-cyan-500/20 transition shrink-0">
                          {card.icon}
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 block mb-0.5">
                            {card.title}
                          </span>
                          <p className="text-[11px] text-slate-400">{card.desc}</p>
                        </div>
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
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.2 }}
                    className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    {!isUser && (
                      <div className="w-7 h-7 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md shadow-cyan-900/20 mt-0.5">
                        <Bot className="w-3.5 h-3.5 text-white" />
                      </div>
                    )}

                    <div className={`max-w-[85%] sm:max-w-[78%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                      <div
                        className={`rounded-2xl px-4 py-2.5 text-xs sm:text-sm leading-relaxed ${
                          isUser
                            ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-950/30'
                            : 'bg-[#131b2c] border border-white/10 text-slate-200 shadow-md'
                        }`}
                      >
                        <p className="whitespace-pre-wrap">{msg.text}</p>

                        {/* Cognitive Mind Verification Badge */}
                        {(msg.action?.action === 'PROFILE_CHECK' ||
                          msg.action?.actionName === 'PROFILE_CHECK' ||
                          msg.action?.verified_from_profile) && (
                          <div className="mt-2.5 p-2 rounded-xl bg-cyan-950/40 border border-cyan-500/30 flex items-center justify-between gap-2 text-[10px] font-mono">
                            <div className="flex items-center gap-1.5 text-cyan-300">
                              <Brain className="w-3.5 h-3.5 text-cyan-400" />
                              <span>Verified from KYRON_MIND.md • Asif Aslam Profile</span>
                            </div>
                            <span className="text-emerald-400 font-bold bg-emerald-950/60 px-1.5 py-0.2 rounded border border-emerald-500/30">
                              ✓ Profile-First
                            </span>
                          </div>
                        )}

                        {/* Capabilities & Features Grid Card */}
                        {(msg.action?.action === 'CAPABILITIES' || msg.action?.actionName === 'CAPABILITIES') && (
                          <div className="mt-3 p-3.5 rounded-2xl bg-gradient-to-br from-[#0c1626]/95 via-[#101e34]/90 to-[#141b2a]/95 border border-cyan-500/30 text-xs shadow-2xl backdrop-blur-xl">
                            <div className="flex items-center justify-between pb-2 mb-2.5 border-b border-white/10">
                              <div className="flex items-center gap-2">
                                <div className="w-6 h-6 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
                                  <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                                </div>
                                <h4 className="text-xs font-bold text-white">
                                  KYRON AGI Hands-Free Capabilities
                                </h4>
                              </div>
                              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded-full border border-cyan-500/30">
                                Real macOS AGI
                              </span>
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 my-2">
                              <button
                                onClick={() => handleSendMessage("battery health check karo")}
                                className="p-2.5 rounded-xl bg-black/30 hover:bg-cyan-500/10 border border-white/5 hover:border-cyan-500/30 text-left transition flex items-center justify-between group"
                              >
                                <div className="flex items-center gap-2">
                                  <div className="w-7 h-7 rounded-lg bg-emerald-500/20 flex items-center justify-center shrink-0">
                                    <Zap className="w-3.5 h-3.5 text-emerald-400" />
                                  </div>
                                  <div>
                                    <span className="text-xs font-bold text-slate-200 group-hover:text-cyan-300 block">
                                      Battery & System Health
                                    </span>
                                    <span className="text-[10px] text-slate-400">Live pmset, cycles & ioreg</span>
                                  </div>
                                </div>
                              </button>

                              <button
                                onClick={() => handleSendMessage("whatsapp me unread messages check karo")}
                                className="p-2.5 rounded-xl bg-black/30 hover:bg-emerald-500/10 border border-white/5 hover:border-emerald-500/30 text-left transition flex items-center justify-between group"
                              >
                                <div className="flex items-center gap-2">
                                  <div className="w-7 h-7 rounded-lg bg-emerald-500/20 flex items-center justify-center shrink-0">
                                    <MessageCircle className="w-3.5 h-3.5 text-emerald-400" />
                                  </div>
                                  <div>
                                    <span className="text-xs font-bold text-slate-200 group-hover:text-emerald-300 block">
                                      Authentic WhatsApp Agent
                                    </span>
                                    <span className="text-[10px] text-slate-400">Zero mock SQLite peeker & sender</span>
                                  </div>
                                </div>
                              </button>

                              <button
                                onClick={() => handleSendMessage("kya open hai mac me")}
                                className="p-2.5 rounded-xl bg-black/30 hover:bg-purple-500/10 border border-white/5 hover:border-purple-500/30 text-left transition flex items-center justify-between group"
                              >
                                <div className="flex items-center gap-2">
                                  <div className="w-7 h-7 rounded-lg bg-purple-500/20 flex items-center justify-center shrink-0">
                                    <Monitor className="w-3.5 h-3.5 text-purple-400" />
                                  </div>
                                  <div>
                                    <span className="text-xs font-bold text-slate-200 group-hover:text-purple-300 block">
                                      macOS App Control
                                    </span>
                                    <span className="text-[10px] text-slate-400">Open/quit Safari, apps & volume</span>
                                  </div>
                                </div>
                              </button>

                              <button
                                onClick={() => handleSendMessage("nvidia status batao")}
                                className="p-2.5 rounded-xl bg-black/30 hover:bg-lime-500/10 border border-white/5 hover:border-lime-500/30 text-left transition flex items-center justify-between group"
                              >
                                <div className="flex items-center gap-2">
                                  <div className="w-7 h-7 rounded-lg bg-lime-500/20 flex items-center justify-center shrink-0">
                                    <Sparkles className="w-3.5 h-3.5 text-lime-400" />
                                  </div>
                                  <div>
                                    <span className="text-xs font-bold text-slate-200 group-hover:text-lime-300 block">
                                      NVIDIA Brev & GPU Stack
                                    </span>
                                    <span className="text-[10px] text-slate-400">NemoClaw, Hermes & Sandboxes</span>
                                  </div>
                                </div>
                              </button>
                            </div>
                          </div>
                        )}

                        {/* Social Action Cards (WhatsApp Peek / Reply / Instagram) */}
                        {msg.action && (
                          <MacSocialCard
                            action={msg.action}
                            onReplyCustom={handleReplyCustom}
                            onSmartReply={handleSmartReplyWhatsApp}
                            onAutoReplyInstagram={handleAutoReplyInstagram}
                          />
                        )}



                        {/* macOS Hardware, Battery & System Status Card */}
                        {(msg.action?.action === 'SYSTEM_STATUS' ||
                          msg.action?.actionName === 'SYSTEM_STATUS' ||
                          msg.action?.action === 'RUNNING_APPS' ||
                          msg.action?.actionName === 'RUNNING_APPS') && (
                          <MacSystemStatusCard action={msg.action} />
                        )}



                        {/* App Launch confirmation card */}
                        {(msg.action?.action === 'APP_OPEN' || msg.action?.actionName === 'APP_OPEN') && (
                          <div className="mt-2.5 p-3 rounded-xl bg-slate-900/90 border border-purple-500/30 flex items-center justify-between gap-3">
                            <div className="flex items-center gap-2.5">
                              <div className="w-7 h-7 rounded-lg bg-purple-500/20 flex items-center justify-center">
                                <Monitor className="w-3.5 h-3.5 text-purple-400" />
                              </div>
                              <div>
                                <span className="text-xs font-semibold text-purple-300 block">
                                  {msg.action.result?.app || 'App'} Launched
                                </span>
                                <span className="text-[10px] text-slate-400">Frontmost window in macOS Desktop</span>
                              </div>
                            </div>
                            <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                              Active
                            </span>
                          </div>
                        )}



                        {/* NVIDIA Brev Action Card */}
                        {(msg.action?.action?.startsWith('BREV_') ||
                          msg.action?.actionName?.startsWith('BREV_') ||
                          msg.action?.action === 'BREV_STATUS' ||
                          msg.action?.action === 'BREV_LAUNCHABLE_PREPARED') && (
                          <div className="mt-3">
                            <NvidiaBrevCard />
                          </div>
                        )}



                        {/* YouTube Media Play Card */}
                        {msg.action?.type === 'media_play' && (
                          <div className="mt-2.5 p-3 rounded-xl bg-slate-900/90 border border-emerald-500/30 flex items-center justify-between gap-3">
                            <div className="flex items-center gap-2.5">
                              <div className="w-7 h-7 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                                <Music className="w-3.5 h-3.5 text-emerald-400 animate-bounce" />
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



                        {/* Code Diff Review Card */}
                        {msg.action?.type === 'diff_review' && (
                          <div className="mt-2.5">
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



                        {/* Action Preview Card (Safety Gate) */}
                        {msg.action?.type === 'action_preview' && msg.action.pendingAction && (
                          <div className="mt-2.5">
                            <ActionPreviewCard
                              actionId={msg.action.pendingAction.action_id}
                              type="system"
                              app={msg.action.pendingAction.app || 'macOS'}
                              target={msg.action.pendingAction.target_contact || 'Contact'}
                              description={msg.action.pendingAction.description}
                              status={msg.action.pendingAction.status}
                              onConfirm={async (actionId) => {
                                try {
                                  await api.post('/api/kyron/system-control/confirm', {
                                    action_id: actionId,
                                    confirmed: true
                                  });
                                  toast.success('Action confirmed and executed!');
                                  speak('Action confirmed and executed successfully Boss!');
                                } catch (e) {
                                  toast.error('Failed to confirm action');
                                }
                              }}
                              onReject={async (actionId) => {
                                try {
                                  await api.post('/api/kyron/system-control/confirm', {
                                    action_id: actionId,
                                    confirmed: false
                                  });
                                  toast('Action rejected and discarded');
                                } catch (_) {}
                              }}
                            />
                          </div>
                        )}


                      </div>

                      {/* Action Bar Below Bubble */}
                      <div className="flex items-center gap-2 mt-1 px-1 text-[10px] text-slate-500 font-mono">
                        <span>{msg.timestamp}</span>
                        {!isUser && (
                          <>
                            <button
                              onClick={() => speak(msg.text)}
                              className="hover:text-cyan-400 transition flex items-center gap-0.5"
                              title="Listen"
                            >
                              <Volume2 className="w-3 h-3" />
                              <span>Listen</span>
                            </button>
                            <button
                              onClick={() => copyMessage(msg.id, msg.text)}
                              className="hover:text-cyan-400 transition flex items-center gap-0.5"
                              title="Copy"
                            >
                              {copiedId === msg.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                              <span>{copiedId === msg.id ? 'Copied' : 'Copy'}</span>
                            </button>
                          </>
                        )}


                      </div>
                    </div>

                    {isUser && (
                      <div className="w-7 h-7 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 mt-0.5">
                        <User className="w-3.5 h-3.5 text-slate-300" />
                      </div>
                    )}
                  </motion.div>
                );
              })}

              {isProcessing && (
                <div className="flex items-center gap-2.5">
                  <div className="w-7 h-7 rounded-xl bg-cyan-600 flex items-center justify-center shrink-0 animate-pulse">
                    <Bot className="w-3.5 h-3.5 text-white" />
                  </div>
                  <div className="p-2.5 rounded-2xl bg-[#131b2c] border border-white/10 text-xs text-cyan-300 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    <span>KYRON is executing directive & updating screen mirror...</span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* LIVE TRANSCRIPT PILL (FLOATING ABOVE BOTTOM DOCK) */}
          <AnimatePresence>
            {liveTranscript && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="max-w-xl mx-auto w-full px-4 mb-2 z-10"
              >
                <div className="p-2.5 rounded-2xl bg-cyan-950/90 border border-cyan-500/50 backdrop-blur-xl shadow-xl flex items-center gap-3">
                  <div className="flex items-center gap-0.5 h-3.5">
                    <span className="w-1 bg-cyan-400 rounded-full animate-bounce h-3"></span>
                    <span className="w-1 bg-cyan-400 rounded-full animate-bounce h-4"></span>
                    <span className="w-1 bg-cyan-400 rounded-full animate-bounce h-2"></span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-[9px] font-mono text-cyan-400 uppercase tracking-wider block">
                      Live Voice Dictation (Auto-Send on silence)
                    </span>
                    <p className="text-xs font-semibold text-white truncate">
                      "{liveTranscript}"
                    </p>
                  </div>
                  <button
                    onClick={() => handleSendMessage(liveTranscript)}
                    className="px-2.5 py-1 rounded-lg bg-cyan-500 text-slate-950 font-bold text-xs hover:bg-cyan-400 transition"
                  >
                    Send Now
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* FLOATING macOS DOCK INPUT BAR */}
          <div className="shrink-0 p-3 bg-gradient-to-t from-[#070b12] via-[#070b12]/90 to-transparent">
            <div className="max-w-3xl mx-auto">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                className={`relative flex items-center rounded-2xl bg-[#121929]/90 border backdrop-blur-xl transition-all ${
                  isListening && inputText
                    ? 'border-cyan-400 shadow-[0_0_20px_rgba(6,182,212,0.35)] ring-1 ring-cyan-400/50'
                    : 'border-white/10 focus-within:border-cyan-500/60 shadow-2xl'
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
                  title={isListening ? 'Click to Pause Mic' : 'Click to Turn Mic ON'}
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
                      ? 'Boliye... jo bolenge type hoga aur pause pe auto-send ho jayega...'
                      : 'Direct Kyron: "whatsapp dekho", "khud se reply karo", "insta dms"...'
                  }
                  disabled={isProcessing}
                  className="flex-1 bg-transparent py-3 px-2 text-sm text-slate-100 placeholder-slate-400 focus:outline-none"
                />

                {/* Send Button */}
                <button
                  type="submit"
                  disabled={!inputText.trim() || isProcessing}
                  className={`p-2 mr-2 rounded-xl transition ${
                    inputText.trim() && !isProcessing
                      ? 'bg-gradient-to-tr from-cyan-500 to-indigo-600 text-white shadow-md shadow-cyan-900/40 hover:opacity-90'
                      : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>

              {/* Minimal Hint */}
              <div className="flex items-center justify-between mt-1.5 px-2 text-[10px] text-slate-400 font-mono">
                <span>Wake: <strong className="text-cyan-300">"Hey Kyron"</strong> or 👏 <strong>Clap</strong></span>
                <span>Chrome Mirror & Hermes Memory Synchronized</span>
              </div>
            </div>
          </div>
        </>
      )}
    </main>

    {/* ======================================================== */}
    {/* RIGHT COLUMN: LIVE SCREEN & BROWSER MIRROR + STEPS STREAM */}
    {/* EXCLUSIVE TO KYRON AGI (`activePanel === 'kyron'`)       */}
    {/* ======================================================== */}
    {activePanel === 'kyron' && (
      <AnimatePresence initial={false}>
        {mirrorOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 380, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="h-full shrink-0 overflow-hidden"
          >
            <MacScreenMirror
              mirrorState={mirrorState}
              onSwitchMode={handleSwitchMirror}
              onPeekWhatsApp={handlePeekWhatsApp}
              onSmartReplyWhatsApp={() => handleSmartReplyWhatsApp()}
              onAutoReplyInstagram={handleAutoReplyInstagram}
              isProcessing={isProcessing}
            />
          </motion.div>
        )}
      </AnimatePresence>
    )}
      </div>

      {/* Full Personalize & Document Vault Modal Overlay */}
      {showPersonalizeModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-5xl h-[85vh] bg-[#0c1322] border border-cyan-500/30 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
            <MacPersonalizePanel onClose={() => setShowPersonalizeModal(false)} />
          </div>
        </div>
      )}
    </div>
  );
}
