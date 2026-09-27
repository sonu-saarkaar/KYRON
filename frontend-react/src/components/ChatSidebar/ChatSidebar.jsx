import { useState } from 'react';
import { X, MessageSquare, User, Database, Clock, Trash2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { profileAPI, documentsAPI } from '../../services/api';

export default function ChatSidebar({ show, onClose, activeTab, onTabChange, messages }) {
  const [chatHistory, setChatHistory] = useState([]);

  // Fetch profile
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await profileAPI.get();
      return response.profile || {};
    },
  });

  // Fetch documents
  const { data: documents } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await documentsAPI.list();
      return response.documents || [];
    },
  });

  // Group messages by date
  const groupedMessages = messages.reduce((acc, msg) => {
    const date = new Date(msg.timestamp).toLocaleDateString();
    if (!acc[date]) acc[date] = [];
    acc[date].push(msg);
    return acc;
  }, {});

  return (
    <div
      className={`w-80 bg-white border-r border-gray-200 flex flex-col transition-transform duration-300 ${
        show ? 'translate-x-0' : '-translate-x-full absolute left-0 z-10 h-full'
      }`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <h2 className="text-lg font-bold text-gray-900">KYRON</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded-lg transition"
        >
          <X className="w-5 h-5 text-gray-600" />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => onTabChange('chat')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition ${
            activeTab === 'chat'
              ? 'text-purple-600 border-b-2 border-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <MessageSquare className="w-4 h-4" />
            <span>Chat History</span>
          </div>
        </button>
        <button
          onClick={() => onTabChange('profile')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition ${
            activeTab === 'profile'
              ? 'text-purple-600 border-b-2 border-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <User className="w-4 h-4" />
            <span>Profile</span>
          </div>
        </button>
        <button
          onClick={() => onTabChange('database')}
          className={`flex-1 px-4 py-3 text-sm font-medium transition ${
            activeTab === 'database'
              ? 'text-purple-600 border-b-2 border-purple-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <div className="flex items-center justify-center space-x-2">
            <Database className="w-4 h-4" />
            <span>Database</span>
          </div>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'chat' && (
          <div className="p-4 space-y-4">
            {Object.entries(groupedMessages).map(([date, dateMessages]) => (
              <div key={date}>
                <div className="text-xs text-gray-500 mb-2 px-2">{date}</div>
                <div className="space-y-2">
                  {dateMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition cursor-pointer"
                    >
                      <div className="text-sm text-gray-900 line-clamp-2">
                        {msg.type === 'user' ? 'You: ' : 'KYRON: '}
                        {msg.text}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
            {messages.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No chat history yet</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="p-4 space-y-4">
            <div className="bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg p-4 text-white">
              <h3 className="font-semibold mb-2">Master Profile</h3>
              <p className="text-sm text-purple-100">
                {profile?.fullName || 'Not set'}
              </p>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Full Name</label>
                <p className="text-sm text-gray-900 mt-1">{profile?.fullName || '—'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Email</label>
                <p className="text-sm text-gray-900 mt-1">{profile?.email || '—'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Phone</label>
                <p className="text-sm text-gray-900 mt-1">{profile?.phone || '—'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Date of Birth</label>
                <p className="text-sm text-gray-900 mt-1">{profile?.dateOfBirth || '—'}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Address</label>
                <p className="text-sm text-gray-900 mt-1">
                  {profile?.address ? `${profile.address}, ${profile.city}, ${profile.state} ${profile.pincode}` : '—'}
                </p>
              </div>
            </div>

            <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium">
              Edit Profile
            </button>
          </div>
        )}

        {activeTab === 'database' && (
          <div className="p-4 space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">Document Vault</h3>
              <p className="text-xs text-blue-700">
                {documents?.length || 0} documents stored
              </p>
            </div>

            <div className="space-y-2">
              {documents?.slice(0, 5).map((doc) => (
                <div
                  key={doc.id}
                  className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                      <p className="text-xs text-gray-500">{doc.type}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {(!documents || documents.length === 0) && (
              <div className="text-center py-8 text-gray-500">
                <Database className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No documents yet</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

