"""
This file handles user authentication (login, signup, logout).
It manages user accounts and generates tokens for API access.
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from passlib.context import CryptContext

from auth_utils import create_token, verify_token, revoke_token
from services.database_manager import get_database_manager

# Create router for authentication endpoints
router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Try to get database manager (fallback to in-memory if not available)
try:
    db_manager = get_database_manager()
    use_database = db_manager.is_available()
except:
    use_database = False
    users_db = {}  # Fallback in-memory storage

# Request/Response models
class SignupRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    token: str
    user_id: str
    email: str

# Password hashing using bcrypt
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt. Bcrypt has a 72-byte limit."""
    # Bcrypt has a 72-byte limit. Truncate if necessary.
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Use bcrypt directly to avoid passlib issues
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash. Bcrypt has a 72-byte limit."""
    # Bcrypt has a 72-byte limit. Truncate if necessary to match hashing behavior.
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Use bcrypt directly to avoid passlib issues
    hashed_bytes = password_hash.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

@router.post("/signup", response_model=AuthResponse)
def signup(request: SignupRequest):
    """
    Create a new user account.
    Returns token and user info.
    """
    # Check if user already exists
    if use_database:
        existing_user = db_manager.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    else:
        if request.email in users_db:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate user ID
    import uuid
    user_id = str(uuid.uuid4())
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Store user
    user_data = {
        "id": user_id,
        "email": request.email,
        "fullName": request.name,
        "hashed_password": password_hash,
        "created_at": None  # Will be set by database
    }
    
    if use_database:
        try:
            db_manager.create_user(user_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")
    else:
        # Fallback to in-memory
        users_db[request.email] = {
            "user_id": user_id,
            "password_hash": password_hash,
            "name": request.name,
            "email": request.email
        }
    
    # Generate token using auth_utils
    token = create_token(user_id)
    
    return AuthResponse(
        success=True,
        message="Account created successfully",
        token=token,
        user_id=user_id,
        email=request.email
    )

@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    """
    Log in an existing user and get an authentication token.
    """
    # Get user from database or in-memory
    if use_database:
        user = db_manager.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(request.password, user.get("hashed_password", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_id = user.get("id") or user.get("_id")
        if isinstance(user_id, dict):
            user_id = str(user_id)
    else:
        # Fallback to in-memory
        if request.email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = users_db[request.email]
        
        # Verify password
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user_id = user["user_id"]
    
    # Generate token using auth_utils
    token = create_token(str(user_id))
    
    return AuthResponse(
        success=True,
        message="Login successful",
        token=token,
        user_id=str(user_id),
        email=request.email
    )

@router.post("/logout")
def logout(authorization: str = Header(None)):
    """
    Log out the current user by revoking their token.
    """
    # Verify token and get user_id
    try:
        user_id = verify_token(authorization)
        
        # Revoke the token
        token = authorization.split(" ")[1]
        revoke_token(token)
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except HTTPException:
        # Token is invalid, but we can still return success
        return {
            "success": True,
            "message": "Logged out successfully"
        }

