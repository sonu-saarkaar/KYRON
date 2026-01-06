"""
KYRON Standalone Automation Routes
Works without Chrome Extension - Direct Playwright automation
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

from auth_utils import verify_token

# Try to get profile from database manager, fallback to old method
try:
    from services.database_manager import get_database_manager
    db_manager = get_database_manager()
    use_database = db_manager.is_available()
except:
    use_database = False
    try:
        from profile import profiles_db
    except:
        profiles_db = {}

# Optional imports - handle gracefully if not available
try:
    from services.playwright_automation import get_automation_engine
except ImportError:
    get_automation_engine = None
    
try:
    from services.ai_vision import create_ai_vision_service
except ImportError:
    create_ai_vision_service = None
    
try:
    from services.form_mapper import get_form_mapper
except ImportError:
    get_form_mapper = None

router = APIRouter()

# Active automation sessions
automation_sessions: Dict[str, Dict] = {}

class AutomationTriggerRequest(BaseModel):
    """Request to trigger automation"""
    url: str
    auto_fill: bool = True  # Automatically fill form after analysis
    wait_for_user: bool = False  # Wait for user confirmation before filling
    service_id: Optional[str] = None  # Service ID (pan_card, etc.)
    service_config: Optional[Dict[str, Any]] = None  # Service-specific configuration

class AutomationControlRequest(BaseModel):
    """Control automation session"""
    action: str  # "fill", "screenshot", "close"
    field_overrides: Optional[Dict[str, str]] = None  # Override specific fields

@router.post("/trigger")
async def trigger_automation(
    request: AutomationTriggerRequest,
    authorization: str = Header(None)
):
    """
    Trigger automation for a URL - Works standalone without Chrome extension
    This creates a Playwright session, navigates to URL, analyzes the page,
    and optionally fills the form automatically.
    """
    user_id = verify_token(authorization)
    
    # Get user profile from database or in-memory
    if use_database:
        user_profile = db_manager.get_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found. Please complete your profile first.")
    else:
        # Fallback to in-memory
        if user_id not in profiles_db:
            raise HTTPException(status_code=404, detail="User profile not found. Please complete your profile first.")
        user_profile = profiles_db[user_id]
    
    # Check if automation engine is available
    if get_automation_engine is None:
        raise HTTPException(
            status_code=503, 
            detail="Playwright automation engine not available. Please install: pip install playwright && playwright install chromium"
        )
    
    # Create session
    session_id = str(uuid.uuid4())
    engine = get_automation_engine()
    
    try:
        # Initialize engine (this will install Playwright if needed)
        try:
            await engine.initialize()
        except RuntimeError as e:
            error_msg = str(e)
            if "not installed" in error_msg.lower() or "install" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail=f"Playwright not installed. Please run: cd backend && .\\INSTALL_PLAYWRIGHT.ps1"
                )
            raise HTTPException(
                status_code=503,
                detail=f"Playwright initialization failed: {error_msg}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to initialize automation engine: {str(e)}. Please install Playwright: cd backend && .\\INSTALL_PLAYWRIGHT.ps1"
            )
        
        # Verify engine is ready
        if engine.browser is None:
            raise HTTPException(
                status_code=503,
                detail="Browser not initialized. Please install Playwright: cd backend && .\\INSTALL_PLAYWRIGHT.ps1"
            )
        
        # Create browser session
        try:
            await engine.create_session(session_id, request.url)
        except RuntimeError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Failed to create browser session: {str(e)}"
            )
        
        # Store session info
        automation_sessions[session_id] = {
            "user_id": user_id,
            "url": request.url,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Capture screenshot and analyze
        screenshot = await engine.capture_screenshot(session_id, full_page=True)
        html, detected_fields = await engine.get_page_html(session_id)
        
        # Detect payment requirements
        payment_info = None
        try:
            from services.payment_detector import get_payment_detector
            payment_detector = get_payment_detector()
            page_text = await engine.active_sessions[session_id]['page'].evaluate("() => document.body.innerText")
            payment_info = payment_detector.detect_payment(html, page_text)
            
            if payment_info and payment_info.get("required"):
                automation_sessions[session_id]["payment_required"] = True
                automation_sessions[session_id]["payment_info"] = payment_info
                automation_sessions[session_id]["status"] = "payment_required"
                automation_sessions[session_id]["current_action"] = f"Payment required: ₹{payment_info.get('amount', 0)}"
        except Exception as e:
            logger.warning(f"Payment detection failed: {str(e)}")
        
        # AI Vision Analysis (optional)
        ai_analysis = None
        if create_ai_vision_service:
            try:
                ai_service = create_ai_vision_service()
                ai_analysis = ai_service.analyze_screenshot(screenshot, html[:2000])
            except Exception as e:
                # If AI service fails, continue with basic field detection
                ai_analysis = {
                    "success": False,
                    "error": str(e),
                    "analysis": {"fields": []}
                }
        
        # Form mapping
        if get_form_mapper:
            form_mapper = get_form_mapper()
        else:
            # Fallback: create basic mapper
            from services.form_mapper import FormFieldMapper
            form_mapper = FormFieldMapper()
        
        # Normalize user profile keys (handle both camelCase and snake_case)
        normalized_profile = {}
        for key, value in user_profile.items():
            # Convert snake_case to camelCase for matching
            if '_' in key:
                camel_key = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(key.split('_')))
                normalized_profile[camel_key] = value
            normalized_profile[key] = value
        
        # Use AI detected fields if available, otherwise use DOM detected fields
        fields_to_map = []
        if ai_analysis and ai_analysis.get("success") and ai_analysis.get("analysis", {}).get("fields"):
            fields_to_map = ai_analysis["analysis"]["fields"]
        else:
            # Convert DOM fields to format expected by mapper
            # Improve selector generation
            fields_to_map = []
            for f in detected_fields:
                selector = f.get("selector", "")
                # If no selector, try to create one
                if not selector:
                    if f.get("id"):
                        selector = f"#{f['id']}"
                    elif f.get("name"):
                        selector = f"[name='{f['name']}']"
                    elif f.get("label"):
                        # Try to find by label text
                        selector = f"input[placeholder*='{f['label'][:20]}']"
                
                fields_to_map.append({
                    "label": f.get("label", ""),
                    "name": f.get("name", ""),
                    "id": f.get("id", ""),
                    "type": f.get("type", "text"),
                    "selector": selector,
                    "maps_to": ""
                })
        
        # Use normalized profile for mapping
        mapped_fields = form_mapper.map_fields_to_profile(fields_to_map, normalized_profile)
        fillable_fields = form_mapper.get_fillable_fields(mapped_fields, min_confidence=0.6)  # Lower threshold for better matching
        
        # Auto-fill if requested
        fill_result = None
        if request.auto_fill and fillable_fields:
            field_mappings = [
                {
                    "selector": f["selector"],
                    "value": str(f["value"]),  # Ensure value is string
                    "label": f.get("label", f["selector"])  # Include label for progress
                }
                for f in fillable_fields
                if f.get("selector") and f.get("value")  # Only include valid mappings
            ]
            
            if field_mappings:
                try:
                    # Update session status
                    automation_sessions[session_id]["status"] = "filling"
                    automation_sessions[session_id]["current_action"] = "Starting form fill..."
                    
                    # Progress callback for step-by-step updates
                    def update_progress(progress_info):
                        automation_sessions[session_id]["current_action"] = progress_info.get("action", "Processing...")
                        automation_sessions[session_id]["progress"] = {
                            "step": progress_info.get("step", 0),
                            "total": progress_info.get("total", 0),
                            "status": progress_info.get("status", "processing")
                        }
                    
                    fill_result = await engine.fill_form_batch(session_id, field_mappings, update_progress)
                    
                    # Update final status
                    if fill_result.get("success") and fill_result.get("successful", 0) > 0:
                        automation_sessions[session_id]["status"] = "completed"
                        automation_sessions[session_id]["current_action"] = f"Form filled successfully! ({fill_result.get('successful')}/{fill_result.get('total')} fields)"
                    else:
                        automation_sessions[session_id]["status"] = "error"
                        automation_sessions[session_id]["current_action"] = f"Form filling completed with errors"
                        
                except Exception as e:
                    logger.error(f"Form filling error: {str(e)}")
                    automation_sessions[session_id]["status"] = "error"
                    automation_sessions[session_id]["error"] = str(e)
                    fill_result = {
                        "success": False,
                        "error": str(e),
                        "total": len(field_mappings),
                        "successful": 0,
                        "failed": len(field_mappings)
                    }
            else:
                fill_result = {
                    "success": False,
                    "error": "No valid fields to fill",
                    "total": 0,
                    "successful": 0,
                    "failed": 0
                }
        
        return {
            "success": True,
            "session_id": session_id,
            "url": request.url,
            "screenshot": screenshot,  # Base64 encoded
            "analysis": ai_analysis,
            "detected_fields": detected_fields,
            "mapped_fields": mapped_fields,
            "fillable_fields": fillable_fields,
            "fill_result": fill_result,
            "payment_info": payment_info,
            "message": "Form filled automatically" if (request.auto_fill and fill_result) else "Page analyzed, ready for filling"
        }
        
    except Exception as e:
        # Cleanup on error
        if session_id in automation_sessions:
            try:
                await engine.close_session(session_id)
                del automation_sessions[session_id]
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Automation failed: {str(e)}")

@router.get("/sessions")
async def get_sessions(authorization: str = Header(None)):
    """Get all automation sessions for the current user"""
    user_id = verify_token(authorization)
    
    user_sessions = [
        {
            "session_id": session_id,
            "url": session["url"],
            "created_at": session.get("created_at", ""),
            "status": session.get("status", "active")
        }
        for session_id, session in automation_sessions.items()
        if session.get("user_id") == user_id
    ]
    
    return {
        "success": True,
        "sessions": user_sessions
    }

@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Get session details"""
    user_id = verify_token(authorization)
    
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = automation_sessions[session_id]
    if session.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return {
        "success": True,
        "session_id": session_id,
        "url": session.get("url", ""),
        "status": session.get("status", "active"),
        "current_action": session.get("current_action", ""),
        "progress": session.get("progress"),
        "error": session.get("error"),
        "error_type": session.get("error_type"),
        "error_action": session.get("error_action"),
        "payment_url": session.get("payment_url"),
        "created_at": session.get("created_at", ""),
        "session": session  # Full session for backward compatibility
    }

@router.get("/session/{session_id}/screenshot")
async def get_session_screenshot(
    session_id: str,
    authorization: str = Header(None)
):
    """Get current screenshot of automation session"""
    user_id = verify_token(authorization)
    
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if automation_sessions[session_id].get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if get_automation_engine is None:
        raise HTTPException(status_code=503, detail="Playwright not available")
    
    engine = get_automation_engine()
    screenshot = await engine.capture_screenshot(session_id, full_page=True)
    
    return {
        "success": True,
        "screenshot": screenshot
    }

@router.post("/session/{session_id}/fill")
async def fill_form_session(
    session_id: str,
    field_overrides: Optional[Dict[str, str]] = None,
    authorization: str = Header(None)
):
    """
    Fill form in an existing session
    """
    user_id = verify_token(authorization)
    
    # Verify session
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if automation_sessions[session_id].get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Get user profile from database or in-memory
    if use_database:
        user_profile = db_manager.get_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")
    else:
        # Fallback to in-memory
        if user_id not in profiles_db:
            raise HTTPException(status_code=404, detail="User profile not found")
        user_profile = profiles_db[user_id]
    
    if get_automation_engine is None:
        raise HTTPException(status_code=503, detail="Playwright not available")
    
    engine = get_automation_engine()
    html, detected_fields = await engine.get_page_html(session_id)
    
    # Map fields
    if get_form_mapper:
        form_mapper = get_form_mapper()
    else:
        from services.form_mapper import BasicMapper
        form_mapper = BasicMapper()
    
    fields_to_map = [
        {
            "label": f.get("label", ""),
            "name": f.get("name", ""),
            "id": f.get("id", ""),
            "type": f.get("type", "text"),
            "selector": f.get("selector", ""),
            "maps_to": ""
        }
        for f in detected_fields
    ]
    
    mapped_fields = form_mapper.map_fields_to_profile(fields_to_map, user_profile)
    fillable_fields = form_mapper.get_fillable_fields(mapped_fields, min_confidence=0.7)
    
    # Apply overrides if provided
    if field_overrides:
        for field in fillable_fields:
            if field["selector"] in field_overrides:
                field["value"] = field_overrides[field["selector"]]
    
    # Fill form
    field_mappings = [
        {
            "selector": f["selector"],
            "value": f["value"]
        }
        for f in fillable_fields
    ]
    
    fill_result = await engine.fill_form_batch(session_id, field_mappings)
    
    return {
        "success": True,
        "fill_result": fill_result,
        "fields_filled": len([r for r in fill_result.get("results", []) if r.get("success")])
    }

@router.delete("/session/{session_id}")
async def close_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Close an automation session"""
    user_id = verify_token(authorization)
    
    if session_id not in automation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if automation_sessions[session_id].get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Close browser session
    if get_automation_engine:
        try:
            engine = get_automation_engine()
            await engine.close_session(session_id)
        except:
            pass
    
    # Remove from sessions
    del automation_sessions[session_id]
    
    return {
        "success": True,
        "message": "Session closed"
    }
