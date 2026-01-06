"""
Initialize first MASTER_ADMIN for KYRON Admin Panel.
Run this script once to create the initial master admin account.

Usage:
    python init_admin.py
"""

import sys
import getpass
from services.database import DatabaseService
from core.security import hash_password

def create_master_admin():
    """Create the first MASTER_ADMIN account"""
    print("=" * 60)
    print("KYRON Admin Panel - Master Admin Initialization")
    print("=" * 60)
    print()
    
    # Get admin details
    print("Enter details for the MASTER_ADMIN account:")
    print()
    
    name = input("Name: ").strip()
    if not name:
        print("Error: Name is required")
        return False
    
    email = input("Email: ").strip()
    if not email or "@" not in email:
        print("Error: Valid email is required")
        return False
    
    password = getpass.getpass("Password (min 8 characters): ")
    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return False
    
    confirm_password = getpass.getpass("Confirm Password: ")
    if password != confirm_password:
        print("Error: Passwords do not match")
        return False
    
    # Create database service
    db_service = DatabaseService()
    
    # Check if admin already exists
    existing = db_service.get_admin_by_email(email)
    if existing:
        print(f"Error: Admin with email {email} already exists")
        return False
    
    # Create admin document
    admin_data = {
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "role": "MASTER_ADMIN",
        "permissions": [],
        "status": "active"
    }
    
    try:
        admin_id = db_service.create_admin(admin_data)
        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Master admin created successfully!")
        print(f"Admin ID: {admin_id}")
        print(f"Email: {email}")
        print(f"Role: MASTER_ADMIN")
        print()
        print("You can now login to the admin panel at:")
        print("  http://localhost:8000/admin_panel/login.html")
        print()
        return True
    except Exception as e:
        print(f"Error creating admin: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_master_admin()
    sys.exit(0 if success else 1)

