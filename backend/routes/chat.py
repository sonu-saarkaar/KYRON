"""
KYRON Chat/Conversation API
Handles conversational interactions like ChatGPT/Gemini
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import json
import time
import os
from datetime import datetime

from auth_utils import verify_token

# Debug logging helper
def debug_log(location, message, data, hypothesis_id="A", run_id="run1"):
    log_data = {
        "sessionId": "debug-session",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000)
    }
    print(f"[DEBUG] {json.dumps(log_data)}")  # Console fallback
    try:
        log_path = r'c:\Users\Sonu Bhai\Desktop\Project\KYRON\.cursor\debug.log'
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_data) + '\n')
    except Exception as log_err:
        print(f"[DEBUG] Log write failed: {log_err}")

# Try to get profile from database manager
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

# Import service catalog
try:
    from services_catalog import get_service_catalog, get_service_definition
except:
    get_service_catalog = None
    get_service_definition = None

router = APIRouter()

# Chat history storage (in-memory, can be moved to database)
chat_history: Dict[str, List[Dict]] = {}

# Session state storage (maintains active service and stage)
session_state: Dict[str, Dict[str, Any]] = {}

# PAN Card data collection steps
PAN_COLLECTION_STEPS = {
    "CONFIRM_PROCEED": "confirm_proceed",
    "ASK_APPLICANT_TYPE": "ask_applicant_type",  # Individual or Company
    "ASK_APPLICATION_TYPE": "ask_application_type",  # New or Correction
    "ASK_EXISTING_PAN": "ask_existing_pan",  # Existing PAN if Correction
    "ASK_DELIVERY_TYPE": "ask_delivery_type",   # Digital or Physical
    "VERIFY_AADHAAR": "verify_aadhaar",  # Verify Aadhaar if missing
    "CONFIRM_DETAILS": "confirm_details",
    "READY_TO_SUBMIT": "ready_to_submit"
}

# BRC data collection steps
BRC_COLLECTION_STEPS = {
    "CONFIRM_PROCEED": "confirm_proceed",
    "ASK_APPLICANT_NAME": "ask_applicant_name",
    "ASK_FATHER_NAME": "ask_father_name",
    "ASK_MOTHER_NAME": "ask_mother_name",
    "ASK_DOB": "ask_dob",
    "ASK_GENDER": "ask_gender",
    "ASK_MOBILE": "ask_mobile",
    "ASK_AADHAAR": "ask_aadhaar",
    "ASK_ADDRESS": "ask_address",
    "ASK_DISTRICT": "ask_district",
    "ASK_BLOCK": "ask_block",
    "ASK_PANCHAYAT": "ask_panchayat",
    "ASK_POST_OFFICE": "ask_post_office",
    "ASK_PIN_CODE": "ask_pin_code",
    "ASK_PURPOSE": "ask_purpose",
    "CONFIRM_DETAILS": "confirm_details",
    "READY_TO_SUBMIT": "ready_to_submit"
}

class ChatMessage(BaseModel):
    """Chat message model"""
    text: str
    language: str = "en"  # "en" or "hi"

class ChatResponse(BaseModel):
    """Chat response model"""
    text: str
    actions: Optional[List[Dict[str, Any]]] = None
    service_id: Optional[str] = None
    service_config: Optional[Dict[str, Any]] = None
    start_automation: bool = False
    should_speak: bool = False
    explanation: Optional[Dict[str, Any]] = None  # Structured explanation
    stage: Optional[str] = None  # EXPLANATION, APPLY, EXECUTION

@router.post("/message")
async def process_chat_message(
    message: ChatMessage,
    authorization: str = Header(None)
):
    """
    Process a chat message and return AI response
    Similar to ChatGPT/Gemini interaction
    """
    # CRITICAL: Log immediately at function entry - before anything else
    print("=" * 80)
    print("[CHAT ROUTE] process_chat_message CALLED")
    print(f"[CHAT ROUTE] Message: {message.text[:50] if message.text else 'None'}")
    print(f"[CHAT ROUTE] Has Auth: {authorization is not None}")
    print("=" * 80)
    
    # #region agent log
    try:
        debug_log("chat.py:89", "process_chat_message entry", {
            "hasAuth": authorization is not None,
            "authHeader": authorization[:20] + "..." if authorization and len(authorization) > 20 else authorization,
            "textLength": len(message.text) if message.text else 0,
            "textPreview": message.text[:50] if message.text else None,
            "language": message.language
        }, "A")
    except Exception as log_err:
        print(f"[CHAT ROUTE] Logging failed: {log_err}")
    # #endregion
    
    try:
        # #region agent log
        debug_log("chat.py:107", "before verify_token", {"hasAuth": authorization is not None}, "E")
        # #endregion
        user_id = verify_token(authorization)
        # #region agent log
        debug_log("chat.py:107", "auth verification success", {"userId": user_id}, "E")
        # #endregion
    except HTTPException as http_err:
        # #region agent log
        debug_log("chat.py:107", "auth HTTPException", {
            "statusCode": http_err.status_code,
            "detail": http_err.detail
        }, "E")
        # #endregion
        raise  # Re-raise HTTPException so FastAPI handles it
    except Exception as auth_err:
        # #region agent log
        debug_log("chat.py:107", "auth verification failed", {
            "error": str(auth_err),
            "errorType": type(auth_err).__name__
        }, "E")
        # #endregion
        raise
    
    # Initialize chat history if needed
    if user_id not in chat_history:
        chat_history[user_id] = []
    
    # Add user message to history
    user_msg = {
        "id": str(uuid.uuid4()),
        "type": "user",
        "text": message.text,
        "timestamp": datetime.now().isoformat()
    }
    chat_history[user_id].append(user_msg)
    
    # Process message with error handling
    try:
        # #region agent log
        debug_log("chat.py:116", "before process_user_message", {
            "text": message.text[:50],
            "language": message.language,
            "userId": user_id
        }, "B")
        # #endregion
        response = await process_user_message(message.text, message.language, user_id)
        # #region agent log
        debug_log("chat.py:116", "after process_user_message", {
            "responseText": response.text[:50] if response.text else None,
            "hasActions": response.actions is not None,
            "serviceId": response.service_id
        }, "B")
        # #endregion
    except Exception as e:
        import traceback
        # #region agent log
        debug_log("chat.py:123", "exception in process_user_message", {
            "error": str(e),
            "errorType": type(e).__name__
        }, "D")
        # #endregion
        print(f"Error processing chat message: {e}")
        traceback.print_exc()
        # Return error response
        error_response = ChatResponse(
            text="Sorry, an error occurred. Please try again." if message.language == "en" else "क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।",
            should_speak=False
        )
        bot_msg = {
            "id": str(uuid.uuid4()),
            "type": "bot",
            "text": error_response.text,
            "timestamp": datetime.now().isoformat()
        }
        chat_history[user_id].append(bot_msg)
        return {
            "success": False,
            "response": error_response.dict(),
            "message_id": bot_msg["id"],
            "error": str(e)
        }
    
    # Add bot response to history
    bot_msg = {
        "id": str(uuid.uuid4()),
        "type": "bot",
        "text": response.text,
        "actions": response.actions,
        "timestamp": datetime.now().isoformat()
    }
    chat_history[user_id].append(bot_msg)
    
    return {
        "success": True,
        "response": response.dict(),
        "message_id": bot_msg["id"]
    }

@router.get("/history")
async def get_chat_history(
    authorization: str = Header(None),
    limit: int = 50
):
    """Get chat history for user"""
    user_id = verify_token(authorization)
    
    if user_id not in chat_history:
        return {
            "success": True,
            "messages": []
        }
    
    messages = chat_history[user_id][-limit:]
    return {
        "success": True,
        "messages": messages
    }

@router.delete("/history")
async def clear_chat_history(authorization: str = Header(None)):
    """Clear chat history"""
    user_id = verify_token(authorization)
    
    if user_id in chat_history:
        chat_history[user_id] = []
    
    return {"success": True, "message": "Chat history cleared"}

async def process_user_message(text: str, language: str, user_id: str) -> ChatResponse:
    """
    Process user message with KYRON Service Intent Flow:
    1. Understand Intent (detect service)
    2. Explain Service (what it is, requirements, benefits)
    3. Show CTA Button [Apply with KYRON]
    4. Check Master Profile (what data exists)
    5. Request Missing Data (only ask for what's needed)
    6. Execute Automation
    """
    # #region agent log
    debug_log("chat.py:198", "process_user_message entry", {
        "text": text[:50],
        "language": language,
        "userId": user_id
    }, "A")
    # #endregion
    
    try:
        from services.service_explainer import generate_service_explanation
        from services.intent_detector import detect_service_intent, extract_service_parameters
        from services.master_profile_checker import MasterProfileChecker
        # #region agent log
        debug_log("chat.py:168", "import services success", {}, "A")
        # #endregion
    except ImportError as e:
        # #region agent log
        debug_log("chat.py:168", "import services failed", {"error": str(e)}, "A")
        # #endregion
        print(f"Warning: Could not import services: {e}")
        generate_service_explanation = None
        detect_service_intent = None
        extract_service_parameters = None
        MasterProfileChecker = None
    
    # Get user's Master Profile
    try:
        if use_database:
            user_profile = db_manager.get_user_profile(user_id) or {}
        else:
            from profile import profiles_db
            user_profile = profiles_db.get(user_id, {})
    except:
        user_profile = {}
    
    # Get or initialize session state
    if user_id not in session_state:
        # #region agent log
        debug_log("chat.py:174", "initializing new session state", {"userId": user_id}, "F")
        # #endregion
        session_state[user_id] = {
            "active_service": None,
            "stage": None,  # EXPLANATION, APPLY, DATA_COLLECTION, EXECUTION
            "collection_step": None,
            "collected_data": {}
        }
    
    state = session_state[user_id]
    # #region agent log
    debug_log("chat.py:182", "session state retrieved", {
        "activeService": state.get("active_service"),
        "stage": state.get("stage"),
        "collectionStep": state.get("collection_step")
    }, "F")
    # #endregion
    text_lower = text.lower().strip()
    
    # Handle empty or very short messages
    if not text_lower or len(text_lower) < 1:
        if language == "hi":
            return ChatResponse(
                text="कृपया अपना संदेश लिखें।",
                should_speak=False
            )
        else:
            return ChatResponse(
                text="Please type your message.",
                should_speak=False
            )
    
    # Check for confirmation FIRST if we're in CONFIRM_DETAILS step (before data collection handler)
    if state.get("active_service") == "pan_card" and state.get("collection_step") == PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]:
        # #region agent log
        debug_log("chat.py:309", "CONFIRM_DETAILS step detected", {
            "text": text_lower,
            "collectedData": state.get("collected_data", {})
        }, "D")
        # #endregion
        
        confirmation_keywords = {
            "en": ["yes", "proceed", "continue", "ok", "sure", "go ahead", "start", "yep", "yeah", "yes proceed", "yes, proceed", "apply for pan card", "apply"],
            "hi": ["हाँ", "आगे", "जारी", "ठीक", "बिल्कुल", "शुरू करें", "हां", "जी हाँ", "हाँ आगे", "हाँ, आगे", "पैन कार्ड के लिए आवेदन"]
        }
        lang_confirm = confirmation_keywords.get(language, confirmation_keywords["en"])
        
        if any(keyword in text_lower for keyword in lang_confirm):
            # #region agent log
            debug_log("chat.py:316", "confirmation keyword matched", {"matched": True}, "D")
            # #endregion
            
            try:
                # Start automation
                state["collection_step"] = PAN_COLLECTION_STEPS["READY_TO_SUBMIT"]
                state["stage"] = "EXECUTION"
                
                # #region agent log
                debug_log("chat.py:320", "before get_service_definition", {
                    "activeService": state["active_service"],
                    "hasGetServiceDefinition": get_service_definition is not None
                }, "D")
                # #endregion
                
                if not get_service_definition:
                    raise ValueError("get_service_definition is not available")
                
                service = get_service_definition(state["active_service"])
                
                # #region agent log
                debug_log("chat.py:320", "after get_service_definition", {
                    "serviceFound": service is not None,
                    "serviceName": service.name if service else None
                }, "D")
                # #endregion
                
                if not service:
                    raise ValueError(f"Service '{state['active_service']}' not found")
                
                # Prepare service config with collected data
                # CRITICAL: Store values as collected, normalization happens in automation engine
                collected = state.get("collected_data", {})
                service_config = {
                    "applicant_type": collected.get("applicant_type", "individual"),
                    "delivery_type": collected.get("delivery_type", "epan"),
                    "application_type": collected.get("application_type", "new"),
                    "existing_pan": collected.get("existing_pan"),  # For correction applications
                    "aadhaar_number": collected.get("aadhaar_number")  # If explicitly collected
                }
                
                # Log for debugging
                debug_log("chat.py:service_config", "Service config prepared", service_config, "D")
                
                # #region agent log
                debug_log("chat.py:323", "prepared service_config", service_config, "D")
                # #endregion
                
                if language == "hi":
                    return ChatResponse(
                        text="मैं आधिकारिक PAN card वेबसाइट खोल रहा हूं और आवेदन शुरू कर रहा हूं।",
                        service_id=state["active_service"],
                        service_config=service_config,
                        start_automation=True,
                        stage="EXECUTION",
                        should_speak=True
                    )
                else:
                    return ChatResponse(
                        text="I am opening the official PAN card website and starting the application.",
                        service_id=state["active_service"],
                        service_config=service_config,
                        start_automation=True,
                        stage="EXECUTION",
                        should_speak=True
                    )
            except Exception as auto_err:
                # #region agent log
                debug_log("chat.py:316", "error in CONFIRM_DETAILS handler", {
                    "error": str(auto_err),
                    "errorType": type(auto_err).__name__
                }, "D")
                # #endregion
                import traceback
                print(f"Error in CONFIRM_DETAILS handler: {auto_err}")
                traceback.print_exc()
                # Return error message instead of crashing
                if language == "hi":
                    return ChatResponse(
                        text=f"स्वचालन शुरू करने में त्रुटि: {str(auto_err)}. कृपया पुनः प्रयास करें।",
                        service_id=state["active_service"],
                        should_speak=False
                    )
                else:
                    return ChatResponse(
                        text=f"Error starting automation: {str(auto_err)}. Please try again.",
                        service_id=state["active_service"],
                        should_speak=False
                    )
    
    # Handle BRC multi-step data collection
    if state.get("active_service") == "bihar_residence_certificate" and state.get("stage") == "COLLECTING_DATA":
        try:
            result = await handle_brc_data_collection(text, text_lower, language, state)
            return result
        except Exception as coll_err:
            import traceback
            print(f"Error in BRC data collection handler: {coll_err}")
            traceback.print_exc()
            if language == "hi":
                return ChatResponse(
                    text=f"डेटा संग्रह में त्रुटि: {str(coll_err)}. कृपया पुनः प्रयास करें।",
                    service_id=state["active_service"],
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text=f"Error in data collection: {str(coll_err)}. Please try again.",
                    service_id=state["active_service"],
                    should_speak=False
                )
    
    # Handle PAN card multi-step data collection
    if state.get("active_service") == "pan_card" and state.get("stage") == "COLLECTING_DATA":
        # #region agent log
        debug_log("chat.py:409", "COLLECTING_DATA stage detected", {
            "collectionStep": state.get("collection_step"),
            "text": text_lower[:50]
        }, "C")
        # #endregion
        
        try:
            result = await handle_pan_card_data_collection(text, text_lower, language, state)
            # #region agent log
            debug_log("chat.py:410", "data collection handler success", {
                "responseText": result.text[:100] if result.text else None
            }, "C")
            # #endregion
            return result
        except Exception as coll_err:
            # #region agent log
            debug_log("chat.py:410", "data collection handler error", {
                "error": str(coll_err),
                "errorType": type(coll_err).__name__
            }, "C")
            # #endregion
            import traceback
            print(f"Error in data collection handler: {coll_err}")
            traceback.print_exc()
            # Return error message instead of crashing
            if language == "hi":
                return ChatResponse(
                    text=f"डेटा संग्रह में त्रुटि: {str(coll_err)}. कृपया पुनः प्रयास करें।",
                    service_id=state["active_service"],
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text=f"Error in data collection: {str(coll_err)}. Please try again.",
                    service_id=state["active_service"],
                    should_speak=False
                )
    
    # Handle action buttons
    if text_lower in ["apply for pan card", "pan card के लिए आवेदन करें", "apply_service"]:
        # Handle BRC apply
        if state.get("active_service") == "bihar_residence_certificate":
            if state.get("stage") == "EXPLANATION":
                state["stage"] = "COLLECTING_DATA"
                state["collection_step"] = BRC_COLLECTION_STEPS["ASK_APPLICANT_NAME"]
                
                # Check Master Profile first
                try:
                    if MasterProfileChecker:
                        profile_checker = MasterProfileChecker(user_profile)
                        available_data = profile_checker.get_profile_data_for_service(
                            get_service_definition("bihar_residence_certificate") if get_service_definition else None
                        )
                        if available_data:
                            state["collected_data"].update(available_data)
                except:
                    pass
                
                # Start data collection
                if not state["collected_data"].get("applicant_name"):
                    if language == "hi":
                        return ChatResponse(
                            text="✅ बिहार निवास प्रमाण पत्र के लिए आवेदन शुरू कर रहे हैं।\n\n**पहला सवाल:** आपका पूरा नाम क्या है? (जैसा आधार कार्ड पर है)",
                            service_id="bihar_residence_certificate",
                            stage="COLLECTING_DATA",
                            should_speak=True
                        )
                    else:
                        return ChatResponse(
                            text="✅ Starting application for Bihar Residence Certificate.\n\n**First question:** What is your full name? (as per Aadhaar card)",
                            service_id="bihar_residence_certificate",
                            stage="COLLECTING_DATA",
                            should_speak=True
                        )
                else:
                    # Move to next missing field
                    return await handle_brc_data_collection(text, text_lower, language, state)
        
        if state.get("active_service") == "pan_card":
            # If in EXPLANATION stage, start data collection with Master Profile check
            if state.get("stage") == "EXPLANATION":
                state["stage"] = "COLLECTING_DATA"
                
                # Check Master Profile first - don't ask for data that already exists
                if MasterProfileChecker:
                    try:
                        profile_checker = MasterProfileChecker(user_profile)
                        available_data = profile_checker.get_profile_data_for_service(
                            get_service_definition("pan_card") if get_service_definition else None
                        )
                        # Merge available data
                        if available_data:
                            state["collected_data"].update(available_data)
                    except:
                        pass
                
                # Only ask for missing data - CRITICAL: Check in correct order
                if not state["collected_data"].get("applicant_type"):
                    state["collection_step"] = PAN_COLLECTION_STEPS["ASK_APPLICANT_TYPE"]
                elif not state["collected_data"].get("application_type"):
                    state["collection_step"] = PAN_COLLECTION_STEPS["ASK_APPLICATION_TYPE"]
                elif not state["collected_data"].get("delivery_type"):
                    state["collection_step"] = PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]
                else:
                    # All data collected, move to confirmation
                    state["collection_step"] = PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]
                
                if language == "hi":
                    return ChatResponse(
                        text="बहुत बढ़िया! मुझे कुछ जानकारी चाहिए।\n\n**पहला सवाल:** आप किस प्रकार का PAN Card चाहते हैं?\n\n1️⃣ **Individual** (व्यक्तिगत) - अपने लिए\n2️⃣ **Company/HUF** (कंपनी/HUF) - व्यापार/कंपनी के लिए",
                        actions=[
                            {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                            {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                        ],
                        service_id="pan_card",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
                else:
                    return ChatResponse(
                        text="Great! I need to collect some information from you.\n\n**First question:** What type of PAN card do you want?\n\n1️⃣ **Individual** - For personal use\n2️⃣ **Company/HUF** - For business/company use",
                        actions=[
                            {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                            {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                        ],
                        service_id="pan_card",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
            # If all data collected (CONFIRM_DETAILS step), start execution
            elif state.get("collection_step") == PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]:
                state["collection_step"] = PAN_COLLECTION_STEPS["READY_TO_SUBMIT"]
                state["stage"] = "EXECUTION"
                service = get_service_definition(state["active_service"])
                if service:
                    # Prepare service config with collected data
                    service_config = {
                        "applicant_type": state["collected_data"].get("applicant_type", "individual"),
                        "delivery_type": state["collected_data"].get("delivery_type", "epan"),
                        "application_type": "new"
                    }
                    
                    if language == "hi":
                        return ChatResponse(
                            text="मैं आधिकारिक PAN card वेबसाइट खोल रहा हूं और आवेदन शुरू कर रहा हूं।",
                            service_id=state["active_service"],
                            service_config=service_config,
                            start_automation=True,
                            stage="EXECUTION",
                            should_speak=True
                        )
                    else:
                        return ChatResponse(
                            text="I am opening the official PAN card website and starting the application.",
                            service_id=state["active_service"],
                            service_config=service_config,
                            start_automation=True,
                            stage="EXECUTION",
                            should_speak=True
                        )
    
    if text_lower in ["cancel", "रद्द करें"]:
        state["active_service"] = None
        state["stage"] = None
        if language == "hi":
            return ChatResponse(
                text="ठीक है, मैं आपकी और कैसे मदद कर सकता हूं?",
                should_speak=False
            )
        else:
            return ChatResponse(
                text="Okay, how else can I help you?",
                should_speak=False
            )
    
    # If active service exists in EXPLANATION stage, show proceed option
    if state.get("active_service") == "pan_card" and state.get("stage") == "EXPLANATION":
        # Don't show generic message, let the apply_service action handle it
        # This prevents the loop
        pass
    elif state.get("active_service") and state.get("stage") != "EXECUTION" and state.get("stage") != "COLLECTING_DATA":
        # Continue conversation within service context (for other services)
        service = get_service_definition(state["active_service"])
        if service:
            if language == "hi":
                return ChatResponse(
                    text=f"आप {service.name} के लिए आवेदन कर रहे हैं। क्या आप आगे बढ़ना चाहेंगे?",
                    actions=[
                        {"label": f"{service.name} के लिए आवेदन करें", "action": "apply_service", "service_id": state["active_service"]},
                        {"label": "प्रश्न पूछें", "action": "ask_questions"},
                        {"label": "रद्द करें", "action": "cancel"}
                    ],
                    service_id=state["active_service"],
                    stage=state.get("stage"),
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text=f"You're applying for {service.name}. Would you like to proceed?",
                    actions=[
                        {"label": f"Apply for {service.name}", "action": "apply_service", "service_id": state["active_service"]},
                        {"label": "Ask Questions", "action": "ask_questions"},
                        {"label": "Cancel", "action": "cancel"}
                    ],
                    service_id=state["active_service"],
                    stage=state.get("stage"),
                    should_speak=False
                )
    
    # KYRON Service Intent Detection - Use intent detector
    detected_service = None
    service_params = {}
    
    if detect_service_intent:
        intent_result = detect_service_intent(text)
        if intent_result:
            detected_service_type, confidence = intent_result
            detected_service = detected_service_type.value
            
            # Extract service-specific parameters
            if extract_service_parameters:
                service_params = extract_service_parameters(text, detected_service_type)
    
    # Fallback to keyword-based detection if intent detector not available
    # CRITICAL: Also check if user wants to restart/reset service
    if not detected_service:
        service_keywords = {
            "pan_card": {
                "en": ["pan card", "pan", "permanent account number", "i want to apply for pan", "apply for pan", "apply for pan card", "pan card apply", "get pan", "need pan"],
                "hi": ["पैन", "पैन कार्ड", "पैन कार्ड बनवाना", "मैं पैन कार्ड के लिए आवेदन करना चाहता हूं", "पैन के लिए आवेदन"]
            },
            "income_certificate": {
                "en": ["income certificate", "income", "salary certificate"],
                "hi": ["आय प्रमाण पत्र", "आय", "वेतन प्रमाण पत्र"]
            },
            "bihar_residence_certificate": {
                "en": ["bihar residence certificate", "bihar residence", "brc", "niwas praman patra", "residence certificate bihar"],
                "hi": ["बिहार निवास प्रमाण पत्र", "बिहार निवास", "निवास प्रमाण पत्र बिहार", "निवास बनवाना"]
            },
        }
        
        for service_id, keywords in service_keywords.items():
            lang_keywords = keywords.get(language, keywords.get("en", []))
            if any(keyword in text_lower for keyword in lang_keywords):
                detected_service = service_id
                # CRITICAL: Reset state if user explicitly requests service again
                if state.get("active_service") != service_id:
                    state["active_service"] = None
                    state["stage"] = None
                    state["collection_step"] = None
                    state["collected_data"] = {}
                break
    
    # KYRON Service Intent Flow: If service detected, show EXPLANATION with CTA
    if detected_service and get_service_definition:
        # #region agent log
        debug_log("chat.py:374", "service detected", {
            "detectedService": detected_service,
            "serviceParams": service_params,
            "hasGetServiceDefinition": get_service_definition is not None
        }, "C")
        # #endregion
        try:
            service = get_service_definition(detected_service)
            # #region agent log
            debug_log("chat.py:376", "get_service_definition result", {
                "serviceFound": service is not None,
                "serviceName": service.name if service else None
            }, "C")
            # #endregion
            if service:
                # Lock the service in session state
                state["active_service"] = detected_service
                state["stage"] = "EXPLANATION"
                # Store extracted parameters
                if service_params:
                    state["collected_data"].update(service_params)
                
                # Check Master Profile for available data
                profile_checker = None
                available_data = {}
                missing_data = []
                
                if MasterProfileChecker:
                    try:
                        profile_checker = MasterProfileChecker(user_profile)
                        profile_status = profile_checker.check_service_requirements(service)
                        available_data = profile_status.get("available", {})
                        missing_data = profile_status.get("missing", [])
                        
                        # Merge available data into collected_data
                        state["collected_data"].update(available_data)
                    except Exception as profile_err:
                        print(f"Error checking Master Profile: {profile_err}")
                
                # Generate service explanation
                explanation_text = ""
                if generate_service_explanation:
                    try:
                        explanation_text = generate_service_explanation(service, language)
                    except:
                        pass
                
                # If no explanation generated, use default
                if not explanation_text:
                    if language == "hi":
                        explanation_text = f"""
**{service.name}** के बारे में:

{service.description}

**लाभ:**
{chr(10).join('• ' + benefit for benefit in service.benefits)}

**आवश्यक दस्तावेज:**
{chr(10).join('• ' + doc for doc in service.required_documents)}

**अनुमानित समय:** {service.estimated_time}
"""
                    else:
                        explanation_text = f"""
**About {service.name}:**

{service.description}

**Benefits:**
{chr(10).join('• ' + benefit for benefit in service.benefits)}

**Required Documents:**
{chr(10).join('• ' + doc for doc in service.required_documents)}

**Estimated Time:** {service.estimated_time}
"""
                
                # Add Master Profile status message
                if available_data and len(available_data) > 0:
                    if language == "hi":
                        explanation_text += f"\n\n✅ मैंने आपके Master Profile से {len(available_data)} जानकारी पाई है।"
                    else:
                        explanation_text += f"\n\n✅ I found {len(available_data)} details in your Master Profile."
                
                if missing_data and len(missing_data) > 0:
                    if language == "hi":
                        explanation_text += f"\n⚠️ कुछ जानकारी चाहिए: {', '.join(missing_data[:3])}"
                        if len(missing_data) > 3:
                            explanation_text += f" और {len(missing_data) - 3} और..."
                    else:
                        explanation_text += f"\n⚠️ Need some information: {', '.join(missing_data[:3])}"
                        if len(missing_data) > 3:
                            explanation_text += f" and {len(missing_data) - 3} more..."
                
                # Show CTA button
                if language == "hi":
                    return ChatResponse(
                        text=explanation_text,
                        actions=[
                            {"label": f"KYRON के साथ {service.name} के लिए आवेदन करें", "action": "apply_service", "service_id": detected_service}
                        ],
                        service_id=detected_service,
                        stage="EXPLANATION",
                        explanation={
                            "service_name": service.name,
                            "description": service.description,
                            "benefits": service.benefits,
                            "required_documents": service.required_documents,
                            "estimated_time": service.estimated_time,
                            "available_data": list(available_data.keys()),
                            "missing_data": missing_data
                        },
                        should_speak=True
                    )
                else:
                    return ChatResponse(
                        text=explanation_text,
                        actions=[
                            {"label": f"Apply {service.name} with KYRON", "action": "apply_service", "service_id": detected_service}
                        ],
                        service_id=detected_service,
                        stage="EXPLANATION",
                        explanation={
                            "service_name": service.name,
                            "description": service.description,
                            "benefits": service.benefits,
                            "required_documents": service.required_documents,
                            "estimated_time": service.estimated_time,
                            "available_data": list(available_data.keys()),
                            "missing_data": missing_data
                        },
                        should_speak=True
                    )
                
                # Generate structured explanation
                explanation = None
                if generate_service_explanation:
                    try:
                        explanation = generate_service_explanation(detected_service, language)
                    except Exception as e:
                        print(f"Error generating service explanation: {e}")
                        explanation = None
                
                if explanation:
                    # Convert explanation to text format for display
                    explanation_text = f"# {explanation['title']}\n\n"
                    for section in explanation.get("sections", []):
                        explanation_text += f"## {section['heading']}\n{section['content']}\n\n"
                    
                    # Add brief summary and ask for confirmation
                    if detected_service == "pan_card":
                        if language == "hi":
                            explanation_text += "\n**संक्षेप में:** PAN Card के लिए आवेदन करने के लिए आपको कुछ जानकारी देनी होगी।\n\n"
                            explanation_text += "क्या आप आगे बढ़ना चाहेंगे?"
                        else:
                            explanation_text += "\n**In brief:** To apply for a PAN card, I'll need to collect some information from you.\n\n"
                            explanation_text += "Would you like to proceed?"
                    
                    # For PAN card, show "Apply for PAN Card" button that starts data collection
                    if detected_service == "pan_card":
                        actions = [
                            {"label": language == "hi" and "PAN Card के लिए आवेदन करें" or "Apply for PAN Card", "action": "apply_service", "service_id": detected_service},
                            {"label": language == "hi" and "प्रश्न पूछें" or "Ask Questions", "action": "ask_questions"},
                            {"label": language == "hi" and "रद्द करें" or "Cancel", "action": "cancel"}
                        ]
                    else:
                        actions = [
                            {"label": language == "hi" and "हाँ, आगे बढ़ें" or "Yes, proceed", "action": "confirm_proceed", "service_id": detected_service},
                            {"label": language == "hi" and "प्रश्न पूछें" or "Ask Questions", "action": "ask_questions"},
                            {"label": language == "hi" and "रद्द करें" or "Cancel", "action": "cancel"}
                        ]
                    
                    return ChatResponse(
                        text=explanation_text,
                        explanation=explanation,
                        actions=actions,
                        service_id=detected_service,
                        stage="EXPLANATION",
                        should_speak=True
                    )
                else:
                    # Fallback if explanation generation fails
                    if language == "hi":
                        return ChatResponse(
                            text=f"{service.name} के लिए आवेदन करने के लिए तैयार हैं?",
                            actions=[
                                {"label": f"{service.name} के लिए आवेदन करें", "action": "apply_service", "service_id": detected_service},
                                {"label": "रद्द करें", "action": "cancel"}
                            ],
                            service_id=detected_service,
                            stage="EXPLANATION",
                            should_speak=False
                        )
                    else:
                        return ChatResponse(
                            text=f"Ready to apply for {service.name}?",
                            actions=[
                                {"label": f"Apply for {service.name}", "action": "apply_service", "service_id": detected_service},
                                {"label": "Cancel", "action": "cancel"}
                            ],
                            service_id=detected_service,
                            stage="EXPLANATION",
                            should_speak=False
                        )
        except Exception as e:
            import traceback
            print(f"Error in service detection/explanation: {e}")
            traceback.print_exc()
            # Continue to default response
    
    # Default response (only if no active service)
    if not state.get("active_service"):
        if language == "hi":
            return ChatResponse(
                text="मैं आपकी कैसे मदद कर सकता हूं? आप PAN कार्ड, आय प्रमाण पत्र, या अन्य सेवाओं के लिए आवेदन कर सकते हैं।",
                should_speak=False
            )
        else:
            return ChatResponse(
                text="How can I help you? You can apply for PAN card, income certificate, or other services.",
                should_speak=False
            )
    
    # Handle confirmations for PAN card
    if state.get("active_service") == "pan_card":
        confirmation_keywords = {
            "en": ["yes", "proceed", "continue", "ok", "sure", "go ahead", "start", "yep", "yeah", "yes proceed"],
            "hi": ["हाँ", "आगे", "जारी", "ठीक", "बिल्कुल", "शुरू करें", "हां", "जी हाँ", "हाँ आगे"]
        }
        lang_confirm = confirmation_keywords.get(language, confirmation_keywords["en"])
        
        if any(keyword in text_lower for keyword in lang_confirm):
            # If data collection is complete, start automation
            if state.get("collection_step") == PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]:
                # #region agent log
                debug_log("chat.py:603", "CONFIRM_DETAILS confirmation received", {
                    "collectedData": state.get("collected_data", {}),
                    "activeService": state.get("active_service")
                }, "D")
                # #endregion
                
                try:
                    state["collection_step"] = PAN_COLLECTION_STEPS["READY_TO_SUBMIT"]
                    state["stage"] = "EXECUTION"
                    
                    # #region agent log
                    debug_log("chat.py:606", "before get_service_definition", {
                        "activeService": state["active_service"],
                        "hasGetServiceDefinition": get_service_definition is not None
                    }, "D")
                    # #endregion
                    
                    if not get_service_definition:
                        raise ValueError("get_service_definition is not available")
                    
                    service = get_service_definition(state["active_service"])
                    
                    # #region agent log
                    debug_log("chat.py:606", "after get_service_definition", {
                        "serviceFound": service is not None,
                        "serviceName": service.name if service else None
                    }, "D")
                    # #endregion
                    
                    if not service:
                        raise ValueError(f"Service '{state['active_service']}' not found")
                    
                    # Prepare service config with collected data
                    service_config = {
                        "applicant_type": state["collected_data"].get("applicant_type", "individual"),
                        "delivery_type": state["collected_data"].get("delivery_type", "epan"),
                        "application_type": "new"
                    }
                    
                    # #region agent log
                    debug_log("chat.py:609", "prepared service_config", service_config, "D")
                    # #endregion
                    
                    if language == "hi":
                        return ChatResponse(
                            text="मैं आधिकारिक PAN card वेबसाइट खोल रहा हूं और आवेदन शुरू कर रहा हूं।",
                            service_id=state["active_service"],
                            service_config=service_config,
                            start_automation=True,
                            stage="EXECUTION",
                            should_speak=True
                        )
                    else:
                        return ChatResponse(
                            text="I am opening the official PAN card website and starting the application.",
                            service_id=state["active_service"],
                            service_config=service_config,
                            start_automation=True,
                            stage="EXECUTION",
                            should_speak=True
                        )
                except Exception as auto_err:
                    # #region agent log
                    debug_log("chat.py:603", "error starting automation", {
                        "error": str(auto_err),
                        "errorType": type(auto_err).__name__
                    }, "D")
                    # #endregion
                    import traceback
                    print(f"Error starting automation: {auto_err}")
                    traceback.print_exc()
                    # Return error message instead of crashing
                    if language == "hi":
                        return ChatResponse(
                            text=f"स्वचालन शुरू करने में त्रुटि: {str(auto_err)}. कृपया पुनः प्रयास करें।",
                            service_id=state["active_service"],
                            should_speak=False
                        )
                    else:
                        return ChatResponse(
                            text=f"Error starting automation: {str(auto_err)}. Please try again.",
                            service_id=state["active_service"],
                            should_speak=False
                        )
            elif state.get("stage") == "EXPLANATION":
                # User confirmed after explanation, start data collection
                state["stage"] = "COLLECTING_DATA"
                state["collection_step"] = PAN_COLLECTION_STEPS["ASK_APPLICANT_TYPE"]
                state["collected_data"] = {}
                
                if language == "hi":
                    return ChatResponse(
                        text="बहुत बढ़िया! मुझे कुछ जानकारी चाहिए।\n\n**पहला सवाल:** आप किस प्रकार का PAN Card चाहते हैं?\n\n1️⃣ **Individual** (व्यक्तिगत) - अपने लिए\n2️⃣ **Company/HUF** (कंपनी/HUF) - व्यापार/कंपनी के लिए",
                        actions=[
                            {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                            {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                        ],
                        service_id="pan_card",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
                else:
                    return ChatResponse(
                        text="Great! I need to collect some information from you.\n\n**First question:** What type of PAN card do you want?\n\n1️⃣ **Individual** - For personal use\n2️⃣ **Company/HUF** - For business/company use",
                        actions=[
                            {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                            {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                        ],
                        service_id="pan_card",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
    
    # If active service exists but no specific action, maintain context
    return ChatResponse(
        text=text,  # Echo back or provide contextual help
        service_id=state.get("active_service"),
        stage=state.get("stage"),
        should_speak=False
    )

async def handle_pan_card_data_collection(text: str, text_lower: str, language: str, state: Dict[str, Any]) -> ChatResponse:
    """Handle multi-step PAN card data collection"""
    # CRITICAL: Normalize text_lower - strip whitespace and ensure lowercase
    text_lower = text_lower.strip().lower() if text_lower else ""
    text = text.strip() if text else ""
    
    step = state.get("collection_step")
    collected = state.get("collected_data", {})
    
    # #region agent log
    debug_log("chat.py:786", "handle_pan_card_data_collection entry", {
        "step": step,
        "text": text_lower[:50],
        "textOriginal": text[:50],
        "collected": collected,
        "activeService": state.get("active_service"),
        "stage": state.get("stage")
    }, "F")
    # #endregion
    
    # CRITICAL: If no step is set but we're in COLLECTING_DATA, start from beginning
    if not step and state.get("stage") == "COLLECTING_DATA":
        step = PAN_COLLECTION_STEPS["ASK_APPLICANT_TYPE"]
        state["collection_step"] = step
        logger.warning(f"[PAN_DATA_COLLECTION] No step set, defaulting to ASK_APPLICANT_TYPE")
    
    # Step 1: Ask applicant type (Individual or Company)
    if step == PAN_COLLECTION_STEPS["ASK_APPLICANT_TYPE"]:
        # #region agent log
        debug_log("chat.py:837", "ASK_APPLICANT_TYPE step", {
            "text": text,
            "text_lower": text_lower,
            "language": language
        }, "F")
        # #endregion
        
        # Detect applicant type from user input
        # Support exact button text AND keyword variations
        individual_keywords = {
            "en": ["individual", "personal", "1", "one", "for me", "myself"],
            "hi": ["व्यक्तिगत", "अपने", "1", "एक", "मेरे लिए", "individual"]
        }
        company_keywords = {
            "en": ["company", "huf", "business", "2", "two", "corporate", "company/huf"],
            "hi": ["कंपनी", "huf", "व्यापार", "2", "दो", "कारपोरेट", "company"]
        }
        
        lang_individual = individual_keywords.get(language, individual_keywords["en"])
        lang_company = company_keywords.get(language, company_keywords["en"])
        
        # #region agent log
        debug_log("chat.py:852", "checking applicant type keywords", {
            "langIndividual": lang_individual,
            "langCompany": lang_company,
            "textLower": text_lower
        }, "F")
        # #endregion
        
        if any(keyword in text_lower for keyword in lang_individual):
            # #region agent log
            debug_log("chat.py:856", "Individual applicant type detected", {
                "matched": True
            }, "F")
            # #endregion
            
            collected["applicant_type"] = "individual"
            state["collection_step"] = PAN_COLLECTION_STEPS["ASK_APPLICATION_TYPE"]
            
            if language == "hi":
                return ChatResponse(
                    text="✅ Individual PAN Card चुना गया।\n\n**अगला सवाल:** आप किस प्रकार का आवेदन करना चाहते हैं?\n\n1️⃣ **नया PAN Card** - पहली बार आवेदन\n2️⃣ **सुधार/अपडेट** - मौजूदा PAN में बदलाव",
                    actions=[
                        {"label": "नया PAN Card", "action": "select_application_type", "value": "new"},
                        {"label": "सुधार/अपडेट", "action": "select_application_type", "value": "correction"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ Individual PAN Card selected.\n\n**Next question:** What type of application do you want?\n\n1️⃣ **New PAN Card** - Applying for first time\n2️⃣ **Correction/Update** - Update existing PAN",
                    actions=[
                        {"label": "New PAN Card", "action": "select_application_type", "value": "new"},
                        {"label": "Correction/Update", "action": "select_application_type", "value": "correction"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        elif any(keyword in text_lower for keyword in lang_company):
            # #region agent log
            debug_log("chat.py:882", "Company applicant type detected", {
                "matched": True
            }, "F")
            # #endregion
            
            collected["applicant_type"] = "company"
            state["collection_step"] = PAN_COLLECTION_STEPS["ASK_APPLICATION_TYPE"]
            
            if language == "hi":
                return ChatResponse(
                    text="✅ Company/HUF PAN Card चुना गया।\n\n**अगला सवाल:** आप किस प्रकार का PAN Card चाहते हैं?\n\n1️⃣ **Digital (e-PAN)** - निःशुल्क, 24-48 घंटे में मिलेगा\n2️⃣ **Physical Card** - ₹93 शुल्क, 15-20 दिन में मिलेगा",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ Company/HUF PAN Card selected.\n\n**Next question:** What type of PAN card delivery do you prefer?\n\n1️⃣ **Digital (e-PAN)** - Free, delivered in 24-48 hours\n2️⃣ **Physical Card** - ₹93 fee, delivered in 15-20 days",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            # Invalid input, ask again
            if language == "hi":
                return ChatResponse(
                    text="कृपया सही विकल्प चुनें:\n\n1️⃣ **Individual** (व्यक्तिगत)\n2️⃣ **Company/HUF** (कंपनी)",
                    actions=[
                        {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                        {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please select a valid option:\n\n1️⃣ **Individual**\n2️⃣ **Company/HUF**",
                    actions=[
                        {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                        {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    # Step 2: Ask application type (New or Correction)
    elif step == PAN_COLLECTION_STEPS["ASK_APPLICATION_TYPE"]:
        # Detect application type from user input
        new_keywords = {
            "en": ["new", "first time", "apply", "1", "one", "don't have", "don't have pan"],
            "hi": ["नया", "पहली बार", "आवेदन", "1", "एक", "नहीं है", "new"]
        }
        correction_keywords = {
            "en": ["correction", "update", "change", "modify", "2", "two", "existing", "have pan"],
            "hi": ["सुधार", "अपडेट", "बदलना", "2", "दो", "मौजूद", "correction"]
        }
        
        lang_new = new_keywords.get(language, new_keywords["en"])
        lang_correction = correction_keywords.get(language, correction_keywords["en"])
        
        if any(keyword in text_lower for keyword in lang_new):
            collected["application_type"] = "new"
            state["collection_step"] = PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]
            
            if language == "hi":
                return ChatResponse(
                    text="✅ नया PAN Card आवेदन चुना गया।\n\n**अगला सवाल:** आप किस प्रकार का PAN Card चाहते हैं?\n\n1️⃣ **Digital (e-PAN)** - निःशुल्क, 24-48 घंटे में मिलेगा\n2️⃣ **Physical Card** - ₹93 शुल्क, 15-20 दिन में मिलेगा",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ New PAN Card application selected.\n\n**Next question:** What type of PAN card delivery do you prefer?\n\n1️⃣ **Digital (e-PAN)** - Free, delivered in 24-48 hours\n2️⃣ **Physical Card** - ₹93 fee, delivered in 15-20 days",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        elif any(keyword in text_lower for keyword in lang_correction):
            collected["application_type"] = "correction"
            state["collection_step"] = PAN_COLLECTION_STEPS["ASK_EXISTING_PAN"]
            
            if language == "hi":
                return ChatResponse(
                    text="✅ PAN Card सुधार/अपडेट चुना गया।\n\n**अगला सवाल:** कृपया अपना मौजूदा PAN नंबर दर्ज करें (उदाहरण: ABCDE1234F):",
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ PAN Card correction/update selected.\n\n**Next question:** Please enter your existing PAN number (e.g., ABCDE1234F):",
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            # Invalid input, ask again
            if language == "hi":
                return ChatResponse(
                    text="कृपया सही विकल्प चुनें:\n\n1️⃣ **नया PAN Card** - पहली बार आवेदन\n2️⃣ **सुधार/अपडेट** - मौजूदा PAN में बदलाव",
                    actions=[
                        {"label": "नया PAN Card", "action": "select_application_type", "value": "new"},
                        {"label": "सुधार/अपडेट", "action": "select_application_type", "value": "correction"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please select a valid option:\n\n1️⃣ **New PAN Card** - Applying for first time\n2️⃣ **Correction/Update** - Update existing PAN",
                    actions=[
                        {"label": "New PAN Card", "action": "select_application_type", "value": "new"},
                        {"label": "Correction/Update", "action": "select_application_type", "value": "correction"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    # Step 3: Ask existing PAN if Correction
    elif step == PAN_COLLECTION_STEPS["ASK_EXISTING_PAN"]:
        # Extract PAN number from text (format: ABCDE1234F or ABCDE 1234 F)
        import re
        pan_pattern = r'[A-Z]{5}\d{4}[A-Z]'
        pan_match = re.search(pan_pattern, text.upper().replace(" ", ""))
        
        if pan_match:
            collected["existing_pan"] = pan_match.group()
            state["collection_step"] = PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]
            
            if language == "hi":
                return ChatResponse(
                    text=f"✅ PAN नंबर दर्ज किया गया: {collected['existing_pan']}\n\n**अगला सवाल:** आप किस प्रकार का PAN Card चाहते हैं?\n\n1️⃣ **Digital (e-PAN)** - निःशुल्क, 24-48 घंटे में मिलेगा\n2️⃣ **Physical Card** - ₹93 शुल्क, 15-20 दिन में मिलेगा",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text=f"✅ PAN number recorded: {collected['existing_pan']}\n\n**Next question:** What type of PAN card delivery do you prefer?\n\n1️⃣ **Digital (e-PAN)** - Free, delivered in 24-48 hours\n2️⃣ **Physical Card** - ₹93 fee, delivered in 15-20 days",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            # Invalid PAN format
            if language == "hi":
                return ChatResponse(
                    text="❌ गलत PAN नंबर प्रारूप। कृपया सही प्रारूप में दर्ज करें:\n\n**उदाहरण:** ABCDE1234F\n\nकृपया अपना PAN नंबर दोबारा दर्ज करें:",
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="❌ Invalid PAN number format. Please enter in correct format:\n\n**Example:** ABCDE1234F\n\nPlease enter your PAN number again:",
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    # Step 4: Ask delivery type (Digital or Physical)
    elif step == PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]:
        # #region agent log
        debug_log("chat.py:884", "ASK_DELIVERY_TYPE step", {
            "text": text_lower,
            "textOriginal": text,
            "language": language,
            "step": step,
            "collected": collected
        }, "F")
        # #endregion
        
        # CRITICAL: Ensure we have the right step
        if step != PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]:
            logger.error(f"[PAN_DATA_COLLECTION] Step mismatch! Expected ASK_DELIVERY_TYPE, got: {step}")
            # Fix the step
            state["collection_step"] = PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]
            step = PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]
        
        # Support exact button text AND keyword variations
        # CRITICAL: Make matching more flexible - check if text contains keyword
        digital_keywords = {
            "en": ["digital", "epan", "e-pan", "electronic", "1", "one", "free", "digital (e-pan)", "online", "e pan", "e-pan only"],
            "hi": ["डिजिटल", "ई-पैन", "इलेक्ट्रॉनिक", "1", "एक", "निःशुल्क", "digital", "ऑनलाइन"]
        }
        physical_keywords = {
            "en": ["physical", "card", "hard copy", "2", "two", "printed", "physical card", "both", "physical and"],
            "hi": ["फिजिकल", "कार्ड", "हार्ड कॉपी", "2", "दो", "प्रिंटेड", "physical", "दोनों"]
        }
        
        lang_digital = digital_keywords.get(language, digital_keywords["en"])
        lang_physical = physical_keywords.get(language, physical_keywords["en"])
        
        # #region agent log
        debug_log("chat.py:897", "checking keywords", {
            "langDigital": lang_digital,
            "langPhysical": lang_physical,
            "textLower": text_lower
        }, "F")
        # #endregion
        
        # CRITICAL: More flexible matching - check both exact match and contains
        text_clean = text_lower.strip() if text_lower else ""
        digital_match = False
        
        # CRITICAL: Simple check first - if text is just "digital", match it
        if text_clean == "digital":
            digital_match = True
        # Try exact match
        elif text_clean in lang_digital:
            digital_match = True
        # Then try contains match
        if not digital_match:
            for keyword in lang_digital:
                if keyword in text_clean:
                    digital_match = True
                    break
        # Also check if text starts with any keyword
        if not digital_match:
            for keyword in lang_digital:
                if len(keyword) > 2 and text_clean.startswith(keyword):
                    digital_match = True
                    break
        
        if digital_match:
            # #region agent log
            debug_log("chat.py:950", "Digital delivery type detected", {
                "matched": True,
                "textClean": text_clean,
                "matchedKeyword": [k for k in lang_digital if k in text_clean or text_clean == k][0] if digital_match else None
            }, "F")
            # #endregion
            
            collected["delivery_type"] = "epan"
            state["collection_step"] = PAN_COLLECTION_STEPS["VERIFY_AADHAAR"]
            
            # Check Aadhaar and proceed to confirmation if exists, otherwise ask
            user_id = state.get("user_id")
            if user_id:
                try:
                    user_profile = db_manager.get_user_profile(user_id) or {}
                except:
                    user_profile = {}
                aadhaar_in_profile = user_profile.get("aadhaarNumber") or user_profile.get("aadhaar_number")
                if aadhaar_in_profile:
            state["collection_step"] = PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]
                    # Continue to confirmation below
                else:
                    # Ask for Aadhaar
                    if language == "hi":
                        return ChatResponse(
                            text="**Aadhaar नंबर आवश्यक है**\n\nकृपया अपना 12 अंकों का Aadhaar नंबर दर्ज करें (उदाहरण: 1234 5678 9012):",
                            service_id="pan_card",
                            stage="COLLECTING_DATA",
                            should_speak=True
                        )
                    else:
                        return ChatResponse(
                            text="**Aadhaar Number Required**\n\nPlease enter your 12-digit Aadhaar number (e.g., 1234 5678 9012):",
                            service_id="pan_card",
                            stage="COLLECTING_DATA",
                            should_speak=True
                        )
            
            # If we reach here, Aadhaar exists, show confirmation
            if state["collection_step"] == PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]:
            # Show summary and ask for final confirmation
            applicant_type_text = "Individual" if collected.get("applicant_type") == "individual" else "Company/HUF"
                application_type_text = "New" if collected.get("application_type") == "new" else "Correction/Update"
            delivery_type_text = "Digital (e-PAN)" if collected.get("delivery_type") == "epan" else "Physical Card"
                
                summary_parts = [
                    f"• PAN Card Type: {applicant_type_text}",
                    f"• Application Type: {application_type_text}"
                ]
                if collected.get("existing_pan"):
                    summary_parts.append(f"• Existing PAN: {collected.get('existing_pan')}")
                summary_parts.append(f"• Delivery Type: {delivery_type_text}")
                summary_text = "\n".join(summary_parts)
            
            if language == "hi":
                return ChatResponse(
                        text=f"✅ सभी जानकारी एकत्र हो गई है!\n\n**आपकी पसंद:**\n{summary_text}\n\nअब मैं आधिकारिक वेबसाइट खोलकर आपकी प्रोफ़ाइल से जानकारी भरूंगा।\n\nक्या आप आगे बढ़ना चाहेंगे?",
                    actions=[
                        {"label": "हाँ, आगे बढ़ें", "action": "confirm_proceed", "service_id": "pan_card"},
                        {"label": "रद्द करें", "action": "cancel"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                        text=f"✅ All information collected!\n\n**Your choices:**\n{summary_text}\n\nI'll now open the official website and fill in your information from your profile.\n\nWould you like to proceed?",
                    actions=[
                        {"label": "Yes, proceed", "action": "confirm_proceed", "service_id": "pan_card"},
                        {"label": "Cancel", "action": "cancel"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            # Check physical keywords with flexible matching
            physical_match = False
            # Try exact match first
            if text_clean in lang_physical:
                physical_match = True
            # Then try contains match
            if not physical_match:
                for keyword in lang_physical:
                    if keyword in text_clean:
                        physical_match = True
                        break
            # Also check if text starts with any keyword
            if not physical_match:
                for keyword in lang_physical:
                    if len(keyword) > 2 and text_clean.startswith(keyword):
                        physical_match = True
                        break
            
            if physical_match:
            # #region agent log
            debug_log("chat.py:978", "Physical delivery type detected", {
                "matched": True
            }, "F")
            # #endregion
            
            collected["delivery_type"] = "physical"
                state["collection_step"] = PAN_COLLECTION_STEPS["VERIFY_AADHAAR"]
                
                # Check Aadhaar and proceed to confirmation if exists, otherwise ask
                user_id = state.get("user_id")
                if user_id:
                    try:
                        user_profile = db_manager.get_user_profile(user_id) or {}
                    except:
                        user_profile = {}
                    aadhaar_in_profile = user_profile.get("aadhaarNumber") or user_profile.get("aadhaar_number")
                    if aadhaar_in_profile:
            state["collection_step"] = PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]
                        # Continue to confirmation below
                    else:
                        # Ask for Aadhaar
                        if language == "hi":
                            return ChatResponse(
                                text="**Aadhaar नंबर आवश्यक है**\n\nकृपया अपना 12 अंकों का Aadhaar नंबर दर्ज करें (उदाहरण: 1234 5678 9012):",
                                service_id="pan_card",
                                stage="COLLECTING_DATA",
                                should_speak=True
                            )
                        else:
                            return ChatResponse(
                                text="**Aadhaar Number Required**\n\nPlease enter your 12-digit Aadhaar number (e.g., 1234 5678 9012):",
                                service_id="pan_card",
                                stage="COLLECTING_DATA",
                                should_speak=True
                            )
                
                # If we reach here, Aadhaar exists, show confirmation
                if state["collection_step"] == PAN_COLLECTION_STEPS["CONFIRM_DETAILS"]:
            # Show summary and ask for final confirmation
            applicant_type_text = "Individual" if collected.get("applicant_type") == "individual" else "Company/HUF"
                    application_type_text = "New" if collected.get("application_type") == "new" else "Correction/Update"
            delivery_type_text = "Digital (e-PAN)" if collected.get("delivery_type") == "epan" else "Physical Card"
                    
                    summary_parts = [
                        f"• PAN Card Type: {applicant_type_text}",
                        f"• Application Type: {application_type_text}"
                    ]
                    if collected.get("existing_pan"):
                        summary_parts.append(f"• Existing PAN: {collected.get('existing_pan')}")
                    summary_parts.append(f"• Delivery Type: {delivery_type_text}")
                    summary_text = "\n".join(summary_parts)
            
            if language == "hi":
                return ChatResponse(
                            text=f"✅ सभी जानकारी एकत्र हो गई है!\n\n**आपकी पसंद:**\n{summary_text}\n\nअब मैं आधिकारिक वेबसाइट खोलकर आपकी प्रोफ़ाइल से जानकारी भरूंगा।\n\nक्या आप आगे बढ़ना चाहेंगे?",
                    actions=[
                        {"label": "हाँ, आगे बढ़ें", "action": "confirm_proceed", "service_id": "pan_card"},
                        {"label": "रद्द करें", "action": "cancel"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                            text=f"✅ All information collected!\n\n**Your choices:**\n{summary_text}\n\nI'll now open the official website and fill in your information from your profile.\n\nWould you like to proceed?",
                    actions=[
                        {"label": "Yes, proceed", "action": "confirm_proceed", "service_id": "pan_card"},
                        {"label": "Cancel", "action": "cancel"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            # #region agent log
            debug_log("chat.py:1060", "No delivery type keyword matched", {
                "text": text,
                "text_lower": text_lower,
                "langDigital": lang_digital,
                "langPhysical": lang_physical
            }, "F")
            # #endregion
            
            # Invalid input - polite response
            if language == "hi":
                return ChatResponse(
                    text="कृपया दिए गए विकल्पों में से एक चुनें:\n\n1️⃣ **Digital (e-PAN)** - निःशुल्क, 24-48 घंटे में मिलेगा\n2️⃣ **Physical Card** - ₹93 शुल्क, 15-20 दिन में मिलेगा",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please choose one of the available options:\n\n1️⃣ **Digital (e-PAN)** - Free, delivered in 24-48 hours\n2️⃣ **Physical Card** - ₹93 fee, delivered in 15-20 days",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    # Default fallback - provide helpful context based on current state
    current_step = state.get("collection_step")
    active_service = state.get("active_service")
    
    # If in PAN card data collection, show context-specific message
    if active_service == "pan_card" and state.get("stage") == "COLLECTING_DATA":
        if current_step == PAN_COLLECTION_STEPS["ASK_APPLICANT_TYPE"]:
    if language == "hi":
        return ChatResponse(
                    text="कृपया सही विकल्प चुनें:\n\n1️⃣ **Individual** (व्यक्तिगत)\n2️⃣ **Company/HUF** (कंपनी)",
                    actions=[
                        {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                        {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                    ],
            service_id="pan_card",
            stage="COLLECTING_DATA",
            should_speak=False
        )
    else:
        return ChatResponse(
                    text="Please select a valid option:\n\n1️⃣ **Individual**\n2️⃣ **Company/HUF**",
                    actions=[
                        {"label": "Individual", "action": "select_applicant_type", "value": "individual"},
                        {"label": "Company/HUF", "action": "select_applicant_type", "value": "company"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
        elif current_step == PAN_COLLECTION_STEPS["ASK_DELIVERY_TYPE"]:
            if language == "hi":
                return ChatResponse(
                    text="कृपया दिए गए विकल्पों में से एक चुनें:\n\n1️⃣ **Digital (e-PAN)** - निःशुल्क, 24-48 घंटे में मिलेगा\n2️⃣ **Physical Card** - ₹93 शुल्क, 15-20 दिन में मिलेगा",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
                    service_id="pan_card",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please choose one of the available options:\n\n1️⃣ **Digital (e-PAN)** - Free, delivered in 24-48 hours\n2️⃣ **Physical Card** - ₹93 fee, delivered in 15-20 days",
                    actions=[
                        {"label": "Digital (e-PAN)", "action": "select_delivery_type", "value": "epan"},
                        {"label": "Physical Card", "action": "select_delivery_type", "value": "physical"}
                    ],
            service_id="pan_card",
            stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    # Generic fallback
    if language == "hi":
        return ChatResponse(
            text="कृपया दिए गए विकल्पों में से चुनें।",
            service_id=active_service,
            stage=state.get("stage"),
            should_speak=False
        )
    else:
        return ChatResponse(
            text="Please select from the given options.",
            service_id=active_service,
            stage=state.get("stage"),
            should_speak=False
        )

async def handle_brc_data_collection(text: str, text_lower: str, language: str, state: Dict[str, Any]) -> ChatResponse:
    """Handle multi-step BRC data collection"""
    step = state.get("collection_step")
    collected = state.get("collected_data", {})
    
    # Get user profile to check for existing data
    try:
        if use_database:
            user_profile = db_manager.get_user_profile(state.get("user_id", "")) or {}
        else:
            from profile import profiles_db
            user_profile = profiles_db.get(state.get("user_id", ""), {})
    except:
        user_profile = {}
    
    # Merge existing profile data
    if not collected.get("applicant_name") and user_profile.get("full_name"):
        collected["applicant_name"] = user_profile.get("full_name")
    if not collected.get("father_name") and user_profile.get("father_name"):
        collected["father_name"] = user_profile.get("father_name")
    if not collected.get("mother_name") and user_profile.get("mother_name"):
        collected["mother_name"] = user_profile.get("mother_name")
    if not collected.get("date_of_birth") and user_profile.get("date_of_birth"):
        collected["date_of_birth"] = user_profile.get("date_of_birth")
    if not collected.get("gender") and user_profile.get("gender"):
        collected["gender"] = user_profile.get("gender")
    if not collected.get("mobile_number") and user_profile.get("mobile_number"):
        collected["mobile_number"] = user_profile.get("mobile_number")
    if not collected.get("aadhaar_number") and user_profile.get("aadhaar_number"):
        collected["aadhaar_number"] = user_profile.get("aadhaar_number")
    if not collected.get("permanent_address") and user_profile.get("permanent_address"):
        collected["permanent_address"] = user_profile.get("permanent_address")
    if not collected.get("district") and user_profile.get("district"):
        collected["district"] = user_profile.get("district")
    if not collected.get("pin_code") and user_profile.get("pin_code"):
        collected["pin_code"] = user_profile.get("pin_code")
    
    state["collected_data"] = collected
    
    # Determine next step
    if not step:
        if not collected.get("applicant_name"):
            step = BRC_COLLECTION_STEPS["ASK_APPLICANT_NAME"]
        elif not collected.get("father_name"):
            step = BRC_COLLECTION_STEPS["ASK_FATHER_NAME"]
        elif not collected.get("mother_name"):
            step = BRC_COLLECTION_STEPS["ASK_MOTHER_NAME"]
        elif not collected.get("date_of_birth"):
            step = BRC_COLLECTION_STEPS["ASK_DOB"]
        elif not collected.get("gender"):
            step = BRC_COLLECTION_STEPS["ASK_GENDER"]
        elif not collected.get("mobile_number"):
            step = BRC_COLLECTION_STEPS["ASK_MOBILE"]
        elif not collected.get("aadhaar_number"):
            step = BRC_COLLECTION_STEPS["ASK_AADHAAR"]
        elif not collected.get("permanent_address"):
            step = BRC_COLLECTION_STEPS["ASK_ADDRESS"]
        elif not collected.get("district"):
            step = BRC_COLLECTION_STEPS["ASK_DISTRICT"]
        elif not collected.get("block_circle"):
            step = BRC_COLLECTION_STEPS["ASK_BLOCK"]
        elif not collected.get("panchayat_ward"):
            step = BRC_COLLECTION_STEPS["ASK_PANCHAYAT"]
        elif not collected.get("post_office"):
            step = BRC_COLLECTION_STEPS["ASK_POST_OFFICE"]
        elif not collected.get("pin_code"):
            step = BRC_COLLECTION_STEPS["ASK_PIN_CODE"]
        elif not collected.get("purpose"):
            step = BRC_COLLECTION_STEPS["ASK_PURPOSE"]
        else:
            step = BRC_COLLECTION_STEPS["CONFIRM_DETAILS"]
    
    # Handle each step
    if step == BRC_COLLECTION_STEPS["ASK_APPLICANT_NAME"]:
        if text_lower and text_lower not in ["skip", "next"]:
            collected["applicant_name"] = text
            state["collection_step"] = BRC_COLLECTION_STEPS["ASK_FATHER_NAME"]
            if language == "hi":
                return ChatResponse(
                    text="✅ नाम दर्ज किया गया।\n\n**अगला सवाल:** आपके पिता का नाम क्या है?",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ Name recorded.\n\n**Next question:** What is your father's name?",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            if language == "hi":
                return ChatResponse(
                    text="कृपया अपना पूरा नाम दर्ज करें (जैसा आधार कार्ड पर है)।",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please enter your full name (as per Aadhaar card).",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    elif step == BRC_COLLECTION_STEPS["ASK_FATHER_NAME"]:
        if text_lower and text_lower not in ["skip", "next"]:
            collected["father_name"] = text
            state["collection_step"] = BRC_COLLECTION_STEPS["ASK_MOTHER_NAME"]
            if language == "hi":
                return ChatResponse(
                    text="✅ पिता का नाम दर्ज किया गया।\n\n**अगला सवाल:** आपकी माता का नाम क्या है?",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ Father's name recorded.\n\n**Next question:** What is your mother's name?",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            if language == "hi":
                return ChatResponse(
                    text="कृपया अपने पिता का पूरा नाम दर्ज करें।",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please enter your father's full name.",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    elif step == BRC_COLLECTION_STEPS["ASK_MOTHER_NAME"]:
        if text_lower and text_lower not in ["skip", "next"]:
            collected["mother_name"] = text
            state["collection_step"] = BRC_COLLECTION_STEPS["ASK_DOB"]
            if language == "hi":
                return ChatResponse(
                    text="✅ माता का नाम दर्ज किया गया।\n\n**अगला सवाल:** आपकी जन्म तिथि क्या है? (DD-MM-YYYY format में)",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ Mother's name recorded.\n\n**Next question:** What is your date of birth? (in DD-MM-YYYY format)",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            if language == "hi":
                return ChatResponse(
                    text="कृपया अपनी माता का पूरा नाम दर्ज करें।",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please enter your mother's full name.",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    elif step == BRC_COLLECTION_STEPS["ASK_DOB"]:
        if text_lower and text_lower not in ["skip", "next"]:
            # Validate date format
            import re
            if re.match(r'^\d{2}-\d{2}-\d{4}$', text):
                collected["date_of_birth"] = text
                state["collection_step"] = BRC_COLLECTION_STEPS["ASK_GENDER"]
                if language == "hi":
                    return ChatResponse(
                        text="✅ जन्म तिथि दर्ज की गई।\n\n**अगला सवाल:** आपका लिंग क्या है?",
                        actions=[
                            {"label": "पुरुष (Male)", "action": "select_gender", "value": "male"},
                            {"label": "महिला (Female)", "action": "select_gender", "value": "female"},
                            {"label": "अन्य (Other)", "action": "select_gender", "value": "other"}
                        ],
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
                else:
                    return ChatResponse(
                        text="✅ Date of birth recorded.\n\n**Next question:** What is your gender?",
                        actions=[
                            {"label": "Male", "action": "select_gender", "value": "male"},
                            {"label": "Female", "action": "select_gender", "value": "female"},
                            {"label": "Other", "action": "select_gender", "value": "other"}
                        ],
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
            else:
                if language == "hi":
                    return ChatResponse(
                        text="कृपया सही format में जन्म तिथि दर्ज करें (DD-MM-YYYY), जैसे: 15-01-1990",
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=False
                    )
                else:
                    return ChatResponse(
                        text="Please enter date of birth in correct format (DD-MM-YYYY), e.g., 15-01-1990",
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=False
                    )
        else:
            if language == "hi":
                return ChatResponse(
                    text="कृपया अपनी जन्म तिथि दर्ज करें (DD-MM-YYYY format में)।",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please enter your date of birth (in DD-MM-YYYY format).",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    elif step == BRC_COLLECTION_STEPS["ASK_GENDER"]:
        gender_map = {"male": "male", "female": "female", "other": "other", "1": "male", "2": "female", "3": "other"}
        if text_lower in gender_map or "select_gender" in text_lower:
            gender_value = gender_map.get(text_lower, "male")
            if "select_gender" in text_lower:
                # Extract value from action
                import json
                try:
                    if "value" in text_lower:
                        gender_value = text_lower.split("value")[1].strip().strip("=").strip('"').strip("'")
                except:
                    pass
            collected["gender"] = gender_value
            state["collection_step"] = BRC_COLLECTION_STEPS["ASK_MOBILE"]
            if language == "hi":
                return ChatResponse(
                    text="✅ लिंग दर्ज किया गया।\n\n**अगला सवाल:** आपका मोबाइल नंबर क्या है? (10 अंकों का)",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="✅ Gender recorded.\n\n**Next question:** What is your mobile number? (10 digits)",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=True
                )
        else:
            if language == "hi":
                return ChatResponse(
                    text="कृपया दिए गए विकल्पों में से चुनें:\n\n1️⃣ पुरुष (Male)\n2️⃣ महिला (Female)\n3️⃣ अन्य (Other)",
                    actions=[
                        {"label": "पुरुष (Male)", "action": "select_gender", "value": "male"},
                        {"label": "महिला (Female)", "action": "select_gender", "value": "female"},
                        {"label": "अन्य (Other)", "action": "select_gender", "value": "other"}
                    ],
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please select from the given options:\n\n1️⃣ Male\n2️⃣ Female\n3️⃣ Other",
                    actions=[
                        {"label": "Male", "action": "select_gender", "value": "male"},
                        {"label": "Female", "action": "select_gender", "value": "female"},
                        {"label": "Other", "action": "select_gender", "value": "other"}
                    ],
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    # Continue with remaining steps (mobile, aadhaar, address, district, block, panchayat, post office, pin, purpose)
    # For brevity, I'll add a simplified version that collects all remaining fields
    elif step in [BRC_COLLECTION_STEPS["ASK_MOBILE"], BRC_COLLECTION_STEPS["ASK_AADHAAR"], 
                   BRC_COLLECTION_STEPS["ASK_ADDRESS"], BRC_COLLECTION_STEPS["ASK_DISTRICT"],
                   BRC_COLLECTION_STEPS["ASK_BLOCK"], BRC_COLLECTION_STEPS["ASK_PANCHAYAT"],
                   BRC_COLLECTION_STEPS["ASK_POST_OFFICE"], BRC_COLLECTION_STEPS["ASK_PIN_CODE"],
                   BRC_COLLECTION_STEPS["ASK_PURPOSE"]]:
        # Simplified: collect all remaining fields in sequence
        field_map = {
            BRC_COLLECTION_STEPS["ASK_MOBILE"]: ("mobile_number", "ASK_AADHAAR", "मोबाइल नंबर", "mobile number"),
            BRC_COLLECTION_STEPS["ASK_AADHAAR"]: ("aadhaar_number", "ASK_ADDRESS", "आधार नंबर", "Aadhaar number"),
            BRC_COLLECTION_STEPS["ASK_ADDRESS"]: ("permanent_address", "ASK_DISTRICT", "पता", "permanent address"),
            BRC_COLLECTION_STEPS["ASK_DISTRICT"]: ("district", "ASK_BLOCK", "जिला", "district"),
            BRC_COLLECTION_STEPS["ASK_BLOCK"]: ("block_circle", "ASK_PANCHAYAT", "ब्लॉक/सर्कल", "block/circle"),
            BRC_COLLECTION_STEPS["ASK_PANCHAYAT"]: ("panchayat_ward", "ASK_POST_OFFICE", "पंचायत/वार्ड", "panchayat/ward"),
            BRC_COLLECTION_STEPS["ASK_POST_OFFICE"]: ("post_office", "ASK_PIN_CODE", "डाकघर", "post office"),
            BRC_COLLECTION_STEPS["ASK_PIN_CODE"]: ("pin_code", "ASK_PURPOSE", "पिन कोड", "PIN code"),
            BRC_COLLECTION_STEPS["ASK_PURPOSE"]: ("purpose", "CONFIRM_DETAILS", "उद्देश्य", "purpose")
        }
        
        field_name, next_step_key, hi_label, en_label = field_map.get(step, (None, None, None, None))
        
        if field_name and text_lower and text_lower not in ["skip", "next"]:
            collected[field_name] = text
            state["collection_step"] = BRC_COLLECTION_STEPS[next_step_key] if next_step_key else BRC_COLLECTION_STEPS["CONFIRM_DETAILS"]
            
            if next_step_key == "CONFIRM_DETAILS":
                # Show confirmation summary
                summary_hi = f"✅ सभी जानकारी एकत्र की गई।\n\n**संग्रहीत जानकारी:**\n"
                summary_en = f"✅ All information collected.\n\n**Collected Information:**\n"
                
                for key, value in collected.items():
                    summary_hi += f"- {key}: {value}\n"
                    summary_en += f"- {key}: {value}\n"
                
                summary_hi += "\nक्या आप आगे बढ़ना चाहते हैं?"
                summary_en += "\nWould you like to proceed?"
                
                if language == "hi":
                    return ChatResponse(
                        text=summary_hi,
                        actions=[
                            {"label": "हाँ, आगे बढ़ें", "action": "confirm_proceed", "service_id": "bihar_residence_certificate"},
                            {"label": "संशोधन करें", "action": "edit_details"}
                        ],
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
                else:
                    return ChatResponse(
                        text=summary_en,
                        actions=[
                            {"label": "Yes, proceed", "action": "confirm_proceed", "service_id": "bihar_residence_certificate"},
                            {"label": "Edit details", "action": "edit_details"}
                        ],
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
            else:
                next_field_map = {
                    "ASK_AADHAAR": ("आधार नंबर", "Aadhaar number"),
                    "ASK_ADDRESS": ("पता", "permanent address"),
                    "ASK_DISTRICT": ("जिला", "district"),
                    "ASK_BLOCK": ("ब्लॉक/सर्कल", "block/circle"),
                    "ASK_PANCHAYAT": ("पंचायत/वार्ड", "panchayat/ward"),
                    "ASK_POST_OFFICE": ("डाकघर", "post office"),
                    "ASK_PIN_CODE": ("पिन कोड", "PIN code"),
                    "ASK_PURPOSE": ("उद्देश्य", "purpose")
                }
                next_hi, next_en = next_field_map.get(next_step_key, ("अगला फ़ील्ड", "next field"))
                
                if language == "hi":
                    return ChatResponse(
                        text=f"✅ {hi_label} दर्ज किया गया।\n\n**अगला सवाल:** आपका {next_hi} क्या है?",
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
                else:
                    return ChatResponse(
                        text=f"✅ {en_label} recorded.\n\n**Next question:** What is your {next_en}?",
                        service_id="bihar_residence_certificate",
                        stage="COLLECTING_DATA",
                        should_speak=True
                    )
        else:
            if language == "hi":
                return ChatResponse(
                    text=f"कृपया अपना {hi_label} दर्ज करें।",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text=f"Please enter your {en_label}.",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    elif step == BRC_COLLECTION_STEPS["CONFIRM_DETAILS"]:
        confirmation_keywords = {
            "en": ["yes", "proceed", "continue", "ok", "sure", "go ahead", "start"],
            "hi": ["हाँ", "आगे", "जारी", "ठीक", "बिल्कुल", "शुरू करें"]
        }
        lang_confirm = confirmation_keywords.get(language, confirmation_keywords["en"])
        
        if any(keyword in text_lower for keyword in lang_confirm):
            # Start automation
            state["collection_step"] = BRC_COLLECTION_STEPS["READY_TO_SUBMIT"]
            state["stage"] = "EXECUTION"
            
            service_config = collected.copy()
            
            if language == "hi":
                return ChatResponse(
                    text="मैं आधिकारिक RTPS Bihar वेबसाइट खोल रहा हूं और आवेदन शुरू कर रहा हूं।",
                    service_id="bihar_residence_certificate",
                    service_config=service_config,
                    start_automation=True,
                    stage="EXECUTION",
                    should_speak=True
                )
            else:
                return ChatResponse(
                    text="I am opening the official RTPS Bihar website and starting the application.",
                    service_id="bihar_residence_certificate",
                    service_config=service_config,
                    start_automation=True,
                    stage="EXECUTION",
                    should_speak=True
                )
        else:
            if language == "hi":
                return ChatResponse(
                    text="कृपया पुष्टि करें कि आप आगे बढ़ना चाहते हैं।",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
            else:
                return ChatResponse(
                    text="Please confirm that you want to proceed.",
                    service_id="bihar_residence_certificate",
                    stage="COLLECTING_DATA",
                    should_speak=False
                )
    
    # Default fallback
    if language == "hi":
        return ChatResponse(
            text="कृपया दिए गए विकल्पों में से चुनें।",
            service_id="bihar_residence_certificate",
            stage="COLLECTING_DATA",
            should_speak=False
        )
    else:
        return ChatResponse(
            text="Please select from the given options.",
            service_id="bihar_residence_certificate",
            stage="COLLECTING_DATA",
            should_speak=False
        )

