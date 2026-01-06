import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, Play, Pause, Square, HelpCircle, Monitor, 
  ChevronLeft, ChevronRight, ExternalLink, Volume2 
} from 'lucide-react';
import { agentAPI, voiceAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function FloatingAgentControl({ 
  sessionId, 
  language = 'en',
  onClose 
}) {
  const [isMinimized, setIsMinimized] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  // Get session status (optimized polling)
  const { data: sessionData } = useQuery({
    queryKey: ['agent-session', sessionId],
    queryFn: () => agentAPI.getSession(sessionId),
    enabled: !!sessionId,
    refetchInterval: 3000, // Reduced from 2000 to 3000ms
    staleTime: 2000, // Consider data fresh for 2 seconds
  });

  const session = sessionData?.session || {};
  const status = session.status || 'idle';
  const currentAction = session.current_action || '';
  const progress = session.progress || { step: 0, total: 0 };
  const officialUrl = session.official_url;

  const getStatusColor = () => {
    switch (status) {
      case 'active':
      case 'filling':
      case 'analyzing':
        return 'bg-green-500';
      case 'paused':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      case 'completed':
        return 'bg-blue-500';
      case 'payment_required':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'active':
        return language === 'hi' ? 'सक्रिय' : 'Active';
      case 'analyzing':
        return language === 'hi' ? 'विश्लेषण' : 'Analyzing';
      case 'filling':
        return language === 'hi' ? 'भर रहा है' : 'Filling';
      case 'paused':
        return language === 'hi' ? 'रोका गया' : 'Paused';
      case 'error':
        return language === 'hi' ? 'त्रुटि' : 'Error';
      case 'completed':
        return language === 'hi' ? 'पूर्ण' : 'Completed';
      case 'payment_required':
        return language === 'hi' ? 'भुगतान आवश्यक' : 'Payment Required';
      default:
        return language === 'hi' ? 'निष्क्रिय' : 'Idle';
    }
  };

  const handlePause = async () => {
    try {
      await agentAPI.pause(sessionId);
      toast.success(language === 'hi' ? 'रोक दिया गया' : 'Paused');
    } catch (error) {
      toast.error('Failed to pause');
    }
  };

  const handleResume = async () => {
    try {
      await agentAPI.resume(sessionId);
      toast.success(language === 'hi' ? 'फिर से शुरू' : 'Resumed');
    } catch (error) {
      toast.error('Failed to resume');
    }
  };

  const handleStop = async () => {
    try {
      await agentAPI.stop(sessionId);
      toast.success(language === 'hi' ? 'रोक दिया गया' : 'Stopped');
      onClose();
    } catch (error) {
      toast.error('Failed to stop');
    }
  };

  const handleExplain = async () => {
    const explanation = language === 'hi'
      ? `KYRON वर्तमान में ${currentAction || 'प्रक्रिया कर रहा है'}। यह वास्तविक आधिकारिक वेबसाइट पर काम कर रहा है।`
      : `KYRON is currently ${currentAction || 'processing'}. It's working on the real official website.`;
    
    toast.info(explanation);
    try {
      await voiceAPI.speak(explanation, language);
    } catch (error) {
      console.error('TTS failed:', error);
    }
  };

  const handleScreenShare = () => {
    toast.info(language === 'hi' ? 'स्क्रीन शेयर मोड जल्द ही उपलब्ध होगा' : 'Screen share mode coming soon');
  };

  // Minimized view
  if (isMinimized) {
    return (
      <motion.div
        className="fixed bottom-4 right-4 z-[9999] cursor-pointer"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => setIsMinimized(false)}
      >
        <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-full shadow-2xl flex items-center justify-center relative">
          <span className="text-white font-bold text-2xl">K</span>
          <div className={`absolute -top-1 -right-1 w-4 h-4 ${getStatusColor()} rounded-full border-2 border-white animate-pulse`} />
        </div>
      </motion.div>
    );
  }

  // Expanded view
  return (
    <motion.div
      className="fixed bottom-4 right-4 z-[9999] bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden"
      initial={{ opacity: 0, y: 50, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 50, scale: 0.9 }}
      style={{ width: isExpanded ? '380px' : '320px' }}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
            <span className="text-purple-600 font-bold text-lg">K</span>
          </div>
          <div>
            <h3 className="text-white font-bold text-sm">KYRON Agent</h3>
            <p className="text-purple-100 text-xs">Real-world execution</p>
          </div>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setIsMinimized(true)}
            className="p-1.5 hover:bg-white/20 rounded-lg transition"
          >
            <ChevronRight className="w-4 h-4 text-white" />
          </button>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-white/20 rounded-lg transition"
          >
            <X className="w-4 h-4 text-white" />
          </button>
        </div>
      </div>

      {/* Status */}
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${getStatusColor()} animate-pulse`} />
            <span className="text-sm font-medium text-gray-700">{getStatusText()}</span>
          </div>
          {officialUrl && (
            <a
              href={officialUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-purple-600 hover:text-purple-700 flex items-center space-x-1"
            >
              <ExternalLink className="w-3 h-3" />
              <span>View Site</span>
            </a>
          )}
        </div>
        {currentAction && (
          <p className="text-xs text-gray-600 mt-1 line-clamp-2">{currentAction}</p>
        )}
        {progress.total > 0 && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>{language === 'hi' ? 'प्रगति' : 'Progress'}</span>
              <span>{progress.step} / {progress.total}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-gradient-to-r from-purple-600 to-indigo-600 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${(progress.step / progress.total) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="px-4 py-3">
        <div className="grid grid-cols-4 gap-2">
          {status === 'paused' ? (
            <button
              onClick={handleResume}
              className="flex flex-col items-center justify-center p-2 bg-green-50 hover:bg-green-100 rounded-lg transition text-sm text-green-700"
            >
              <Play className="w-5 h-5 mb-1" />
              <span className="text-xs">{language === 'hi' ? 'जारी' : 'Resume'}</span>
            </button>
          ) : (
            <button
              onClick={handlePause}
              className="flex flex-col items-center justify-center p-2 bg-yellow-50 hover:bg-yellow-100 rounded-lg transition text-sm text-yellow-700"
            >
              <Pause className="w-5 h-5 mb-1" />
              <span className="text-xs">{language === 'hi' ? 'रोकें' : 'Pause'}</span>
            </button>
          )}
          <button
            onClick={handleStop}
            className="flex flex-col items-center justify-center p-2 bg-red-50 hover:bg-red-100 rounded-lg transition text-sm text-red-700"
          >
            <Square className="w-5 h-5 mb-1" />
            <span className="text-xs">{language === 'hi' ? 'बंद' : 'Stop'}</span>
          </button>
          <button
            onClick={handleExplain}
            className="flex flex-col items-center justify-center p-2 bg-blue-50 hover:bg-blue-100 rounded-lg transition text-sm text-blue-700"
          >
            <HelpCircle className="w-5 h-5 mb-1" />
            <span className="text-xs">{language === 'hi' ? 'समझाएं' : 'Explain'}</span>
          </button>
          <button
            onClick={handleScreenShare}
            className="flex flex-col items-center justify-center p-2 bg-gray-50 hover:bg-gray-100 rounded-lg transition text-sm text-gray-700"
          >
            <Monitor className="w-5 h-5 mb-1" />
            <span className="text-xs">{language === 'hi' ? 'शेयर' : 'Share'}</span>
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
        <p className="text-xs text-gray-600 text-center">
          {language === 'hi' 
            ? 'KYRON वास्तविक वेबसाइट पर काम कर रहा है' 
            : 'KYRON is working on the real website'}
        </p>
      </div>
    </motion.div>
  );
}

