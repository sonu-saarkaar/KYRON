import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuth } from './hooks/useAuth'
import Layout from './components/Layout/Layout'
import Login from './pages/Login/Login'
import Signup from './pages/Signup/Signup'
import Dashboard from './pages/Dashboard/Dashboard'
import Profile from './pages/Profile/Profile'
import Vault from './pages/Vault/Vault'
import Automation from './pages/Automation/Automation'
import Applications from './pages/Applications/Applications'
import Blockchain from './pages/Blockchain/Blockchain'
import Voice from './pages/Voice/Voice'
import Chat from './pages/Chat/Chat'
import Settings from './pages/Settings/Settings'
import Services from './pages/Services/Services'

function App() {
  const { isAuthenticated, loading } = useAuth()

  console.log('[App] Render:', { isAuthenticated, loading });

  // Show loading state
  if (loading) {
    console.log('[App] Showing loading state');
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  console.log('[App] Rendering routes, isAuthenticated:', isAuthenticated);

  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/chat" replace />} />
        <Route path="/signup" element={!isAuthenticated ? <Signup /> : <Navigate to="/chat" replace />} />
        
        {/* Protected routes */}
        <Route path="/chat" element={isAuthenticated ? <Chat /> : <Navigate to="/login" replace />} />
        
        {/* Layout routes (protected) */}
        <Route path="/" element={isAuthenticated ? <Layout /> : <Navigate to="/login" replace />}>
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="profile" element={<Profile />} />
          <Route path="settings" element={<Settings />} />
          <Route path="services" element={<Services />} />
          <Route path="vault" element={<Vault />} />
          <Route path="automation" element={<Automation />} />
          <Route path="applications" element={<Applications />} />
          <Route path="blockchain" element={<Blockchain />} />
          <Route path="voice" element={<Voice />} />
        </Route>
      </Routes>
    </>
  )
}

export default App

