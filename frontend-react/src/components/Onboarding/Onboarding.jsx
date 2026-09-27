import { useState } from 'react';
import { X, User, FileText, CheckCircle, ArrowRight, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Onboarding({ onComplete }) {
  const [step, setStep] = useState(1);
  const navigate = useNavigate();

  const steps = [
    {
      id: 1,
      title: 'Welcome to KYRON',
      description: 'Your AI-powered digital execution agent',
      icon: <Sparkles className="w-12 h-12 text-purple-600" />,
      content: (
        <div className="text-center space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            KYRON helps you fill government forms, apply for services, and manage your documents automatically.
          </p>
          <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-500 mx-auto mb-2" />
              <p className="text-sm font-semibold">Auto-Fill Forms</p>
            </div>
            <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-500 mx-auto mb-2" />
              <p className="text-sm font-semibold">Secure Storage</p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 2,
      title: 'Create Master Profile',
      description: 'Fill once, use everywhere',
      icon: <User className="w-12 h-12 text-indigo-600" />,
      content: (
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400 text-center">
            Create your Master Profile with all your personal information. KYRON will use this to auto-fill forms automatically.
          </p>
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <strong>Benefits:</strong>
            </p>
            <ul className="text-sm text-gray-600 dark:text-gray-400 mt-2 space-y-1">
              <li>• No repeated data entry</li>
              <li>• Faster form filling</li>
              <li>• Reduced errors</li>
              <li>• One-time setup</li>
            </ul>
          </div>
        </div>
      ),
    },
    {
      id: 3,
      title: 'Upload Documents',
      description: 'Store your important documents securely',
      icon: <FileText className="w-12 h-12 text-blue-600" />,
      content: (
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400 text-center">
            Upload your documents (Aadhaar, PAN, Photo, Signature) to KYRON's secure vault. Access them anytime for form filling.
          </p>
          <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              <strong>Supported Documents:</strong>
            </p>
            <ul className="text-sm text-gray-600 dark:text-gray-400 mt-2 space-y-1">
              <li>• Aadhaar Card</li>
              <li>• PAN Card</li>
              <li>• Photo</li>
              <li>• Signature</li>
              <li>• Educational Certificates</li>
            </ul>
          </div>
        </div>
      ),
    },
  ];

  const handleNext = () => {
    if (step < steps.length) {
      setStep(step + 1);
    } else {
      handleComplete();
    }
  };

  const handleComplete = () => {
    if (onComplete) {
      onComplete();
    } else {
      navigate('/profile');
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const currentStep = steps[step - 1];

  return (
    <div className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
        <button
          onClick={handleSkip}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>

        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center mb-4">
            {currentStep.icon}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {currentStep.title}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {currentStep.description}
          </p>
        </div>

        <div className="mb-6">
          {currentStep.content}
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center space-x-2 mb-6">
          {steps.map((s) => (
            <div
              key={s.id}
              className={`h-2 rounded-full transition-all ${
                s.id <= step
                  ? 'bg-purple-600 w-8'
                  : 'bg-gray-200 dark:bg-gray-700 w-2'
              }`}
            />
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition"
            >
              Previous
            </button>
          )}
          <div className="flex-1" />
          <button
            onClick={handleNext}
            className="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition flex items-center space-x-2"
          >
            <span>{step === steps.length ? 'Get Started' : 'Next'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

