"""
Script to create or update admin account with email: admin@kyron.com and password: admin123
"""

from services.database import DatabaseService
from core.security import hash_password

def setup_admin():
    """Create or update admin account"""
    db_service = DatabaseService()
    
    # Using "admin" as the identifier - converting to email format
    # You can change this to any valid email format you prefer
    email = "admin@kyron.com"  # or use "admin@admin.com" if you prefer
    password = "admin123"
    
    # Check if admin already exists
    existing = db_service.get_admin_by_email(email)
    
    if existing:
        # Update existing admin
        print(f"Admin with email {email} already exists. Updating password...")
        db_service.update_admin(existing["id"], {
            "password_hash": hash_password(password),
            "status": "active",
            "role": "MASTER_ADMIN"
        })
        print(f"[SUCCESS] Admin password updated successfully!")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Role: MASTER_ADMIN")
    else:
        # Create new admin
        print(f"Creating new admin account...")
        admin_data = {
            "email": email,
            "password_hash": hash_password(password),
            "name": "Admin",
            "role": "MASTER_ADMIN",
            "permissions": [],
            "status": "active"
        }
        
        admin_id = db_service.create_admin(admin_data)
        print(f"[SUCCESS] Admin created successfully!")
        print(f"  Admin ID: {admin_id}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  Role: MASTER_ADMIN")
    
    print("\nYou can now login to the admin panel with:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")

if __name__ == "__main__":
    try:
        setup_admin()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

