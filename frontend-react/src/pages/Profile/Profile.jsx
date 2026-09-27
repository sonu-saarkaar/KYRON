import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { profileAPI, agentAPI, documentsAPI } from '../../services/api';
import { Save, User, Mail, Phone, MapPin, Calendar, GraduationCap, Building2, FileText, CreditCard, Briefcase, Shield, Activity, X, Upload, Image, FileCheck, Trash2, Eye } from 'lucide-react';
import toast from 'react-hot-toast';
import TrackRequest from '../../components/TrackRequest/TrackRequest';

export default function Profile() {
  const queryClient = useQueryClient();
  const [showTrackRequest, setShowTrackRequest] = useState(false);
  const [selectedRequestId, setSelectedRequestId] = useState(null);
  const [requests, setRequests] = useState([]);
  const [formData, setFormData] = useState({
    // Personal Information (English & Hindi)
    fullName: '',
    fullNameHindi: '',
    fatherName: '',
    fatherNameHindi: '',
    motherName: '',
    motherNameHindi: '',
    
    // Date & Age
    dateOfBirth: '',
    age: '',
    
    // Gender & Caste
    gender: '',
    caste: '',
    category: '',
    
    // Government IDs
    aadhaarNumber: '',
    panNumber: '',
    voterIdNumber: '',
    
    // Contact Information
    email: '',
    alternateEmail: '',
    phone: '',
    alternatePhone: '',
    emergencyPhone: '',
    
    // Current Address
    address: '',
    city: '',
    state: '',
    pincode: '',
    
    // Permanent Address
    permanentAddress: '',
    permanentCity: '',
    permanentState: '',
    permanentPincode: '',
    
    // 10th Grade
    class10Board: '',
    class10School: '',
    class10Year: '',
    class10Percentage: '',
    class10RollNumber: '',
    
    // 12th Grade
    class12Board: '',
    class12School: '',
    class12Year: '',
    class12Percentage: '',
    class12RollNumber: '',
    class12Stream: '',
    
    // Current Education
    currentEducation: '',
    currentInstitution: '',
    currentCourse: '',
    currentYear: '',
    
    // Higher Education
    qualification: '',
    university: '',
    
    // Occupation
    occupation: '',
    
    // Bank Details
    bankName: '',
    accountNumber: '',
    ifsc: '',
    
    // Documents
    photoUrl: '',
    signatureUrl: '',
    
    // Additional Address Fields (for Bihar/State services)
    district: '',
    block: '',
    panchayat: '',
    postOffice: '',
    
    // Additional Personal Details
    maritalStatus: '',
    spouseName: '',
    bloodGroup: '',
    nationality: '',
    
    // Additional Contact
    whatsappNumber: '',
    telegramUsername: '',
    
    // Additional IDs
    drivingLicenseNumber: '',
    passportNumber: '',
    rationCardNumber: '',
    
    // Family Details
    numberOfDependents: '',
    familyIncome: '',
    
    // Additional Education
    graduationYear: '',
    graduationPercentage: '',
    postGraduationYear: '',
    postGraduationPercentage: '',
    
    // Professional Details
    companyName: '',
    designation: '',
    workExperience: '',
    salary: '',
  });
  
  // Documents state
  const [documents, setDocuments] = useState([]);
  const [uploadingDoc, setUploadingDoc] = useState(false);

  // Fetch profile
  const { data: profileData, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await profileAPI.get();
      return response.profile || {};
    },
  });
  
  // Fetch documents
  const { data: documentsData, refetch: refetchDocuments } = useQuery({
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
  
  useEffect(() => {
    if (documentsData) {
      setDocuments(documentsData);
    }
  }, [documentsData]);

  // Update profile mutation
  const updateMutation = useMutation({
    mutationFn: profileAPI.update,
    onSuccess: () => {
      toast.success('Profile updated successfully!');
      queryClient.invalidateQueries(['profile']);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    },
  });

  useEffect(() => {
    if (profileData && Object.keys(profileData).length > 0) {
      setFormData({
        // Personal Information
        fullName: profileData.fullName || '',
        fullNameHindi: profileData.fullNameHindi || '',
        fatherName: profileData.fatherName || '',
        fatherNameHindi: profileData.fatherNameHindi || '',
        motherName: profileData.motherName || '',
        motherNameHindi: profileData.motherNameHindi || '',
        
        // Date & Age
        dateOfBirth: profileData.dateOfBirth || '',
        age: profileData.age || '',
        
        // Gender & Caste
        gender: profileData.gender || '',
        caste: profileData.caste || '',
        category: profileData.category || '',
        
        // Government IDs
        aadhaarNumber: profileData.aadhaarNumber || '',
        panNumber: profileData.panNumber || '',
        voterIdNumber: profileData.voterIdNumber || '',
        
        // Contact
        email: profileData.email || '',
        alternateEmail: profileData.alternateEmail || '',
        phone: profileData.phone || '',
        alternatePhone: profileData.alternatePhone || '',
        emergencyPhone: profileData.emergencyPhone || '',
        
        // Current Address
        address: profileData.address || '',
        city: profileData.city || '',
        state: profileData.state || '',
        pincode: profileData.pincode || '',
        
        // Permanent Address
        permanentAddress: profileData.permanentAddress || '',
        permanentCity: profileData.permanentCity || '',
        permanentState: profileData.permanentState || '',
        permanentPincode: profileData.permanentPincode || '',
        
        // 10th Grade
        class10Board: profileData.class10Board || '',
        class10School: profileData.class10School || '',
        class10Year: profileData.class10Year || '',
        class10Percentage: profileData.class10Percentage || '',
        class10RollNumber: profileData.class10RollNumber || '',
        
        // 12th Grade
        class12Board: profileData.class12Board || '',
        class12School: profileData.class12School || '',
        class12Year: profileData.class12Year || '',
        class12Percentage: profileData.class12Percentage || '',
        class12RollNumber: profileData.class12RollNumber || '',
        class12Stream: profileData.class12Stream || '',
        
        // Current Education
        currentEducation: profileData.currentEducation || '',
        currentInstitution: profileData.currentInstitution || '',
        currentCourse: profileData.currentCourse || '',
        currentYear: profileData.currentYear || '',
        
        // Higher Education
        qualification: profileData.qualification || '',
        university: profileData.university || '',
        
        // Occupation
        occupation: profileData.occupation || '',
        
        // Bank
        bankName: profileData.bankName || '',
        accountNumber: profileData.accountNumber || '',
        ifsc: profileData.ifsc || '',
        
        // Documents
        photoUrl: profileData.photoUrl || '',
        signatureUrl: profileData.signatureUrl || '',
        
        // Additional Address Fields
        district: profileData.district || '',
        block: profileData.block || profileData.block_circle || '',
        panchayat: profileData.panchayat || profileData.panchayat_ward || '',
        postOffice: profileData.postOffice || profileData.post_office || '',
        
        // Additional Personal Details
        maritalStatus: profileData.maritalStatus || '',
        spouseName: profileData.spouseName || '',
        bloodGroup: profileData.bloodGroup || '',
        nationality: profileData.nationality || 'Indian',
        
        // Additional Contact
        whatsappNumber: profileData.whatsappNumber || '',
        telegramUsername: profileData.telegramUsername || '',
        
        // Additional IDs
        drivingLicenseNumber: profileData.drivingLicenseNumber || '',
        passportNumber: profileData.passportNumber || '',
        rationCardNumber: profileData.rationCardNumber || '',
        
        // Family Details
        numberOfDependents: profileData.numberOfDependents || '',
        familyIncome: profileData.familyIncome || '',
        
        // Additional Education
        graduationYear: profileData.graduationYear || '',
        graduationPercentage: profileData.graduationPercentage || '',
        postGraduationYear: profileData.postGraduationYear || '',
        postGraduationPercentage: profileData.postGraduationPercentage || '',
        
        // Professional Details
        companyName: profileData.companyName || '',
        designation: profileData.designation || '',
        workExperience: profileData.workExperience || '',
        salary: profileData.salary || '',
      });
    }
  }, [profileData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    // Auto-calculate age from date of birth
    if (name === 'dateOfBirth' && value) {
      const birthDate = new Date(value);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      setFormData(prev => ({ ...prev, age: age }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateMutation.mutate(formData);
  };
  
  // Document upload handler
  const handleDocumentUpload = async (e, docType) => {
    const file = e.target.files[0];
    if (!file) return;
    
    setUploadingDoc(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', `${docType} document`);
      
      const response = await documentsAPI.upload(file, `${docType} document`);
      
      // Update profile with document ID
      if (docType === 'photo') {
        setFormData(prev => ({ ...prev, photoUrl: response.document_id || response.document?.id }));
      } else if (docType === 'signature') {
        setFormData(prev => ({ ...prev, signatureUrl: response.document_id || response.document?.id }));
      }
      
      // Also update the profile in backend
      updateMutation.mutate({
        ...formData,
        [docType === 'photo' ? 'photoUrl' : 'signatureUrl']: response.document_id || response.document?.id
      });
      
      toast.success(`${docType} uploaded successfully!`);
      refetchDocuments();
    } catch (error) {
      toast.error(`Failed to upload ${docType}: ${error.message}`);
    } finally {
      setUploadingDoc(false);
    }
  };
  
  // Delete document
  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await documentsAPI.delete(docId);
      toast.success('Document deleted successfully!');
      refetchDocuments();
    } catch (error) {
      toast.error(`Failed to delete document: ${error.message}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Load requests on mount
  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      // This would fetch from backend - for now using mock data
      // const response = await agentAPI.getUserRequests();
      // setRequests(response.requests || []);
      
      // Mock data for demonstration
      const mockRequests = [
        {
          id: 'req-1',
          service_id: 'pan_card',
          status: 'running',
          current_action: 'Filling form fields',
          progress: { completed: 3, total: 6 },
          created_at: new Date().toISOString(),
          official_url: 'https://www.pan.utiitsl.com'
        }
      ];
      setRequests(mockRequests);
    } catch (error) {
      console.error('Error loading requests:', error);
    }
  };

  const handleTrackRequest = (requestId) => {
    setSelectedRequestId(requestId);
    setShowTrackRequest(true);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Track Request Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Activity className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Track Requests</h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">Monitor your automation progress</p>
            </div>
          </div>
          <button
            onClick={loadRequests}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
          >
            Refresh
          </button>
        </div>

        {requests.length === 0 ? (
          <div className="text-center py-8">
            <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">No active requests</p>
            <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
              Start a new request from the Chat page
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {requests.map((request) => (
              <div
                key={request.id}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-purple-300 dark:hover:border-purple-700 transition cursor-pointer"
                onClick={() => handleTrackRequest(request.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        request.status === 'running' ? 'bg-blue-500 animate-pulse' :
                        request.status === 'completed' ? 'bg-green-500' :
                        request.status === 'error' ? 'bg-red-500' :
                        'bg-gray-400'
                      }`} />
                      <h3 className="font-semibold text-gray-900 dark:text-white capitalize">
                        {request.service_id?.replace('_', ' ') || 'Request'}
                      </h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        request.status === 'running' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200' :
                        request.status === 'completed' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200' :
                        request.status === 'error' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200' :
                        'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
                      }`}>
                        {request.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      {request.current_action || 'No action in progress'}
                    </p>
                    {request.progress && (
                      <div className="mt-3">
                        <div className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 mb-1">
                          <span>Progress</span>
                          <span>{request.progress.completed} / {request.progress.total} steps</span>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2 rounded-full transition-all"
                            style={{
                              width: `${(request.progress.completed / request.progress.total) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                  <button className="ml-4 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-semibold">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Track Request Modal */}
      {showTrackRequest && selectedRequestId && (
        <div className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Request Details</h2>
              <button
                onClick={() => {
                  setShowTrackRequest(false);
                  setSelectedRequestId(null);
                }}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              >
                <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              </button>
            </div>
            <TrackRequest requestId={selectedRequestId} />
          </div>
        </div>
      )}

      {/* Master Profile Section */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-8 border border-gray-200 dark:border-gray-700">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Master Profile</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Fill in your comprehensive information once. KYRON will use it to auto-fill forms like PAN card applications, university applications, and more.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <Section title="Personal Information" icon={<User className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Full Name (English)"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                required
              />
              <InputField
                label="Full Name (Hindi)"
                name="fullNameHindi"
                value={formData.fullNameHindi}
                onChange={handleChange}
                placeholder="पूरा नाम"
              />
              <InputField
                label="Father's Name (English)"
                name="fatherName"
                value={formData.fatherName}
                onChange={handleChange}
              />
              <InputField
                label="Father's Name (Hindi)"
                name="fatherNameHindi"
                value={formData.fatherNameHindi}
                onChange={handleChange}
                placeholder="पिता का नाम"
              />
              <InputField
                label="Mother's Name (English)"
                name="motherName"
                value={formData.motherName}
                onChange={handleChange}
              />
              <InputField
                label="Mother's Name (Hindi)"
                name="motherNameHindi"
                value={formData.motherNameHindi}
                onChange={handleChange}
                placeholder="माता का नाम"
              />
              <InputField
                label="Date of Birth"
                name="dateOfBirth"
                type="date"
                value={formData.dateOfBirth}
                onChange={handleChange}
              />
              <InputField
                label="Age"
                name="age"
                type="number"
                value={formData.age}
                onChange={handleChange}
                disabled
              />
              <InputField
                label="Gender"
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                type="select"
                options={['', 'Male', 'Female', 'Other']}
              />
              <InputField
                label="Caste"
                name="caste"
                value={formData.caste}
                onChange={handleChange}
              />
              <InputField
                label="Category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                type="select"
                options={['', 'General', 'OBC', 'SC', 'ST', 'EWS']}
              />
              <InputField
                label="Occupation"
                name="occupation"
                value={formData.occupation}
                onChange={handleChange}
              />
            </div>
          </Section>

          {/* Government ID Documents */}
          <Section title="Government ID Documents" icon={<Shield className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <InputField
                label="Aadhaar Number"
                name="aadhaarNumber"
                value={formData.aadhaarNumber}
                onChange={handleChange}
                placeholder="XXXX-XXXX-XXXX"
              />
              <InputField
                label="PAN Number"
                name="panNumber"
                value={formData.panNumber}
                onChange={handleChange}
                placeholder="ABCDE1234F"
              />
              <InputField
                label="Voter ID Number"
                name="voterIdNumber"
                value={formData.voterIdNumber}
                onChange={handleChange}
              />
            </div>
          </Section>

          {/* Contact Information */}
          <Section title="Contact Information" icon={<Mail className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Primary Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
              />
              <InputField
                label="Alternate Email"
                name="alternateEmail"
                type="email"
                value={formData.alternateEmail}
                onChange={handleChange}
              />
              <InputField
                label="Primary Phone"
                name="phone"
                type="tel"
                value={formData.phone}
                onChange={handleChange}
              />
              <InputField
                label="Alternate Phone"
                name="alternatePhone"
                type="tel"
                value={formData.alternatePhone}
                onChange={handleChange}
              />
              <InputField
                label="Emergency Phone"
                name="emergencyPhone"
                type="tel"
                value={formData.emergencyPhone}
                onChange={handleChange}
              />
            </div>
          </Section>

          {/* Current Address */}
          <Section title="Current Address" icon={<MapPin className="w-5 h-5" />}>
            <div className="grid grid-cols-1 gap-4">
              <InputField
                label="Address"
                name="address"
                value={formData.address}
                onChange={handleChange}
              />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <InputField
                  label="City"
                  name="city"
                  value={formData.city}
                  onChange={handleChange}
                />
                <InputField
                  label="State"
                  name="state"
                  value={formData.state}
                  onChange={handleChange}
                />
                <InputField
                  label="Pincode"
                  name="pincode"
                  value={formData.pincode}
                  onChange={handleChange}
                />
              </div>
            </div>
          </Section>

          {/* Permanent Address */}
          <Section title="Permanent Address" icon={<MapPin className="w-5 h-5" />}>
            <div className="grid grid-cols-1 gap-4">
              <InputField
                label="Permanent Address"
                name="permanentAddress"
                value={formData.permanentAddress}
                onChange={handleChange}
              />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <InputField
                  label="City"
                  name="permanentCity"
                  value={formData.permanentCity}
                  onChange={handleChange}
                />
                <InputField
                  label="State"
                  name="permanentState"
                  value={formData.permanentState}
                  onChange={handleChange}
                />
                <InputField
                  label="Pincode"
                  name="permanentPincode"
                  value={formData.permanentPincode}
                  onChange={handleChange}
                />
              </div>
            </div>
          </Section>

          {/* 10th Grade Details */}
          <Section title="10th Grade Details" icon={<GraduationCap className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Board"
                name="class10Board"
                value={formData.class10Board}
                onChange={handleChange}
                placeholder="e.g., CBSE, ICSE, State Board"
              />
              <InputField
                label="School Name"
                name="class10School"
                value={formData.class10School}
                onChange={handleChange}
              />
              <InputField
                label="Year of Passing"
                name="class10Year"
                value={formData.class10Year}
                onChange={handleChange}
                placeholder="e.g., 2018"
              />
              <InputField
                label="Percentage/CGPA"
                name="class10Percentage"
                value={formData.class10Percentage}
                onChange={handleChange}
                placeholder="e.g., 85% or 8.5 CGPA"
              />
              <InputField
                label="Roll Number"
                name="class10RollNumber"
                value={formData.class10RollNumber}
                onChange={handleChange}
              />
            </div>
          </Section>

          {/* 12th Grade Details */}
          <Section title="12th Grade Details" icon={<GraduationCap className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Board"
                name="class12Board"
                value={formData.class12Board}
                onChange={handleChange}
                placeholder="e.g., CBSE, ICSE, State Board"
              />
              <InputField
                label="School Name"
                name="class12School"
                value={formData.class12School}
                onChange={handleChange}
              />
              <InputField
                label="Stream"
                name="class12Stream"
                value={formData.class12Stream}
                onChange={handleChange}
                type="select"
                options={['', 'Science', 'Commerce', 'Arts']}
              />
              <InputField
                label="Year of Passing"
                name="class12Year"
                value={formData.class12Year}
                onChange={handleChange}
                placeholder="e.g., 2020"
              />
              <InputField
                label="Percentage/CGPA"
                name="class12Percentage"
                value={formData.class12Percentage}
                onChange={handleChange}
                placeholder="e.g., 85% or 8.5 CGPA"
              />
              <InputField
                label="Roll Number"
                name="class12RollNumber"
                value={formData.class12RollNumber}
                onChange={handleChange}
              />
            </div>
          </Section>

          {/* Current Education Status */}
          <Section title="Current Education Status" icon={<Calendar className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Current Education"
                name="currentEducation"
                value={formData.currentEducation}
                onChange={handleChange}
                type="select"
                options={['', 'Pursuing', 'Completed', 'Not Pursuing']}
              />
              <InputField
                label="Institution Name"
                name="currentInstitution"
                value={formData.currentInstitution}
                onChange={handleChange}
              />
              <InputField
                label="Course Name"
                name="currentCourse"
                value={formData.currentCourse}
                onChange={handleChange}
                placeholder="e.g., B.Tech, MBA, BA"
              />
              <InputField
                label="Current Year/Semester"
                name="currentYear"
                value={formData.currentYear}
                onChange={handleChange}
                placeholder="e.g., 2nd Year, 4th Semester"
              />
            </div>
          </Section>

          {/* Higher Education */}
          <Section title="Higher Education" icon={<GraduationCap className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Highest Qualification"
                name="qualification"
                value={formData.qualification}
                onChange={handleChange}
                placeholder="e.g., Bachelor's, Master's, PhD"
              />
              <InputField
                label="University"
                name="university"
                value={formData.university}
                onChange={handleChange}
              />
            </div>
          </Section>

          {/* Bank Details */}
          <Section title="Bank Details" icon={<Building2 className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <InputField
                label="Bank Name"
                name="bankName"
                value={formData.bankName}
                onChange={handleChange}
              />
              <InputField
                label="Account Number"
                name="accountNumber"
                value={formData.accountNumber}
                onChange={handleChange}
              />
              <InputField
                label="IFSC Code"
                name="ifsc"
                value={formData.ifsc}
                onChange={handleChange}
              />
            </div>
          </Section>

          {/* Additional Address Fields */}
          <Section title="Additional Address Details (For State Services)" icon={<MapPin className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="District"
                name="district"
                value={formData.district}
                onChange={handleChange}
                placeholder="e.g., Patna, Gaya"
              />
              <InputField
                label="Block / Circle"
                name="block"
                value={formData.block}
                onChange={handleChange}
                placeholder="Block or Circle name"
              />
              <InputField
                label="Panchayat / Ward"
                name="panchayat"
                value={formData.panchayat}
                onChange={handleChange}
                placeholder="Panchayat or Ward number"
              />
              <InputField
                label="Post Office"
                name="postOffice"
                value={formData.postOffice}
                onChange={handleChange}
                placeholder="Post office name"
              />
            </div>
          </Section>
          
          {/* Additional Personal Details */}
          <Section title="Additional Personal Details" icon={<User className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Marital Status"
                name="maritalStatus"
                value={formData.maritalStatus}
                onChange={handleChange}
                type="select"
                options={['', 'Single', 'Married', 'Divorced', 'Widowed']}
              />
              <InputField
                label="Spouse Name"
                name="spouseName"
                value={formData.spouseName}
                onChange={handleChange}
              />
              <InputField
                label="Blood Group"
                name="bloodGroup"
                value={formData.bloodGroup}
                onChange={handleChange}
                type="select"
                options={['', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']}
              />
              <InputField
                label="Nationality"
                name="nationality"
                value={formData.nationality}
                onChange={handleChange}
              />
            </div>
          </Section>
          
          {/* Additional Contact */}
          <Section title="Additional Contact Information" icon={<Phone className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="WhatsApp Number"
                name="whatsappNumber"
                value={formData.whatsappNumber}
                onChange={handleChange}
                type="tel"
                placeholder="10-digit WhatsApp number"
              />
              <InputField
                label="Telegram Username"
                name="telegramUsername"
                value={formData.telegramUsername}
                onChange={handleChange}
                placeholder="@username"
              />
            </div>
          </Section>
          
          {/* Additional IDs */}
          <Section title="Additional Identity Documents" icon={<Shield className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <InputField
                label="Driving License Number"
                name="drivingLicenseNumber"
                value={formData.drivingLicenseNumber}
                onChange={handleChange}
              />
              <InputField
                label="Passport Number"
                name="passportNumber"
                value={formData.passportNumber}
                onChange={handleChange}
              />
              <InputField
                label="Ration Card Number"
                name="rationCardNumber"
                value={formData.rationCardNumber}
                onChange={handleChange}
              />
            </div>
          </Section>
          
          {/* Family Details */}
          <Section title="Family Details" icon={<User className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Number of Dependents"
                name="numberOfDependents"
                type="number"
                value={formData.numberOfDependents}
                onChange={handleChange}
                placeholder="0"
              />
              <InputField
                label="Family Income (Annual)"
                name="familyIncome"
                value={formData.familyIncome}
                onChange={handleChange}
                placeholder="₹ per annum"
              />
            </div>
          </Section>
          
          {/* Additional Education */}
          <Section title="Additional Education Details" icon={<GraduationCap className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Graduation Year"
                name="graduationYear"
                value={formData.graduationYear}
                onChange={handleChange}
                placeholder="e.g., 2020"
              />
              <InputField
                label="Graduation Percentage/CGPA"
                name="graduationPercentage"
                value={formData.graduationPercentage}
                onChange={handleChange}
                placeholder="e.g., 85% or 8.5"
              />
              <InputField
                label="Post Graduation Year"
                name="postGraduationYear"
                value={formData.postGraduationYear}
                onChange={handleChange}
                placeholder="e.g., 2022"
              />
              <InputField
                label="Post Graduation Percentage/CGPA"
                name="postGraduationPercentage"
                value={formData.postGraduationPercentage}
                onChange={handleChange}
                placeholder="e.g., 90% or 9.0"
              />
            </div>
          </Section>
          
          {/* Professional Details */}
          <Section title="Professional Details" icon={<Briefcase className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputField
                label="Company Name"
                name="companyName"
                value={formData.companyName}
                onChange={handleChange}
              />
              <InputField
                label="Designation"
                name="designation"
                value={formData.designation}
                onChange={handleChange}
              />
              <InputField
                label="Work Experience (Years)"
                name="workExperience"
                type="number"
                value={formData.workExperience}
                onChange={handleChange}
                placeholder="e.g., 5"
              />
              <InputField
                label="Salary (Annual)"
                name="salary"
                value={formData.salary}
                onChange={handleChange}
                placeholder="₹ per annum"
              />
            </div>
          </Section>
          
          {/* Documents Upload & Display */}
          <Section title="Documents Upload & Management" icon={<FileText className="w-5 h-5" />}>
            <div className="space-y-6">
              {/* Photo Upload */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Profile Photo
                </label>
                <div className="flex items-center space-x-4">
                  {formData.photoUrl && (
                    <div className="relative">
                      <img 
                        src={formData.photoUrl.startsWith('http') ? formData.photoUrl : `/api/documents/${formData.photoUrl}`}
                        alt="Profile Photo" 
                        className="w-24 h-24 object-cover rounded-lg border border-gray-300 dark:border-gray-600"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  <div className="flex-1">
                    <label className="cursor-pointer">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleDocumentUpload(e, 'photo')}
                        className="hidden"
                        disabled={uploadingDoc}
                      />
                      <div className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition inline-flex items-center space-x-2">
                        <Upload className="w-4 h-4" />
                        <span>{formData.photoUrl ? 'Change Photo' : 'Upload Photo'}</span>
                      </div>
                    </label>
                    {formData.photoUrl && (
                      <InputField
                        label="Photo URL (or upload above)"
                        name="photoUrl"
                        value={formData.photoUrl}
                        onChange={handleChange}
                        placeholder="URL or document ID"
                      />
                    )}
                  </div>
                </div>
              </div>
              
              {/* Signature Upload */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Signature
                </label>
                <div className="flex items-center space-x-4">
                  {formData.signatureUrl && (
                    <div className="relative">
                      <img 
                        src={formData.signatureUrl.startsWith('http') ? formData.signatureUrl : `/api/documents/${formData.signatureUrl}`}
                        alt="Signature" 
                        className="w-32 h-16 object-contain rounded-lg border border-gray-300 dark:border-gray-600 bg-white"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  <div className="flex-1">
                    <label className="cursor-pointer">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleDocumentUpload(e, 'signature')}
                        className="hidden"
                        disabled={uploadingDoc}
                      />
                      <div className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition inline-flex items-center space-x-2">
                        <Upload className="w-4 h-4" />
                        <span>{formData.signatureUrl ? 'Change Signature' : 'Upload Signature'}</span>
                      </div>
                    </label>
                    {formData.signatureUrl && (
                      <InputField
                        label="Signature URL (or upload above)"
                        name="signatureUrl"
                        value={formData.signatureUrl}
                        onChange={handleChange}
                        placeholder="URL or document ID"
                      />
                    )}
                  </div>
                </div>
              </div>
              
              {/* All Documents List */}
              <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                  All Uploaded Documents
                </label>
                {documents.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No documents uploaded yet.</p>
                ) : (
                  <div className="space-y-2">
                    {documents.map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <FileCheck className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{doc.filename || doc.description || 'Document'}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'Unknown date'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => window.open(`/api/documents/${doc.id}`, '_blank')}
                            className="p-2 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition"
                            title="View Document"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteDocument(doc.id)}
                            className="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg transition"
                            title="Delete Document"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  💡 Tip: Upload your documents here. KYRON will automatically use them when filling forms. You can also manually set document URLs in the fields above.
                </p>
              </div>
            </div>
          </Section>

          {/* Submit Button */}
          <div className="flex justify-end pt-6 border-t">
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 shadow-lg"
            >
              {updateMutation.isPending ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  <span>Save Master Profile</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function Section({ title, icon, children }) {
  return (
    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:border-purple-300 dark:hover:border-purple-700 transition bg-white dark:bg-gray-800">
      <div className="flex items-center space-x-2 mb-4">
        <div className="text-purple-600 dark:text-purple-400">{icon}</div>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h2>
      </div>
      {children}
    </div>
  );
}

function InputField({ label, name, value, onChange, type = 'text', required = false, options = null, placeholder = '', disabled = false }) {
  if (type === 'select' && options) {
    return (
      <div>
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label} {required && <span className="text-red-500">*</span>}
        </label>
        <select
          id={name}
          name={name}
          value={value}
          onChange={onChange}
          required={required}
          disabled={disabled}
          className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none transition disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          {options.map((opt) => (
            <option key={opt} value={opt}>
              {opt || `Select ${label}`}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent outline-none transition disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
      />
    </div>
  );
}
