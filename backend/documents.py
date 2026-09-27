"""
This file handles Document Vault operations.
Users can upload, view, and delete documents.
Documents are stored securely and can be referenced by the AI agent.
OCR processing is performed to extract text from uploaded documents.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Header, Form
from typing import List, Optional
import os
from datetime import datetime
import uuid
import hashlib

from auth_utils import verify_token
try:
    from services.ocr_service import get_ocr_service
except ImportError:
    def get_ocr_service():
        return None
from services.database_manager import get_database_manager

# Create router for document endpoints
router = APIRouter()

# Try to get database manager
try:
    db_manager = get_database_manager()
    use_database = db_manager.is_available()
except:
    db_manager = None
    use_database = False

# In-memory document storage (fallback if database is not available)
documents_db = {}

# Upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    authorization: str = Header(None)
):
    """Upload a document to the vault"""
    user_id = verify_token(authorization)
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    # Read file content
    content = await file.read()
    
    # Generate file hash for integrity
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Save file to disk
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}{file_extension}")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Perform OCR if service is available
    extracted_text = None
    try:
        ocr_service = get_ocr_service()
        if ocr_service:
            extracted_text = await ocr_service.extract_text(file_path)
    except Exception as e:
        print(f"OCR extraction failed: {e}")
    
    # Create document metadata
    document = {
        "id": doc_id,
        "user_id": user_id,
        "filename": file.filename,
        "description": description,
        "file_path": file_path,
        "file_hash": file_hash,
        "file_size": len(content),
        "mime_type": file.content_type,
        "extracted_text": extracted_text,
        "uploaded_at": datetime.now().isoformat(),
    }
    
    # Store in database or memory
    if use_database:
        try:
            db_manager.store_document(user_id, document)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to store document: {str(e)}")
    else:
        if user_id not in documents_db:
            documents_db[user_id] = []
        documents_db[user_id].append(document)
    
    return {
        "success": True,
        "document_id": doc_id,
        "filename": file.filename,
        "extracted_text_preview": extracted_text[:200] if extracted_text else None
    }

@router.get("")
async def list_documents(authorization: str = Header(None)):
    """List all documents for the authenticated user"""
    user_id = verify_token(authorization)
    
    # Get documents from database or memory
    if use_database:
        try:
            documents = db_manager.get_user_documents(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")
    else:
        documents = documents_db.get(user_id, [])
    
    # Return document list (without full extracted text)
    return {
        "documents": [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "description": doc.get("description"),
                "file_size": doc["file_size"],
                "mime_type": doc["mime_type"],
                "uploaded_at": doc["uploaded_at"],
                "has_extracted_text": bool(doc.get("extracted_text"))
            }
            for doc in documents
        ]
    }

@router.get("/{document_id}")
async def get_document(document_id: str, authorization: str = Header(None)):
    """Get document metadata"""
    user_id = verify_token(authorization)
    
    # Get document from database or memory
    if use_database:
        try:
            document = db_manager.get_document(user_id, document_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")
    else:
        user_docs = documents_db.get(user_id, [])
        document = next((doc for doc in user_docs if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.get("/{document_id}/text")
async def get_document_text(document_id: str, authorization: str = Header(None)):
    """Get extracted text from document"""
    user_id = verify_token(authorization)
    
    # Get document from database or memory
    if use_database:
        try:
            document = db_manager.get_document(user_id, document_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")
    else:
        user_docs = documents_db.get(user_id, [])
        document = next((doc for doc in user_docs if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    extracted_text = document.get("extracted_text")
    if not extracted_text:
        raise HTTPException(status_code=404, detail="No extracted text available for this document")
    
    return {
        "document_id": document_id,
        "filename": document["filename"],
        "extracted_text": extracted_text
    }

@router.delete("/{document_id}")
async def delete_document(document_id: str, authorization: str = Header(None)):
    """Delete a document"""
    user_id = verify_token(authorization)
    
    # Get document from database or memory
    if use_database:
        try:
            document = db_manager.get_document(user_id, document_id)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Delete file from disk
            if os.path.exists(document["file_path"]):
                os.remove(document["file_path"])
            
            # Delete from database
            db_manager.delete_document(user_id, document_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
    else:
        user_docs = documents_db.get(user_id, [])
        document = next((doc for doc in user_docs if doc["id"] == document_id), None)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from disk
        if os.path.exists(document["file_path"]):
            os.remove(document["file_path"])
        
        # Delete from memory
        documents_db[user_id] = [doc for doc in user_docs if doc["id"] != document_id]
    
    return {
        "success": True,
        "message": "Document deleted successfully"
    }

@router.post("/{document_id}/reprocess")
async def reprocess_document(document_id: str, authorization: str = Header(None)):
    """Reprocess document with OCR"""
    user_id = verify_token(authorization)
    
    # Get document from database or memory
    if use_database:
        try:
            document = db_manager.get_document(user_id, document_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")
    else:
        user_docs = documents_db.get(user_id, [])
        document = next((doc for doc in user_docs if doc["id"] == document_id), None)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Perform OCR
    try:
        ocr_service = get_ocr_service()
        if not ocr_service:
            raise HTTPException(status_code=503, detail="OCR service not available")
        
        extracted_text = await ocr_service.extract_text(document["file_path"])
        
        # Update document
        document["extracted_text"] = extracted_text
        
        # Update in database or memory
        if use_database:
            db_manager.update_document(user_id, document_id, {"extracted_text": extracted_text})
        else:
            # Memory is already updated by reference
            pass
        
        return {
            "success": True,
            "document_id": document_id,
            "extracted_text_preview": extracted_text[:200] if extracted_text else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
