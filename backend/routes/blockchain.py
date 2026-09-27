"""
KYRON Blockchain Routes
API endpoints for blockchain data integrity and verification
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any
import hashlib

from auth_utils import verify_token
from services.blockchain_service import get_blockchain_service

router = APIRouter()

class RecordAutomationRequest(BaseModel):
    """Request to record automation in blockchain"""
    session_id: str
    action: str  # "form_filled", "document_uploaded", etc.
    data: Dict[str, Any]

class RecordDocumentRequest(BaseModel):
    """Request to record document in blockchain"""
    document_id: str
    document_hash: str

@router.post("/record/automation")
def record_automation(
    request: RecordAutomationRequest,
    authorization: str = Header(None)
):
    """Record automation action in blockchain"""
    user_id = verify_token(authorization)
    
    blockchain_service = get_blockchain_service()
    result = blockchain_service.record_automation(
        user_id=user_id,
        session_id=request.session_id,
        action=request.action,
        data=request.data
    )
    
    return {
        "success": True,
        "message": "Automation recorded in blockchain",
        "block": result
    }

@router.post("/record/document")
def record_document(
    request: RecordDocumentRequest,
    authorization: str = Header(None)
):
    """Record document in blockchain"""
    user_id = verify_token(authorization)
    
    blockchain_service = get_blockchain_service()
    result = blockchain_service.record_document(
        user_id=user_id,
        document_id=request.document_id,
        document_hash=request.document_hash
    )
    
    return {
        "success": True,
        "message": "Document recorded in blockchain",
        "block": result
    }

@router.get("/verify/{block_index}")
def verify_block(
    block_index: int,
    expected_hash: Optional[str] = None,
    authorization: str = Header(None)
):
    """Verify blockchain block integrity"""
    verify_token(authorization)  # Just verify auth
    
    blockchain_service = get_blockchain_service()
    
    if expected_hash:
        result = blockchain_service.verify_integrity(block_index, expected_hash)
    else:
        # Just check if blockchain is valid
        result = {
            "success": True,
            "valid": blockchain_service.blockchain.is_valid(),
            "block_index": block_index
        }
    
    return result

@router.get("/info")
def get_blockchain_info(authorization: str = Header(None)):
    """Get blockchain information"""
    verify_token(authorization)
    
    blockchain_service = get_blockchain_service()
    info = blockchain_service.get_chain_info()
    
    return {
        "success": True,
        "blockchain": info
    }

@router.get("/history")
def get_user_history(authorization: str = Header(None)):
    """Get user's blockchain history"""
    user_id = verify_token(authorization)
    
    blockchain_service = get_blockchain_service()
    history = blockchain_service.get_user_history(user_id)
    
    return {
        "success": True,
        "history": history,
        "total_blocks": len(history)
    }

@router.get("/chain")
def get_chain(authorization: str = Header(None)):
    """Get entire blockchain (for verification)"""
    verify_token(authorization)
    
    blockchain_service = get_blockchain_service()
    chain_data = blockchain_service.blockchain.get_chain_data()
    
    return {
        "success": True,
        "chain": chain_data,
        "length": len(chain_data),
        "is_valid": blockchain_service.blockchain.is_valid()
    }

