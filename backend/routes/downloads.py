"""
Download routes for KYRON.
Handles Chrome Extension ZIP file downloads.
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path
import os
import sys

router = APIRouter()

@router.get("/extension")
async def download_extension():
    """
    Download the KYRON Chrome Extension ZIP file.
    """
    try:
        # Path to the extension ZIP
        # downloads.py is at backend/routes/downloads.py
        # So backend_dir = backend/
        backend_dir = Path(__file__).parent.parent
        zip_path = backend_dir / "static" / "downloads" / "kyron-extension.zip"
        
        # Ensure downloads directory exists
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists
        if not zip_path.exists():
            # Try to package it first
            try:
                # Add backend directory to Python path for import
                backend_path = str(backend_dir)
                if backend_path not in sys.path:
                    sys.path.insert(0, backend_path)
                
                # Import and call package_extension
                from package_extension import package_extension
                package_extension()
                
                # Check again
                if not zip_path.exists():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Extension package not found after packaging. Please contact support."
                    )
            except HTTPException:
                raise
            except ImportError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to import package_extension: {str(e)}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to package extension: {str(e)}"
                )
        
        # Verify file exists and is readable
        if not zip_path.exists() or not zip_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Extension package file not found"
            )
        
        # Return the file (use absolute path)
        zip_path_absolute = zip_path.resolve()
        return FileResponse(
            path=str(zip_path_absolute),
            filename="kyron-extension.zip",
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment; filename=kyron-extension.zip"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

