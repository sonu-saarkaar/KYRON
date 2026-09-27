import { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, RefreshCw, Monitor, Square } from 'lucide-react';
import { automationAPI, screenShareAPI, voiceAPI, agentAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function AutomationViewer({ sessionId, language, onClose, useAgentAPI = true }) {
  const [showScreenShare, setShowScreenShare] = useState(false);
  const [screenShareSessionId, setScreenShareSessionId] = useState(null);
  const lastSpokenAction = useRef('');

  // Get session details (optimized polling)
  const { data: sessionDetails } = useQuery({
    queryKey: useAgentAPI ? ['agent-session', sessionId] : ['automation-session', sessionId],
    queryFn: () => useAgentAPI 
      ? agentAPI.getSession(sessionId)
      : automationAPI.getSession(sessionId),
    enabled: !!sessionId,
    refetchInterval: 3000, // Reduced from 2000 to 3000ms
    staleTime: 2000,
  });

  // Get screenshot (optimized - screenshots are heavy)
  const { data: screenshotData, refetch: refetchScreenshot } = useQuery({
    queryKey: useAgentAPI ? ['agent-screenshot', sessionId] : ['screenshot', sessionId],
    queryFn: () => useAgentAPI
      ? agentAPI.getScreenshot(sessionId)
      : automationAPI.getScreenshot(sessionId),
    enabled: !!sessionId,
    refetchInterval: 5000, // Increased from 3000 to 5000ms
    staleTime: 3000,
  });

  // Get screen share screenshot
  const { data: screenShareScreenshot } = useQuery({
    queryKey: ['screen-share-screenshot', screenShareSessionId],
    queryFn: () => screenShareAPI.getScreenshot(screenShareSessionId),
    enabled: !!screenShareSessionId,
    refetchInterval: 2000,
  });

  const handleStop = async () => {
    try {
      if (useAgentAPI) {
        await agentAPI.stop(sessionId);
      } else {
        await automationAPI.closeSession(sessionId);
      }
      toast.success(language === 'hi' ? 'स्वचालन रोक दिया गया' : 'Automation stopped');
      onClose();
    } catch (error) {
      toast.error('Failed to stop automation');
    }
  };

  const handleScreenShare = async () => {
    try {
      const result = await screenShareAPI.createSession('automatic');
      setScreenShareSessionId(result.session_id);
      setShowScreenShare(true);
    } catch (error) {
      toast.error('Failed to start screen sharing');
    }
  };

  const session = sessionDetails?.session || sessionDetails;
  const currentAction = session?.current_action || (language === 'hi' ? 'प्रसंस्करण...' : 'Processing...');
  
  // REMOVED: Auto-speak is now disabled by default
  // User can manually trigger speech if needed

  return (
    <div className="border-t border-gray-200 bg-white">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900">
              {language === 'hi' ? 'स्वचालन दृश्य' : 'Automation View'}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <p className="text-sm text-gray-600">{currentAction}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleScreenShare}
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center space-x-2 text-sm"
            >
              <Monitor className="w-4 h-4" />
              <span>{language === 'hi' ? 'स्क्रीन शेयर' : 'Screen Share'}</span>
            </button>
            <button
              onClick={() => refetchScreenshot()}
              className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={handleStop}
              className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition flex items-center space-x-2 text-sm"
            >
              <Square className="w-4 h-4" />
              <span>{language === 'hi' ? 'रोकें' : 'Stop'}</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Screenshot */}
        {screenshotData?.screenshot && (
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <img
              src={`data:image/png;base64,${screenshotData.screenshot}`}
              alt="Automation"
              className="w-full"
            />
          </div>
        )}

        {/* Screen Share */}
        {showScreenShare && screenShareScreenshot?.screenshot && (
          <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
              <p className="text-sm font-medium text-gray-700">
                {language === 'hi' ? 'लाइव स्क्रीन शेयर' : 'Live Screen Share'}
              </p>
            </div>
            <img
              src={`data:image/png;base64,${screenShareScreenshot.screenshot}`}
              alt="Screen Share"
              className="w-full"
            />
          </div>
        )}

        {/* Progress */}
        {session?.progress && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">
                {language === 'hi' ? 'प्रगति' : 'Progress'}
              </span>
              <span className="text-sm text-gray-600">
                {session.progress.step} / {session.progress.total}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(session.progress.step / session.progress.total) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

