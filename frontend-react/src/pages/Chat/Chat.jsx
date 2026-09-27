import { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, Mic, MicOff, Settings, X, Moon, Sun } from 'lucide-react';
import toast from 'react-hot-toast';
import { useTheme } from '../../contexts/ThemeContext';
import { profileAPI, automationAPI, serviceAPI, voiceAPI, chatAPI, agentAPI } from '../../services/api';
import { useConversations } from '../../hooks/useConversations';
import ConversationHistory from '../../components/ConversationHistory/ConversationHistory';
import MessageBubble from '../../components/MessageBubble/MessageBubble';
import AutomationViewer from '../../components/AutomationViewer/AutomationViewer';
import Onboarding from '../../components/Onboarding/Onboarding';

const LANGUAGES = {
  en: 'English',
  hi: 'हिंदी (Hindi)'
};

export default function Chat() {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [language, setLanguage] = useState('en');
  const [currentService, setCurrentService] = useState(null);
  const [automationSession, setAutomationSession] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const { theme, toggleTheme } = useTheme();
  
  // Conversation management
  const {
    conversations,
    activeConversationId,
    setActiveConversationId,
    addConversation,
    deleteConversation,
    addMessageToConversation,
    getActiveConversation,
    loading: conversationsLoading,
  } = useConversations();

  const activeConversation = getActiveConversation();
  const [messages, setMessages] = useState(activeConversation?.messages || []);
  
  // Session state management
  const [sessionState, setSessionState] = useState({
    active_service: null,
    stage: null
  });

  const queryClient = useQueryClient();

  // Update messages when active conversation changes
  useEffect(() => {
    if (activeConversation) {
      setMessages(activeConversation.messages || []);
      // Load history from backend if needed
      if (activeConversation.messages.length === 0) {
        loadHistory();
      }
    }
  }, [activeConversationId, activeConversation]);

  // Check if first time user
  useEffect(() => {
    const hasSeenOnboarding = localStorage.getItem('kyron-onboarding-seen');
    if (!hasSeenOnboarding) {
      setShowOnboarding(true);
    }
  }, []);

  // Load chat history from backend
  const loadHistory = async () => {
    try {
      const history = await chatAPI.getHistory();
      if (history.messages && history.messages.length > 0) {
        const loadedMessages = history.messages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(loadedMessages);
        // Update conversation with loaded messages
        if (activeConversationId) {
          conversations.forEach(conv => {
            if (conv.id === activeConversationId) {
              conv.messages = loadedMessages;
            }
          });
        }
      } else if (messages.length === 0) {
        // Welcome message if no history
        const welcomeMessage = {
          id: Date.now(),
          type: 'bot',
          text: language === 'hi' 
            ? 'नमस्ते! मैं KYRON हूं, आपका AI सहायक। मैं आपकी सरकारी फॉर्म भरने में मदद कर सकता हूं। आप क्या करना चाहेंगे?'
            : 'Hello! I\'m KYRON, your AI assistant. I can help you fill government forms. What would you like to do?',
          timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Voice recognition
  const startListening = async () => {
    try {
      setIsListening(true);
      const response = await voiceAPI.listen();
      if (response.text) {
        setInput(response.text);
        setIsListening(false);
      }
    } catch (error) {
      console.error('Voice recognition error:', error);
      setIsListening(false);
      toast.error('Voice recognition failed');
    }
  };

  // Send message
  // Ensure we always have an active conversation before sending
  const ensureActiveConversation = () => {
    if (!activeConversationId) {
      const newConv = addConversation();
      setActiveConversationId(newConv.id);
      return newConv.id;
    }
    return activeConversationId;
  };

  const handleSend = async (text = null) => {
    const messageText = text || input.trim();
    if (!messageText) return;

    const convId = ensureActiveConversation();

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: messageText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    addMessageToConversation(convId, userMessage);
    setInput('');

    // Get bot response
    try {
      console.log('[Chat] Sending message:', messageText);
      const apiResponse = await chatAPI.sendMessage(messageText, language);
      console.log('[Chat] API Response received:', apiResponse);
      
      // Backend returns { success, response: {...}, message_id }
      // Extract the actual response object
      const chatResponse = apiResponse.response || apiResponse;
      console.log('[Chat] Extracted response:', chatResponse);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: chatResponse.text || 'Sorry, I could not process that request.',
        actions: chatResponse.actions,
        explanation: chatResponse.explanation,
        serviceId: chatResponse.service_id || chatResponse.serviceId,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
      addMessageToConversation(convId, botMessage);

      // Handle service actions
      const serviceId = chatResponse.service_id || chatResponse.serviceId;
      if (serviceId) {
        const catalog = await serviceAPI.getCatalog();
        const service = catalog.services?.find(s => s.id === serviceId);
        if (service) {
          setCurrentService(service);
        }
      }

      // Handle automation start
      if (chatResponse.start_automation || chatResponse.startAutomation) {
        startAutomationFlow(serviceId, chatResponse.service_config || chatResponse.serviceConfig || {});
      }
    } catch (error) {
      console.error('Chat API error:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        isNetworkError: error.isNetworkError
      });
      
      let errorText = language === 'hi'
        ? 'क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।'
        : 'Sorry, an error occurred. Please try again.';
      
      // Provide more specific error messages
      if (error.isNetworkError || !error.response) {
        errorText = language === 'hi'
          ? 'सर्वर से कनेक्ट नहीं हो सका। कृपया जांचें कि बैकएंड चल रहा है।'
          : 'Cannot connect to server. Please check if backend is running.';
      } else if (error.response?.status === 401) {
        errorText = language === 'hi'
          ? 'आपको लॉगिन करना होगा।'
          : 'Please log in to continue.';
      } else if (error.response?.data?.detail) {
        errorText = error.response.data.detail;
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: errorText,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      addMessageToConversation(activeConversationId, errorMessage);
      toast.error(errorText);
    }
  };

  // Start automation flow
  const startAutomationFlow = async (serviceId, serviceConfig) => {
    try {
      const requestData = {
        applicant_type: serviceConfig.applicant_type || 'Individual',
        delivery_type: serviceConfig.delivery_type || 'Digital',
        timestamp: new Date().toLocaleString()
      };
      
      const progressMessages = [
        { 
          text: language === 'hi' 
            ? `📋 **अनुरोध बनाया गया**\n• PAN Type: ${requestData.applicant_type}\n• Delivery: ${requestData.delivery_type}\n• समय: ${requestData.timestamp}` 
            : `📋 **Request Created**\n• PAN Type: ${requestData.applicant_type}\n• Delivery: ${requestData.delivery_type}\n• Time: ${requestData.timestamp}`,
          delay: 0 
        },
        { 
          text: language === 'hi' ? '🌐 आधिकारिक वेबसाइट खोल रहा हूं...' : '🌐 Opening official website...', 
          delay: 1000 
        },
        { 
          text: language === 'hi' ? '🔍 PAN Card Apply section खोज रहा हूं...' : '🔍 Finding PAN Card Apply section...', 
          delay: 2000 
        },
        { 
          text: language === 'hi' ? '📝 आपका data भर रहा हूं...' : '📝 Filling your data...', 
          delay: 3000 
        },
      ];
      
      for (const progressMsg of progressMessages) {
        setTimeout(() => {
          const msg = {
            id: Date.now() + progressMsg.delay,
            type: 'bot',
            text: progressMsg.text,
            timestamp: new Date(),
            isProgress: true,
          };
          setMessages(prev => [...prev, msg]);
          addMessageToConversation(activeConversationId, msg);
        }, progressMsg.delay);
      }
      
      const result = await agentAPI.start(serviceId, {
        ...serviceConfig,
        headless: false,
        open_in_new_tab: true
      });
      setAutomationSession(result.session_id);
      
      const successMessage = {
        id: Date.now(),
        type: 'bot',
        text: language === 'hi'
          ? `✅ **आवेदन शुरू हो गया!**\n\n📍 **स्तर:** Form भरना शुरू\n📊 **प्रगति:** 0/6 pages\n🌐 **वेबसाइट:** ${result.official_url || 'NSDL/UTIITSL'}\n\n💡 KYRON अब आपके data से form भर रहा है।`
          : `✅ **Application Started!**\n\n📍 **Level:** Starting form fill\n📊 **Progress:** 0/6 pages\n🌐 **Website:** ${result.official_url || 'NSDL/UTIITSL'}\n\n💡 KYRON is now filling the form with your data.`,
        timestamp: new Date(),
        automation: true,
        sessionId: result.session_id,
      };
      
      setTimeout(() => {
        setMessages(prev => [...prev, successMessage]);
        addMessageToConversation(activeConversationId, successMessage);
      }, 4000);
    } catch (error) {
      console.error('Automation error:', error);
      toast.error(language === 'hi' ? 'स्वचालन शुरू करने में विफल' : 'Failed to start automation');
    }
  };

  const handleAction = (action, serviceId, value = null) => {
    const convId = ensureActiveConversation();

    if (action === 'apply_service') {
      setSessionState(prev => ({
        active_service: serviceId || prev.active_service,
        stage: 'EXECUTION'
      }));
      handleSend(language === 'hi' ? 'Apply for PAN Card' : 'Apply for PAN Card');
    } else if (action === 'confirm_proceed') {
      handleSend(language === 'hi' ? 'हाँ, आगे बढ़ें' : 'Yes, proceed');
    } else if (action === 'select_applicant_type') {
      const selection = value === 'individual' ? 'Individual' : 'Company';
      handleSend(selection);
    } else if (action === 'select_delivery_type') {
      const selection = value === 'epan' ? 'Digital' : 'Physical';
      handleSend(selection);
    } else if (action === 'cancel') {
      setCurrentService(null);
      setSessionState({ active_service: null, stage: null });
      handleSend(language === 'hi' ? 'रद्द करें' : 'Cancel');
    }
  };

  const handleNewConversation = () => {
    const newConv = addConversation();
    setMessages([]);
  };

  const handleSelectConversation = (id) => {
    setActiveConversationId(id);
  };

  const handleDeleteConversation = (id) => {
    if (conversations.length === 1) {
      toast.error('Cannot delete the last conversation');
      return;
    }
    deleteConversation(id);
  };

  if (conversationsLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Conversation History Sidebar */}
      {showSidebar && (
        <div className="w-64 flex-shrink-0">
          <ConversationHistory
            conversations={conversations}
            activeConversationId={activeConversationId}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            onDeleteConversation={handleDeleteConversation}
          />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {!showSidebar && (
              <button
                onClick={() => setShowSidebar(true)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              >
                <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            )}
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">K</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">KYRON</h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">AI Assistant</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="px-3 py-1.5 border border-gray-300 dark:border-gray-700 rounded-lg text-sm focus:ring-2 focus:ring-purple-600 outline-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              {Object.entries(LANGUAGES).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
            <button
              onClick={toggleTheme}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              title="Toggle theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-5 h-5 text-yellow-400" />
              ) : (
                <Moon className="w-5 h-5 text-gray-600" />
              )}
            </button>
            <button 
              onClick={() => setShowSettings(true)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              title="Settings"
            >
              <Settings className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div 
          ref={chatContainerRef}
          className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-white dark:bg-gray-900"
        >
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-2xl">K</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">How can I help you today?</h2>
                <p className="text-gray-600 dark:text-gray-400">Start a conversation with KYRON</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                language={language}
                onAction={handleAction}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Automation Viewer */}
        {automationSession && (
          <AutomationViewer
            sessionId={automationSession}
            language={language}
            onClose={() => setAutomationSession(null)}
          />
        )}

        {/* Settings Modal */}
        {showSettings && (
          <div className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 max-w-md w-full mx-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Settings</h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                >
                  <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Language
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {Object.entries(LANGUAGES).map(([code, name]) => (
                      <option key={code} value={code}>{name}</option>
                    ))}
                  </select>
                </div>
                
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Voice messages are muted by default. Click the speak button on any message to hear it.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-6 py-4">
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder={language === 'hi' ? 'संदेश टाइप करें...' : 'Type a message...'}
                rows={1}
                className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none resize-none max-h-32 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
              />
              <button
                onClick={startListening}
                disabled={isListening}
                className={`absolute right-2 bottom-2 p-2 rounded-lg transition ${
                  isListening
                    ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 animate-pulse'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
            </div>
            <button
              onClick={() => handleSend()}
              disabled={!input.trim()}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg"
            >
              <Send className="w-5 h-5" />
              <span>{language === 'hi' ? 'भेजें' : 'Send'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Onboarding Modal */}
      {showOnboarding && (
        <Onboarding
          onComplete={() => {
            setShowOnboarding(false);
            localStorage.setItem('kyron-onboarding-seen', 'true');
          }}
        />
      )}
    </div>
  );
}
