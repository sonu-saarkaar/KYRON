"""
KYRON PostgreSQL Database Service
Handles relational data, complex queries, and transactions
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
import logging
import os

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    service_requests = relationship("ServiceRequest", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Basic Personal Information (English & Hindi)
    full_name = Column(String)
    full_name_hindi = Column(String)
    father_name = Column(String)
    father_name_hindi = Column(String)
    mother_name = Column(String)
    mother_name_hindi = Column(String)
    
    # Date of Birth & Age
    date_of_birth = Column(String)
    age = Column(Integer)
    
    # Gender & Caste/Category
    gender = Column(String)
    caste = Column(String)
    category = Column(String)
    
    # Government ID Documents
    aadhaar_number = Column(String)
    pan_number = Column(String)
    voter_id_number = Column(String)
    
    # Contact Information (Multiple)
    email = Column(String)
    alternate_email = Column(String)
    phone = Column(String)
    alternate_phone = Column(String)
    emergency_phone = Column(String)
    
    # Current Address
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    pincode = Column(String)
    
    # Permanent Address
    permanent_address = Column(Text)
    permanent_city = Column(String)
    permanent_state = Column(String)
    permanent_pincode = Column(String)
    
    # 10th Grade Details
    class10_board = Column(String)
    class10_school = Column(String)
    class10_year = Column(String)
    class10_percentage = Column(String)
    class10_roll_number = Column(String)
    
    # 12th Grade Details
    class12_board = Column(String)
    class12_school = Column(String)
    class12_year = Column(String)
    class12_percentage = Column(String)
    class12_roll_number = Column(String)
    class12_stream = Column(String)
    
    # Current Education Status
    current_education = Column(String)
    current_institution = Column(String)
    current_course = Column(String)
    current_year = Column(String)
    
    # Higher Education
    qualification = Column(String)
    university = Column(String)
    
    # Occupation
    occupation = Column(String)
    
    # Bank Details
    bank_name = Column(String)
    account_number = Column(String)
    ifsc = Column(String)
    
    # Pre-uploaded Documents (URLs/Paths)
    photo_url = Column(String)
    signature_url = Column(String)
    
    # Flexible additional fields
    profile_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="profile")

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(String, nullable=False)
    service_name = Column(String)
    status = Column(String, default="draft")
    form_data = Column(JSON)
    selected_options = Column(JSON)
    acknowledgement_number = Column(String)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="service_requests")

class AutomationSession(Base):
    __tablename__ = "automation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(String)
    status = Column(String, default="active")
    mode = Column(String, default="automatic")  # manual or automatic
    session_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class AgentActivity(Base):
    __tablename__ = "agent_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    description = Column(Text)
    activity_metadata = Column(JSON)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    timestamp = Column(DateTime, default=datetime.now, index=True)


class PostgreSQLService:
    """PostgreSQL service for KYRON relational data"""
    
    def __init__(self):
        """Initialize PostgreSQL connection"""
        postgres_url = os.getenv(
            "POSTGRES_URL",
            "postgresql://postgres:postgres@localhost:5432/kyron_db"
        )
        
        try:
            self.engine = create_engine(postgres_url, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            logger.info(f"PostgreSQL connected: {postgres_url}")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    # ==================== User Operations ====================
    
    def create_user(self, user_data: Dict) -> int:
        """Create a new user"""
        db = self.get_session()
        try:
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user.id
        finally:
            db.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "hashed_password": user.hashed_password,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "is_active": user.is_active
                }
            return None
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        db = self.get_session()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                return {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "is_active": user.is_active
                }
            return None
        finally:
            db.close()
    
    # ==================== Profile Operations ====================
    
    def create_or_update_profile(self, user_id: int, profile_data: Dict) -> Dict:
        """Create or update user profile"""
        db = self.get_session()
        try:
            profile = db.query(Profile).filter(Profile.user_id == user_id).first()
            
            # Convert camelCase to snake_case for database
            field_mapping = {
                "fullName": "full_name",
                "fullNameHindi": "full_name_hindi",
                "fatherName": "father_name",
                "fatherNameHindi": "father_name_hindi",
                "motherName": "mother_name",
                "motherNameHindi": "mother_name_hindi",
                "dateOfBirth": "date_of_birth",
                "aadhaarNumber": "aadhaar_number",
                "panNumber": "pan_number",
                "voterIdNumber": "voter_id_number",
                "alternateEmail": "alternate_email",
                "alternatePhone": "alternate_phone",
                "emergencyPhone": "emergency_phone",
                "permanentAddress": "permanent_address",
                "permanentCity": "permanent_city",
                "permanentState": "permanent_state",
                "permanentPincode": "permanent_pincode",
                "class10Board": "class10_board",
                "class10School": "class10_school",
                "class10Year": "class10_year",
                "class10Percentage": "class10_percentage",
                "class10RollNumber": "class10_roll_number",
                "class12Board": "class12_board",
                "class12School": "class12_school",
                "class12Year": "class12_year",
                "class12Percentage": "class12_percentage",
                "class12RollNumber": "class12_roll_number",
                "class12Stream": "class12_stream",
                "currentEducation": "current_education",
                "currentInstitution": "current_institution",
                "currentCourse": "current_course",
                "currentYear": "current_year",
                "bankName": "bank_name",
                "accountNumber": "account_number",
                "photoUrl": "photo_url",
                "signatureUrl": "signature_url",
            }
            
            db_data = {}
            for key, value in profile_data.items():
                db_key = field_mapping.get(key, key)
                db_data[db_key] = value
            
            if profile:
                # Update existing
                for key, value in db_data.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                profile.updated_at = datetime.now()
            else:
                # Create new
                db_data["user_id"] = user_id
                profile = Profile(**db_data)
                db.add(profile)
            
            db.commit()
            db.refresh(profile)
            
            # Return with camelCase keys
            return self.get_profile(user_id)
        finally:
            db.close()
    
    def get_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile with all comprehensive fields"""
        db = self.get_session()
        try:
            profile = db.query(Profile).filter(Profile.user_id == user_id).first()
            if profile:
                return {
                    "id": profile.id,
                    "user_id": profile.user_id,
                    # Basic Information (English & Hindi)
                    "fullName": profile.full_name,
                    "fullNameHindi": profile.full_name_hindi,
                    "fatherName": profile.father_name,
                    "fatherNameHindi": profile.father_name_hindi,
                    "motherName": profile.mother_name,
                    "motherNameHindi": profile.mother_name_hindi,
                    # Date & Age
                    "dateOfBirth": profile.date_of_birth,
                    "age": profile.age,
                    # Gender & Caste
                    "gender": profile.gender,
                    "caste": profile.caste,
                    "category": profile.category,
                    # Government IDs
                    "aadhaarNumber": profile.aadhaar_number,
                    "panNumber": profile.pan_number,
                    "voterIdNumber": profile.voter_id_number,
                    # Contact Information
                    "email": profile.email,
                    "alternateEmail": profile.alternate_email,
                    "phone": profile.phone,
                    "alternatePhone": profile.alternate_phone,
                    "emergencyPhone": profile.emergency_phone,
                    # Current Address
                    "address": profile.address,
                    "city": profile.city,
                    "state": profile.state,
                    "pincode": profile.pincode,
                    # Permanent Address
                    "permanentAddress": profile.permanent_address,
                    "permanentCity": profile.permanent_city,
                    "permanentState": profile.permanent_state,
                    "permanentPincode": profile.permanent_pincode,
                    # 10th Grade
                    "class10Board": profile.class10_board,
                    "class10School": profile.class10_school,
                    "class10Year": profile.class10_year,
                    "class10Percentage": profile.class10_percentage,
                    "class10RollNumber": profile.class10_roll_number,
                    # 12th Grade
                    "class12Board": profile.class12_board,
                    "class12School": profile.class12_school,
                    "class12Year": profile.class12_year,
                    "class12Percentage": profile.class12_percentage,
                    "class12RollNumber": profile.class12_roll_number,
                    "class12Stream": profile.class12_stream,
                    # Current Education
                    "currentEducation": profile.current_education,
                    "currentInstitution": profile.current_institution,
                    "currentCourse": profile.current_course,
                    "currentYear": profile.current_year,
                    # Higher Education
                    "qualification": profile.qualification,
                    "university": profile.university,
                    # Occupation
                    "occupation": profile.occupation,
                    # Bank Details
                    "bankName": profile.bank_name,
                    "accountNumber": profile.account_number,
                    "ifsc": profile.ifsc,
                    # Documents
                    "photoUrl": profile.photo_url,
                    "signatureUrl": profile.signature_url,
                }
            return None
        finally:
            db.close()
    
    # ==================== Service Request Operations ====================
    
    def create_service_request(self, user_id: int, request_data: Dict) -> int:
        """Create a service request"""
        db = self.get_session()
        try:
            request_data["user_id"] = user_id
            request = ServiceRequest(**request_data)
            db.add(request)
            db.commit()
            db.refresh(request)
            return request.id
        finally:
            db.close()
    
    def get_user_service_requests(self, user_id: int) -> List[Dict]:
        """Get all service requests for a user"""
        db = self.get_session()
        try:
            requests = db.query(ServiceRequest).filter(
                ServiceRequest.user_id == user_id
            ).order_by(ServiceRequest.created_at.desc()).all()
            
            return [{
                "id": req.id,
                "service_id": req.service_id,
                "service_name": req.service_name,
                "status": req.status,
                "form_data": req.form_data,
                "created_at": req.created_at.isoformat() if req.created_at else None
            } for req in requests]
        finally:
            db.close()
    
    # ==================== Health Check ====================
    
    def health_check(self) -> Dict:
        """Check database health"""
        try:
            db = self.get_session()
            db.execute("SELECT 1")
            db.close()
            return {"status": "healthy", "database": "postgresql"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


# Global instance
_postgres_service: Optional[PostgreSQLService] = None

def get_postgres_service() -> Optional[PostgreSQLService]:
    """Get or create global PostgreSQL service instance"""
    global _postgres_service
    if _postgres_service is None:
        try:
            _postgres_service = PostgreSQLService()
        except Exception as e:
            logger.warning(f"PostgreSQL not available: {e}. Continuing with MongoDB only.")
            return None
    return _postgres_service

