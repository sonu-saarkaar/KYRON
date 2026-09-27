"""
KYRON Seed Data Script
Creates mock user data for testing and development
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import profile and auth modules (use in-memory storage for seeding)
from profile import profiles_db
from auth import users_db
from documents import documents_db
from agent_logic import agent_status_db
import uuid
from datetime import datetime

def seed_data():
    """Seed the database with mock user data"""
    
    print("🌱 Seeding KYRON database with mock data...")
    
    # Test User 1
    user1_id = "user_001"
    users_db[user1_id] = {
        "id": user1_id,
        "email": "john.doe@example.com",
        "fullName": "John Doe",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Z0pW.7t0jKXS",  # password: test123
        "created_at": datetime.now().isoformat()
    }
    
    profiles_db[user1_id] = {
        # Personal Information (English & Hindi)
        "fullName": "John Doe",
        "fullNameHindi": "जॉन डो",
        "fatherName": "Robert Doe",
        "fatherNameHindi": "रॉबर्ट डो",
        "motherName": "Mary Doe",
        "motherNameHindi": "मैरी डो",
        
        # Date & Age
        "dateOfBirth": "1990-05-15",
        "age": 34,
        
        # Gender & Caste
        "gender": "Male",
        "caste": "General",
        "category": "General",
        
        # Government IDs
        "aadhaarNumber": "1234-5678-9012",
        "panNumber": "ABCDE1234F",
        "voterIdNumber": "ABC1234567",
        
        # Contact Information
        "email": "john.doe@example.com",
        "alternateEmail": "john.alternate@example.com",
        "phone": "+91-9876543210",
        "alternatePhone": "+91-9876543299",
        "emergencyPhone": "+91-9876543288",
        
        # Current Address
        "address": "123 Main Street, Apartment 4B",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400001",
        
        # Permanent Address
        "permanentAddress": "456 Old Street, Village Center",
        "permanentCity": "Pune",
        "permanentState": "Maharashtra",
        "permanentPincode": "411001",
        
        # 10th Grade
        "class10Board": "CBSE",
        "class10School": "Delhi Public School",
        "class10Year": "2006",
        "class10Percentage": "88.5%",
        "class10RollNumber": "1234567",
        
        # 12th Grade
        "class12Board": "CBSE",
        "class12School": "Delhi Public School",
        "class12Year": "2008",
        "class12Percentage": "85.2%",
        "class12RollNumber": "1234568",
        "class12Stream": "Science",
        
        # Current Education
        "currentEducation": "Completed",
        "currentInstitution": "IIT Mumbai",
        "currentCourse": "B.Tech in Computer Science",
        "currentYear": "Graduated",
        
        # Higher Education
        "qualification": "Bachelor of Engineering",
        "university": "Mumbai University",
        
        # Occupation
        "occupation": "Software Engineer",
        
        # Bank Details
        "bankName": "State Bank of India",
        "accountNumber": "123456789012",
        "ifsc": "SBIN0001234",
        
        # Documents
        "photoUrl": "/uploads/john_photo.jpg",
        "signatureUrl": "/uploads/john_signature.jpg",
    }
    
    agent_status_db[user1_id] = "inactive"
    
    # Mock document for user 1
    documents_db[user1_id] = [
        {
            "id": str(uuid.uuid4()),
            "name": "PAN Card",
            "type": "PAN",
            "file_path": "uploads/mock_pan.pdf",
            "file_extension": ".pdf",
            "uploaded_at": datetime.now().isoformat(),
            "ocr_processed": True,
            "ocr_result": {
                "success": True,
                "method": "ocr",
                "confidence": 95.5
            },
            "extracted_text": "INCOME TAX DEPARTMENT\nGOVT. OF INDIA\nPermanent Account Number Card\nABCDE1234F\nName: JOHN DOE\nFather's Name: ROBERT DOE\nDate of Birth: 15/05/1990\nSignature",
            "text_length": 150
        }
    ]
    
    # Test User 2
    user2_id = "user_002"
    users_db[user2_id] = {
        "id": user2_id,
        "email": "jane.smith@example.com",
        "fullName": "Jane Smith",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Z0pW.7t0jKXS",  # password: test123
        "created_at": datetime.now().isoformat()
    }
    
    profiles_db[user2_id] = {
        # Personal Information (English & Hindi)
        "fullName": "Jane Smith",
        "fullNameHindi": "जेन स्मिथ",
        "fatherName": "James Smith",
        "fatherNameHindi": "जेम्स स्मिथ",
        "motherName": "Patricia Smith",
        "motherNameHindi": "पेट्रीशिया स्मिथ",
        
        # Date & Age
        "dateOfBirth": "1992-08-22",
        "age": 32,
        
        # Gender & Caste
        "gender": "Female",
        "caste": "OBC",
        "category": "OBC",
        
        # Government IDs
        "aadhaarNumber": "2345-6789-0123",
        "panNumber": "XYZAB5678C",
        "voterIdNumber": "DEF7890123",
        
        # Contact Information
        "email": "jane.smith@example.com",
        "alternateEmail": "jane.work@example.com",
        "phone": "+91-9876543211",
        "alternatePhone": "+91-9876543277",
        "emergencyPhone": "+91-9876543266",
        
        # Current Address
        "address": "456 Oak Avenue, Block C",
        "city": "Delhi",
        "state": "Delhi",
        "pincode": "110001",
        
        # Permanent Address
        "permanentAddress": "789 Green Park, Sector 12",
        "permanentCity": "Noida",
        "permanentState": "Uttar Pradesh",
        "permanentPincode": "201301",
        
        # 10th Grade
        "class10Board": "ICSE",
        "class10School": "St. Mary's School",
        "class10Year": "2008",
        "class10Percentage": "92.0%",
        "class10RollNumber": "2345678",
        
        # 12th Grade
        "class12Board": "ICSE",
        "class12School": "St. Mary's School",
        "class12Year": "2010",
        "class12Percentage": "89.5%",
        "class12RollNumber": "2345679",
        "class12Stream": "Commerce",
        
        # Current Education
        "currentEducation": "Pursuing",
        "currentInstitution": "Delhi University",
        "currentCourse": "MBA in Finance",
        "currentYear": "2nd Year",
        
        # Higher Education
        "qualification": "Master of Business Administration",
        "university": "Delhi University",
        
        # Occupation
        "occupation": "Business Analyst",
        
        # Bank Details
        "bankName": "HDFC Bank",
        "accountNumber": "987654321098",
        "ifsc": "HDFC0009876",
        
        # Documents
        "photoUrl": "/uploads/jane_photo.jpg",
        "signatureUrl": "/uploads/jane_signature.jpg",
    }
    
    agent_status_db[user2_id] = "inactive"
    
    # Test User 3 (Minimal profile)
    user3_id = "user_003"
    users_db[user3_id] = {
        "id": user3_id,
        "email": "test.user@example.com",
        "fullName": "Test User",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Z0pW.7t0jKXS",  # password: test123
        "created_at": datetime.now().isoformat()
    }
    
    profiles_db[user3_id] = {
        "fullName": "Test User",
        "email": "test.user@example.com",
        "phone": "+91-9876543212"
    }
    
    agent_status_db[user3_id] = "waiting"
    
    print(f"✅ Created {len(users_db)} test users:")
    print(f"   - User 1: {user1_id} (john.doe@example.com) - Complete profile with PAN card")
    print(f"   - User 2: {user2_id} (jane.smith@example.com) - Complete profile")
    print(f"   - User 3: {user3_id} (test.user@example.com) - Minimal profile")
    print(f"\n📝 Password for all test users: test123")
    print(f"\n📚 Created {len(documents_db.get(user1_id, []))} mock document(s)")
    print(f"\n🎯 Agent Status:")
    print(f"   - {user1_id}: {agent_status_db.get(user1_id, 'inactive')}")
    print(f"   - {user2_id}: {agent_status_db.get(user2_id, 'inactive')}")
    print(f"   - {user3_id}: {agent_status_db.get(user3_id, 'inactive')}")
    print("\n✨ Seeding complete!")

if __name__ == "__main__":
    seed_data()

