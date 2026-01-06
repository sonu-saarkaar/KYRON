import { useState, useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { automationAPI, screenShareAPI } from '../../services/api';
import { Zap, Play, Square, Camera, RefreshCw, Globe, Monitor, ToggleLeft, ToggleRight, ArrowLeft, AlertCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import ServiceCatalog from '../../components/ServiceCatalog/ServiceCatalog';
import ServiceForm from '../../components/ServiceForm/ServiceForm';
import AutomationControlPanel from '../../components/AutomationControlPanel/AutomationControlPanel';
import KyronFloatingLogo from '../../components/KyronFloatingLogo/KyronFloatingLogo';
import PaymentHandler from '../../components/PaymentHandler/PaymentHandler';

const AUTOMATION_STEPS = {
  IDLE: 'idle',
  SELECTING_SERVICE: 'selecting_service',
  FILLING_FORM: 'filling_form',
  STARTING: 'starting',
  RUNNING: 'running',
  PAUSED: 'paused',
  ERROR: 'error',
  COMPLETED: 'completed',
};

export default function Automation() {
  const queryClient = useQueryClient();
  const [currentStep, setCurrentStep] = useState(AUTOMATION_STEPS.SELECTING_SERVICE);
  const [selectedService, setSelectedService] = useState(null);
  const [serviceFormData, setServiceFormData] = useState(null);
  const [url, setUrl] = useState('');
  const [autoFill, setAutoFill] = useState(true);
  const [selectedSession, setSelectedSession] = useState(null);
  const [screenShareMode, setScreenShareMode] = useState('manual');
  const [screenShareSessionId, setScreenShareSessionId] = useState(null);
  const [automationStatus, setAutomationStatus] = useState('idle');
  const [currentAction, setCurrentAction] = useState('');
  const [error, setError] = useState(null);

  // Fetch sessions
  const { data: sessionsData } = useQuery({
    queryKey: ['automation-sessions'],
    queryFn: automationAPI.getSessions,
    refetchInterval: currentStep === AUTOMATION_STEPS.RUNNING ? 2000 : 5000,
  });

  // Get session details for status tracking
  const { data: sessionDetails } = useQuery({
    queryKey: ['automation-session', selectedSession],
    queryFn: () => automationAPI.getSession(selectedSession),
    enabled: !!selectedSession,
    refetchInterval: currentStep === AUTOMATION_STEPS.RUNNING ? 1000 : false,
  });

  // Get session screenshot
  const { data: screenshotData, refetch: refetchScreenshot } = useQuery({
    queryKey: ['screenshot', selectedSession],
    queryFn: () => automationAPI.getScreenshot(selectedSession),
    enabled: !!selectedSession,
    refetchInterval: currentStep === AUTOMATION_STEPS.RUNNING ? 3000 : false,
  });

  // Screen Share Session
  const { data: screenShareSession } = useQuery({
    queryKey: ['screen-share-session', screenShareSessionId],
    queryFn: () => screenShareAPI.getSession(screenShareSessionId),
    enabled: !!screenShareSessionId,
    refetchInterval: 2000,
  });

  // Update automation status from session
  useEffect(() => {
    if (sessionDetails?.session) {
      const session = sessionDetails.session;
      setAutomationStatus(session.status || 'idle');
      setCurrentAction(session.current_action || '');
      
      // Update progress
      if (session.progress) {
        const progress = session.progress;
        const progressText = progress.status === 'processing' 
          ? `${progress.action} (${progress.step}/${progress.total})`
          : progress.action || '';
        setCurrentAction(progressText);
      }
      
      // Check for payment requirement
      if (session.payment_required || session.status === 'payment_required') {
        setShowPaymentHandler(true);
        setPaymentInfo(session.payment_info || {
          amount: 0,
          currency: 'INR',
          payment_methods: ['qr', 'netbanking', 'card']
        });
        setCurrentStep(AUTOMATION_STEPS.ERROR);
      }
      // Check for errors
      else if (session.error) {
        setError({
          message: session.error,
          action: session.error_action || null,
          onAction: () => {
            // Handle error action (e.g., payment)
            if (session.error_type === 'payment_required') {
              setShowPaymentHandler(true);
              setPaymentInfo(session.payment_info);
            }
            setError(null);
          },
        });
        setCurrentStep(AUTOMATION_STEPS.ERROR);
      } else if (session.status === 'completed') {
        setCurrentStep(AUTOMATION_STEPS.COMPLETED);
        if (session.current_action && !session.current_action.includes('successfully')) {
          toast.success('Automation completed successfully!');
        }
      } else if (session.status === 'filling' || session.status === 'running') {
        setCurrentStep(AUTOMATION_STEPS.RUNNING);
      }
    }
  }, [sessionDetails]);

  // Trigger automation mutation
  const triggerMutation = useMutation({
    mutationFn: ({ url, autoFill, serviceData }) => {
      if (serviceData) {
        return automationAPI.triggerService(
          serviceData.serviceId,
          serviceData.config,
          autoFill
        );
      }
      return automationAPI.trigger(url, autoFill);
    },
    onSuccess: (data) => {
      toast.success('Automation started successfully!');
      queryClient.invalidateQueries(['automation-sessions']);
      setSelectedSession(data.session_id);
      setCurrentStep(AUTOMATION_STEPS.RUNNING);
      setAutomationStatus('running');
      
      // Create screen share session
      createScreenShareMutation.mutate(screenShareMode);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Automation failed');
      setCurrentStep(AUTOMATION_STEPS.ERROR);
      setError({
        message: error.response?.data?.detail || 'Failed to start automation',
      });
    },
  });

  // Create screen share session
  const createScreenShareMutation = useMutation({
    mutationFn: (mode) => screenShareAPI.createSession(mode),
    onSuccess: (data) => {
      setScreenShareSessionId(data.session_id);
    },
    onError: (error) => {
      console.error('Failed to create screen share session:', error);
    },
  });

  // Update screen share mode
  const updateModeMutation = useMutation({
    mutationFn: ({ id, mode }) => screenShareAPI.setMode(id, mode),
    onSuccess: () => {
      toast.success('Screen share mode updated!');
      queryClient.invalidateQueries(['screen-share-session', screenShareSessionId]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update mode');
    },
  });

  // Get screen share screenshot
  const { data: screenShareScreenshot, refetch: refetchScreenShare } = useQuery({
    queryKey: ['screen-share-screenshot', screenShareSessionId],
    queryFn: () => screenShareAPI.getScreenshot(screenShareSessionId),
    enabled: !!screenShareSessionId,
    refetchInterval: screenShareSession?.mode === 'automatic' ? 2000 : false,
  });

  const handleServiceSelect = (service) => {
    setSelectedService(service);
    setCurrentStep(AUTOMATION_STEPS.FILLING_FORM);
  };

  const handleFormComplete = (formData) => {
    setServiceFormData(formData);
    setCurrentStep(AUTOMATION_STEPS.STARTING);
    
    // Start automation with service data
    triggerMutation.mutate({
      url: '',
      autoFill: true,
      serviceData: {
        serviceId: selectedService.id,
        config: formData,
      },
    });
  };

  const handleBackToServices = () => {
    setSelectedService(null);
    setServiceFormData(null);
    setCurrentStep(AUTOMATION_STEPS.SELECTING_SERVICE);
    setError(null);
  };

  const handleManualTrigger = () => {
    if (!url.trim()) {
      toast.error('Please enter a URL');
      return;
    }
    setCurrentStep(AUTOMATION_STEPS.STARTING);
    triggerMutation.mutate({ url, autoFill });
  };

  const handleStop = async () => {
    if (selectedSession) {
      try {
        await automationAPI.closeSession(selectedSession);
        setCurrentStep(AUTOMATION_STEPS.IDLE);
        setAutomationStatus('stopped');
        toast.success('Automation stopped');
      } catch (error) {
        toast.error('Failed to stop automation');
      }
    }
  };

  const handlePause = () => {
    setCurrentStep(AUTOMATION_STEPS.PAUSED);
    setAutomationStatus('paused');
    toast.info('Automation paused');
  };

  const handleResume = () => {
    setCurrentStep(AUTOMATION_STEPS.RUNNING);
    setAutomationStatus('running');
    toast.success('Automation resumed');
  };

  const sessions = sessionsData?.sessions || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Automation</h1>
            <p className="text-gray-600">Let KYRON fill forms automatically</p>
          </div>
        </div>
      </div>

      {/* Service Selection Flow */}
      {currentStep === AUTOMATION_STEPS.SELECTING_SERVICE && (
        <ServiceCatalog onSelectService={handleServiceSelect} />
      )}

      {/* Service Form Flow */}
      {currentStep === AUTOMATION_STEPS.FILLING_FORM && selectedService && (
        <div>
          <button
            onClick={handleBackToServices}
            className="mb-4 flex items-center space-x-2 text-purple-600 hover:text-purple-700"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Services</span>
          </button>
          <ServiceForm
            service={selectedService}
            onComplete={handleFormComplete}
            onBack={handleBackToServices}
          />
        </div>
      )}

      {/* Manual URL Input (Fallback) */}
      {currentStep === AUTOMATION_STEPS.IDLE && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Manual Automation</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Website URL
              </label>
              <div className="flex space-x-2">
                <div className="flex-1 relative">
                  <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="url"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com/form"
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none"
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="autoFill"
                checked={autoFill}
                onChange={(e) => setAutoFill(e.target.checked)}
                className="w-4 h-4 text-purple-600 rounded focus:ring-purple-600"
              />
              <label htmlFor="autoFill" className="text-sm text-gray-700">
                Auto-fill form after analysis
              </label>
            </div>

            <button
              onClick={handleManualTrigger}
              disabled={triggerMutation.isPending}
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {triggerMutation.isPending ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Starting...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Start Automation</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {currentStep === AUTOMATION_STEPS.STARTING && (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Starting Automation...</h3>
          <p className="text-gray-600">KYRON is analyzing the form and preparing to fill it</p>
        </div>
      )}

      {/* Screenshot Display */}
      {screenshotData?.screenshot && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Live Automation View</h2>
            <button
              onClick={() => refetchScreenshot()}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
          <img
            src={`data:image/png;base64,${screenshotData.screenshot}`}
            alt="Screenshot"
            className="w-full rounded-lg border border-gray-200"
          />
          {currentAction && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Current Action:</strong> {currentAction}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Screen Sharing */}
      {screenShareSessionId && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold">Screen Sharing</h2>
              <p className="text-sm text-gray-600">Monitor automation in real-time</p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Mode:</span>
              <button
                onClick={() => {
                  const newMode = screenShareMode === 'manual' ? 'automatic' : 'manual';
                  setScreenShareMode(newMode);
                  updateModeMutation.mutate({ id: screenShareSessionId, mode: newMode });
                }}
                className="flex items-center space-x-2 px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
              >
                {screenShareMode === 'automatic' ? (
                  <ToggleRight className="w-5 h-5 text-purple-600" />
                ) : (
                  <ToggleLeft className="w-5 h-5 text-gray-400" />
                )}
                <span className="text-sm">
                  {screenShareMode === 'automatic' ? 'Automatic' : 'Manual'}
                </span>
              </button>
            </div>
          </div>

          {screenShareScreenshot?.screenshot && (
            <div>
              <img
                src={`data:image/png;base64,${screenShareScreenshot.screenshot}`}
                alt="Screen Share"
                className="w-full rounded-lg border border-gray-200"
              />
            </div>
          )}
        </div>
      )}

      {/* Active Sessions */}
      {sessions.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Active Sessions</h2>
          <div className="space-y-3">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
              >
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{session.url}</p>
                  <p className="text-sm text-gray-500">
                    Created: {new Date(session.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => {
                      setSelectedSession(session.session_id);
                      refetchScreenshot();
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition flex items-center space-x-2"
                  >
                    <Camera className="w-4 h-4" />
                    <span>Screenshot</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Control Panel */}
      <AutomationControlPanel
        sessionId={selectedSession}
        status={automationStatus}
        onStop={handleStop}
        onPause={handlePause}
        onResume={handleResume}
        onRefresh={() => refetchScreenshot()}
        currentStep={currentAction}
        error={error}
        onDismissError={() => setError(null)}
      />

      {/* Floating KYRON Logo */}
      {selectedSession && (currentStep === AUTOMATION_STEPS.RUNNING || currentStep === AUTOMATION_STEPS.STARTING) && (
        <KyronFloatingLogo
          onStop={handleStop}
          onExplain={() => {
            toast.info('KYRON is currently filling the form. All steps are automated.');
          }}
          onScreenShare={() => {
            if (!screenShareSessionId) {
              createScreenShareMutation.mutate(screenShareMode);
            }
            toast.info('Screen sharing is active. Check the screen share section above.');
          }}
          isMinimized={isLogoMinimized}
          onToggleMinimize={() => setIsLogoMinimized(!isLogoMinimized)}
        />
      )}

      {/* Payment Handler */}
      {showPaymentHandler && paymentInfo && (
        <PaymentHandler
          amount={paymentInfo.amount || 0}
          currency={paymentInfo.currency || 'INR'}
          onPaymentMethodSelect={(method) => {
            toast.success(`Payment method selected: ${method.name}`);
            // Here you would integrate with payment gateway
            // For now, just close and continue
            setShowPaymentHandler(false);
            setCurrentStep(AUTOMATION_STEPS.RUNNING);
          }}
          onCancel={() => {
            setShowPaymentHandler(false);
            handleStop();
          }}
        />
      )}
    </div>
  );
}
