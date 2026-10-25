import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PhoneCall,
  PhoneForwarded,
  Settings,
  User,
  Radio,
  CheckCircle2,
  Save,
  Mic,
  Volume2,
  Smartphone,
  ShieldCheck,
  Zap,
  Globe,
  Plus,
  RefreshCw,
  ExternalLink,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../../services/api';

export default function MacCallingSetupSidebar() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [dialing, setDialing] = useState(false);
  const [activeCall, setActiveCall] = useState(null);

  // Calling Setup State
  const [setup, setSetup] = useState({
    user_phone: '+91 98350 78219',
    user_name: 'Asif Aslam (Sonu Sarkar)',
    caller_id: '+91 80000 59766',
    carrier_gateway: 'Twilio Voice & WebRTC SIP Trunk',
    voice_tone: 'Sonu Sarkar Personal & High-Agency Tone',
    auto_recording: true,
    noise_cancellation: true,
    sip_status: 'Connected • 18ms Latency',
    verified: true,
    country_code: '+91',
    speed_dial: [
      { name: 'Sonu (Self / Personal Mobile)', phone: '+91 98350 78219', role: 'Owner' },
      { name: 'Rohit Kumar (Fleet & Ops Lead)', phone: '+91 98101 44520', role: 'BookMyGaadi Lead' },
      { name: 'Rahul Dev (Senior Engineer)', phone: '+91 98765 11200', role: 'KYRON Tech' },
      { name: 'Client Priority Hotline', phone: '+91 99341 55621', role: 'VIP Client' }
    ]
  });

  // Dialer State
  const [targetPhone, setTargetPhone] = useState('');
  const [targetName, setTargetName] = useState('');
  const [callPurpose, setCallPurpose] = useState('');
  const [triggerMacOsCall, setTriggerMacOsCall] = useState(true);
  const [expandedSection, setExpandedSection] = useState('dialer'); // 'dialer' | 'setup' | 'speed_dial'

  // Fetch Setup from Backend
  const fetchSetup = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/kyron/calls/setup');
      if (res.data?.success && res.data.setup) {
        setSetup(res.data.setup);
      }
    } catch (e) {
      console.debug('Failed to load call setup:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSetup();
  }, []);

  // Save Setup
  const handleSaveSetup = async () => {
    try {
      setSaving(true);
      const res = await api.post('/api/kyron/calls/setup', { setup });
      if (res.data?.success) {
        toast.success('Calling setup & user number saved successfully!');
      }
    } catch (e) {
      toast.error('Failed to save calling setup');
    } finally {
      setSaving(false);
    }
  };

  // Dial Real-time Call
  const handleDialCall = async (phoneToDial = null, nameToDial = null, purposeToDial = null) => {
    const finalPhone = phoneToDial || targetPhone;
    const finalName = nameToDial || targetName || 'Direct Contact';
    const finalPurpose = purposeToDial || callPurpose || 'Real-time Telephony Call with Sonu Sarkar';

    if (!finalPhone || !finalPhone.trim()) {
      toast.error('Please enter a phone number to dial');
      return;
    }

    try {
      setDialing(true);
      const res = await api.post('/api/kyron/calls/dial', {
        target_phone: finalPhone.trim(),
        caller_name: finalName,
        purpose: finalPurpose,
        trigger_macos_call: triggerMacOsCall
      });

      if (res.data?.success) {
        setActiveCall(res.data.active_call);
        toast.success(res.data.voice_vocalization || `Real-time call placed to ${finalPhone}!`);
        // Notify MacCallSupportPanel in center workspace
        window.dispatchEvent(new CustomEvent('kyron:call_updated'));
      }
    } catch (e) {
      toast.error('Failed to dial real-time call');
    } finally {
      setDialing(false);
    }
  };

  // End Active Call
  const handleEndCall = async () => {
    try {
      const res = await api.post('/api/kyron/calls/end');
      if (res.data?.success) {
        setActiveCall(null);
        toast.success('Call ended and recorded in CRM logs');
        window.dispatchEvent(new CustomEvent('kyron:call_updated'));
      }
    } catch (e) {
      toast.error('Failed to end call');
    }
  };

  return (
    <div className="space-y-3 select-none">
      {/* 1. TOP STATUS BADGE */}
      <div className="rounded-2xl bg-gradient-to-br from-emerald-950/60 via-slate-900/90 to-[#0c1424] border border-emerald-500/30 p-3.5 shadow-xl backdrop-blur-xl">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <PhoneCall className="w-4 h-4 animate-pulse" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-white tracking-wide flex items-center gap-1.5">
                Real-Time Calling Setup
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              </h3>
              <p className="text-[10px] text-emerald-400/80 font-mono">
                {setup.sip_status || 'SIP Online • 18ms Latency'}
              </p>
            </div>
          </div>
          <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-500/40">
            Caller ID Verified
          </span>
        </div>

        <div className="grid grid-cols-2 gap-1.5 mt-2 pt-2 border-t border-white/5 text-[10px]">
          <div className="flex items-center gap-1 text-slate-300">
            <Smartphone className="w-3 h-3 text-cyan-400 shrink-0" />
            <span className="truncate">{setup.user_phone || '+91 98350 78219'}</span>
          </div>
          <div className="flex items-center gap-1 text-slate-300 justify-end">
            <Radio className="w-3 h-3 text-emerald-400 shrink-0" />
            <span className="truncate">WebRTC 48kHz</span>
          </div>
        </div>
      </div>

      {/* 2. REAL-TIME OUTBOUND DIALER */}
      <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-3.5 shadow-xl backdrop-blur-xl">
        <div 
          onClick={() => setExpandedSection(expandedSection === 'dialer' ? null : 'dialer')}
          className="flex items-center justify-between cursor-pointer mb-2.5"
        >
          <div className="flex items-center gap-2">
            <PhoneForwarded className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              Real-Time Outbound Dialer
            </span>
          </div>
          {expandedSection === 'dialer' ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          )}
        </div>

        {expandedSection === 'dialer' && (
          <div className="space-y-2.5">
            <div>
              <label className="text-[10px] text-slate-400 font-medium block mb-1">
                Target Phone Number (Direct Dial)
              </label>
              <div className="flex items-center gap-1.5">
                <input
                  type="text"
                  placeholder="+91 98350 XXXXX"
                  value={targetPhone}
                  onChange={(e) => setTargetPhone(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleDialCall()}
                  className="flex-1 bg-black/40 border border-white/10 focus:border-emerald-500/50 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 outline-none font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-slate-400 font-medium block mb-1">
                  Recipient Name
                </label>
                <input
                  type="text"
                  placeholder="e.g. Rajesh / Client"
                  value={targetName}
                  onChange={(e) => setTargetName(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 focus:border-cyan-500/50 rounded-xl px-2.5 py-1.5 text-xs text-white placeholder-slate-500 outline-none"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 font-medium block mb-1">
                  Purpose / Intent
                </label>
                <input
                  type="text"
                  placeholder="e.g. Booking / Demo"
                  value={callPurpose}
                  onChange={(e) => setCallPurpose(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 focus:border-cyan-500/50 rounded-xl px-2.5 py-1.5 text-xs text-white placeholder-slate-500 outline-none"
                />
              </div>
            </div>

            <label className="flex items-center gap-2 text-[10px] text-slate-300 cursor-pointer pt-0.5">
              <input
                type="checkbox"
                checked={triggerMacOsCall}
                onChange={(e) => setTriggerMacOsCall(e.target.checked)}
                className="accent-emerald-500 rounded"
              />
              <span>Trigger macOS Phone / FaceTime Cellular Relay</span>
            </label>

            {/* DIAL BUTTON */}
            <button
              onClick={() => handleDialCall()}
              disabled={dialing || !targetPhone.trim()}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-500 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-emerald-950/50 disabled:opacity-50 disabled:cursor-not-allowed transition transform active:scale-95 cursor-pointer"
            >
              {dialing ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Connecting Real-time SIP...</span>
                </>
              ) : (
                <>
                  <PhoneCall className="w-3.5 h-3.5" />
                  <span>DIAL REAL-TIME CALL NOW</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* 3. USER PHONE & NUMBER CONFIGURATION BOX */}
      <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-3.5 shadow-xl backdrop-blur-xl">
        <div 
          onClick={() => setExpandedSection(expandedSection === 'setup' ? null : 'setup')}
          className="flex items-center justify-between cursor-pointer mb-2.5"
        >
          <div className="flex items-center gap-2">
            <Settings className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              Caller ID & Number Setup
            </span>
          </div>
          {expandedSection === 'setup' ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          )}
        </div>

        {expandedSection === 'setup' && (
          <div className="space-y-2.5">
            <div>
              <label className="text-[10px] text-slate-400 font-medium block mb-1">
                Aapka Primary Phone Number (User Number)
              </label>
              <input
                type="text"
                value={setup.user_phone}
                onChange={(e) => setSetup({ ...setup, user_phone: e.target.value })}
                placeholder="+91 98350 78219"
                className="w-full bg-black/40 border border-white/10 focus:border-cyan-500/50 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-500 outline-none font-mono"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] text-slate-400 font-medium block mb-1">
                  Caller Name
                </label>
                <input
                  type="text"
                  value={setup.user_name}
                  onChange={(e) => setSetup({ ...setup, user_name: e.target.value })}
                  placeholder="Asif Aslam (Sonu Sarkar)"
                  className="w-full bg-black/40 border border-white/10 focus:border-cyan-500/50 rounded-xl px-2.5 py-1.5 text-xs text-white placeholder-slate-500 outline-none"
                />
              </div>
              <div>
                <label className="text-[10px] text-slate-400 font-medium block mb-1">
                  Outbound Caller ID
                </label>
                <input
                  type="text"
                  value={setup.caller_id}
                  onChange={(e) => setSetup({ ...setup, caller_id: e.target.value })}
                  placeholder="+91 80000 59766"
                  className="w-full bg-black/40 border border-white/10 focus:border-cyan-500/50 rounded-xl px-2.5 py-1.5 text-xs text-white placeholder-slate-500 outline-none font-mono"
                />
              </div>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 font-medium block mb-1">
                Telephony Gateway / Carrier Provider
              </label>
              <select
                value={setup.carrier_gateway}
                onChange={(e) => setSetup({ ...setup, carrier_gateway: e.target.value })}
                className="w-full bg-black/40 border border-white/10 focus:border-cyan-500/50 rounded-xl px-2.5 py-1.5 text-xs text-white outline-none"
              >
                <option value="Twilio Voice & WebRTC SIP Trunk">Twilio Voice & WebRTC SIP Trunk (Default)</option>
                <option value="Exotel India Enterprise SIP">Exotel India Enterprise SIP (Local +91 Numbers)</option>
                <option value="Plivo Voice Cloud">Plivo Voice Cloud</option>
                <option value="macOS iPhone Cellular Continuity Relay">macOS iPhone Cellular Continuity Relay</option>
              </select>
            </div>

            <div>
              <label className="text-[10px] text-slate-400 font-medium block mb-1">
                AI Voice Persona (Calling Tone)
              </label>
              <select
                value={setup.voice_tone}
                onChange={(e) => setSetup({ ...setup, voice_tone: e.target.value })}
                className="w-full bg-black/40 border border-white/10 focus:border-cyan-500/50 rounded-xl px-2.5 py-1.5 text-xs text-white outline-none"
              >
                <option value="Sonu Sarkar Personal & High-Agency Tone">Sonu Sarkar Personal & High-Agency Tone (Hindi/Hinglish)</option>
                <option value="BookMyGaadi 24/7 Priority Cab Booking AI">BookMyGaadi 24/7 Priority Cab Booking AI</option>
                <option value="KYRON Enterprise Sub-25ms Architecture Support">KYRON Enterprise Sub-25ms Architecture Support</option>
              </select>
            </div>

            {/* Hardware Toggles */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              <label className="flex items-center gap-1.5 text-[10px] text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={setup.auto_recording}
                  onChange={(e) => setSetup({ ...setup, auto_recording: e.target.checked })}
                  className="accent-indigo-500 rounded"
                />
                <span>Auto-Record Calls</span>
              </label>
              <label className="flex items-center gap-1.5 text-[10px] text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={setup.noise_cancellation}
                  onChange={(e) => setSetup({ ...setup, noise_cancellation: e.target.checked })}
                  className="accent-indigo-500 rounded"
                />
                <span>Voice Isolation</span>
              </label>
            </div>

            {/* Save Setup Button */}
            <button
              onClick={handleSaveSetup}
              disabled={saving}
              className="w-full py-2 rounded-xl bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/40 text-indigo-200 font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer"
            >
              {saving ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
              <span>{saving ? 'Saving Setup...' : 'Save Telephony Preferences'}</span>
            </button>
          </div>
        )}
      </div>

      {/* 4. SPEED DIAL CONTACTS */}
      <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-3.5 shadow-xl backdrop-blur-xl">
        <div 
          onClick={() => setExpandedSection(expandedSection === 'speed_dial' ? null : 'speed_dial')}
          className="flex items-center justify-between cursor-pointer mb-2"
        >
          <div className="flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">
              Speed Dial & Quick Contacts
            </span>
          </div>
          {expandedSection === 'speed_dial' ? (
            <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
          ) : (
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          )}
        </div>

        {expandedSection === 'speed_dial' && (
          <div className="space-y-1.5 mt-2">
            {setup.speed_dial?.map((contact, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-2 rounded-xl bg-black/30 border border-white/5 hover:border-emerald-500/30 transition group"
              >
                <div>
                  <div className="text-xs font-semibold text-slate-200">{contact.name}</div>
                  <div className="text-[10px] text-slate-400 font-mono">{contact.phone} • {contact.role}</div>
                </div>
                <button
                  onClick={() => handleDialCall(contact.phone, contact.name, `Priority call to ${contact.name}`)}
                  disabled={dialing}
                  className="p-1.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/40 text-emerald-300 transition cursor-pointer"
                  title={`Dial ${contact.name}`}
                >
                  <PhoneCall className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
