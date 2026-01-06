import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../contexts/ThemeContext';
import { LogIn, Mail, Lock, AlertCircle, Wifi, WifiOff, Sparkles, Zap, Shield, Moon, Sun } from 'lucide-react';
import toast from 'react-hot-toast';
import { checkBackendHealth, handleApiError } from '../../utils/errorHandler';
import KyronChatAnimation from '../../components/KyronChatAnimation/KyronChatAnimation';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState(null);
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    // Check backend health on mount
    checkBackendHealth().then((status) => {
      setBackendStatus(status);
      if (!status.healthy) {
        toast.error('Backend not reachable. Please start the backend server.', {
          duration: 5000,
        });
      }
    });
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(email, password);

      if (result.success) {
        toast.success('Login successful!');
        // Small delay to ensure state is updated
        setTimeout(() => {
          window.location.href = '/chat';
        }, 100);
      } else {
        toast.error(result.error || 'Login failed');
      }
    } catch (error) {
      const errorInfo = handleApiError(error);
      toast.error(errorInfo.message, {
        duration: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-full flex items-center justify-center bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="absolute top-4 right-4 p-3 rounded-full bg-white/10 dark:bg-gray-800/50 backdrop-blur-sm hover:bg-white/20 dark:hover:bg-gray-700/50 transition-all z-10"
        aria-label="Toggle theme"
      >
        {theme === 'dark' ? (
          <Sun className="w-5 h-5 text-yellow-400" />
        ) : (
          <Moon className="w-5 h-5 text-gray-700" />
        )}
      </button>

      {/* Desktop Layout: Split Screen - Fixed, No Scroll */}
      <div className="w-full h-screen max-w-[1920px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-0 items-stretch relative z-10 overflow-hidden">
        {/* Left Side: KYRON Chat Animation - Desktop Only, TV Size */}
        <div className="hidden lg:flex items-center justify-center h-screen bg-gradient-to-br from-purple-900/50 via-indigo-900/50 to-blue-900/50 dark:from-gray-900/50 dark:via-gray-800/50 dark:to-gray-900/50 p-6">
          <div className="w-full h-full max-w-5xl">
            <KyronChatAnimation />
          </div>
        </div>

        {/* Right Side: Login Form - Fixed Position */}
        <div className="w-full h-screen flex items-center justify-center bg-white/5 dark:bg-gray-900/5 backdrop-blur-sm p-4 lg:p-8 overflow-y-auto">
          <div className="w-full max-w-md">
        <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-gray-700/50 w-full my-auto">
          {/* Logo & Branding */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-600 via-indigo-600 to-blue-600 rounded-2xl mb-4 shadow-lg transform hover:scale-105 transition-transform">
              <Sparkles className="text-white w-10 h-10" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 bg-clip-text text-transparent dark:from-purple-400 dark:via-indigo-400 dark:to-blue-400">
              KYRON
            </h1>
            <p className="text-gray-600 dark:text-gray-300 mt-2 text-lg font-medium">
              AI Digital Execution Agent
            </p>
            <div className="flex items-center justify-center gap-2 mt-3">
              <Zap className="w-4 h-4 text-yellow-500" />
              <span className="text-sm text-gray-500 dark:text-gray-400">Powered by Advanced AI</span>
              <Shield className="w-4 h-4 text-green-500" />
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="your@email.com"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 w-5 h-5" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none transition bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 text-white py-3.5 rounded-xl font-bold hover:from-purple-700 hover:via-indigo-700 hover:to-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Logging in...</span>
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>Login to KYRON</span>
                </>
              )}
            </button>
          </form>

          {/* Signup Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <Link to="/signup" className="text-purple-600 dark:text-purple-400 font-semibold hover:text-purple-700 dark:hover:text-purple-300 transition">
                Create Account
              </Link>
            </p>
          </div>

          {/* Backend Status */}
          {backendStatus && (
            <div className={`mt-6 p-4 rounded-xl flex items-center space-x-2 ${
              backendStatus.healthy 
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' 
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
            }`}>
              {backendStatus.healthy ? (
                <>
                  <Wifi className="w-4 h-4 text-green-600 dark:text-green-400" />
                  <p className="text-xs text-green-600 dark:text-green-400 font-medium">Backend connected</p>
                </>
              ) : (
                <>
                  <WifiOff className="w-4 h-4 text-red-600 dark:text-red-400" />
                  <div className="flex-1">
                    <p className="text-xs text-red-600 dark:text-red-400 font-semibold">Backend not connected</p>
                    <p className="text-xs text-red-500 dark:text-red-500 mt-1">{backendStatus.error}</p>
                  </div>
                </>
              )}
            </div>
          )}

          {/* Test Credentials */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-600 dark:text-gray-400 mb-2 font-semibold">Test Credentials:</p>
            <p className="text-xs text-gray-500 dark:text-gray-500">Email: john.doe@example.com</p>
            <p className="text-xs text-gray-500 dark:text-gray-500">Password: test123</p>
          </div>

          {/* Features Highlight - Mobile Only */}
          <div className="mt-6 grid grid-cols-3 gap-4 text-center lg:hidden">
            <div className="bg-white/10 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-3 border border-white/20 dark:border-gray-700/50">
              <Zap className="w-5 h-5 text-yellow-400 mx-auto mb-1" />
              <p className="text-xs text-white font-medium">Fast</p>
            </div>
            <div className="bg-white/10 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-3 border border-white/20 dark:border-gray-700/50">
              <Shield className="w-5 h-5 text-green-400 mx-auto mb-1" />
              <p className="text-xs text-white font-medium">Secure</p>
            </div>
            <div className="bg-white/10 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-3 border border-white/20 dark:border-gray-700/50">
              <Sparkles className="w-5 h-5 text-purple-400 mx-auto mb-1" />
              <p className="text-xs text-white font-medium">AI-Powered</p>
            </div>
          </div>
        </div>
        </div>
        </div>
        </div>

      <style>{`
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
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
