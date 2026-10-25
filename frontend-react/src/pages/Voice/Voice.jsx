import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Radio,
  Zap,
  Sparkles,
  Laptop,
  Battery,
  BatteryCharging,
  Sliders,
  Play,
  Pause,
  Camera,
  Terminal,
  Calculator,
  Compass,
  FileText,
  Moon,
  Sun,
  ShieldCheck,
  CheckCircle2,
  Music,
  Send,
  Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';

import { dograhAPI } from '../../services/api';
import { useKyronVoice } from '../../hooks/useKyronVoice';

export default function Voice() {
  const [inputText, setInputText] = useState('');
  const [history, setHistory] = useState([
    {
      id: 'init-1',
      command: 'system status batao',
      action: 'SYSTEM_STATUS',
      response: 'Sab badiya Boss! Battery charging pe hai, volume set hai aur KYRON ready hai.',
      latency_ms: 140,
      timestamp: 'Just now'
    }
  ]);

  // Fetch Dograh platform status & macOS diagnostics
  const { data: dograhStatus, refetch: refetchStatus } = useQuery({
    queryKey: ['dograh-status'],
    queryFn: dograhAPI.getStatus,
    refetchInterval: 10000
  });

  const { data: macSystem, refetch: refetchSystem } = useQuery({
    queryKey: ['dograh-system'],
    queryFn: dograhAPI.getSystemStatus,
    refetchInterval: 5000
  });

  // Direct Dograh voice command mutation
  const commandMutation = useMutation({
    mutationFn: (directive) => dograhAPI.executeCommand(directive),
    onSuccess: (data, variables) => {
      if (data.voice_vocalization) {
        notifyAssistantSpeaking(data.voice_vocalization);
        if (!data.spoken_by_dograh) {
          speak(data.voice_vocalization);
        }
      }
      setHistory((prev) => [
        {
          id: `cmd-${Date.now()}`,
          command: variables,
          action: data.action || 'EXECUTED',
          response: data.voice_vocalization || 'Directive executed Boss.',
          latency_ms: data.latency_ms || 25,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
        },
        ...prev.slice(0, 15)
      ]);
      refetchSystem();
      toast.success(`Executed: ${data.action || 'Command'}`);
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || 'Execution error');
    }
  });

  // Voice engine hook
  const {
    isListening,
    isSpeaking,
    isMuted,
    liveTranscript,
    audioLevel,
    speak,
    stopSpeaking,
    toggleListening,
    toggleMute,
    notifyAssistantSpeaking
  } = useKyronVoice({
    onDirectiveSubmit: (directive) => {
      if (directive.trim()) {
        commandMutation.mutate(directive.trim());
      }
    },
    language: 'en-IN'
  });

  const handleManualSubmit = (e) => {
    e?.preventDefault();
    const text = inputText.trim();
    if (!text || commandMutation.isPending) return;
    setInputText('');
    commandMutation.mutate(text);
  };

  const quickDirectives = [
    { label: '🔊 Volume 60%', directive: 'volume 60 percent kar do', icon: Sliders },
    { label: '🔋 Battery & System Status', directive: 'system status batao', icon: Battery },
    { label: '🧭 Open Safari', directive: 'safari kholo', icon: Compass },
    { label: '🖩 Open Calculator', directive: 'calculator open karo', icon: Calculator },
    { label: '💻 Open Terminal', directive: 'terminal kholo', icon: Terminal },
    { label: '📸 Take Screenshot', directive: 'screenshot lo', icon: Camera },
    { label: '🎵 YouTube Songs', directive: 'youtube pe lofi gana bajao', icon: Music },
    { label: '📝 Note in Notes', directive: 'note me likho Buy groceries and check server logs', icon: FileText },
    { label: '🌓 Toggle Dark Mode', directive: 'dark mode toggle karo', icon: Moon },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12 select-none">
      {/* Header & Dograh Status Banner */}
      <div className="rounded-2xl p-6 bg-gradient-to-r from-[#0d1424] via-[#0f172a] to-[#13112c] border border-cyan-500/30 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

        <div className="flex flex-wrap items-center justify-between gap-4 relative z-10">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500 to-indigo-600 p-0.5 shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-[#0a0f1d] rounded-2xl flex items-center justify-center">
                <Radio className="w-7 h-7 text-cyan-400 animate-pulse" />
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <h1 className="text-2xl font-bold tracking-tight text-white font-mono">
                  KYRON // DOGRAH VOICE ENGINE
                </h1>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                  SUB-25MS LATENCY
                </span>
              </div>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                Powered by Dograh Voice Architecture + Native macOS Apple Silicon Hardware Control
              </p>
            </div>
          </div>

          {/* Quick Hardware Indicators */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700/60 flex items-center space-x-2 text-xs font-mono text-slate-200">
              <Laptop className="w-4 h-4 text-cyan-400" />
              <span>macOS Apple Silicon</span>
            </div>
            {macSystem && (
              <>
                <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700/60 flex items-center space-x-2 text-xs font-mono text-emerald-400">
                  {macSystem.is_charging ? (
                    <BatteryCharging className="w-4 h-4 text-emerald-400 animate-bounce" />
                  ) : (
                    <Battery className="w-4 h-4 text-emerald-400" />
                  )}
                  <span>{macSystem.battery || '100%'}</span>
                </div>
                <div className="px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-700/60 flex items-center space-x-2 text-xs font-mono text-indigo-300">
                  <Sliders className="w-4 h-4 text-indigo-400" />
                  <span>Vol: {macSystem.output_volume}%</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Main Interactive Voice Radar & Waveform HUD */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Radar & Audio Orb (Left 2 cols) */}
        <div className="lg:col-span-2 rounded-2xl bg-[#0a0f1d]/90 border border-cyan-500/30 p-6 flex flex-col justify-between shadow-xl relative overflow-hidden backdrop-blur-md min-h-[380px]">
          <div className="flex items-center justify-between z-10">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span className="text-xs font-mono font-semibold text-cyan-300 tracking-wider uppercase">
                REAL-TIME VOICE CONTROL HUD
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleMute}
                className={`p-2 rounded-lg border transition ${
                  isMuted
                    ? 'bg-rose-500/20 border-rose-500/40 text-rose-300'
                    : 'bg-slate-800/60 border-slate-700 text-slate-300 hover:text-white'
                }`}
                title={isMuted ? 'Unmute TTS' : 'Mute TTS'}
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Central Pulsing Audio Orb */}
          <div className="my-auto flex flex-col items-center justify-center text-center py-6 relative z-10">
            <div className="relative flex items-center justify-center">
              {/* Outer pulsing ring proportional to audioLevel */}
              <motion.div
                animate={{
                  scale: isListening ? 1 + audioLevel / 80 : 1,
                  opacity: isListening ? 0.3 + audioLevel / 150 : 0.1
                }}
                transition={{ type: 'spring', damping: 15 }}
                className="absolute w-44 h-44 rounded-full bg-cyan-500 blur-xl pointer-events-none"
              />

              {/* Middle Wave Ring */}
              <motion.div
                animate={{
                  scale: isSpeaking ? [1, 1.15, 1] : 1,
                  borderColor: isSpeaking ? '#a855f7' : isListening ? '#06b6d4' : '#475569'
                }}
                transition={{ repeat: Infinity, duration: 1.5 }}
                className="w-36 h-36 rounded-full border-2 border-dashed flex items-center justify-center p-3 relative"
              >
                {/* Main Mic Button */}
                <button
                  onClick={toggleListening}
                  className={`w-28 h-28 rounded-full flex flex-col items-center justify-center transition-all duration-300 shadow-2xl active:scale-95 ${
                    isListening
                      ? 'bg-gradient-to-tr from-cyan-500 to-blue-600 text-slate-950 shadow-cyan-500/40'
                      : 'bg-slate-800/80 border border-slate-700 text-slate-400 hover:text-white'
                  }`}
                >
                  {isListening ? (
                    <>
                      <Mic className="w-10 h-10 animate-pulse text-slate-950" />
                      <span className="text-[10px] font-mono font-bold tracking-wider mt-1 text-slate-950 uppercase">
                        LISTENING
                      </span>
                    </>
                  ) : (
                    <>
                      <MicOff className="w-9 h-9 text-slate-400" />
                      <span className="text-[10px] font-mono font-semibold tracking-wider mt-1 uppercase">
                        TAP TO SPEAK
                      </span>
                    </>
                  )}
                </button>
              </motion.div>
            </div>

            {/* Live Audio Equalizer Bars */}
            <div className="flex items-center space-x-1.5 h-8 mt-6">
              {[...Array(20)].map((_, i) => {
                const heightPct = isListening ? Math.min(100, Math.max(15, (audioLevel * ((i % 5) + 1)) / 4)) : 10;
                return (
                  <motion.div
                    key={i}
                    animate={{ height: `${heightPct}%` }}
                    transition={{ ease: 'linear', duration: 0.05 }}
                    className={`w-1 rounded-full ${
                      isSpeaking
                        ? 'bg-purple-400'
                        : isListening
                        ? 'bg-gradient-to-t from-cyan-500 to-emerald-400'
                        : 'bg-slate-700'
                    }`}
                  />
                );
              })}
            </div>

            {/* Live Detected Speech Bubble */}
            <div className="mt-4 px-4 py-2.5 rounded-xl bg-black/40 border border-slate-800 max-w-lg min-h-[44px] flex items-center justify-center text-center">
              <span className="text-xs sm:text-sm font-sans text-slate-200">
                {liveTranscript ? (
                  <span className="italic font-medium text-cyan-300">"{liveTranscript}"</span>
                ) : isListening ? (
                  <span className="text-slate-500 font-mono text-xs">
                    Listening for voice command... (e.g. "Safari kholo", "Volume 50 percent karo")
                  </span>
                ) : (
                  <span className="text-slate-500 font-mono text-xs">Mic is paused. Tap microphone to start.</span>
                )}
              </span>
            </div>
          </div>

          {/* Bottom Directive Manual Input */}
          <form onSubmit={handleManualSubmit} className="relative z-10 pt-4 border-t border-slate-800 flex gap-2">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Or type a command: 'Safari kholo', 'Volume 60 percent karo', 'Screenshot lo'..."
              className="flex-1 bg-slate-900/90 border border-slate-700 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-sans"
            />
            <button
              type="submit"
              disabled={commandMutation.isPending || !inputText.trim()}
              className="px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold text-xs font-mono transition flex items-center space-x-1.5 disabled:opacity-50"
            >
              {commandMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              <span>Execute</span>
            </button>
          </form>
        </div>

        {/* Right Column: Active Voices & Hardware Metrics */}
        <div className="rounded-2xl bg-[#0a0f1d]/90 border border-cyan-500/30 p-6 flex flex-col justify-between shadow-xl space-y-4">
          <div>
            <div className="flex items-center space-x-2 border-b border-slate-800 pb-3 mb-4">
              <Zap className="w-4 h-4 text-cyan-400" />
              <h2 className="text-xs font-mono font-semibold text-slate-200 uppercase tracking-wider">
                Dograh Voice Engine Specs
              </h2>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">Audio Pipeline:</span>
                <span className="text-cyan-300 font-semibold">Full-Duplex WS + Native</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">Speech Latency:</span>
                <span className="text-emerald-400 font-semibold">&lt; 25ms Hardware Say</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">Hindi Voice:</span>
                <span className="text-slate-200 font-semibold">{dograhStatus?.voices?.hindi || 'Lekha (hi_IN)'}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex justify-between items-center">
                <span className="text-slate-400">English Voice:</span>
                <span className="text-slate-200 font-semibold">{dograhStatus?.voices?.indian_english || 'Aman (en_IN)'}</span>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-950/20 to-slate-900 border border-cyan-500/20 space-y-2">
            <span className="text-xs font-mono font-bold text-cyan-300 block">
              ⚡ Instant Vocalization Active
            </span>
            <p className="text-[11px] text-slate-400 leading-relaxed font-sans">
              KYRON is optimized specifically for macOS. Voice commands bypass cloud audio latency and trigger native system calls directly via Dograh's streaming pipeline.
            </p>
          </div>
        </div>
      </div>

      {/* Quick Mac Voice Directives Chips */}
      <div className="rounded-2xl bg-[#0a0f1d]/90 border border-cyan-500/20 p-5 shadow-xl space-y-3">
        <span className="text-xs font-mono font-semibold text-cyan-400 tracking-wider uppercase block">
          One-Click Mac System Voice Directives (Or Speak Naturally)
        </span>
        <div className="flex flex-wrap gap-2.5">
          {quickDirectives.map((item, idx) => {
            const Icon = item.icon;
            return (
              <button
                key={idx}
                onClick={() => commandMutation.mutate(item.directive)}
                disabled={commandMutation.isPending}
                className="px-3.5 py-2 rounded-xl bg-slate-900/90 hover:bg-cyan-950/40 border border-slate-700/80 hover:border-cyan-500/50 text-xs font-mono text-slate-200 hover:text-cyan-300 transition-all flex items-center space-x-2 active:scale-95 disabled:opacity-50"
              >
                <Icon className="w-3.5 h-3.5 text-cyan-400" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Real-time Voice Directives Execution Log */}
      <div className="rounded-2xl bg-[#0a0f1d]/90 border border-slate-800 p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <Radio className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-mono font-semibold text-slate-200 uppercase tracking-wider">
              Recent Voice Command Telemetry Log
            </h3>
          </div>
          <span className="text-[11px] font-mono text-slate-500">Live Execution History</span>
        </div>

        <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
          {history.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs font-mono"
            >
              <div className="flex items-center space-x-3">
                <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[10px] font-bold">
                  {item.action}
                </span>
                <span className="text-slate-300 font-semibold font-sans">"{item.command}"</span>
              </div>

              <div className="flex items-center space-x-4">
                <span className="text-emerald-400 font-sans italic text-[11px]">
                  "{item.response}"
                </span>
                <span className="text-[10px] text-slate-500 px-2 py-0.5 rounded bg-slate-800">
                  ⚡ {item.latency_ms}ms
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
