import { useQuery } from '@tanstack/react-query';
import { blockchainAPI } from '../../services/api';
import { Link2, Clock, CheckCircle, Hash, Database } from 'lucide-react';

export default function Blockchain() {
  // Fetch blockchain info
  const { data: info, isLoading: infoLoading } = useQuery({
    queryKey: ['blockchain-info'],
    queryFn: blockchainAPI.getInfo,
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  // Fetch blockchain history
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['blockchain-history'],
    queryFn: blockchainAPI.getHistory,
    refetchInterval: 10000,
  });

  if (infoLoading || historyLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const blockchain = info?.blockchain || {};
  const history = historyData?.history || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <Link2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Blockchain Verification</h1>
            <p className="text-gray-600">Immutable audit log for all automation activities</p>
          </div>
        </div>
      </div>

      {/* Blockchain Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">Total Blocks</h3>
          <p className="text-2xl font-bold text-gray-900">{blockchain.block_count || 0}</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">Chain Valid</h3>
          <p className="text-2xl font-bold text-gray-900">
            {blockchain.is_valid ? 'Yes' : 'No'}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Hash className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <h3 className="text-sm font-medium text-gray-600 mb-1">Last Hash</h3>
          <p className="text-sm font-mono text-gray-900 truncate">
            {blockchain.last_hash || 'N/A'}
          </p>
        </div>
      </div>

      {/* Blockchain History */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h2 className="text-lg font-semibold mb-4">Blockchain History</h2>
        
        {history.length === 0 ? (
          <div className="text-center py-12">
            <Link2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 text-lg mb-2">No blockchain records yet</p>
            <p className="text-gray-500">Automation activities will be recorded here</p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((block, index) => (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                        <span className="text-purple-600 font-bold text-sm">#{block.index || index}</span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {block.data?.type || 'Automation Record'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {block.data?.description || 'No description'}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2 space-y-1">
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <Hash className="w-3 h-3" />
                        <span className="font-mono truncate">{block.hash}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-xs text-gray-500">
                        <Clock className="w-3 h-3" />
                        <span>
                          {block.timestamp
                            ? new Date(block.timestamp).toLocaleString()
                            : 'Unknown time'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="ml-4">
                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                      Verified
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

