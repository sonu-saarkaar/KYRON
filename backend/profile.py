"""
This file handles Master Profile operations.
Users can create, read, update their profile data.
This data will be used by the AI agent to auto-fill forms.
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from auth_utils import verify_token
from services.database_manager import get_database_manager

# Create router for profile endpoints
router = APIRouter()

# Try to get database manager
try:
    db_manager = get_database_manager()
    use_database = db_manager.is_available()
except:
    use_database = False
    profiles_db = {}  # Fallback in-memory storage

# Comprehensive Profile data model for KYRON Autofill
class ProfileUpdate(BaseModel):
    # Basic Personal Information (English & Hindi)
    fullName: Optional[str] = None
    fullNameHindi: Optional[str] = None
    fatherName: Optional[str] = None
    fatherNameHindi: Optional[str] = None
    motherName: Optional[str] = None
    motherNameHindi: Optional[str] = None
    
    # Date of Birth & Age
    dateOfBirth: Optional[str] = None
    age: Optional[int] = None
    
    # Gender & Caste/Category
    gender: Optional[str] = None
    caste: Optional[str] = None
    category: Optional[str] = None  # General, OBC, SC, ST, etc.
    
    # Government ID Documents
    aadhaarNumber: Optional[str] = None
    panNumber: Optional[str] = None
    voterIdNumber: Optional[str] = None
    
    # Contact Information (Multiple)
    email: Optional[str] = None
    alternateEmail: Optional[str] = None
    phone: Optional[str] = None
    alternatePhone: Optional[str] = None
    emergencyPhone: Optional[str] = None
    
    # Current Address
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    
    # Permanent Address
    permanentAddress: Optional[str] = None
    permanentCity: Optional[str] = None
    permanentState: Optional[str] = None
    permanentPincode: Optional[str] = None
    
    # 10th Grade Details
    class10Board: Optional[str] = None
    class10School: Optional[str] = None
    class10Year: Optional[str] = None
    class10Percentage: Optional[str] = None
    class10RollNumber: Optional[str] = None
    
    # 12th Grade Details
    class12Board: Optional[str] = None
    class12School: Optional[str] = None
    class12Year: Optional[str] = None
    class12Percentage: Optional[str] = None
    class12RollNumber: Optional[str] = None
    class12Stream: Optional[str] = None  # Science, Commerce, Arts
    
    # Current Education Status
    currentEducation: Optional[str] = None  # Pursuing/Completed
    currentInstitution: Optional[str] = None
    currentCourse: Optional[str] = None
    currentYear: Optional[str] = None
    
    # Higher Education (Existing fields)
    qualification: Optional[str] = None
    university: Optional[str] = None
    
    # Occupation
    occupation: Optional[str] = None
    
    # Bank Details
    bankName: Optional[str] = None
    accountNumber: Optional[str] = None
    ifsc: Optional[str] = None
    
    # Pre-uploaded Documents (URLs/Paths)
    photoUrl: Optional[str] = None
    signatureUrl: Optional[str] = None
    
    # Additional Address Fields (for Bihar/State services)
    district: Optional[str] = None
    block: Optional[str] = None
    block_circle: Optional[str] = None
    panchayat: Optional[str] = None
    panchayat_ward: Optional[str] = None
    postOffice: Optional[str] = None
    post_office: Optional[str] = None
    
    # Additional Personal Details
    maritalStatus: Optional[str] = None
    spouseName: Optional[str] = None
    bloodGroup: Optional[str] = None
    nationality: Optional[str] = None
    
    # Additional Contact
    whatsappNumber: Optional[str] = None
    telegramUsername: Optional[str] = None
    
    # Additional IDs
    drivingLicenseNumber: Optional[str] = None
    passportNumber: Optional[str] = None
    rationCardNumber: Optional[str] = None
    
    # Family Details
    numberOfDependents: Optional[int] = None
    familyIncome: Optional[str] = None
    
    # Additional Education
    graduationYear: Optional[str] = None
    graduationPercentage: Optional[str] = None
    postGraduationYear: Optional[str] = None
    postGraduationPercentage: Optional[str] = None
    
    # Professional Details
    companyName: Optional[str] = None
    designation: Optional[str] = None
    workExperience: Optional[str] = None
    salary: Optional[str] = None

@router.get("/me")
def get_profile_me(authorization: str = Header(None, alias="Authorization")):
    """
    Get current user's profile data.
    Uses /me endpoint so frontend doesn't need to know user_id.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Get profile from database
    if use_database:
        profile = db_manager.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
    else:
        # Fallback to in-memory
        if user_id not in profiles_db:
            raise HTTPException(status_code=404, detail="Profile not found")
        profile = profiles_db[user_id]
    
    return {
        "success": True,
        "message": "Profile retrieved successfully",
        "profile": profile
    }

@router.put("/update")
def update_profile(profile: ProfileUpdate, authorization: str = Header(None, alias="Authorization")):
    """
    Create or update current user's profile data.
    Uses /update endpoint so frontend doesn't need to know user_id.
    """
    # Verify token and get user_id
    user_id = verify_token(authorization)
    
    # Prepare profile data
    profile_data = profile.dict(exclude_unset=True)
    
    # Update or create profile in database
    if use_database:
        try:
            updated_profile = db_manager.create_or_update_profile(user_id, profile_data)
            return {
                "success": True,
                "message": "Profile saved successfully",
                "profile": updated_profile
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")
    else:
        # Fallback to in-memory
        if user_id in profiles_db:
            existing_profile = profiles_db[user_id]
            existing_profile.update(profile_data)
            profiles_db[user_id] = existing_profile
        else:
            profiles_db[user_id] = profile_data
        
        return {
            "success": True,
            "message": "Profile saved successfully",
            "profile": profiles_db[user_id]
        }

# Keep old endpoints for backward compatibility
@router.get("/{user_id}")
def get_profile(user_id: str, authorization: str = Header(None)):
    """Get user's profile data (old endpoint, kept for compatibility)"""
    verify_token(authorization)  # Verify token but allow any user_id for now
    if user_id not in profiles_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profiles_db[user_id]

@router.put("/{user_id}")
def update_profile_old(user_id: str, profile: ProfileUpdate, authorization: str = Header(None)):
    """Update user's profile data (old endpoint, kept for compatibility)"""
    verify_token(authorization)  # Verify token but allow any user_id for now
    if user_id in profiles_db:
        existing_profile = profiles_db[user_id]
        update_data = profile.dict(exclude_unset=True)
        existing_profile.update(update_data)
        profiles_db[user_id] = existing_profile
    else:
        profiles_db[user_id] = profile.dict(exclude_unset=True)
    return {"message": "Profile saved successfully", "profile": profiles_db[user_id]}

