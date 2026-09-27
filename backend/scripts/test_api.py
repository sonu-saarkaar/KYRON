"""
Quick API Test Script
Tests all endpoints to ensure they're working
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_signup():
    """Test signup endpoint"""
    print("\nTesting /api/auth/signup endpoint...")
    try:
        data = {
            "email": "test@example.com",
            "password": "test123",
            "name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
        print(f"✅ Signup: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Token: {result.get('token', 'N/A')[:20]}...")
            return result.get('token')
        else:
            print(f"   Response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Signup failed: {e}")
        return None

def test_login():
    """Test login endpoint"""
    print("\nTesting /api/auth/login endpoint...")
    try:
        data = {
            "email": "test@example.com",
            "password": "test123"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Token: {result.get('token', 'N/A')[:20]}...")
            return result.get('token')
        else:
            print(f"   Response: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_profile(token):
    """Test profile endpoints"""
    if not token:
        print("\n⚠️  Skipping profile tests (no token)")
        return
    
    print("\nTesting /api/profile/me endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/profile/me", headers=headers)
        print(f"✅ Get Profile: {response.status_code}")
        if response.status_code == 200:
            print(f"   Profile: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Profile test failed: {e}")

def test_documents(token):
    """Test documents endpoints"""
    if not token:
        print("\n⚠️  Skipping documents tests (no token)")
        return
    
    print("\nTesting /api/documents endpoint...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/documents", headers=headers)
        print(f"✅ Get Documents: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Documents count: {len(result.get('documents', []))}")
    except Exception as e:
        print(f"❌ Documents test failed: {e}")

def main():
    print("=" * 50)
    print("KYRON API Test Suite")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("\n❌ Backend is not running or not accessible!")
        print("   Please start backend: cd backend; .\START.ps1")
        return
    
    # Test signup
    token = test_signup()
    
    # Test login
    if not token:
        token = test_login()
    
    # Test authenticated endpoints
    if token:
        test_profile(token)
        test_documents(token)
    
    print("\n" + "=" * 50)
    print("✅ API Tests Complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()

