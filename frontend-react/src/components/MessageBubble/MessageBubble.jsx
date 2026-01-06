import { useState } from 'react';
import { Bot, User, Loader, CheckCircle, Volume2, VolumeX } from 'lucide-react';
import { voiceAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function MessageBubble({ message, language, onAction }) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const isUser = message.type === 'user';
  const isLoading = message.isLoading;
  const hasExplanation = message.explanation && message.explanation.type === 'service_explanation';

  const handleSpeak = async () => {
    if (!message.text || isUser) return;
    
    try {
      setIsSpeaking(true);
      await voiceAPI.speak(message.text, language);
      setIsSpeaking(false);
    } catch (error) {
      console.error('TTS failed:', error);
      toast.error('Failed to speak message');
      setIsSpeaking(false);
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex items-start space-x-3 max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser 
            ? 'bg-gray-200' 
            : 'bg-gradient-to-br from-purple-600 to-indigo-600'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-gray-600" />
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className={`flex-1 ${isUser ? 'text-right' : ''}`}>
          <div className={`inline-block px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-purple-600 text-white'
              : hasExplanation
                ? 'bg-white border-2 border-purple-200 text-gray-900 shadow-lg'
                : 'bg-white border border-gray-200 text-gray-900 shadow-sm'
          }`}>
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <Loader className="w-4 h-4 animate-spin" />
                <span className="text-sm">KYRON is thinking...</span>
              </div>
            ) : message.isProgress ? (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="w-2 h-2 bg-purple-600 rounded-full animate-pulse" />
                <span>{message.text}</span>
              </div>
            ) : hasExplanation ? (
              // Structured Service Explanation
              <div className="max-w-2xl">
                <div className="flex items-start justify-between mb-4 pb-2 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900">
                    {message.explanation.title}
                  </h2>
                  
                  {/* Speak Button for explanation */}
                  {message.text && (
                    <button
                      onClick={handleSpeak}
                      disabled={isSpeaking}
                      className={`flex-shrink-0 p-1.5 rounded-lg transition ml-2 ${
                        isSpeaking
                          ? 'bg-purple-100 text-purple-600'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                      title="Speak message"
                    >
                      {isSpeaking ? (
                        <VolumeX className="w-4 h-4 animate-pulse" />
                      ) : (
                        <Volume2 className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>
                
                <div className="space-y-4 mb-4">
                  {message.explanation.sections?.map((section, idx) => (
                    <div key={idx} className="border-l-4 border-purple-500 pl-4">
                      <h3 className="font-semibold text-gray-800 mb-2">{section.heading}</h3>
                      <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                        {section.content}
                      </p>
                    </div>
                  ))}
                </div>
                
                {/* Action Buttons */}
                {message.explanation.actions && message.explanation.actions.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200 space-y-2">
                    {message.explanation.actions.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => onAction(action.action, action.service_id, action.value)}
                        className={`block w-full px-4 py-3 rounded-lg text-sm font-semibold transition ${
                          action.action === 'apply_service'
                            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-md'
                            : action.action === 'cancel'
                            ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            : 'bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200'
                        }`}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <>
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm whitespace-pre-wrap flex-1">{message.text}</p>
                  
                  {/* Speak Button (only for bot messages) */}
                  {!isUser && message.text && (
                    <button
                      onClick={handleSpeak}
                      disabled={isSpeaking}
                      className={`flex-shrink-0 p-1.5 rounded-lg transition ${
                        isSpeaking
                          ? 'bg-purple-100 text-purple-600'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                      title="Speak message"
                    >
                      {isSpeaking ? (
                        <VolumeX className="w-4 h-4 animate-pulse" />
                      ) : (
                        <Volume2 className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>
                
                {/* Action Buttons (for non-explanation messages) */}
                {message.actions && message.actions.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {message.actions.map((action, idx) => (
                      <button
                        key={idx}
                        onClick={() => onAction(action.action, action.service_id || action.serviceId, action.value)}
                        className={`block w-full px-4 py-2 rounded-lg text-sm font-medium transition ${
                          action.action === 'apply_service' || action.action === 'confirm_proceed'
                            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-md'
                            : action.action === 'cancel'
                            ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            : isUser
                            ? 'bg-white text-purple-600 hover:bg-purple-50'
                            : 'bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200'
                        }`}
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}

                {/* Automation Status */}
                {message.automation && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center space-x-2 text-xs text-gray-600">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                      <span>Automation in progress...</span>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Timestamp */}
          <div className={`mt-1 text-xs text-gray-500 ${isUser ? 'text-right' : ''}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
}

