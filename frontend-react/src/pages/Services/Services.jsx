import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { serviceAPI } from '../../services/api';
import { 
  CreditCard, 
  GraduationCap, 
  FileText, 
  Building2, 
  Shield, 
  Car, 
  Home, 
  Heart,
  Briefcase,
  Sparkles,
  ArrowRight,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const SERVICE_ICONS = {
  pan_card: CreditCard,
  aadhaar: Shield,
  passport: FileText,
  driving_license: Car,
  voter_id: FileText,
  education: GraduationCap,
  job: Briefcase,
  housing: Home,
  health: Heart,
  business: Building2,
};

export default function Services() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const { data: catalog, isLoading } = useQuery({
    queryKey: ['services'],
    queryFn: async () => {
      const response = await serviceAPI.getCatalog();
      return response;
    },
  });

  const categories = [
    { id: 'all', name: 'All Services', icon: Sparkles },
    { id: 'government', name: 'Government', icon: Building2 },
    { id: 'education', name: 'Education', icon: GraduationCap },
    { id: 'financial', name: 'Financial', icon: CreditCard },
    { id: 'healthcare', name: 'Healthcare', icon: Heart },
    { id: 'other', name: 'Other', icon: FileText },
  ];

  const filteredServices = catalog?.services?.filter(service => {
    const matchesSearch = service.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         service.description?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || service.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }) || [];

  const handleServiceClick = (serviceId) => {
    navigate(`/chat?service=${serviceId}`);
    toast.success('Redirecting to chat...');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">KYRON Services</h1>
            <p className="text-gray-600 dark:text-gray-400">Discover what KYRON can do for you</p>
          </div>
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search services..."
            className="w-full px-4 py-3 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
          />
        </div>
      </div>

      {/* Categories */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-3">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition ${
                  selectedCategory === category.id
                    ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{category.name}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Services Grid */}
      {filteredServices.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">No services found</p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
            Try adjusting your search or category filter
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServices.map((service) => {
            const Icon = SERVICE_ICONS[service.id] || FileText;
            return (
              <div
                key={service.id}
                onClick={() => handleServiceClick(service.id)}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 border-2 border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-700 transition-all cursor-pointer group shadow-sm hover:shadow-lg"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-indigo-100 dark:from-purple-900/30 dark:to-indigo-900/30 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Icon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition" />
                </div>
                
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                  {service.name || service.id.replace('_', ' ').toUpperCase()}
                </h3>
                
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                  {service.description || 'Automated form filling service'}
                </p>

                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-xs text-gray-500 dark:text-gray-400">Available</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Info Section */}
      <div className="mt-12 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-2xl p-8 border border-purple-200 dark:border-purple-800">
        <div className="flex items-start space-x-4">
          <Sparkles className="w-8 h-8 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              How KYRON Services Work
            </h3>
            <p className="text-gray-700 dark:text-gray-300 mb-4">
              KYRON uses your Master Profile to automatically fill forms for various government and private services. 
              Just select a service, and KYRON will handle the rest.
            </p>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Automatic form filling using your Master Profile</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Secure document handling</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Real-time progress tracking</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>24/7 AI assistance</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

