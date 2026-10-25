import React from 'react';
import {
  Battery,
  BatteryCharging,
  Zap,
  Volume2,
  VolumeX,
  Monitor,
  Cpu,
  Layers,
  Activity,
  CheckCircle2,
  Clock,
  Sparkles
} from 'lucide-react';

export default function MacSystemStatusCard({ action }) {
  const result = action?.result || action || {};
  const batteryPct = result.battery || 'Unknown';
  const isCharging = !!result.is_charging;
  const health = result.battery_health || '100%';
  const condition = result.battery_condition || 'Normal';
  const cycles = result.cycle_count ?? 0;
  const timeRemaining = result.time_remaining || '';
  const frontApp = result.frontmost_app || 'macOS';
  const volume = result.output_volume ?? 50;
  const isMuted = !!result.muted;
  const runningApps = result.running_apps || [];
  const appCount = result.running_apps_count || runningApps.length;

  const pctNum = parseInt(batteryPct.replace('%', ''), 10) || 50;
  const batteryColor =
    pctNum > 50 ? 'text-emerald-400' : pctNum > 20 ? 'text-amber-400' : 'text-rose-400';
  const batteryBg =
    pctNum > 50 ? 'bg-emerald-500' : pctNum > 20 ? 'bg-amber-500' : 'bg-rose-500';

  return (
    <div className="mt-3 p-4 rounded-2xl bg-gradient-to-br from-[#0a1220]/95 via-[#0e192c]/90 to-[#121c30]/95 border border-cyan-500/30 shadow-2xl backdrop-blur-xl text-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-cyan-400 animate-pulse" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
              <span>macOS Apple Silicon Hardware Status</span>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-mono border border-cyan-500/30">
                Live Telemetry
              </span>
            </h4>
            <span className="text-[10px] text-slate-400">
              Native hardware diagnostics queried via pmset & ioreg
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1 text-[11px] font-mono font-bold text-emerald-400 bg-emerald-950/70 px-2.5 py-1 rounded-full border border-emerald-500/30">
          <Activity className="w-3 h-3 text-emerald-400 animate-pulse" />
          <span>Optimal</span>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mb-3">
        {/* Battery Card */}
        <div className="p-3 rounded-xl bg-black/30 border border-white/5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              {isCharging ? (
                <BatteryCharging className="w-3.5 h-3.5 text-amber-400" />
              ) : (
                <Battery className={`w-3.5 h-3.5 ${batteryColor}`} />
              )}
              <span>Battery Power</span>
            </span>
            <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${isCharging ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-slate-800 text-slate-300'}`}>
              {isCharging ? 'Charging' : 'On Battery'}
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <span className={`text-2xl font-black font-mono tracking-tight ${batteryColor}`}>
              {batteryPct}
            </span>
            {timeRemaining && (
              <span className="text-[10px] text-slate-400 font-mono">
                {timeRemaining}
              </span>
            )}
          </div>

          {/* Progress bar */}
          <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
            <div
              className={`h-full ${batteryBg} transition-all duration-500`}
              style={{ width: `${Math.min(pctNum, 100)}%` }}
            />
          </div>

          {/* Battery Health details */}
          <div className="pt-1 border-t border-white/5 flex items-center justify-between text-[10px] text-slate-400 font-mono">
            <span>Health: <strong className="text-emerald-400">{health}</strong></span>
            <span>Cycles: <strong className="text-white">{cycles}</strong></span>
          </div>
        </div>

        {/* Volume & Audio Card */}
        <div className="p-3 rounded-xl bg-black/30 border border-white/5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              {isMuted ? (
                <VolumeX className="w-3.5 h-3.5 text-rose-400" />
              ) : (
                <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
              )}
              <span>Output Audio</span>
            </span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-cyan-950/60 text-cyan-300 border border-cyan-500/30">
              {isMuted ? 'Muted' : 'Active'}
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-black font-mono text-cyan-400 tracking-tight">
              {isMuted ? '0%' : `${volume}%`}
            </span>
            <span className="text-[10px] text-slate-400 font-mono">
              Tara Voice ready
            </span>
          </div>

          <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
            <div
              className="h-full bg-cyan-500 transition-all duration-500"
              style={{ width: `${isMuted ? 0 : Math.min(volume, 100)}%` }}
            />
          </div>

          <div className="pt-1 border-t border-white/5 text-[10px] text-slate-400 font-mono flex items-center justify-between">
            <span>TTS Engine: <strong className="text-cyan-300">Apple Tara</strong></span>
          </div>
        </div>

        {/* Frontmost App & Workspace Card */}
        <div className="p-3 rounded-xl bg-black/30 border border-white/5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Monitor className="w-3.5 h-3.5 text-purple-400" />
              <span>Active App</span>
            </span>
            <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-purple-950/60 text-purple-300 border border-purple-500/30">
              {appCount} Running
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <span className="text-lg font-bold text-white tracking-tight truncate max-w-[140px]">
              {frontApp}
            </span>
            <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-0.5">
              <CheckCircle2 className="w-3 h-3" />
              Front
            </span>
          </div>

          <div className="pt-2 border-t border-white/5 text-[10px] text-slate-400 font-mono truncate">
            Workspace: <span className="text-slate-200">KYRON AGI Hands-Free</span>
          </div>
        </div>
      </div>

      {/* Running Apps List */}
      {runningApps.length > 0 && (
        <div className="p-2.5 rounded-xl bg-black/20 border border-white/5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Layers className="w-3 h-3 text-cyan-400" />
              <span>Running Applications ({runningApps.length})</span>
            </span>
            <span className="text-[9px] text-slate-500 font-mono">macOS WindowServer</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {runningApps.map((app, i) => (
              <span
                key={i}
                className={`text-[10px] font-medium px-2 py-0.5 rounded-lg border transition ${
                  app === frontApp
                    ? 'bg-purple-500/20 text-purple-200 border-purple-500/40 shadow-sm shadow-purple-950/50'
                    : 'bg-slate-900/60 text-slate-300 border-white/5 hover:border-white/10'
                }`}
              >
                {app}
                {app === frontApp && <span className="ml-1 text-[8px] text-purple-400 font-bold">•</span>}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
