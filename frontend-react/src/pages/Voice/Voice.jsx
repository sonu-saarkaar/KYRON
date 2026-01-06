import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { voiceAPI } from '../../services/api';
import { Mic, Volume2, Loader, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Voice() {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('en');

  // Get voice status
  const { data: status } = useQuery({
    queryKey: ['voice-status'],
    queryFn: voiceAPI.getStatus,
  });

  // Text-to-Speech mutation
  const speakMutation = useMutation({
    mutationFn: ({ text, language }) => voiceAPI.speak(text, language),
    onSuccess: () => {
      toast.success('Text spoken successfully!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to speak text');
    },
  });

  // Speech-to-Text mutation
  const listenMutation = useMutation({
    mutationFn: voiceAPI.listen,
    onSuccess: (data) => {
      if (data.text) {
        setText(data.text);
        toast.success('Speech recognized!');
      } else {
        toast.error('No speech detected');
      }
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to recognize speech');
    },
  });

  const handleSpeak = () => {
    if (!text.trim()) {
      toast.error('Please enter text to speak');
      return;
    }
    speakMutation.mutate({ text, language });
  };

  const handleListen = () => {
    listenMutation.mutate();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <Volume2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Voice Guidance</h1>
            <p className="text-gray-600">Text-to-Speech and Speech-to-Text capabilities</p>
          </div>
        </div>
      </div>

      {/* Status */}
      {status && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-sm text-gray-600">
              Voice service is {status.status || 'active'}
            </span>
          </div>
        </div>
      )}

      {/* Text-to-Speech */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Text-to-Speech</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Text to Speak
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter text you want to hear..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Language
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="hi">Hindi</option>
            </select>
          </div>

          <button
            onClick={handleSpeak}
            disabled={speakMutation.isPending || !text.trim()}
            className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {speakMutation.isPending ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Speaking...</span>
              </>
            ) : (
              <>
                <Volume2 className="w-5 h-5" />
                <span>Speak Text</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Speech-to-Text */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Speech-to-Text</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recognized Text
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Click 'Listen' to start voice recognition..."
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none"
              readOnly
            />
          </div>

          <button
            onClick={handleListen}
            disabled={listenMutation.isPending}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {listenMutation.isPending ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Listening...</span>
              </>
            ) : (
              <>
                <Mic className="w-5 h-5" />
                <span>Start Listening</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">How to Use</h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Text-to-Speech: Enter text and click "Speak Text" to hear it</li>
          <li>Speech-to-Text: Click "Start Listening" and speak into your microphone</li>
          <li>Voice guidance helps with accessibility and hands-free operation</li>
        </ul>
      </div>
    </div>
  );
}

