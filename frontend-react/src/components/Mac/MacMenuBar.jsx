import React, { useState, useEffect } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Wifi,
  Battery,
  Sparkles,
  Command,
  Globe,
  Radio,
  Sliders,
  Bell
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function MacMenuBar({
  isListening,
  toggleListening,
  isSpeaking,
  stopSpeaking,
  isMuted,
  toggleMute,
  audioLevel,
  selectedLanguage,
  setVoiceLanguage,
  triggerWakeup,
  onOpenApprovalQueue
}) {
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const options = {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      setCurrentTime(now.toLocaleString('en-US', options));
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-8 bg-[#0a0f18]/90 backdrop-blur-2xl border-b border-white/10 px-3 flex items-center justify-between text-xs text-slate-300 select-none z-30 shrink-0">
      {/* Left: Apple / Kyron Logo & macOS Application Menus */}
      <div className="flex items-center gap-4">
        {/* Kyron Apple Icon */}
        <div
          onClick={triggerWakeup}
          className="cursor-pointer flex items-center gap-1.5 hover:text-white transition font-bold text-cyan-400 group"
          title="Click to trigger Kyron wake-up"
        >
          <div className="w-4 h-4 rounded-full bg-gradient-to-tr from-cyan-400 to-indigo-500 flex items-center justify-center text-[9px] text-slate-950 font-black shadow-sm group-hover:scale-110 transition-transform">
            ⚡
          </div>
          <span className="font-semibold text-white tracking-tight">KyronOS</span>
        </div>

        {/* Mac Menus */}
        <div className="hidden sm:flex items-center gap-3 text-slate-400 text-[11px] font-medium">
          <button
            onClick={() => toast('Kyron AGI v2.0 Tahoe Edition running with Dograh Voice')}
            className="hover:text-white transition"
          >
            Tasks
          </button>
          <button
            onClick={() => toast('Connected to WhatsApp Web & Instagram Direct')}
            className="hover:text-white transition"
          >
            Social
          </button>
          <button
            onClick={() => toast('Hermes Memory Manager: Master Profile & Persona Active')}
            className="hover:text-white transition"
          >
            Memory
          </button>
          <button
            onClick={() => toast('Chrome Playwright Viewport Mirror Active')}
            className="hover:text-white transition"
          >
            Mirror
          </button>
          <button
            onClick={() => toast('macOS Native System Control: Volume, Dark Mode, Apps')}
            className="hover:text-white transition"
          >
            System
          </button>
        </div>
      </div>

      {/* Right: Mac Status Area / Control Center Widgets */}
      <div className="flex items-center gap-2.5">
        {/* Wispr Audio Level Visualizer */}
        <div
          onClick={triggerWakeup}
          className="cursor-pointer flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-[10px] font-mono hover:bg-cyan-900/50 transition"
          title="Audio sensitivity level. Say 'Hey Kyron' or clap to wake"
        >
          <div className="flex items-end gap-0.5 h-2.5 w-3">
            <span
              className="w-0.5 bg-cyan-400 rounded-full transition-all duration-75"
              style={{ height: `${Math.max(2, (audioLevel * 10) / 100)}px` }}
            />
            <span
              className="w-0.5 bg-emerald-400 rounded-full transition-all duration-75"
              style={{ height: `${Math.max(3, (audioLevel * 12) / 100)}px` }}
            />
            <span
              className="w-0.5 bg-cyan-400 rounded-full transition-all duration-75"
              style={{ height: `${Math.max(1.5, (audioLevel * 8) / 100)}px` }}
            />
          </div>
          <span className="hidden md:inline">
            {isListening ? 'Wispr Active' : 'Wispr Mic'}
          </span>
        </div>

        {/* Mic Toggle Button */}
        <button
          onClick={toggleListening}
          className={`px-2 py-0.5 rounded-md flex items-center gap-1 text-[11px] transition ${
            isListening
              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
              : 'text-slate-400 hover:text-white'
          }`}
          title={isListening ? 'Mic Active' : 'Mic Off'}
        >
          {isListening ? (
            <>
              <Mic className="w-3 h-3 text-emerald-400 animate-pulse" />
              <span className="hidden sm:inline font-mono">ON</span>
            </>
          ) : (
            <>
              <MicOff className="w-3 h-3" />
              <span className="hidden sm:inline font-mono">OFF</span>
            </>
          )}
        </button>

        {/* Language Switcher */}
        <button
          onClick={() => {
            const next = selectedLanguage === 'hi-IN' ? 'en-IN' : 'hi-IN';
            setVoiceLanguage(next);
            toast.success(next === 'hi-IN' ? 'Listening in 🇮🇳 Hindi/Hinglish' : 'Listening in 🌐 English');
          }}
          className="px-2 py-0.5 rounded-md bg-white/[0.04] hover:bg-white/[0.08] text-[11px] font-mono text-slate-300 transition"
          title="Toggle recognition language"
        >
          {selectedLanguage === 'hi-IN' ? '🇮🇳 HI' : '🌐 EN'}
        </button>

        {/* Stop Speech / Active Speaker Pill */}
        {isSpeaking && (
          <button
            onClick={stopSpeaking}
            className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-rose-500/20 border border-rose-500/40 text-rose-300 text-[10px] font-bold animate-pulse"
            title="Stop speaking"
          >
            <VolumeX className="w-3 h-3 text-rose-400" />
            <span>Stop (ESC)</span>
          </button>
        )}

        {/* Mute TTS Speaker */}
        <button
          onClick={toggleMute}
          className="p-1 rounded text-slate-400 hover:text-white transition"
          title={isMuted ? 'Unmute Speaker' : 'Mute Speaker'}
        >
          {isMuted ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
        </button>

        {/* macOS WiFi & Battery icons */}
        <div className="flex items-center gap-1 text-slate-400">
          <Wifi className="w-3.5 h-3.5" />
          <Battery className="w-3.5 h-3.5" />
        </div>

        {/* Real-Time Clock */}
        <span className="font-medium text-slate-300 text-[11px] tracking-tight pl-1">
          {currentTime || 'Sun 25 Oct 04:25 AM'}
        </span>
      </div>
    </header>
  );
}
