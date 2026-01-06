import { useState } from 'react';
import { X, Square, HelpCircle, Monitor, ChevronDown, ChevronUp } from 'lucide-react';

export default function KyronFloatingLogo({ 
  onStop, 
  onExplain, 
  onScreenShare,
  isMinimized = false,
  onToggleMinimize
}) {
  const [showMenu, setShowMenu] = useState(false);

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 left-4 z-50">
        <button
          onClick={onToggleMinimize}
          className="w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-full shadow-lg hover:shadow-xl transition flex items-center justify-center text-white group"
        >
          <span className="text-xl font-bold">K</span>
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 left-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl border border-gray-200 w-64">
        {/* Header */}
        <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-t-xl p-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
              <span className="text-purple-600 font-bold text-lg">K</span>
            </div>
            <div>
              <h3 className="text-white font-bold text-sm">KYRON</h3>
              <p className="text-purple-100 text-xs">AI Assistant</p>
            </div>
          </div>
          <button
            onClick={onToggleMinimize}
            className="text-white hover:text-purple-200 transition"
          >
            <ChevronDown className="w-4 h-4" />
          </button>
        </div>

        {/* Menu */}
        <div className="p-3 space-y-2">
          <button
            onClick={() => {
              setShowMenu(false);
              onStop?.();
            }}
            className="w-full flex items-center space-x-3 px-4 py-3 bg-red-50 hover:bg-red-100 rounded-lg transition text-left group"
          >
            <Square className="w-5 h-5 text-red-600 group-hover:text-red-700" />
            <div>
              <p className="font-medium text-gray-900 text-sm">Stop Automation</p>
              <p className="text-xs text-gray-500">Pause the current process</p>
            </div>
          </button>

          <button
            onClick={() => {
              setShowMenu(false);
              onExplain?.();
            }}
            className="w-full flex items-center space-x-3 px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg transition text-left group"
          >
            <HelpCircle className="w-5 h-5 text-blue-600 group-hover:text-blue-700" />
            <div>
              <p className="font-medium text-gray-900 text-sm">Explain Step</p>
              <p className="text-xs text-gray-500">Get help with current step</p>
            </div>
          </button>

          <button
            onClick={() => {
              setShowMenu(false);
              onScreenShare?.();
            }}
            className="w-full flex items-center space-x-3 px-4 py-3 bg-green-50 hover:bg-green-100 rounded-lg transition text-left group"
          >
            <Monitor className="w-5 h-5 text-green-600 group-hover:text-green-700" />
            <div>
              <p className="font-medium text-gray-900 text-sm">Screen Share</p>
              <p className="text-xs text-gray-500">View automation screen</p>
            </div>
          </button>
        </div>

        {/* Status Indicator */}
        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 rounded-b-xl">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <p className="text-xs text-gray-600">Automation running</p>
          </div>
        </div>
      </div>
    </div>
  );
}

