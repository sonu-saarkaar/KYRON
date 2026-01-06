import { useEffect, useState } from 'react';
import { FileText, CheckCircle, Zap, Sparkles, ArrowRight } from 'lucide-react';

export default function KyronFormAnimation() {
  const [currentStep, setCurrentStep] = useState(0);
  const [filledFields, setFilledFields] = useState([]);

  const formFields = [
    { id: 1, label: 'Full Name', value: 'John Doe', icon: '👤' },
    { id: 2, label: 'Email', value: 'john@example.com', icon: '📧' },
    { id: 3, label: 'Phone', value: '+91 98765 43210', icon: '📱' },
    { id: 4, label: 'Address', value: '123 Main Street', icon: '📍' },
    { id: 5, label: 'City', value: 'Mumbai', icon: '🏙️' },
    { id: 6, label: 'State', value: 'Maharashtra', icon: '🗺️' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      if (currentStep < formFields.length) {
        setFilledFields((prev) => [...prev, formFields[currentStep].id]);
        setCurrentStep((prev) => prev + 1);
      } else {
        // Reset animation
        setCurrentStep(0);
        setFilledFields([]);
      }
    }, 800);

    return () => clearInterval(interval);
  }, [currentStep]);

  return (
    <div className="relative w-full h-full flex items-center justify-center p-4 lg:p-8">
      <div className="w-full max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl mb-4 shadow-lg animate-pulse">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent mb-2">
            KYRON in Action
          </h3>
          <p className="text-sm lg:text-base text-gray-600 dark:text-gray-400">
            Watch KYRON automatically fill forms with AI precision
          </p>
        </div>

        {/* Form Container */}
        <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-2xl shadow-2xl p-6 lg:p-8 border-2 border-purple-200 dark:border-purple-800 relative overflow-hidden">
          {/* Animated Background */}
          <div className="absolute inset-0 opacity-5">
            <div className="absolute top-0 left-0 w-64 h-64 bg-purple-500 rounded-full blur-3xl animate-blob"></div>
            <div className="absolute bottom-0 right-0 w-64 h-64 bg-indigo-500 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
          </div>

          {/* Form Fields */}
          <div className="relative z-10 space-y-4">
            {formFields.map((field, index) => {
              const isFilled = filledFields.includes(field.id);
              const isFilling = currentStep === index;
              
              return (
                <div
                  key={field.id}
                  className={`relative transition-all duration-500 ${
                    isFilled ? 'scale-100' : 'scale-95 opacity-60'
                  }`}
                >
                  {/* Field Label */}
                  <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center space-x-2">
                    <span>{field.icon}</span>
                    <span>{field.label}</span>
                    {isFilled && (
                      <CheckCircle className="w-4 h-4 text-green-500 ml-2 animate-bounce" />
                    )}
                  </label>

                  {/* Input Field */}
                  <div className="relative">
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30 rounded-lg opacity-0 transition-opacity duration-300"
                      style={{ opacity: isFilling ? 0.3 : 0 }}
                    />
                    <input
                      type="text"
                      value={isFilled ? field.value : ''}
                      readOnly
                      className={`w-full px-4 py-3 border-2 rounded-lg transition-all duration-500 ${
                        isFilled
                          ? 'border-green-500 bg-green-50 dark:bg-green-900/20 dark:border-green-600'
                          : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-700'
                      } text-gray-900 dark:text-white font-medium`}
                      style={{
                        animation: isFilling ? 'typing 0.8s ease-in-out' : 'none',
                      }}
                    />
                    
                    {/* Typing Indicator */}
                    {isFilling && (
                      <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></div>
                          <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      </div>
                    )}

                    {/* KYRON Cursor */}
                    {isFilling && (
                      <div className="absolute left-4 top-1/2 transform -translate-y-1/2 animate-pulse">
                        <Zap className="w-5 h-5 text-purple-600" />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Submit Button Animation */}
          {filledFields.length === formFields.length && (
            <div className="mt-6 flex justify-center animate-fade-in">
              <button className="px-8 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-bold shadow-lg hover:shadow-xl transform hover:scale-105 transition-all flex items-center space-x-2">
                <span>Submit Form</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          )}

          {/* Progress Indicator */}
          <div className="mt-6">
            <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
              <span>Progress</span>
              <span>{filledFields.length} / {formFields.length} fields</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2 rounded-full transition-all duration-500"
                style={{
                  width: `${(filledFields.length / formFields.length) * 100}%`,
                }}
              />
            </div>
          </div>
        </div>

        {/* Stats - Desktop Only */}
        <div className="hidden lg:grid mt-6 grid-cols-3 gap-4 text-center">
          <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 dark:from-yellow-900/30 dark:to-yellow-800/30 backdrop-blur-sm rounded-xl p-4 border border-yellow-300/30 dark:border-yellow-700/50">
            <Zap className="w-6 h-6 text-yellow-500 dark:text-yellow-400 mx-auto mb-2" />
            <p className="text-sm font-bold text-gray-900 dark:text-white">Fast</p>
            <p className="text-xs text-gray-700 dark:text-gray-300">Auto-fill in seconds</p>
          </div>
          <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 dark:from-green-900/30 dark:to-green-800/30 backdrop-blur-sm rounded-xl p-4 border border-green-300/30 dark:border-green-700/50">
            <CheckCircle className="w-6 h-6 text-green-500 dark:text-green-400 mx-auto mb-2" />
            <p className="text-sm font-bold text-gray-900 dark:text-white">Accurate</p>
            <p className="text-xs text-gray-700 dark:text-gray-300">Zero errors</p>
          </div>
          <div className="bg-gradient-to-br from-purple-500/20 to-indigo-600/20 dark:from-purple-900/30 dark:to-indigo-800/30 backdrop-blur-sm rounded-xl p-4 border border-purple-300/30 dark:border-purple-700/50">
            <Sparkles className="w-6 h-6 text-purple-500 dark:text-purple-400 mx-auto mb-2" />
            <p className="text-sm font-bold text-gray-900 dark:text-white">Smart</p>
            <p className="text-xs text-gray-700 dark:text-gray-300">AI-powered</p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes typing {
          0% { width: 0; }
          100% { width: 100%; }
        }
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fade-in 0.5s ease-out;
        }
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  );
}

