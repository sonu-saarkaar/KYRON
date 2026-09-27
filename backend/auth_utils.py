"""
Shared authentication utilities for KYRON backend.
This module provides token management and user_id extraction.
"""

# In-memory token storage: {token: user_id}
# In production, use JWT tokens with proper signing/verification
token_to_user_map = {}  # {token: user_id}
user_to_token_map = {}  # {user_id: token} - for single session per user

def create_token(user_id: str) -> str:
    """Create a new token for a user"""
    import secrets
    
    # If user already has a token, remove old mapping
    if user_id in user_to_token_map:
        old_token = user_to_token_map[user_id]
        if old_token in token_to_user_map:
            del token_to_user_map[old_token]
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    
    # Store mapping both ways
    token_to_user_map[token] = user_id
    user_to_token_map[user_id] = token
    
    return token

def get_user_id_from_token(token: str) -> str:
    """Extract user_id from token. Returns None if invalid."""
    return token_to_user_map.get(token)

def verify_token(authorization: str = None) -> str:
    """Verify token from Authorization header and return user_id"""
    # Debug logging
    if not authorization:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Missing Authorization header. Please login first."
        )
    
    if not authorization.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Invalid token format. Expected 'Bearer <token>'"
        )
    
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Malformed token. Expected 'Bearer <token>'"
        )
    
    user_id = get_user_id_from_token(token)
    
    if not user_id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Invalid or expired token. Please login again."
        )
    
    return user_id

def revoke_token(token: str):
    """Revoke/invalidate a token (for logout)"""
    user_id = token_to_user_map.get(token)
    if user_id:
        del token_to_user_map[token]
        if user_id in user_to_token_map:
            del user_to_token_map[user_id]
