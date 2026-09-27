import { useState } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useTheme } from '../../contexts/ThemeContext';
import { useQuery } from '@tanstack/react-query';
import { profileAPI } from '../../services/api';
import { LogOut, User, FileText, Zap, List, Home, Link2, Volume2, MessageSquare, Settings, Sparkles, Moon, Sun, Edit2, Mail, Phone, MapPin, Calendar, Shield, CreditCard, Building2, GraduationCap, X } from 'lucide-react';

export default function Layout() {
  const { logout, isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [showMasterProfile, setShowMasterProfile] = useState(false);

  // Fetch profile for master profile section
  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const response = await profileAPI.get();
      return response.profile || {};
    },
  });

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  const profileCompletion = profile ? (
    ((profile.fullName ? 1 : 0) +
     (profile.email ? 1 : 0) +
     (profile.phone ? 1 : 0) +
     (profile.dateOfBirth ? 1 : 0) +
     (profile.address ? 1 : 0)) / 5 * 100
  ) : 0;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Navigation Bar */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-6">
              <Link to="/chat" className="flex items-center space-x-2 group">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  KYRON
                </span>
              </Link>

              {/* Master Profile Icon in Logo Area */}
              <div 
                className="relative"
                onMouseEnter={() => setShowMasterProfile(true)}
                onMouseLeave={() => setShowMasterProfile(false)}
              >
                <button 
                  className="relative flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 transition-all shadow-lg hover:scale-110 group"
                  title="Master Profile"
                >
                  {profile?.photoUrl ? (
                    <img 
                      src={profile.photoUrl.startsWith('http') ? profile.photoUrl : `/api/documents/${profile.photoUrl}`}
                      alt="Profile" 
                      className="w-full h-full rounded-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <User className={`w-6 h-6 text-white ${profile?.photoUrl ? 'hidden' : ''}`} />
                  {profile && Object.keys(profile).length > 0 && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white dark:border-gray-800 flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  )}
                </button>

                {/* Comprehensive Master Profile Dropdown */}
                {showMasterProfile && (
                  <div className="absolute top-full left-0 mt-3 w-96 max-h-[80vh] overflow-y-auto bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50">
                    {/* Header */}
                    <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between rounded-t-2xl">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-indigo-500 flex items-center justify-center">
                          {profile?.photoUrl ? (
                            <img 
                              src={profile.photoUrl.startsWith('http') ? profile.photoUrl : `/api/documents/${profile.photoUrl}`}
                              alt="Profile" 
                              className="w-full h-full rounded-full object-cover"
                            />
                          ) : (
                            <User className="w-6 h-6 text-white" />
                          )}
                        </div>
                        <div>
                          <h3 className="font-bold text-gray-900 dark:text-white">Master Profile</h3>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {profile?.fullName || 'Complete your profile'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Link
                          to="/profile"
                          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                          title="Edit Profile"
                        >
                          <Edit2 className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </Link>
                        <button
                          onClick={() => setShowMasterProfile(false)}
                          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                        >
                          <X className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </button>
                      </div>
                    </div>
                    
                    {/* Profile Completion */}
                    <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">Profile Completion</span>
                        <span className="font-bold text-purple-600 dark:text-purple-400">{Math.round(profileCompletion)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                        <div
                          className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2.5 rounded-full transition-all"
                          style={{ width: `${profileCompletion}%` }}
                        />
                      </div>
                    </div>

                    {/* Comprehensive Profile Data */}
                    <div className="p-4 space-y-4 max-h-[60vh] overflow-y-auto">
                      {/* Personal Information */}
                      <ProfileSection title="Personal Information" icon={<User className="w-4 h-4" />}>
                        <ProfileField label="Full Name" value={profile?.fullName} />
                        <ProfileField label="Name (Hindi)" value={profile?.fullNameHindi} />
                        <ProfileField label="Father's Name" value={profile?.fatherName} />
                        <ProfileField label="Mother's Name" value={profile?.motherName} />
                        <ProfileField label="Date of Birth" value={profile?.dateOfBirth} />
                        <ProfileField label="Age" value={profile?.age} />
                        <ProfileField label="Gender" value={profile?.gender} />
                        <ProfileField label="Caste" value={profile?.caste} />
                        <ProfileField label="Category" value={profile?.category} />
                        <ProfileField label="Marital Status" value={profile?.maritalStatus} />
                        <ProfileField label="Blood Group" value={profile?.bloodGroup} />
                        <ProfileField label="Nationality" value={profile?.nationality} />
                      </ProfileSection>

                      {/* Contact Information */}
                      <ProfileSection title="Contact Information" icon={<Mail className="w-4 h-4" />}>
                        <ProfileField label="Email" value={profile?.email} />
                        <ProfileField label="Alternate Email" value={profile?.alternateEmail} />
                        <ProfileField label="Phone" value={profile?.phone} />
                        <ProfileField label="Alternate Phone" value={profile?.alternatePhone} />
                        <ProfileField label="Emergency Phone" value={profile?.emergencyPhone} />
                        <ProfileField label="WhatsApp" value={profile?.whatsappNumber} />
                      </ProfileSection>

                      {/* Government IDs */}
                      <ProfileSection title="Government IDs" icon={<Shield className="w-4 h-4" />}>
                        <ProfileField label="Aadhaar" value={profile?.aadhaarNumber ? `****${profile.aadhaarNumber.slice(-4)}` : null} />
                        <ProfileField label="PAN" value={profile?.panNumber} />
                        <ProfileField label="Voter ID" value={profile?.voterIdNumber} />
                        <ProfileField label="Driving License" value={profile?.drivingLicenseNumber} />
                        <ProfileField label="Passport" value={profile?.passportNumber} />
                        <ProfileField label="Ration Card" value={profile?.rationCardNumber} />
                      </ProfileSection>

                      {/* Address */}
                      <ProfileSection title="Current Address" icon={<MapPin className="w-4 h-4" />}>
                        <ProfileField label="Address" value={profile?.address} />
                        <ProfileField label="City" value={profile?.city} />
                        <ProfileField label="State" value={profile?.state} />
                        <ProfileField label="PIN Code" value={profile?.pincode} />
                      </ProfileSection>

                      {/* Permanent Address */}
                      <ProfileSection title="Permanent Address" icon={<MapPin className="w-4 h-4" />}>
                        <ProfileField label="Address" value={profile?.permanentAddress} />
                        <ProfileField label="City" value={profile?.permanentCity} />
                        <ProfileField label="State" value={profile?.permanentState} />
                        <ProfileField label="PIN Code" value={profile?.permanentPincode} />
                      </ProfileSection>

                      {/* Additional Address (State Services) */}
                      <ProfileSection title="Additional Address Details" icon={<MapPin className="w-4 h-4" />}>
                        <ProfileField label="District" value={profile?.district} />
                        <ProfileField label="Block/Circle" value={profile?.block || profile?.block_circle} />
                        <ProfileField label="Panchayat/Ward" value={profile?.panchayat || profile?.panchayat_ward} />
                        <ProfileField label="Post Office" value={profile?.postOffice || profile?.post_office} />
                      </ProfileSection>

                      {/* Education */}
                      <ProfileSection title="Education" icon={<GraduationCap className="w-4 h-4" />}>
                        <ProfileField label="10th Board" value={profile?.class10Board} />
                        <ProfileField label="10th School" value={profile?.class10School} />
                        <ProfileField label="10th Year" value={profile?.class10Year} />
                        <ProfileField label="12th Board" value={profile?.class12Board} />
                        <ProfileField label="12th School" value={profile?.class12School} />
                        <ProfileField label="12th Stream" value={profile?.class12Stream} />
                        <ProfileField label="12th Year" value={profile?.class12Year} />
                        <ProfileField label="Qualification" value={profile?.qualification} />
                        <ProfileField label="University" value={profile?.university} />
                      </ProfileSection>

                      {/* Professional */}
                      <ProfileSection title="Professional" icon={<Building2 className="w-4 h-4" />}>
                        <ProfileField label="Occupation" value={profile?.occupation} />
                        <ProfileField label="Company" value={profile?.companyName} />
                        <ProfileField label="Designation" value={profile?.designation} />
                        <ProfileField label="Experience" value={profile?.workExperience ? `${profile.workExperience} years` : null} />
                      </ProfileSection>

                      {/* Bank Details */}
                      <ProfileSection title="Bank Details" icon={<CreditCard className="w-4 h-4" />}>
                        <ProfileField label="Bank Name" value={profile?.bankName} />
                        <ProfileField label="Account Number" value={profile?.accountNumber ? `****${profile.accountNumber.slice(-4)}` : null} />
                        <ProfileField label="IFSC" value={profile?.ifsc} />
                      </ProfileSection>

                      {/* Family */}
                      <ProfileSection title="Family Details" icon={<User className="w-4 h-4" />}>
                        <ProfileField label="Spouse Name" value={profile?.spouseName} />
                        <ProfileField label="Dependents" value={profile?.numberOfDependents} />
                        <ProfileField label="Family Income" value={profile?.familyIncome} />
                      </ProfileSection>
                    </div>

                    {/* Footer Actions */}
                    <div className="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4 rounded-b-2xl">
                      <Link
                        to="/profile"
                        className="w-full block text-center px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 transition shadow-lg"
                      >
                        <div className="flex items-center justify-center space-x-2">
                          <Edit2 className="w-4 h-4" />
                          <span>Edit Complete Profile</span>
                        </div>
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-1">
              <NavLink to="/chat" icon={<MessageSquare className="w-4 h-4" />}>
                Chat
              </NavLink>
              <NavLink to="/services" icon={<Sparkles className="w-4 h-4" />}>
                Services
              </NavLink>
              <NavLink to="/dashboard" icon={<Home className="w-4 h-4" />}>
                Dashboard
              </NavLink>
              <NavLink to="/profile" icon={<User className="w-4 h-4" />}>
                Profile
              </NavLink>
              <NavLink to="/vault" icon={<FileText className="w-4 h-4" />}>
                Vault
              </NavLink>
              <NavLink to="/automation" icon={<Zap className="w-4 h-4" />}>
                Automation
              </NavLink>
              <NavLink to="/settings" icon={<Settings className="w-4 h-4" />}>
                Settings
              </NavLink>
              <button
                onClick={toggleTheme}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
                title="Toggle theme"
              >
                {theme === 'dark' ? (
                  <Sun className="w-5 h-5 text-yellow-400" />
                ) : (
                  <Moon className="w-5 h-5 text-gray-600" />
                )}
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  );
}

function NavLink({ to, icon, children }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
    >
      {icon}
      <span>{children}</span>
    </Link>
  );
}

function ProfileSection({ title, icon, children }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-2 text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
        <div className="text-purple-600 dark:text-purple-400">{icon}</div>
        <span>{title}</span>
      </div>
      <div className="space-y-1.5 pl-6">
        {children}
      </div>
    </div>
  );
}

function ProfileField({ label, value }) {
  if (!value) return null;
  
  return (
    <div className="flex items-start justify-between text-xs">
      <span className="text-gray-500 dark:text-gray-400 font-medium">{label}:</span>
      <span className="text-gray-900 dark:text-white font-semibold text-right max-w-[60%] break-words">
        {value}
      </span>
    </div>
  );
}

