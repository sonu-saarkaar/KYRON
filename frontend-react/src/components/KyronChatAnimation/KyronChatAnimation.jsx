import { useEffect, useState } from 'react';
import { MessageSquare, User, Bot, CheckCircle, ExternalLink, Activity, Sparkles, ArrowRight } from 'lucide-react';

const conversationSteps = [
  {
    type: 'user',
    message: 'I want to apply PAN card',
    delay: 0,
  },
  {
    type: 'bot',
    message: 'Great! I can help you apply for a PAN card. Let me guide you through the process. Would you like to proceed?',
    delay: 1000,
  },
  {
    type: 'action',
    action: 'apply_clicked',
    delay: 3000,
  },
  {
    type: 'bot',
    message: 'Opening PAN application form...',
    delay: 3500,
  },
  {
    type: 'bot',
    message: '✅ Form opened in new tab. Filling your details...',
    delay: 4500,
  },
  {
    type: 'bot',
    message: '📝 Filling: Name, Email, Phone, Address...',
    delay: 6000,
  },
  {
    type: 'bot',
    message: '✅ All fields filled successfully!',
    delay: 7500,
  },
  {
    type: 'bot',
    message: '🚀 Submitting form...',
    delay: 9000,
  },
  {
    type: 'bot',
    message: '✅ Form submitted successfully!',
    delay: 10500,
  },
  {
    type: 'tracking',
    delay: 12000,
  },
];

export default function KyronChatAnimation() {
  const [currentStep, setCurrentStep] = useState(0);
  const [showTracking, setShowTracking] = useState(false);
  const [messages, setMessages] = useState([]);
  const [showApplyButton, setShowApplyButton] = useState(false);

  useEffect(() => {
    let timers = [];
    let isMounted = true;

    const runAnimation = () => {
      if (!isMounted) return;

      conversationSteps.forEach((step, index) => {
        const timer = setTimeout(() => {
          if (!isMounted) return;
          
          if (step.type === 'user' || step.type === 'bot') {
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now() + index,
                type: step.type,
                text: step.message,
              },
            ]);
          } else if (step.type === 'action' && step.action === 'apply_clicked') {
            setShowApplyButton(true);
          } else if (step.type === 'tracking') {
            setShowTracking(true);
          }
          setCurrentStep(index);
        }, step.delay);

        timers.push(timer);
      });

      // Reset after completion
      const resetTimer = setTimeout(() => {
        if (!isMounted) return;
        setMessages([]);
        setShowApplyButton(false);
        setShowTracking(false);
        setCurrentStep(0);
        // Restart animation
        setTimeout(() => {
          if (isMounted) {
            runAnimation();
          }
        }, 1000);
      }, 18000);

      timers.push(resetTimer);
    };

    runAnimation();

    return () => {
      isMounted = false;
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, []);

  const handleApplyClick = () => {
    setShowApplyButton(false);
    // Animation will continue automatically
  };

  return (
    <div className="relative w-full h-full flex items-center justify-center p-4 lg:p-6">
      <div className="w-full max-w-4xl h-full flex flex-col">
        {/* Header */}
        <div className="text-center mb-4">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl mb-3 shadow-lg">
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <h3 className="text-xl lg:text-2xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent mb-1">
            KYRON in Action
          </h3>
          <p className="text-xs lg:text-sm text-gray-600 dark:text-gray-400">
            Watch KYRON automate your form filling
          </p>
        </div>

        {/* Chat Box - TV Display Size */}
        <div className="flex-1 bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-2xl border-2 border-purple-200 dark:border-purple-800 overflow-hidden flex flex-col" style={{ minHeight: '500px', maxHeight: '600px' }}>
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500 dark:text-gray-400">Starting conversation...</p>
                </div>
              </div>
            )}

            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start space-x-3 ${
                  msg.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {msg.type === 'bot' && (
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.type === 'user'
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                  } shadow-sm`}
                >
                  <p className="text-sm lg:text-base leading-relaxed">{msg.text}</p>
                </div>
                {msg.type === 'user' && (
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                  </div>
                )}
              </div>
            ))}

            {/* Apply Button */}
            {showApplyButton && (
              <div className="flex justify-center animate-fade-in">
                <button
                  onClick={handleApplyClick}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all flex items-center space-x-2"
                >
                  <span>Apply for PAN Card</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            )}

            {/* Tracking Display */}
            {showTracking && (
              <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl border-2 border-green-300 dark:border-green-700 animate-fade-in">
                <div className="flex items-center space-x-3 mb-3">
                  <Activity className="w-6 h-6 text-green-600 dark:text-green-400" />
                  <h4 className="font-bold text-gray-900 dark:text-white">Tracking Request</h4>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-700 dark:text-gray-300">Status:</span>
                    <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-full font-semibold text-xs">
                      Completed
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-700 dark:text-gray-300">Progress:</span>
                    <span className="font-semibold text-gray-900 dark:text-white">6/6 steps</span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
                    <div className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full w-full transition-all duration-500"></div>
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400 mt-2">
                    <ExternalLink className="w-4 h-4" />
                    <span>Application submitted successfully</span>
                  </div>
                </div>
              </div>
            )}

            {/* Typing Indicator */}
            {currentStep < conversationSteps.length - 1 && !showTracking && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-full flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl px-4 py-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Stats - Desktop Only */}
        <div className="hidden lg:grid mt-4 grid-cols-3 gap-3 text-center">
          <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 dark:from-yellow-900/30 dark:to-yellow-800/30 backdrop-blur-sm rounded-xl p-3 border border-yellow-300/30 dark:border-yellow-700/50">
            <Sparkles className="w-5 h-5 text-yellow-500 dark:text-yellow-400 mx-auto mb-1" />
            <p className="text-xs font-bold text-gray-900 dark:text-white">AI-Powered</p>
          </div>
          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 dark:from-green-900/30 dark:to-green-800/30 backdrop-blur-sm rounded-xl p-3 border border-green-300/30 dark:border-green-700/50">
            <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400 mx-auto mb-1" />
            <p className="text-xs font-bold text-gray-900 dark:text-white">100% Accurate</p>
          </div>
          <div className="bg-gradient-to-br from-purple-500/20 to-indigo-600/20 dark:from-purple-900/30 dark:to-indigo-800/30 backdrop-blur-sm rounded-xl p-3 border border-purple-300/30 dark:border-purple-700/50">
            <Activity className="w-5 h-5 text-purple-500 dark:text-purple-400 mx-auto mb-1" />
            <p className="text-xs font-bold text-gray-900 dark:text-white">Real-time Tracking</p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}

