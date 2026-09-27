import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '../../services/api';
import { Upload, FileText, Trash2, Download, Eye, File } from 'lucide-react';
import toast from 'react-hot-toast';
import { useDropzone } from 'react-dropzone';

export default function Vault() {
  const queryClient = useQueryClient();
  const [showUpload, setShowUpload] = useState(false);
  const [uploadData, setUploadData] = useState({ name: '', type: '' });

  // Fetch documents
  const { data, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await documentsAPI.list();
      return response.documents || [];
    },
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: ({ file, name, type }) => documentsAPI.upload(file, name, type),
    onSuccess: () => {
      toast.success('Document uploaded successfully!');
      queryClient.invalidateQueries(['documents']);
      setShowUpload(false);
      setUploadData({ name: '', type: '' });
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Upload failed');
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: documentsAPI.delete,
    onSuccess: () => {
      toast.success('Document deleted successfully!');
      queryClient.invalidateQueries(['documents']);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Delete failed');
    },
  });

  const onDrop = (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (!uploadData.name || !uploadData.type) {
        toast.error('Please enter document name and type');
        return;
      }
      uploadMutation.mutate({ file, name: uploadData.name, type: uploadData.type });
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.png', '.jpg', '.jpeg'],
    },
    maxFiles: 1,
  });

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(id);
    }
  };

  const documents = data || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Document Vault</h1>
            <p className="text-gray-600">
              Store your documents securely. KYRON will use them to auto-fill forms.
            </p>
          </div>
          <button
            onClick={() => setShowUpload(!showUpload)}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition flex items-center space-x-2"
          >
            <Upload className="w-5 h-5" />
            <span>Upload Document</span>
          </button>
        </div>
      </div>

      {/* Upload Form */}
      {showUpload && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Upload New Document</h2>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Name
                </label>
                <input
                  type="text"
                  value={uploadData.name}
                  onChange={(e) => setUploadData({ ...uploadData, name: e.target.value })}
                  placeholder="e.g., PAN Card"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Document Type
                </label>
                <select
                  value={uploadData.type}
                  onChange={(e) => setUploadData({ ...uploadData, type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none"
                  required
                >
                  <option value="">Select Type</option>
                  <option value="PAN">PAN Card</option>
                  <option value="Aadhaar">Aadhaar</option>
                  <option value="Passport">Passport</option>
                  <option value="Driving License">Driving License</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
                isDragActive
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-300 hover:border-purple-400'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              {isDragActive ? (
                <p className="text-purple-600 font-medium">Drop the file here...</p>
              ) : (
                <>
                  <p className="text-gray-600 mb-2">
                    Drag & drop a file here, or click to select
                  </p>
                  <p className="text-sm text-gray-500">PDF, PNG, JPG (Max 10MB)</p>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Documents Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : documents.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 text-lg mb-2">No documents yet</p>
          <p className="text-gray-500">Upload your first document to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} document={doc} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  );
}

function DocumentCard({ document, onDelete }) {
  const getTypeColor = (type) => {
    const colors = {
      PAN: 'bg-blue-100 text-blue-600',
      Aadhaar: 'bg-green-100 text-green-600',
      Passport: 'bg-purple-100 text-purple-600',
      'Driving License': 'bg-yellow-100 text-yellow-600',
    };
    return colors[type] || 'bg-gray-100 text-gray-600';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <File className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{document.name}</h3>
            <span className={`text-xs px-2 py-1 rounded-full ${getTypeColor(document.type)}`}>
              {document.type}
            </span>
          </div>
        </div>
        <button
          onClick={() => onDelete(document.id)}
          className="text-red-500 hover:text-red-700 transition"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </div>
      
      <div className="text-sm text-gray-500 mb-4">
        Uploaded: {new Date(document.uploaded_at).toLocaleDateString()}
      </div>
      
      {document.ocr_processed && (
        <div className="text-xs text-green-600 mb-4">
          ✓ OCR Processed
        </div>
      )}
      
      <div className="flex space-x-2">
        <a
          href={`http://127.0.0.1:8000/api/documents/${document.id}`}
          target="_blank"
          className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm"
        >
          <Download className="w-4 h-4" />
          <span>Download</span>
        </a>
        {document.extracted_text && (
          <button className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-sm">
            <Eye className="w-4 h-4" />
            <span>View Text</span>
          </button>
        )}
      </div>
    </div>
  );
}

