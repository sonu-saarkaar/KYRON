import { useState } from 'react';
import { X, CreditCard, QrCode, Building2, CheckCircle } from 'lucide-react';

export default function PaymentHandler({ 
  amount, 
  currency = 'INR',
  onPaymentMethodSelect,
  onCancel 
}) {
  const [selectedMethod, setSelectedMethod] = useState(null);

  const paymentMethods = [
    {
      id: 'qr',
      name: 'QR Code',
      icon: QrCode,
      description: 'Scan QR code to pay',
      color: 'blue'
    },
    {
      id: 'netbanking',
      name: 'Net Banking',
      icon: Building2,
      description: 'Pay via online banking',
      color: 'green'
    },
    {
      id: 'card',
      name: 'Debit/Credit Card',
      icon: CreditCard,
      description: 'Pay using card',
      color: 'purple'
    },
  ];

  const handleSelect = (method) => {
    setSelectedMethod(method);
    onPaymentMethodSelect?.(method);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-t-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">Payment Required</h2>
              <p className="text-purple-100 text-sm mt-1">Complete payment to continue</p>
            </div>
            <button
              onClick={onCancel}
              className="text-white hover:text-purple-200 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Amount */}
        <div className="p-6 border-b border-gray-200">
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">Total Amount</p>
            <p className="text-3xl font-bold text-gray-900">
              {currency} {amount}
            </p>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="p-6 space-y-3">
          <p className="text-sm font-medium text-gray-700 mb-4">Select Payment Method</p>
          
          {paymentMethods.map((method) => {
            const Icon = method.icon;
            const isSelected = selectedMethod?.id === method.id;
            
            const colorClasses = {
              blue: {
                border: isSelected ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-gray-300',
                bg: 'bg-blue-100',
                text: 'text-blue-600'
              },
              green: {
                border: isSelected ? 'border-green-600 bg-green-50' : 'border-gray-200 hover:border-gray-300',
                bg: 'bg-green-100',
                text: 'text-green-600'
              },
              purple: {
                border: isSelected ? 'border-purple-600 bg-purple-50' : 'border-gray-200 hover:border-gray-300',
                bg: 'bg-purple-100',
                text: 'text-purple-600'
              }
            };
            
            const colors = colorClasses[method.color] || colorClasses.blue;
            
            return (
              <button
                key={method.id}
                onClick={() => handleSelect(method)}
                className={`w-full flex items-center space-x-4 p-4 border-2 rounded-lg transition ${colors.border}`}
              >
                <div className={`w-12 h-12 ${colors.bg} rounded-lg flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${colors.text}`} />
                </div>
                <div className="flex-1 text-left">
                  <p className="font-semibold text-gray-900">{method.name}</p>
                  <p className="text-sm text-gray-500">{method.description}</p>
                </div>
                {isSelected && (
                  <CheckCircle className={`w-5 h-5 ${colors.text}`} />
                )}
              </button>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-6 bg-gray-50 rounded-b-xl border-t border-gray-200">
          <div className="flex items-center space-x-2 text-xs text-gray-600">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span>Secure payment gateway</span>
          </div>
        </div>
      </div>
    </div>
  );
}

