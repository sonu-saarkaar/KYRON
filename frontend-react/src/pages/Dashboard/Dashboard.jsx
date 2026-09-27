import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { profileAPI, documentsAPI, serviceAPI, agentAPI } from '../../services/api';
import { User, FileText, Zap, List, TrendingUp, CheckCircle, Clock, Upload, Eye, Trash2, Mail, Phone, MapPin, Shield, CreditCard, Building2, GraduationCap, Edit2, Plus, MessageSquare, X, Calendar } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [stats, setStats] = useState({
    profileComplete: false,
    documentCount: 0,
    applicationCount: 0,
    agentStatus: 'inactive',
  });
  const [uploadingDoc, setUploadingDoc] = useState(false);
  const [showDocumentPreview, setShowDocumentPreview] = useState(null);

  // Fetch profile
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await profileAPI.get();
      return response.profile || {};
    },
  });

  // Fetch documents
  const { data: documents, isLoading: documentsLoading, refetch: refetchDocuments } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      try {
        const response = await documentsAPI.list();
        return response.documents || [];
      } catch (error) {
        console.error('Error fetching documents:', error);
        return [];
      }
    },
  });

  // Fetch service requests
  const { data: requests } = useQuery({
    queryKey: ['service-requests'],
    queryFn: async () => {
      const response = await serviceAPI.getRequests();
      return response.requests || [];
    },
  });

  // Fetch agent status
  const { data: agentStatus } = useQuery({
    queryKey: ['agent-status'],
    queryFn: async () => {
      const response = await agentAPI.getState();
      return response;
    },
  });

  useEffect(() => {
    if (profile) {
      setStats((prev) => ({
        ...prev,
        profileComplete: !!(profile.fullName && profile.email),
      }));
    }
    if (documents) {
      setStats((prev) => ({
        ...prev,
        documentCount: documents.length,
      }));
    }
    if (requests) {
      setStats((prev) => ({
        ...prev,
        applicationCount: requests.length,
      }));
    }
    if (agentStatus) {
      setStats((prev) => ({
        ...prev,
        agentStatus: agentStatus.state || 'inactive',
      }));
    }
  }, [profile, documents, requests, agentStatus]);

  // Calculate profile completion
  const profileCompletion = profile ? (
    ((profile.fullName ? 1 : 0) +
     (profile.email ? 1 : 0) +
     (profile.phone ? 1 : 0) +
     (profile.dateOfBirth ? 1 : 0) +
     (profile.address ? 1 : 0) +
     (profile.aadhaarNumber ? 1 : 0) +
     (profile.fatherName ? 1 : 0) +
     (profile.motherName ? 1 : 0)) / 8 * 100
  ) : 0;

  // Handle document upload
  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setUploadingDoc(true);
    try {
      const response = await documentsAPI.upload(file, file.name);
      toast.success('Document uploaded successfully!');
      refetchDocuments();
      queryClient.invalidateQueries(['documents']);
    } catch (error) {
      toast.error(`Failed to upload document: ${error.message}`);
    } finally {
      setUploadingDoc(false);
    }
  };

  // Handle document delete
  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await documentsAPI.delete(docId);
      toast.success('Document deleted successfully!');
      refetchDocuments();
      queryClient.invalidateQueries(['documents']);
    } catch (error) {
      toast.error(`Failed to delete document: ${error.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to KYRON</h1>
        <p className="text-purple-100 text-lg">
          Your AI Digital Execution Agent is ready to help you fill government forms.
        </p>
      </div>

      {/* Master Profile Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center">
              {profile?.photoUrl ? (
                <img 
                  src={profile.photoUrl.startsWith('http') ? profile.photoUrl : `/api/documents/${profile.photoUrl}`}
                  alt="Profile" 
                  className="w-full h-full rounded-full object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              ) : (
                <User className="w-6 h-6 text-white" />
              )}
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Master Profile</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {profile?.fullName || 'Complete your profile to get started'}
              </p>
            </div>
          </div>
          <Link
            to="/profile"
            className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition flex items-center space-x-2"
          >
            <Edit2 className="w-4 h-4" />
            <span>Edit Profile</span>
          </Link>
        </div>

        {/* Profile Completion */}
        <div className="mb-6">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600 dark:text-gray-400 font-medium">Profile Completion</span>
            <span className="font-bold text-purple-600 dark:text-purple-400">{Math.round(profileCompletion)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-600 to-indigo-600 h-3 rounded-full transition-all"
              style={{ width: `${profileCompletion}%` }}
            />
          </div>
        </div>

        {/* Profile Data Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProfileDataCard icon={<User className="w-4 h-4" />} label="Full Name" value={profile?.fullName} />
          <ProfileDataCard icon={<Mail className="w-4 h-4" />} label="Email" value={profile?.email} />
          <ProfileDataCard icon={<Phone className="w-4 h-4" />} label="Phone" value={profile?.phone} />
          <ProfileDataCard icon={<Calendar className="w-4 h-4" />} label="Date of Birth" value={profile?.dateOfBirth} />
          <ProfileDataCard icon={<Shield className="w-4 h-4" />} label="Aadhaar" value={profile?.aadhaarNumber ? `****${profile.aadhaarNumber.slice(-4)}` : null} />
          <ProfileDataCard icon={<Shield className="w-4 h-4" />} label="PAN" value={profile?.panNumber} />
          <ProfileDataCard icon={<MapPin className="w-4 h-4" />} label="City" value={profile?.city} />
          <ProfileDataCard icon={<MapPin className="w-4 h-4" />} label="State" value={profile?.state} />
          <ProfileDataCard icon={<MapPin className="w-4 h-4" />} label="PIN Code" value={profile?.pincode} />
          <ProfileDataCard icon={<User className="w-4 h-4" />} label="Father's Name" value={profile?.fatherName} />
          <ProfileDataCard icon={<User className="w-4 h-4" />} label="Mother's Name" value={profile?.motherName} />
          <ProfileDataCard icon={<GraduationCap className="w-4 h-4" />} label="Qualification" value={profile?.qualification} />
        </div>

        {/* Quick Profile Actions */}
        <div className="mt-6 flex items-center space-x-3">
          <Link
            to="/profile"
            className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition text-center"
          >
            View Complete Profile
          </Link>
        </div>
      </div>

      {/* Document Vault Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Document Vault</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {documents?.length || 0} documents uploaded
              </p>
            </div>
          </div>
          <label className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition flex items-center space-x-2 cursor-pointer">
            <Upload className="w-4 h-4" />
            <span>Upload Document</span>
            <input
              type="file"
              onChange={handleDocumentUpload}
              className="hidden"
              disabled={uploadingDoc}
              accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            />
          </label>
        </div>

        {/* Documents Grid */}
        {documentsLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : documents && documents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-purple-300 dark:hover:border-purple-700 transition bg-gray-50 dark:bg-gray-700/50"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {doc.filename || doc.description || 'Document'}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'Unknown date'}
                      </p>
                      {doc.file_size && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {(doc.file_size / 1024).toFixed(2)} KB
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => window.open(`/api/documents/${doc.id}`, '_blank')}
                    className="flex-1 px-3 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition flex items-center justify-center space-x-1 text-sm font-medium"
                    title="View Document"
                  >
                    <Eye className="w-4 h-4" />
                    <span>View</span>
                  </button>
                  <button
                    onClick={() => handleDeleteDocument(doc.id)}
                    className="px-3 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition"
                    title="Delete Document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-2">No documents uploaded yet</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
              Upload documents to help KYRON fill forms automatically
            </p>
            <label className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-indigo-700 transition cursor-pointer">
              <Upload className="w-4 h-4 mr-2" />
              <span>Upload First Document</span>
              <input
                type="file"
                onChange={handleDocumentUpload}
                className="hidden"
                disabled={uploadingDoc}
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              />
            </label>
          </div>
        )}
      </div>

      {/* New Conversation Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center">
              <MessageSquare className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Start New Conversation</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Chat with KYRON to apply for services
              </p>
            </div>
          </div>
        </div>
        
        <Link
          to="/chat"
          className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition shadow-lg"
        >
          <Plus className="w-5 h-5" />
          <span>New Conversation</span>
        </Link>

        <div className="mt-4 p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
          <p className="text-sm text-purple-800 dark:text-purple-200">
            💡 <strong>Tip:</strong> Say "I want to apply for PAN card" or "Bihar Residence Certificate" to get started. KYRON will use your Master Profile and Document Vault to automatically fill forms.
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Profile Status"
          value={stats.profileComplete ? 'Complete' : 'Incomplete'}
          icon={<User className="w-6 h-6" />}
          color={stats.profileComplete ? 'green' : 'yellow'}
          link="/profile"
        />
        <StatCard
          title="Documents"
          value={stats.documentCount}
          icon={<FileText className="w-6 h-6" />}
          color="blue"
          link="/vault"
        />
        <StatCard
          title="Applications"
          value={stats.applicationCount}
          icon={<List className="w-6 h-6" />}
          color="purple"
          link="/applications"
        />
        <StatCard
          title="Agent Status"
          value={stats.agentStatus}
          icon={<Zap className="w-6 h-6" />}
          color={stats.agentStatus === 'active' ? 'green' : 'gray'}
          link="/automation"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <ActionCard
            title="Complete Profile"
            description="Fill in your personal information"
            icon={<User className="w-5 h-5" />}
            link="/profile"
            color="purple"
          />
          <ActionCard
            title="Upload Documents"
            description="Add documents to your vault"
            icon={<FileText className="w-5 h-5" />}
            link="/vault"
            color="blue"
          />
          <ActionCard
            title="Start Automation"
            description="Let KYRON fill forms for you"
            icon={<Zap className="w-5 h-5" />}
            link="/automation"
            color="green"
          />
          <ActionCard
            title="View Applications"
            description="Track your form submissions"
            icon={<List className="w-5 h-5" />}
            link="/applications"
            color="indigo"
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {requests && requests.length > 0 ? (
            requests.slice(0, 5).map((request) => (
              <div
                key={request.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <List className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{request.service_name}</p>
                    <p className="text-sm text-gray-500">Status: {request.status}</p>
                  </div>
                </div>
                <span className="text-sm text-gray-500">
                  {new Date(request.created_at).toLocaleDateString()}
                </span>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color, link }) {
  const colorClasses = {
    green: 'bg-green-100 text-green-600',
    blue: 'bg-blue-100 text-blue-600',
    purple: 'bg-purple-100 text-purple-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    gray: 'bg-gray-100 text-gray-600',
  };

  const content = (
    <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>{icon}</div>
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
    </div>
  );

  if (link) {
    return <Link to={link}>{content}</Link>;
  }

  return content;
}

function ActionCard({ title, description, icon, link, color }) {
  const colorClasses = {
    purple: 'bg-purple-600 hover:bg-purple-700',
    blue: 'bg-blue-600 hover:bg-blue-700',
    green: 'bg-green-600 hover:bg-green-700',
    indigo: 'bg-indigo-600 hover:bg-indigo-700',
  };

  return (
    <Link to={link}>
      <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition">
        <div className={`w-12 h-12 ${colorClasses[color]} rounded-lg flex items-center justify-center text-white mb-4`}>
          {icon}
        </div>
        <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
    </Link>
  );
}

function ProfileDataCard({ icon, label, value }) {
  if (!value) return null;
  
  return (
    <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
      <div className="text-purple-600 dark:text-purple-400 flex-shrink-0">{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">{label}</p>
        <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">{value}</p>
      </div>
    </div>
  );
}

