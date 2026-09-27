import { useState, useEffect } from 'react';
import { Play, Square, Pause, RefreshCw, AlertCircle, CheckCircle, Loader, X } from 'lucide-react';
import toast from 'react-hot-toast';

export default function AutomationControlPanel({ 
  sessionId, 
  status, 
  onStop, 
  onPause, 
  onResume,
  onRefresh,
  currentStep,
  error,
  onDismissError
}) {
  const [isMinimized, setIsMinimized] = useState(false);

  const getStatusColor = () => {
    switch (status) {
      case 'running':
      case 'processing':
        return 'text-green-600 bg-green-50';
      case 'paused':
        return 'text-yellow-600 bg-yellow-50';
      case 'stopped':
      case 'error':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-blue-600 bg-blue-50';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'running':
      case 'processing':
        return <Loader className="w-4 h-4 animate-spin" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      case 'stopped':
        return <Square className="w-4 h-4" />;
      case 'error':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <CheckCircle className="w-4 h-4" />;
    }
  };

  if (!sessionId) return null;

  return (
    <div
      className={`fixed bottom-4 right-4 z-50 bg-white rounded-xl shadow-2xl border border-gray-200 transition-all duration-300 ${
        isMinimized ? 'w-64' : 'w-80'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${status === 'running' ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="font-semibold text-gray-900">KYRON Control</span>
        </div>
        <button
          onClick={() => setIsMinimized(!isMinimized)}
          className="text-gray-400 hover:text-gray-600 transition"
        >
          {isMinimized ? '↑' : '↓'}
        </button>
      </div>

      {!isMinimized && (
        <>
          {/* Status */}
          <div className="p-4 border-b border-gray-200">
            <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${getStatusColor()}`}>
              {getStatusIcon()}
              <span className="text-sm font-medium capitalize">{status || 'Ready'}</span>
            </div>
            {currentStep && (
              <p className="text-xs text-gray-600 mt-2">{currentStep}</p>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border-l-4 border-red-500">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <AlertCircle className="w-4 h-4 text-red-600" />
                    <span className="text-sm font-medium text-red-900">Action Required</span>
                  </div>
                  <p className="text-sm text-red-700">{error.message}</p>
                  {error.action && (
                    <button
                      onClick={error.onAction}
                      className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition"
                    >
                      {error.action}
                    </button>
                  )}
                </div>
                <button
                  onClick={onDismissError}
                  className="text-red-400 hover:text-red-600 ml-2"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Controls */}
          <div className="p-4 space-y-2">
            <div className="grid grid-cols-2 gap-2">
              {status === 'running' || status === 'processing' ? (
                <>
                  <button
                    onClick={onPause}
                    className="flex items-center justify-center space-x-2 px-4 py-2 border border-yellow-300 text-yellow-700 rounded-lg hover:bg-yellow-50 transition"
                  >
                    <Pause className="w-4 h-4" />
                    <span className="text-sm">Pause</span>
                  </button>
                  <button
                    onClick={onStop}
                    className="flex items-center justify-center space-x-2 px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition"
                  >
                    <Square className="w-4 h-4" />
                    <span className="text-sm">Stop</span>
                  </button>
                </>
              ) : status === 'paused' ? (
                <>
                  <button
                    onClick={onResume}
                    className="flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition col-span-2"
                  >
                    <Play className="w-4 h-4" />
                    <span className="text-sm">Resume</span>
                  </button>
                </>
              ) : (
                <button
                  onClick={onRefresh}
                  className="flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition col-span-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span className="text-sm">Refresh</span>
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

