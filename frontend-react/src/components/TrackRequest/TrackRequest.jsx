import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle, Clock, XCircle, AlertCircle, RefreshCw, FileText, Calendar, MapPin } from 'lucide-react';
import { agentAPI } from '../../services/api';

export default function TrackRequest({ requestId, onClose }) {
  const [requestDetails, setRequestDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (requestId) {
      fetchRequestDetails();
    }
  }, [requestId]);

  const fetchRequestDetails = async () => {
    try {
      setLoading(true);
      // Fetch request status from backend
      const status = await agentAPI.getStatus(requestId);
      setRequestDetails(status);
    } catch (error) {
      console.error('Error fetching request details:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'running':
      case 'active':
        return <Clock className="w-6 h-6 text-blue-500 animate-spin" />;
      case 'error':
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'paused':
        return <AlertCircle className="w-6 h-6 text-yellow-500" />;
      default:
        return <Clock className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-200 border-green-300 dark:border-green-800';
      case 'running':
      case 'active':
        return 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-200 border-blue-300 dark:border-blue-800';
      case 'error':
      case 'failed':
        return 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-200 border-red-300 dark:border-red-800';
      case 'paused':
        return 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200 border-yellow-300 dark:border-yellow-800';
      default:
        return 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  if (!requestDetails) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Request details not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Track Request</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Request ID: {requestId}</p>
        </div>
        <button
          onClick={fetchRequestDetails}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
        >
          <RefreshCw className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        </button>
      </div>

      {/* Status Card */}
      <div className={`p-6 rounded-xl border-2 ${getStatusColor(requestDetails.status)}`}>
        <div className="flex items-center space-x-4">
          {getStatusIcon(requestDetails.status)}
          <div className="flex-1">
            <h3 className="text-lg font-semibold">Status: {requestDetails.status || 'Unknown'}</h3>
            <p className="text-sm mt-1 opacity-90">
              {requestDetails.current_action || 'No action in progress'}
            </p>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      {requestDetails.progress && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Progress</span>
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Steps Completed</span>
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                {requestDetails.progress.completed || 0} / {requestDetails.progress.total || 0}
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2 rounded-full transition-all"
                style={{
                  width: `${((requestDetails.progress.completed || 0) / (requestDetails.progress.total || 1)) * 100}%`
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Request Details */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 space-y-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Request Details</h3>
        
        {requestDetails.service_id && (
          <div className="flex items-center space-x-3">
            <FileText className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">Service</p>
              <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                {requestDetails.service_id.replace('_', ' ')}
              </p>
            </div>
          </div>
        )}

        {requestDetails.created_at && (
          <div className="flex items-center space-x-3">
            <Calendar className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">Created At</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {new Date(requestDetails.created_at).toLocaleString()}
              </p>
            </div>
          </div>
        )}

        {requestDetails.official_url && (
          <div className="flex items-center space-x-3">
            <MapPin className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">Website</p>
              <a
                href={requestDetails.official_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-purple-600 dark:text-purple-400 hover:underline"
              >
                {requestDetails.official_url}
              </a>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex space-x-3">
        {requestDetails.status === 'paused' && (
          <button className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition">
            Resume
          </button>
        )}
        {requestDetails.status === 'running' && (
          <button className="flex-1 px-4 py-2 bg-yellow-600 text-white rounded-lg font-semibold hover:bg-yellow-700 transition">
            Pause
          </button>
        )}
        <button className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-semibold hover:bg-gray-300 dark:hover:bg-gray-600 transition">
          View Details
        </button>
      </div>
    </div>
  );
}

