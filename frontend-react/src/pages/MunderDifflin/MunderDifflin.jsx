import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Terminal, Monitor, ListTodo, HelpCircle, Zap, History, Database, Network, Activity, Wrench, Users, Plus, Mic, Send, MoreVertical, Layout, MousePointer2 } from 'lucide-react';
import './MunderDifflin.css';

const MunderDifflin = () => {
  const [repoPath, setRepoPath] = useState('');
  const [connectedRepo, setConnectedRepo] = useState('');
  const [workers, setWorkers] = useState([]);
  const [selectedWorkerId, setSelectedWorkerId] = useState(null);
  const [taskInput, setTaskInput] = useState('');
  const [backendType, setBackendType] = useState('CodeAgent');
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('terminal');

  // Fetch workers
  const fetchWorkers = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/kyron/coding/workers');
      if (res.data.success) {
        setWorkers(res.data.workers);
        if (res.data.connected_repo) setConnectedRepo(res.data.connected_repo);
      }
    } catch (err) {
      console.error("Failed to fetch workers", err);
    }
  };

  useEffect(() => {
    fetchWorkers();
    const interval = setInterval(fetchWorkers, 3000);
    return () => clearInterval(interval);
  }, []);

  // Fetch logs for selected worker
  useEffect(() => {
    let interval;
    if (selectedWorkerId) {
      const fetchLogs = async () => {
        try {
          const res = await axios.get(`http://localhost:8000/api/kyron/coding/logs/${selectedWorkerId}`);
          if (res.data.success) setLogs(res.data.logs);
        } catch (err) {
          console.error("Failed to fetch logs", err);
        }
      };
      fetchLogs();
      interval = setInterval(fetchLogs, 2000);
    }
    return () => { if (interval) clearInterval(interval); };
  }, [selectedWorkerId]);

  const handleConnectProject = async (e) => {
    if (e) e.preventDefault();
    if (!repoPath) return;
    try {
      const res = await axios.post('http://localhost:8000/api/kyron/coding/connect-project', { repo_path: repoPath });
      if (res.data.success) {
        setConnectedRepo(res.data.repo);
        setRepoPath('');
      }
    } catch (err) {
      alert("Failed to connect project: " + (err.response?.data?.detail || err.message));
    }
  };

  const handleDispatchTask = async (e) => {
    if (e) e.preventDefault();
    if (!taskInput || !connectedRepo) return;
    
    try {
      const res = await axios.post('http://localhost:8000/api/kyron/coding/dispatch', {
        task: taskInput,
        backend: backendType
      });
      if (res.data.success) {
        setTaskInput('');
        fetchWorkers();
        setSelectedWorkerId(res.data.worker_id);
        setActiveTab('terminal');
      }
    } catch (err) {
      alert("Failed to dispatch task: " + (err.response?.data?.detail || err.message));
    }
  };

  // Helper to determine status for pixel bubbles
  const getStatusBubble = (worker) => {
    if (worker.status === 'queued') return "idle";
    if (worker.status === 'running') return "fixing bug";
    if (worker.status === 'awaiting_approval') return "reviewing diff";
    if (worker.status === 'done') return "done";
    return "failed";
  };

  return (
    <div className="munder-difflin-container">
      {/* TOP BAR */}
      <div className="md-top-bar">
        <div className="flex items-center gap-3">
          <div className="w-5 h-5 bg-blue-600 rounded flex items-center justify-center text-white font-bold text-xs">M</div>
          <span className="font-bold text-gray-700">munder difflin</span>
          <span className="text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded text-[10px]">v0.4.4</span>
          <div className="flex items-center gap-1 ml-4 bg-gray-100 px-2 py-1 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-[10px] font-medium text-gray-600">auto mode on</span>
          </div>
        </div>
        
        <div className="flex items-center gap-4 text-gray-500">
          {!connectedRepo && (
            <div className="flex items-center gap-2">
              <input 
                type="text" 
                placeholder="Repo path..." 
                className="border border-gray-300 rounded px-2 py-0.5 text-xs outline-none"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleConnectProject()}
              />
              <button onClick={handleConnectProject} className="bg-blue-50 text-blue-600 border border-blue-200 px-2 py-0.5 rounded text-xs font-medium">Connect</button>
            </div>
          )}
          <MousePointer2 className="w-4 h-4 cursor-pointer hover:text-gray-800" />
          <Layout className="w-4 h-4 cursor-pointer hover:text-gray-800" />
          <Zap className="w-4 h-4 cursor-pointer hover:text-gray-800" />
          <MoreVertical className="w-4 h-4 cursor-pointer hover:text-gray-800" />
        </div>
      </div>

      <div className="md-main-layout">
        {/* LEFT/CENTER - PIXEL OFFICE */}
        <div className="md-office-view">
          <div className="md-office-grid">
            {/* Orchestrator Boss */}
            <div className="md-desk" style={{ top: '40px', left: '50px' }}>
              <div className="md-computer"></div>
              <div className="md-character md-boss" style={{ bottom: '10px', right: '-15px' }}>
                <div className="md-speech-bubble font-mono">BOSS working</div>
                M
              </div>
            </div>

            {/* Plants & Decor */}
            <div className="md-plant" style={{ top: '20px', right: '40px' }}></div>
            <div className="md-plant" style={{ bottom: '20px', left: '40px' }}></div>

            {/* Dynamic Workers */}
            {workers.map((w, idx) => {
              // Simple grid distribution
              const row = Math.floor(idx / 3);
              const col = idx % 3;
              const top = 160 + (row * 120);
              const left = 50 + (col * 160);
              
              return (
                <div key={w.worker_id} className="md-desk" style={{ top: `${top}px`, left: `${left}px` }}>
                  <div className="md-computer"></div>
                  <div className="md-character" style={{ bottom: '10px', right: '-10px', backgroundColor: w.backend === 'opencode' ? '#9b59b6' : '#ffb6c1' }}>
                    <div className="md-speech-bubble font-mono">{getStatusBubble(w)}</div>
                    W
                  </div>
                </div>
              );
            })}
          </div>

          {/* BOTTOM STRIP - WORKER TABS ROW */}
          <div className="md-workers-strip">
            {workers.map(w => (
              <div 
                key={w.worker_id} 
                className={`md-worker-card ${selectedWorkerId === w.worker_id ? 'active' : ''}`}
                onClick={() => setSelectedWorkerId(w.worker_id)}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold ${w.backend === 'opencode' ? 'bg-purple-500' : 'bg-pink-400'}`}>
                    W
                  </div>
                  <div className="flex flex-col">
                    <span className="font-bold text-xs text-gray-800">{w.worker_id.slice(-6)}</span>
                    <span className="text-[9px] text-gray-500 uppercase tracking-wide">{w.backend}</span>
                  </div>
                  <div className="ml-auto">
                    <div className={`w-2 h-2 rounded-full ${w.status === 'running' ? 'bg-blue-500' : w.status === 'awaiting_approval' ? 'bg-amber-500' : w.status === 'done' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                  </div>
                </div>
                <div className="text-[10px] text-gray-600 truncate mb-2">{w.task}</div>
                <div className="w-full bg-gray-200 h-1.5 rounded-full overflow-hidden">
                  <div className={`h-full ${w.status === 'done' ? 'bg-green-500 w-full' : w.status === 'awaiting_approval' ? 'bg-amber-500 w-3/4' : 'bg-blue-500 w-1/3'}`}></div>
                </div>
              </div>
            ))}
            {workers.length === 0 && (
              <div className="text-xs text-gray-400 flex items-center h-full px-4 italic">No active workers. Start a task to hire a worker.</div>
            )}
          </div>
        </div>

        {/* RIGHT PANEL - COMMAND CENTER */}
        <div className="md-command-center">
          {/* Header */}
          <div className="md-cc-header flex justify-between items-center bg-gray-50">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-gray-600" />
              <span className="font-bold tracking-tight text-gray-800">COMMAND CENTER</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1 text-[10px] text-gray-500">
                <span className="text-blue-500">●</span> working — Orchestrator runs...
              </div>
              <button className="bg-white border border-gray-300 text-[10px] px-2 py-0.5 rounded shadow-sm font-medium hover:bg-gray-50">IDE</button>
            </div>
          </div>

          {/* Tabs */}
          <div className="md-cc-tabs-container">
            <div className="md-tab-row">
              <div className={`md-tab ${activeTab === 'terminal' ? 'active' : ''}`} onClick={() => setActiveTab('terminal')}>Terminal</div>
              <div className={`md-tab ${activeTab === 'monitor' ? 'active' : ''}`} onClick={() => setActiveTab('monitor')}>Monitor</div>
              <div className={`md-tab ${activeTab === 'tasks' ? 'active' : ''}`} onClick={() => setActiveTab('tasks')}>Tasks</div>
              <div className={`md-tab ${activeTab === 'ask' ? 'active' : ''}`} onClick={() => setActiveTab('ask')}>Ask Me</div>
            </div>
            <div className="md-tab-row">
              <div className={`md-tab ${activeTab === 'triggers' ? 'active' : ''}`} onClick={() => setActiveTab('triggers')}>Triggers</div>
              <div className={`md-tab ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>History</div>
              <div className={`md-tab ${activeTab === 'memory' ? 'active' : ''}`} onClick={() => setActiveTab('memory')}>Memory</div>
              <div className={`md-tab ${activeTab === 'graph' ? 'active' : ''}`} onClick={() => setActiveTab('graph')}>Graph</div>
            </div>
            <div className="md-tab-row">
              <div className={`md-tab ${activeTab === 'activity' ? 'active' : ''}`} onClick={() => setActiveTab('activity')}>Activity</div>
              <div className={`md-tab ${activeTab === 'skills' ? 'active' : ''}`} onClick={() => setActiveTab('skills')}>Skills</div>
              <div className={`md-tab ${activeTab === 'workers' ? 'active' : ''}`} onClick={() => setActiveTab('workers')}>Workers</div>
            </div>
          </div>

          {/* MAIN AREA */}
          <div className="md-main-area">
            {activeTab === 'terminal' && (
              <div className="flex flex-col gap-1">
                <div className="text-gray-500 mb-2">// KYRON Orchestrator Stream Connected</div>
                {!selectedWorkerId ? (
                  <div className="text-gray-400">Select a worker from the bottom strip to view its isolated log stream.</div>
                ) : (
                  <>
                    <div className="text-blue-400 mb-2">$ tail -f .worktrees/{selectedWorkerId}/logs</div>
                    {logs.map((log, idx) => (
                      <div key={idx} className={
                        log.includes('FATAL') ? 'text-red-400' :
                        log.includes('Physical signature') ? 'text-green-400' :
                        log.includes('Awaiting') ? 'text-yellow-400' : 'text-gray-300'
                      }>
                        {log}
                      </div>
                    ))}
                    {workers.find(w => w.worker_id === selectedWorkerId)?.status === 'awaiting_approval' && (
                       <div className="mt-4 p-3 bg-yellow-900/30 border border-yellow-700 rounded flex flex-col gap-2">
                         <span className="text-yellow-400 font-bold">SAFETY GATE TRIGGERED</span>
                         <span className="text-gray-300">Action ID: {workers.find(w => w.worker_id === selectedWorkerId)?.action_id}</span>
                         <span className="text-gray-400 text-xs">Please review the diff in the Global Approvals Panel (Bottom Right) to provide physical signature.</span>
                       </div>
                    )}
                    <div className="w-2 h-4 bg-gray-400 animate-pulse mt-2"></div>
                  </>
                )}
              </div>
            )}

            {activeTab === 'workers' && (
              <div className="text-gray-300">
                <div className="font-bold text-white mb-4">Active Worker Instances</div>
                {workers.map(w => (
                  <div key={w.worker_id} className="mb-4 border-b border-gray-700 pb-2">
                    <div className="text-blue-400 font-bold">{w.worker_id}</div>
                    <div className="text-xs text-gray-400 mt-1">Backend: {w.backend}</div>
                    <div className="text-xs text-gray-400 mt-1">Status: <span className={w.status==='done'?'text-green-400':''}>{w.status}</span></div>
                    <div className="text-xs text-gray-500 mt-1 break-all">Worktree: {w.worktree_path}</div>
                  </div>
                ))}
              </div>
            )}
            
            {activeTab !== 'terminal' && activeTab !== 'workers' && (
              <div className="text-gray-500 italic text-center mt-10">
                [Data feed for {activeTab} wired to existing KYRON backend]
              </div>
            )}
          </div>

          {/* Context Usage Bar */}
          <div className="px-4 py-2 bg-gray-100 border-t border-gray-300 flex items-center justify-between text-[10px] text-gray-600 font-medium">
            <div className="flex items-center gap-2">
              <span>ctx 145k/1000k (14%)</span>
              <div className="w-16 h-1.5 bg-gray-300 rounded-full overflow-hidden">
                <div className="bg-blue-500 w-[14%] h-full"></div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-1 cursor-pointer">
                <input type="checkbox" className="accent-blue-600" />
                <span>bypass permissions</span>
              </label>
              <span>week 4</span>
            </div>
          </div>

          {/* Queue Box */}
          <div className="md-queue-box flex flex-col gap-2">
            <div className="flex justify-between items-center">
              <div className="flex gap-2">
                <select 
                  value={backendType}
                  onChange={(e) => setBackendType(e.target.value)}
                  className="text-[10px] border border-gray-300 rounded px-1 outline-none bg-white text-gray-600"
                >
                  <option value="CodeAgent">CodeAgent</option>
                  <option value="opencode">opencode</option>
                </select>
              </div>
              <span className="text-[10px] text-gray-400 font-medium italic">Orchestrator is busy — queue a message</span>
            </div>
            <div className="flex gap-2">
              <textarea 
                className="md-queue-input"
                rows="2"
                placeholder="Message or new task..."
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
              ></textarea>
            </div>
            <div className="flex justify-between items-center mt-1">
              <div className="flex gap-2">
                <button className="flex items-center gap-1 text-[11px] text-gray-600 bg-gray-100 hover:bg-gray-200 border border-gray-300 px-2 py-1 rounded">
                  <Plus className="w-3 h-3" /> files
                </button>
                <button className="flex items-center gap-1 text-[11px] text-gray-600 bg-gray-100 hover:bg-gray-200 border border-gray-300 px-2 py-1 rounded">
                  <Mic className="w-3 h-3" /> voice
                </button>
              </div>
              <button 
                onClick={handleDispatchTask}
                disabled={!connectedRepo || !taskInput}
                className="flex items-center gap-1 text-[11px] text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 px-3 py-1 rounded font-bold transition-colors shadow-sm"
              >
                <Send className="w-3 h-3" /> SEND
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default MunderDifflin;
