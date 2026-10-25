import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PhoneCall,
  PhoneIncoming,
  PhoneOff,
  User,
  Volume2,
  CheckCircle2,
  Clock,
  Sparkles,
  MapPin,
  Car,
  Bot,
  Layers,
  Smile,
  Radio,
  FileText,
  Search,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function MacCallSupportPanel() {
  const [activeCall, setActiveCall] = useState(null);
  const [callHistory, setCallHistory] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [selectedLog, setSelectedLog] = useState(null);

  // Audio wave animation state
  const [audioWaves, setAudioWaves] = useState([12, 24, 18, 30, 15, 28, 20]);

  // Fetch call history
  const fetchCalls = async () => {
    try {
      const res = await api.get('/api/kyron/calls/history');
      if (res.data?.success && res.data.data) {
        setActiveCall(res.data.data.active_call);
        setCallHistory(res.data.data.call_history || []);
        setMetrics(res.data.data.metrics);
      }
    } catch (e) {
      console.debug('Error loading call history:', e);
    }
  };

  useEffect(() => {
    fetchCalls();
    const handleUpdate = () => fetchCalls();
    window.addEventListener('kyron:call_updated', handleUpdate);

    const interval = setInterval(() => {
      // Animate simulated audio levels
      setAudioWaves([
        Math.floor(Math.random() * 24) + 8,
        Math.floor(Math.random() * 32) + 12,
        Math.floor(Math.random() * 20) + 10,
        Math.floor(Math.random() * 36) + 14,
        Math.floor(Math.random() * 28) + 10,
        Math.floor(Math.random() * 30) + 12,
        Math.floor(Math.random() * 22) + 8
      ]);
    }, 200);

    const pollInterval = setInterval(fetchCalls, 3000);

    return () => {
      window.removeEventListener('kyron:call_updated', handleUpdate);
      clearInterval(interval);
      clearInterval(pollInterval);
    };
  }, []);

  // Simulate inbound call
  const handleSimulateCall = async (type) => {
    try {
      setIsSimulating(true);
      const res = await api.post('/api/kyron/calls/simulate', { caller_type: type });
      if (res.data?.success) {
        setActiveCall(res.data.active_call);
        toast.success(res.data.voice_vocalization || 'Inbound call connected!');
        window.dispatchEvent(new CustomEvent('kyron:call_updated'));
      }
    } catch (e) {
      toast.error('Call simulation error');
    } finally {
      setIsSimulating(false);
    }
  };

  // End active call
  const handleEndCall = async () => {
    try {
      const res = await api.post('/api/kyron/calls/end');
      if (res.data?.success) {
        setActiveCall(null);
        toast.success('Call ended and recorded in CRM logs!');
        fetchCalls();
        window.dispatchEvent(new CustomEvent('kyron:call_updated'));
      }
    } catch (e) {
      toast.error('Error ending call');
    }
  };

  return (
    <div className="flex flex-col h-full bg-[#090e1a] text-slate-200 select-none overflow-hidden">
      {/* Top Telephony Control Bar */}
      <div className="p-4 border-b border-white/10 bg-slate-900/60 backdrop-blur-xl flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-600 flex items-center justify-center text-white shadow-lg shadow-emerald-950/40">
            <PhoneCall className="w-5 h-5 animate-bounce" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white tracking-wide">
                KYRON AI Call Support Center
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-500/40 font-bold">
                24/7 AUTONOMOUS TELEPHONY
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Inbound & Outbound Voice Agent for BookMyGaadi & KYRON AGI
            </p>
          </div>
        </div>

        {/* Quick Simulation Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleSimulateCall('ride_booking')}
            disabled={isSimulating || !!activeCall}
            className="px-3 py-1.5 rounded-xl bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
          >
            <Car className="w-3.5 h-3.5" />
            <span>Simulate Ride Call (BookMyGaadi)</span>
          </button>

          <button
            onClick={() => handleSimulateCall('enterprise_kyron')}
            disabled={isSimulating || !!activeCall}
            className="px-3 py-1.5 rounded-xl bg-cyan-600/30 hover:bg-cyan-600/50 text-cyan-300 border border-cyan-500/40 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
          >
            <Bot className="w-3.5 h-3.5" />
            <span>Simulate Enterprise Demo Call</span>
          </button>
        </div>
      </div>

      {/* Main Container */}
      <div className="flex-1 overflow-y-auto p-4 custom-scrollbar space-y-4">
        {/* KPI Metrics Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: 'Total Calls Today', value: metrics?.total_calls_today || '14', color: 'emerald' },
            { label: 'Autonomous Resolution Rate', value: metrics?.resolution_rate || '98.4%', color: 'cyan' },
            { label: 'Average Handle Time', value: metrics?.avg_duration || '2m 18s', color: 'indigo' },
            { label: 'Customer CSAT Score', value: metrics?.customer_satisfaction || '4.92 / 5.0', color: 'purple' }
          ].map((m, idx) => (
            <div key={idx} className="p-3 rounded-2xl bg-slate-900/50 border border-white/10 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 block font-mono uppercase">{m.label}</span>
                <span className="text-base font-bold text-white font-mono">{m.value}</span>
              </div>
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            </div>
          ))}
        </div>

        {/* ACTIVE CALL WORKSPACE */}
        <AnimatePresence>
          {activeCall ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className="p-5 rounded-3xl bg-gradient-to-br from-[#0d1d2f]/95 via-[#0e273c]/90 to-[#081525]/95 border border-emerald-500/50 shadow-2xl backdrop-blur-2xl"
            >
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 mb-4 border-b border-white/10">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-12 h-12 rounded-2xl bg-emerald-500 flex items-center justify-center text-slate-950 font-black text-lg">
                      {activeCall.caller_name[0]}
                    </div>
                    <span className="absolute -inset-1 rounded-2xl border-2 border-emerald-400 animate-ping pointer-events-none"></span>
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-white">{activeCall.caller_name}</h3>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-500/30 font-bold">
                        LIVE CALL CONNECTED
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 font-mono">
                      {activeCall.caller_phone} • {activeCall.caller_location}
                    </p>
                  </div>
                </div>

                {/* Soundwave Visualizer & End Call */}
                <div className="flex items-center gap-4">
                  {/* Live Equalizer Bars */}
                  <div className="flex items-end gap-1 h-8 px-3 py-1 bg-black/40 rounded-xl border border-white/10">
                    {audioWaves.map((h, i) => (
                      <span
                        key={i}
                        className="w-1.5 bg-gradient-to-t from-emerald-500 to-cyan-400 rounded-full transition-all duration-150"
                        style={{ height: `${h}px` }}
                      />
                    ))}
                  </div>

                  <button
                    onClick={handleEndCall}
                    className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold shadow-lg shadow-rose-950/40 flex items-center gap-2 transition"
                  >
                    <PhoneOff className="w-4 h-4" />
                    <span>Conclude Call & Log</span>
                  </button>
                </div>
              </div>

              {/* Call Details Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4 text-xs">
                <div className="p-3 rounded-xl bg-black/30 border border-white/5">
                  <span className="text-[10px] text-slate-400 block font-mono uppercase mb-0.5">Venture</span>
                  <span className="text-white font-bold">{activeCall.venture}</span>
                </div>
                <div className="p-3 rounded-xl bg-black/30 border border-white/5">
                  <span className="text-[10px] text-slate-400 block font-mono uppercase mb-0.5">Customer Intent</span>
                  <span className="text-cyan-300 font-semibold">{activeCall.intent}</span>
                </div>
                <div className="p-3 rounded-xl bg-black/30 border border-white/5">
                  <span className="text-[10px] text-slate-400 block font-mono uppercase mb-0.5">Customer Sentiment</span>
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <Smile className="w-3.5 h-3.5" />
                    <span>{activeCall.sentiment}</span>
                  </span>
                </div>
              </div>

              {/* Real-Time Live Transcript Stream */}
              <div className="p-4 rounded-2xl bg-black/50 border border-white/10 space-y-2.5">
                <div className="flex items-center justify-between pb-2 border-b border-white/5 text-[10px] font-mono text-slate-400">
                  <span className="flex items-center gap-1.5 text-cyan-300 font-bold">
                    <Radio className="w-3.5 h-3.5 animate-pulse" />
                    LIVE CONVERSATION TRANSCRIPT (WHISPER / WISPR STREAM)
                  </span>
                  <span>Latency: 22ms</span>
                </div>

                <div className="space-y-2 max-h-52 overflow-y-auto custom-scrollbar pr-2 text-xs">
                  {activeCall.transcript?.map((turn, idx) => {
                    const isAi = turn.speaker.includes('Kyron');
                    return (
                      <div
                        key={idx}
                        className={`p-2.5 rounded-xl border flex flex-col gap-1 ${
                          isAi
                            ? 'bg-cyan-950/30 border-cyan-500/30 text-cyan-100 ml-4'
                            : 'bg-slate-900/40 border-white/5 text-slate-200 mr-4'
                        }`}
                      >
                        <div className="flex items-center justify-between text-[10px] font-mono">
                          <span className={`font-bold ${isAi ? 'text-cyan-400' : 'text-slate-400'}`}>
                            {turn.speaker}
                          </span>
                          <span className="text-slate-500">{turn.time}</span>
                        </div>
                        <p className="text-xs leading-relaxed">{turn.text}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          ) : (
            /* Standby Card when no call is active */
            <div className="p-6 rounded-3xl bg-slate-900/40 border border-white/10 text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mx-auto text-emerald-400">
                <PhoneIncoming className="w-6 h-6 animate-pulse" />
              </div>
              <h3 className="text-sm font-bold text-white">Call Support System Armed & Listening</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                No active caller at this moment. Simulated calls or inbound telephone connections for BookMyGaadi and KYRON AGI will appear here in real-time.
              </p>
            </div>
          )}
        </AnimatePresence>

        {/* CALL LOGS & CRM HISTORY TABLE */}
        <div className="p-4 rounded-2xl bg-slate-900/50 border border-white/10 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-white/10">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
                Recent Customer Telephony CRM Logs ({callHistory.length})
              </h4>
            </div>
          </div>

          <div className="space-y-2">
            {callHistory.map((call) => (
              <div
                key={call.id}
                onClick={() => setSelectedLog(selectedLog?.id === call.id ? null : call)}
                className="p-3 rounded-xl bg-black/30 border border-white/5 hover:border-cyan-500/30 cursor-pointer transition text-xs"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-slate-800 flex items-center justify-center font-bold text-[11px] text-cyan-300">
                      {call.caller_name[0]}
                    </div>
                    <div>
                      <span className="font-bold text-white block">{call.caller_name}</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {call.caller_phone} • {call.caller_location}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 font-mono text-[10px]">
                    <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300">
                      {call.venture}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 font-bold border border-emerald-500/30">
                      {call.duration}
                    </span>
                    <span className="text-slate-500">{call.timestamp}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-300 pt-1 border-t border-white/5">
                  <span className="text-cyan-300 font-medium truncate max-w-[70%]">
                    {call.intent}
                  </span>
                  <span className="text-emerald-400 font-bold font-mono text-[10px]">
                    ✓ {call.resolution}
                  </span>
                </div>

                {/* Expanded Transcript Viewer */}
                {selectedLog?.id === call.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-3 pt-3 border-t border-white/10 space-y-2"
                  >
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-mono">
                      Recorded Dialogue Transcript
                    </span>
                    <div className="space-y-1.5 bg-black/40 p-2.5 rounded-lg border border-white/5">
                      {call.transcript?.map((t, i) => (
                        <div key={i} className="text-[11px] flex gap-2">
                          <span className="font-bold text-cyan-400 font-mono shrink-0">{t.speaker}:</span>
                          <span className="text-slate-300">{t.text}</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
