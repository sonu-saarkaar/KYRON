import { useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { 
  Settings as SettingsIcon, 
  Upload, 
  Mail, 
  HelpCircle, 
  Shield, 
  FileText, 
  User, 
  Moon, 
  Sun, 
  Bell,
  Lock,
  Globe,
  Download,
  Trash2,
  Save
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function Settings() {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('profile');
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    automation: true,
  });

  const tabs = [
    { id: 'profile', label: 'Master Profile', icon: <User className="w-5 h-5" /> },
    { id: 'documents', label: 'Documents', icon: <Upload className="w-5 h-5" /> },
    { id: 'notifications', label: 'Notifications', icon: <Bell className="w-5 h-5" /> },
    { id: 'security', label: 'Security', icon: <Shield className="w-5 h-5" /> },
    { id: 'contact', label: 'Contact', icon: <Mail className="w-5 h-5" /> },
    { id: 'help', label: 'Help & Support', icon: <HelpCircle className="w-5 h-5" /> },
    { id: 'policy', label: 'Privacy & Policy', icon: <FileText className="w-5 h-5" /> },
    { id: 'appearance', label: 'Appearance', icon: theme === 'dark' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" /> },
  ];

  const handleSave = () => {
    toast.success('Settings saved successfully!');
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6">
          <div className="flex items-center space-x-3">
            <SettingsIcon className="w-8 h-8 text-white" />
            <h1 className="text-3xl font-bold text-white">Settings</h1>
          </div>
          <p className="text-purple-100 mt-2">Manage your KYRON preferences and account</p>
        </div>

        <div className="flex">
          {/* Sidebar */}
          <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-4">
            <nav className="space-y-2">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                    activeTab === tab.id
                      ? 'bg-purple-600 text-white shadow-lg'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  {tab.icon}
                  <span className="font-medium">{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 p-6">
            {/* Master Profile */}
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Master Profile</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Edit your master profile information. This data will be used to auto-fill forms.
                  </p>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    💡 Your master profile is accessible from the header logo area for quick editing.
                  </p>
                </div>
                <button
                  onClick={() => window.location.href = '/profile'}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition"
                >
                  Go to Master Profile
                </button>
              </div>
            )}

            {/* Documents */}
            {activeTab === 'documents' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Document Upload</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Upload and manage your documents securely in KYRON's vault.
                  </p>
                </div>
                <div className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-12 text-center">
                  <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Drag and drop files here or click to browse
                  </p>
                  <button className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                    Select Files
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Supported Documents</h3>
                    <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                      <li>• Aadhaar Card (PDF/Image)</li>
                      <li>• PAN Card (PDF/Image)</li>
                      <li>• Photo (JPG/PNG)</li>
                      <li>• Signature (JPG/PNG)</li>
                      <li>• Educational Certificates</li>
                    </ul>
                  </div>
                  <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Storage</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      All documents are encrypted and stored securely. Maximum file size: 10MB per file.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Notifications */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Notification Preferences</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Choose how you want to be notified about KYRON activities.
                  </p>
                </div>
                <div className="space-y-4">
                  {Object.entries(notifications).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white capitalize">{key}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {key === 'email' && 'Receive email notifications'}
                          {key === 'push' && 'Browser push notifications'}
                          {key === 'automation' && 'Automation status updates'}
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={value}
                          onChange={(e) => setNotifications({ ...notifications, [key]: e.target.checked })}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Security */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Security Settings</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Manage your account security and privacy settings.
                  </p>
                </div>
                <div className="space-y-4">
                  <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">Change Password</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Update your account password</p>
                      </div>
                      <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                        Change
                      </button>
                    </div>
                  </div>
                  <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">Two-Factor Authentication</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Add an extra layer of security</p>
                      </div>
                      <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                        Enable
                      </button>
                    </div>
                  </div>
                  <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">Active Sessions</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Manage your active login sessions</p>
                      </div>
                      <button className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                        View
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Contact */}
            {activeTab === 'contact' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Contact Us</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Get in touch with the KYRON team for support, feedback, or inquiries.
                  </p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <Mail className="w-8 h-8 text-purple-600 mb-4" />
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Email Support</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">support@kyron.ai</p>
                    <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                      Send Email
                    </button>
                  </div>
                  <div className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <HelpCircle className="w-8 h-8 text-indigo-600 mb-4" />
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Help Center</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Browse our knowledge base</p>
                    <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                      Visit Help Center
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Help & Support */}
            {activeTab === 'help' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Help & Support</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Find answers to common questions and get help using KYRON.
                  </p>
                </div>
                <div className="space-y-4">
                  {[
                    { title: 'Getting Started', desc: 'Learn how to use KYRON for the first time' },
                    { title: 'Master Profile Setup', desc: 'How to create and manage your master profile' },
                    { title: 'Form Automation', desc: 'Understanding KYRON\'s automation features' },
                    { title: 'Document Upload', desc: 'How to upload and manage documents' },
                    { title: 'Troubleshooting', desc: 'Common issues and solutions' },
                  ].map((item, idx) => (
                    <div key={idx} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-purple-300 dark:hover:border-purple-700 transition cursor-pointer">
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{item.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Privacy & Policy */}
            {activeTab === 'policy' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Privacy & Policy</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Read KYRON's privacy policy and terms of service.
                  </p>
                </div>
                <div className="space-y-4">
                  <div className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Privacy Policy</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Learn how KYRON collects, uses, and protects your personal information.
                    </p>
                    <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition">
                      Read Privacy Policy
                    </button>
                  </div>
                  <div className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Terms of Service</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Understand the terms and conditions for using KYRON.
                    </p>
                    <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">
                      Read Terms of Service
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Appearance */}
            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Appearance</h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Customize how KYRON looks and feels.
                  </p>
                </div>
                <div className="p-6 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Theme</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Current theme: <span className="font-semibold capitalize">{theme}</span>
                      </p>
                    </div>
                    <button
                      onClick={toggleTheme}
                      className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition flex items-center space-x-2"
                    >
                      {theme === 'dark' ? (
                        <>
                          <Sun className="w-5 h-5" />
                          <span>Switch to Light</span>
                        </>
                      ) : (
                        <>
                          <Moon className="w-5 h-5" />
                          <span>Switch to Dark</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Save Button */}
            <div className="mt-8 flex justify-end">
              <button
                onClick={handleSave}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition flex items-center space-x-2"
              >
                <Save className="w-5 h-5" />
                <span>Save Settings</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

