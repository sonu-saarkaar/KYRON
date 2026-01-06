"""
Quick Backend Health Check
Run this to verify backend is working
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_imports():
    """Check if all required modules can be imported"""
    print("Checking imports...")
    try:
        import fastapi
        print("[OK] FastAPI imported")
    except ImportError as e:
        print(f"[ERROR] FastAPI not found: {e}")
        return False
    
    try:
        import uvicorn
        print("[OK] Uvicorn imported")
    except ImportError as e:
        print(f"[ERROR] Uvicorn not found: {e}")
        return False
    
    try:
        from main import app
        print("[OK] Main app imported")
    except Exception as e:
        print(f"[ERROR] Failed to import app: {e}")
        return False
    
    return True

def check_routes():
    """Check if routes are registered"""
    print("\nChecking routes...")
    from main import app
    
    routes = [route.path for route in app.routes]
    important_routes = [
        "/health",
        "/api/auth/login",
        "/api/auth/signup",
        "/api/profile/me",
        "/docs"
    ]
    
    for route in important_routes:
        if any(route in r for r in routes):
            print(f"[OK] Route found: {route}")
        else:
            print(f"[WARN] Route not found: {route}")
    
    return True

def main():
    print("=" * 50)
    print("KYRON Backend Health Check")
    print("=" * 50)
    
    if not check_imports():
        print("\n[ERROR] Import check failed!")
        print("   Run: pip install -r requirements_minimal.txt")
        return
    
    check_routes()
    
    print("\n" + "=" * 50)
    print("[OK] Backend check complete!")
    print("=" * 50)
    print("\nTo start backend, run:")
    print("  python run.py")
    print("  or")
    print("  .\\START.ps1")

if __name__ == "__main__":
    main()

