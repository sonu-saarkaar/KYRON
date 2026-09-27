import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Layers, X, Loader2, CheckCircle2 } from 'lucide-react';
import ActionPreviewCard from './ActionPreviewCard';
import { DiffCard } from './MissionCards';
import api from '../../services/api';

/**
 * Unified Approval Panel
 * Central dashboard for all KYRON pending actions across CODE, SYSTEM, and BROWSER agents.
 * Connects to Master Orchestrator queue.
 */
export default function UnifiedApprovalPanel({ isOpen, onClose }) {
  const [pendingActions, setPendingActions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [processingId, setProcessingId] = useState(null);

  const fetchQueue = async () => {
    try {
      const res = await api.get('/kyron/orchestrator/queue');
      setPendingActions(res.data.pending_actions || []);
    } catch (err) {
      console.error("Failed to fetch unified queue:", err);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchQueue();
      // Auto-refresh queue every 10 seconds while open
      const interval = setInterval(fetchQueue, 10000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  // Deep-link check for Windows Toast Notification
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const actionId = urlParams.get('action_id');
    if (actionId) {
      // Auto-open panel if deep linked
      if (!isOpen && typeof onClose === 'function') {
        // Tricky: we don't have openPanel prop here, so this logic 
        // might be better in App.jsx or Chat.jsx which controls the panel.
        // We will just scroll to it if it is open.
      }
      setTimeout(() => {
        const el = document.getElementById(`action-${actionId}`);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          el.classList.add('ring-2', 'ring-cyan-400', 'ring-offset-2', 'ring-offset-slate-900');
          setTimeout(() => el.classList.remove('ring-2', 'ring-cyan-400', 'ring-offset-2', 'ring-offset-slate-900'), 3000);
        }
      }, 500);
    }
  }, [pendingActions, isOpen]);

  const handleConfirm = async (actionId, agentType) => {
    setProcessingId(actionId);
    try {
      let endpoint = '';
      if (agentType === 'CODE') endpoint = '/kyron/code-agent/command'; // Or create a specific confirm route if needed
      else if (agentType === 'SYSTEM') endpoint = '/kyron/system-control/confirm';
      else if (agentType === 'BROWSER') endpoint = '/kyron/browser/confirm';

      if (agentType === 'CODE') {
          // CodeAgent API handles apply via /command with apply=True
          const action = pendingActions.find(a => a.action_id === actionId);
          if (action) {
              await api.post('/kyron/code-agent/command', {
                  target_file: action.payload.target_file,
                  task: action.payload.task,
                  apply: true
              });
          }
      } else {
          await api.post(endpoint, {
            action_id: actionId,
            confirmed: true
          });
      }
      // Remove from list
      setPendingActions(prev => prev.filter(a => a.action_id !== actionId));
    } catch (err) {
      console.error(`Failed to confirm action ${actionId}:`, err);
    }
    setProcessingId(null);
  };

  const handleReject = async (actionId, agentType) => {
    setProcessingId(actionId);
    try {
      if (agentType === 'SYSTEM') {
        await api.post('/kyron/system-control/confirm', { action_id: actionId, confirmed: false });
      } else if (agentType === 'BROWSER') {
        await api.post('/kyron/browser/confirm', { action_id: actionId, confirmed: false });
      }
      setPendingActions(prev => prev.filter(a => a.action_id !== actionId));
    } catch (err) {
      console.error(`Failed to reject action ${actionId}:`, err);
    }
    setProcessingId(null);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 300 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 300 }}
        className="fixed top-0 right-0 h-full w-full max-w-md bg-slate-950/95 border-l border-white/10 shadow-2xl z-50 overflow-y-auto backdrop-blur-xl flex flex-col"
      >
        <div className="p-4 border-b border-white/10 flex items-center justify-between sticky top-0 bg-slate-950/90 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-100 font-mono tracking-wider">APPROVAL QUEUE</h2>
              <div className="text-[10px] text-slate-400 font-mono">{pendingActions.length} Actions Pending</div>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-white/5 text-slate-400 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 p-4 space-y-4">
          {pendingActions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-500 font-mono text-sm">
              <CheckCircle2 className="w-8 h-8 mb-3 opacity-20" />
              <div>Queue is empty</div>
              <div className="text-[10px] mt-1 opacity-60">All safety gates are clear</div>
            </div>
          ) : (
            pendingActions.map(action => {
              const { action_id, agent_type, payload } = action;
              const isProcessing = processingId === action_id;

              if (agent_type === 'CODE') {
                return (
                  <div key={action_id} id={`action-${action_id}`} className="scroll-mt-20">
                    <DiffCard
                      targetFile={payload.target_file}
                      diff={payload.diff}
                      testResult="N/A"
                      onApply={() => handleConfirm(action_id, 'CODE')}
                      onReject={() => handleReject(action_id, 'CODE')}
                      isApplying={isProcessing}
                      applied={false}
                    />
                  </div>
                );
              } else {
                return (
                  <div key={action_id} id={`action-${action_id}`} className="scroll-mt-20">
                    <ActionPreviewCard
                      actionId={action_id}
                      type={agent_type === 'BROWSER' ? 'browser' : 'system'}
                      app={payload.app || payload.page_title || 'Application'}
                      target={payload.target_contact || payload.website}
                      description={payload.description || payload.content}
                      onConfirm={() => handleConfirm(action_id, agent_type)}
                      onReject={() => handleReject(action_id, agent_type)}
                      isConfirming={isProcessing}
                      status="pending_confirmation"
                    />
                  </div>
                );
              }
            })
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
