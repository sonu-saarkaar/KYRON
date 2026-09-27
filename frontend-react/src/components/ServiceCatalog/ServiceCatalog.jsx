import { useQuery } from '@tanstack/react-query';
import { serviceAPI } from '../../services/api';
import { CreditCard, FileText, Award, Home, CheckCircle, Clock } from 'lucide-react';

export default function ServiceCatalog({ onSelectService }) {
  const { data, isLoading } = useQuery({
    queryKey: ['service-catalog'],
    queryFn: serviceAPI.getCatalog,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const services = data?.services || [];

  const getServiceIcon = (serviceId) => {
    const icons = {
      pan_card: CreditCard,
      income_certificate: FileText,
      caste_certificate: Award,
      domicile: Home,
    };
    return icons[serviceId] || FileText;
  };

  const getServiceColor = (serviceId) => {
    const colors = {
      pan_card: 'from-blue-500 to-blue-600',
      income_certificate: 'from-green-500 to-green-600',
      caste_certificate: 'from-purple-500 to-purple-600',
      domicile: 'from-orange-500 to-orange-600',
    };
    return colors[serviceId] || 'from-gray-500 to-gray-600';
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Available Services</h2>
        <p className="text-gray-600">Select a service to start automation</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.map((service) => {
          const Icon = getServiceIcon(service.id);
          const colorClass = getServiceColor(service.id);

          return (
            <div
              key={service.id}
              onClick={() => onSelectService(service)}
              className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg hover:border-purple-300 transition cursor-pointer group"
            >
              <div className={`w-16 h-16 bg-gradient-to-br ${colorClass} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                <Icon className="w-8 h-8 text-white" />
              </div>

              <h3 className="text-xl font-bold text-gray-900 mb-2">{service.name}</h3>
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">{service.description}</p>

              <div className="space-y-2 mb-4">
                <div className="flex items-center text-xs text-gray-500">
                  <Clock className="w-3 h-3 mr-1" />
                  <span>{service.estimated_time}</span>
                </div>
                <div className="flex items-center text-xs text-gray-500">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  <span>{service.steps?.length || 0} steps</span>
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mb-4">
                {service.benefits?.slice(0, 2).map((benefit, idx) => (
                  <span
                    key={idx}
                    className="text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded-full"
                  >
                    {benefit}
                  </span>
                ))}
              </div>

              <button className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-2 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition text-sm">
                Start Automation
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

