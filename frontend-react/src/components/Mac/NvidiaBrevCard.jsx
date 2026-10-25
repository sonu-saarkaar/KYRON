import React, { useState, useEffect } from "react";
import { 
  Cpu, 
  ShieldCheck, 
  Brain, 
  Video, 
  ExternalLink, 
  Terminal, 
  CheckCircle2, 
  Zap, 
  Play, 
  Layers, 
  Sparkles,
  Server,
  CloudLightning,
  X
} from "lucide-react";

export default function NvidiaBrevCard({ onDirectAction, onClose }) {
  const [status, setStatus] = useState(null);
  const [launchables, setLaunchables] = useState([]);
  const [loading, setLoading] = useState(true);
  const [launchingKey, setLaunchingKey] = useState(null);
  const [launchResult, setLaunchResult] = useState(null);
  const [testCode, setTestCode] = useState("import math\nprint('NemoClaw Sandbox OK! sqrt(256) =', math.sqrt(256))");
  const [sandboxOutput, setSandboxOutput] = useState(null);
  const [runningSandbox, setRunningSandbox] = useState(false);

  useEffect(() => {
    fetchStatus();
    fetchLaunchables();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/brev/status");
      const data = await res.json();
      setStatus(data);
    } catch (e) {
      console.error("Failed to load Brev status", e);
    } finally {
      setLoading(false);
    }
  };

  const fetchLaunchables = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/brev/launchables");
      const data = await res.json();
      if (data.launchables) {
        setLaunchables(data.launchables);
      }
    } catch (e) {
      console.error("Failed to load launchables", e);
    }
  };

  const handleLaunch = async (key) => {
    setLaunchingKey(key);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/brev/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ launchable_key: key })
      });
      const data = await res.json();
      setLaunchResult(data);
    } catch (e) {
      console.error("Launch error", e);
    } finally {
      setLaunchingKey(null);
    }
  };

  const handleRunSandbox = async () => {
    setRunningSandbox(true);
    setSandboxOutput(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/brev/sandbox/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: testCode, language: "python" })
      });
      const data = await res.json();
      setSandboxOutput(data);
    } catch (e) {
      setSandboxOutput({ success: false, error: String(e) });
    } finally {
      setRunningSandbox(false);
    }
  };

  const getIconForCategory = (key) => {
    switch (key) {
      case "nemoclaw":
        return <ShieldCheck className="w-5 h-5 text-[#76B900]" />;
      case "hermes":
        return <Brain className="w-5 h-5 text-emerald-400" />;
      case "video_summarizer":
        return <Video className="w-5 h-5 text-cyan-400" />;
      case "isaac_sim":
        return <Cpu className="w-5 h-5 text-amber-400" />;
      case "build_agent":
        return <Terminal className="w-5 h-5 text-purple-400" />;
      default:
        return <Layers className="w-5 h-5 text-[#76B900]" />;
    }
  };

  return (
    <div className="rounded-2xl border border-[#76B900]/30 bg-black/60 backdrop-blur-xl p-5 shadow-2xl text-white mb-6 transition-all hover:border-[#76B900]/50">
      {/* Header with NVIDIA Signature Green Glow */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#76B900]/30 to-[#76B900]/10 border border-[#76B900]/50 flex items-center justify-center shadow-[0_0_15px_rgba(118,185,0,0.3)]">
            <CloudLightning className="w-6 h-6 text-[#76B900]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="font-bold text-lg tracking-wide text-white">NVIDIA Brev Cloud GPU Stack</h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#76B900]/20 text-[#76B900] border border-[#76B900]/40 flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#76B900] animate-pulse"></span>
                <span>Active</span>
              </span>
            </div>
            <p className="text-xs text-white/60">
              NemoClaw Sandbox • Hermes Brain • NVIDIA NIM (Sub-30ms TensorRT-LLM)
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <a
            href="https://brev.nvidia.com"
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg text-xs font-medium bg-white/5 hover:bg-white/10 text-white/80 border border-white/10 flex items-center space-x-1 transition-all"
          >
            <span>Brev Console</span>
            <ExternalLink className="w-3 h-3 text-white/50" />
          </a>

          {onClose && (
            <button
              onClick={onClose}
              className="px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-white/10 hover:bg-rose-500/20 text-slate-300 hover:text-rose-300 border border-white/15 hover:border-rose-500/40 flex items-center space-x-1 transition-all"
              title="Close NVIDIA Brev Dashboard"
            >
              <X className="w-3.5 h-3.5" />
              <span>Close</span>
            </button>
          )}
        </div>
      </div>

      {/* Diagnostics Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <div className="bg-white/5 border border-white/10 rounded-xl p-3">
          <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1 font-mono">Brev CLI</div>
          <div className="text-sm font-semibold text-white flex items-center space-x-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#76B900]" />
            <span className="truncate">{status?.cli_version ? "v0.6.337" : "Installed"}</span>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-xl p-3">
          <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1 font-mono">Cloud Health</div>
          <div className="text-sm font-semibold text-[#76B900] flex items-center space-x-1.5">
            <Server className="w-3.5 h-3.5 text-[#76B900]" />
            <span>{status?.cloud_health || "Healthy"}</span>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-xl p-3">
          <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1 font-mono">NVIDIA NIM</div>
          <div className="text-sm font-semibold text-emerald-400 flex items-center space-x-1.5">
            <Zap className="w-3.5 h-3.5 text-emerald-400" />
            <span>TensorRT Ready</span>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 rounded-xl p-3">
          <div className="text-[10px] text-white/50 uppercase tracking-wider mb-1 font-mono">Sandbox Runtime</div>
          <div className="text-sm font-semibold text-cyan-400 flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span>NemoClaw</span>
          </div>
        </div>
      </div>

      {/* Launchable Grid */}
      <div className="mb-5">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-semibold text-white/80 uppercase tracking-wider font-mono flex items-center space-x-2">
            <Sparkles className="w-3.5 h-3.5 text-[#76B900]" />
            <span>NVIDIA Launchables Catalog (1-Click Deployment)</span>
          </h4>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {launchables.map((item) => (
            <div
              key={item.key}
              className="group relative bg-white/[0.03] hover:bg-white/[0.08] border border-white/10 hover:border-[#76B900]/50 rounded-xl p-4 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between mb-2">
                  <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                    {getIconForCategory(item.key)}
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-white/5 border border-white/10 text-white/60">
                    {item.recommended_gpu}
                  </span>
                </div>

                <h5 className="font-semibold text-sm text-white group-hover:text-[#76B900] transition-colors mb-1">
                  {item.name}
                </h5>
                <p className="text-xs text-white/50 line-clamp-2 mb-3 leading-relaxed">
                  {item.description}
                </p>
              </div>

              <div className="flex items-center space-x-2 pt-2 border-t border-white/5">
                <button
                  onClick={() => handleLaunch(item.key)}
                  disabled={launchingKey === item.key}
                  className="flex-1 py-1.5 px-3 rounded-lg text-xs font-medium bg-[#76B900]/20 hover:bg-[#76B900]/30 text-[#76B900] border border-[#76B900]/40 flex items-center justify-center space-x-1.5 transition-all disabled:opacity-50"
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>{launchingKey === item.key ? "Preparing..." : "Deploy"}</span>
                </button>

                <a
                  href={`https://brev.nvidia.com/launchable/deploy?launchableID=${item.id}`}
                  target="_blank"
                  rel="noreferrer"
                  className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-white/60 hover:text-white border border-white/10 transition-all"
                  title="Open in Brev Cloud"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Launch Confirmation Banner */}
      {launchResult && (
        <div className="mb-5 p-4 rounded-xl bg-[#76B900]/10 border border-[#76B900]/30 text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-[#76B900] flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-[#76B900]" />
              <span>{launchResult.launchable?.name} Launchable Prepared</span>
            </span>
            <a
              href={launchResult.browser_url}
              target="_blank"
              rel="noreferrer"
              className="px-2.5 py-1 rounded bg-[#76B900] text-black font-semibold flex items-center space-x-1 hover:bg-[#88d600] transition-all"
            >
              <span>Deploy on Brev</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <div className="font-mono text-white/70 bg-black/40 p-2 rounded border border-white/10 truncate">
            {launchResult.launch_command}
          </div>
        </div>
      )}

      {/* NemoClaw OpenShell Sandbox Quick Runner */}
      <div className="bg-white/[0.02] border border-white/10 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-[#76B900]" />
            <span className="text-xs font-semibold text-white">NemoClaw Isolated Code Sandbox</span>
          </div>
          <button
            onClick={handleRunSandbox}
            disabled={runningSandbox}
            className="px-3 py-1 rounded-lg text-xs font-semibold bg-[#76B900] text-black hover:bg-[#88d600] flex items-center space-x-1.5 transition-all disabled:opacity-50"
          >
            <Play className="w-3 h-3 fill-current" />
            <span>{runningSandbox ? "Executing..." : "Run in Sandbox"}</span>
          </button>
        </div>

        <textarea
          value={testCode}
          onChange={(e) => setTestCode(e.target.value)}
          rows={2}
          className="w-full bg-black/60 border border-white/10 rounded-lg p-2.5 font-mono text-xs text-white/90 focus:outline-none focus:border-[#76B900]/60 resize-none mb-2"
          placeholder="Enter Python code to test in NemoClaw sandbox..."
        />

        {sandboxOutput && (
          <div className="p-3 rounded-lg bg-black/80 border border-white/10 font-mono text-xs">
            <div className="flex items-center justify-between mb-1 text-[10px] text-white/50 border-b border-white/10 pb-1">
              <span>SANDBOX STDOUT ({sandboxOutput.elapsed_ms}ms)</span>
              <span className={sandboxOutput.success ? "text-[#76B900]" : "text-red-400"}>
                {sandboxOutput.success ? "EXIT 0 (SUCCESS)" : "EXIT CODE ERROR"}
              </span>
            </div>
            <pre className="text-emerald-400 whitespace-pre-wrap">{sandboxOutput.stdout || sandboxOutput.stderr || sandboxOutput.error}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
