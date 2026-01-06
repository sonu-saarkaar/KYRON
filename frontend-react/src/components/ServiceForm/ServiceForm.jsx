import { useState, useEffect } from 'react';
import { profileAPI } from '../../services/api';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, ArrowLeft, CheckCircle, AlertCircle } from 'lucide-react';

export default function ServiceForm({ service, onComplete, onBack }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});

  // Fetch profile to check what data is already available
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await profileAPI.get();
      return response.profile || {};
    },
  });

  const steps = service?.steps || [];
  const currentStepData = steps[currentStep];

  const handleChange = (stepId, value) => {
    setFormData({
      ...formData,
      [stepId]: value,
    });
    // Clear error for this field
    if (errors[stepId]) {
      setErrors({
        ...errors,
        [stepId]: null,
      });
    }
  };

  const validateStep = () => {
    if (!currentStepData) return true;
    
    if (currentStepData.required && !formData[currentStepData.id]) {
      setErrors({
        ...errors,
        [currentStepData.id]: 'This field is required',
      });
      return false;
    }
    return true;
  };

  const handleNext = () => {
    if (!validateStep()) return;

    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // All steps completed
      onComplete(formData);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      onBack();
    }
  };

  const getFieldValue = () => {
    return formData[currentStepData?.id] || '';
  };

  const renderField = () => {
    if (!currentStepData) return null;

    const value = getFieldValue();
    const error = errors[currentStepData.id];

    switch (currentStepData.field_type) {
      case 'radio':
        return (
          <div className="space-y-3">
            {currentStepData.options?.map((option) => (
              <label
                key={option.id}
                className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition ${
                  value === option.value
                    ? 'border-purple-600 bg-purple-50'
                    : 'border-gray-200 hover:border-purple-300'
                }`}
              >
                <input
                  type="radio"
                  name={currentStepData.id}
                  value={option.value}
                  checked={value === option.value}
                  onChange={(e) => handleChange(currentStepData.id, e.target.value)}
                  className="mt-1 mr-3 text-purple-600 focus:ring-purple-600"
                />
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{option.label}</div>
                  {option.description && (
                    <div className="text-sm text-gray-500 mt-1">{option.description}</div>
                  )}
                </div>
              </label>
            ))}
            {error && (
              <div className="flex items-center text-red-600 text-sm mt-2">
                <AlertCircle className="w-4 h-4 mr-1" />
                {error}
              </div>
            )}
          </div>
        );

      case 'select':
        return (
          <div>
            <select
              value={value}
              onChange={(e) => handleChange(currentStepData.id, e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-purple-600 outline-none"
            >
              <option value="">Select {currentStepData.label}</option>
              {currentStepData.options?.map((option) => (
                <option key={option.id} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {error && (
              <div className="flex items-center text-red-600 text-sm mt-2">
                <AlertCircle className="w-4 h-4 mr-1" />
                {error}
              </div>
            )}
          </div>
        );

      case 'text':
        return (
          <div>
            <input
              type="text"
              value={value}
              onChange={(e) => handleChange(currentStepData.id, e.target.value)}
              placeholder={`Enter ${currentStepData.label.toLowerCase()}`}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-purple-600 outline-none"
            />
            {error && (
              <div className="flex items-center text-red-600 text-sm mt-2">
                <AlertCircle className="w-4 h-4 mr-1" />
                {error}
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="bg-white rounded-xl shadow-sm p-8 max-w-2xl mx-auto">
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Step {currentStep + 1} of {steps.length}
          </span>
          <span className="text-sm text-gray-500">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Step Content */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {currentStepData?.label}
        </h2>
        {currentStepData?.description && (
          <p className="text-gray-600 mb-6">{currentStepData.description}</p>
        )}

        {renderField()}
      </div>

      {/* Profile Info Hint */}
      {profile && Object.keys(profile).length > 0 && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start">
            <CheckCircle className="w-5 h-5 text-blue-600 mr-2 mt-0.5" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">Profile data available</p>
              <p className="text-blue-700">
                KYRON will use your master profile data to auto-fill the form. Additional details will be collected here.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between pt-6 border-t">
        <button
          onClick={handlePrevious}
          className="flex items-center space-x-2 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>{currentStep === 0 ? 'Back to Services' : 'Previous'}</span>
        </button>

        <button
          onClick={handleNext}
          className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition"
        >
          <span>{currentStep === steps.length - 1 ? 'Start Automation' : 'Next'}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

