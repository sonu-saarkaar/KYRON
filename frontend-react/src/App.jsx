import React, { useState, useEffect } from 'react'
import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
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
import MunderDifflin from './pages/MunderDifflin/MunderDifflin'
import UnifiedApprovalPanel from './components/Jarvis/UnifiedApprovalPanel'

function App() {
  const { isAuthenticated, loading } = useAuth()
  const [isApprovalPanelOpen, setIsApprovalPanelOpen] = useState(false)
  const location = useLocation()

  // Open panel automatically if deep linked
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search)
    if (urlParams.get('action_id')) {
      setIsApprovalPanelOpen(true)
    }
  }, [location.search])

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
        {/* Redirect login/signup straight to chat */}
        <Route path="/login" element={<Navigate to="/chat" replace />} />
        <Route path="/signup" element={<Navigate to="/chat" replace />} />
        
        {/* Direct Chat Route */}
        <Route path="/chat/:panel?" element={<Chat />} />
        
        {/* Layout routes */}
        <Route path="/" element={<Layout />}>
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
          <Route path="munder-difflin" element={<MunderDifflin />} />
        </Route>
        
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
      
      {/* Global Approval Queue Panel */}
      <UnifiedApprovalPanel 
        isOpen={isApprovalPanelOpen} 
        onClose={() => setIsApprovalPanelOpen(false)} 
      />
      
      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsApprovalPanelOpen(true)}
        className="fixed bottom-6 right-6 p-4 rounded-full bg-cyan-600/90 text-white shadow-lg hover:bg-cyan-500 transition-colors z-40 backdrop-blur-md border border-cyan-400/30 flex items-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-4.24 4.24a1 1 0 0 0 .27 1.4L12 21"/><path d="M16 2v4"/><path d="M3 11v1a4 4 0 0 0 4 4h2"/><path d="M8 2v4"/></svg>
        <span className="font-mono text-sm font-bold">Approvals</span>
      </button>
    </>
  )
}

export default App

