"""
KYRON Profile, Mind, Document Vault & Business Routes
Exposes API endpoints for Asif Aslam's Master Profile, Custom KYRON_MIND.md,
Document Vault & Auto-Crop/Fit Form-Filler, Business Suite, and Call Support Workstation.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os

from services.profile_mind_service import profile_mind_service
from services.document_vault_service import document_vault_service
from services.business_automation_service import business_automation_service
from services.call_support_service import call_support_service
from services.autonomous_actions_service import autonomous_actions_service

router = APIRouter(prefix="/api/kyron", tags=["kyron-profile-mind"])


# =========================================================================
# 1. PROFILE & MIND (ASIF ASLAM / SONU SARKAR)
# =========================================================================

@router.get("/profile/mind")
def get_profile_mind():
    """Retrieve full master profile and active status."""
    return {
        "success": True,
        "profile": profile_mind_service.get_profile(),
        "verified_identity": "Asif Aslam (Sonu Sarkar)"
    }


@router.put("/profile/mind")
def update_profile_mind(payload: Dict[str, Any] = Body(...)):
    """Update profile data."""
    updated = profile_mind_service.update_profile(payload)
    return {
        "success": True,
        "message": "Profile updated successfully and synchronized with Kyron Mind",
        "profile": updated
    }


@router.get("/profile/mind/readme")
def get_mind_readme():
    """Fetch current KYRON_MIND.md markdown document."""
    markdown_content = profile_mind_service.get_mind_markdown()
    return {
        "success": True,
        "markdown": markdown_content
    }


@router.post("/profile/mind/readme")
def save_mind_readme(payload: Dict[str, Any] = Body(...)):
    """Save custom KYRON_MIND.md submitted or uploaded by user."""
    markdown_text = payload.get("markdown", "")
    if not markdown_text.strip():
        raise HTTPException(status_code=400, detail="Markdown content cannot be empty.")
    success = profile_mind_service.update_mind_markdown(markdown_text)
    return {
        "success": success,
        "message": "KYRON_MIND.md saved and active in Kyron Cognitive Memory!"
    }


@router.post("/profile/check")
def check_profile_directive(payload: Dict[str, Any] = Body(...)):
    """Test the profile-first verification engine with any query."""
    query = payload.get("query", "")
    result = profile_mind_service.check_profile_for_query(query)
    return {
        "success": True,
        "result": result
    }


# =========================================================================
# 2. DOCUMENT VAULT & FORM-FILLER RESIZER
# =========================================================================

@router.get("/vault/documents")
def get_vault_documents():
    """Retrieve all stored documents (Aadhaar, PAN, Photo, Signature, Bank) and autofill presets."""
    return {
        "success": True,
        "vault": document_vault_service.get_vault_data()
    }


class FormatDocRequest(BaseModel):
    doc_type: str = "photo"
    target_width: int = 200
    target_height: int = 230
    max_size_kb: int = 50
    output_format: str = "jpeg"


@router.post("/vault/format-doc")
def format_document_for_form(req: FormatDocRequest):
    """
    Crops, resizes, fits aspect-ratio, and compresses a vault document
    to exact website form specifications using native macOS tools.
    """
    res = document_vault_service.process_document_for_form(
        doc_type=req.doc_type,
        target_width=req.target_width,
        target_height=req.target_height,
        max_size_kb=req.max_size_kb,
        output_format=req.output_format
    )
    return res


@router.post("/vault/update-doc")
def update_vault_doc_meta(payload: Dict[str, Any] = Body(...)):
    """Update metadata for Aadhaar, PAN, bank details, etc."""
    doc_key = payload.get("doc_key")
    updates = payload.get("updates", {})
    if not doc_key:
        raise HTTPException(status_code=400, detail="Missing doc_key")
    res = document_vault_service.update_document_meta(doc_key, updates)
    return {
        "success": True,
        "doc": res
    }


@router.post("/vault/update-autofill")
def update_autofill_preset(payload: Dict[str, Any] = Body(...)):
    """Update autofill fields."""
    res = document_vault_service.update_autofill_presets(payload)
    return {
        "success": True,
        "autofill": res
    }


# =========================================================================
# 3. BUSINESS AUTOMATION (LEADS, SUPPORT, BRANDING)
# =========================================================================

@router.get("/business/summary")
def get_business_summary():
    """Returns business overview: ventures, active client leads, tickets, promotions."""
    return {
        "success": True,
        "business": business_automation_service.get_summary()
    }


class CampaignRequest(BaseModel):
    venture_name: str = "KYRON AGI"
    topic: str = "Tahoe Edition 2.0 Launch"
    platform: str = "LinkedIn"


@router.post("/business/generate-campaign")
def generate_branding_campaign(req: CampaignRequest):
    """Generates promotional / branding copy tailored to Asif Aslam's ventures."""
    res = business_automation_service.generate_branding_campaign(
        venture_name=req.venture_name,
        topic=req.topic,
        platform=req.platform
    )
    return res


class ClientReplyRequest(BaseModel):
    client_name: str
    inquiry: str
    service_type: str = "KYRON Enterprise"


@router.post("/business/reply-inquiry")
def generate_client_reply(req: ClientReplyRequest):
    """Generates professional response proposal for inbound client inquiry."""
    res = business_automation_service.generate_client_reply(
        client_name=req.client_name,
        inquiry=req.inquiry,
        service_type=req.service_type
    )
    return res


# =========================================================================
# 4. CALL SUPPORT TELEPHONY WORKSTATION
# =========================================================================

@router.get("/calls/history")
def get_call_support_history():
    """Returns active call and historical call logs."""
    return {
        "success": True,
        "data": call_support_service.get_history()
    }


@router.get("/calls/setup")
def get_call_setup():
    """Returns calling setup, user number, carrier gateway, and speed dial contacts."""
    return {
        "success": True,
        "setup": call_support_service.get_setup()
    }


class UpdateCallSetupRequest(BaseModel):
    setup: Dict[str, Any]


@router.post("/calls/setup")
def update_call_setup(req: UpdateCallSetupRequest):
    """Updates user phone number and calling preferences."""
    return call_support_service.update_setup(req.setup)


class DialRealtimeCallRequest(BaseModel):
    target_phone: str
    caller_name: Optional[str] = None
    purpose: Optional[str] = None
    trigger_macos_call: bool = True


@router.post("/calls/dial")
def dial_realtime_call(req: DialRealtimeCallRequest):
    """Initiates a real-time outbound call to any phone number."""
    if not req.target_phone.strip():
        raise HTTPException(status_code=400, detail="Target phone number is required")
    return call_support_service.dial_realtime_call(
        target_phone=req.target_phone,
        caller_name=req.caller_name,
        purpose=req.purpose,
        trigger_macos_call=req.trigger_macos_call
    )


class SimulateCallRequest(BaseModel):
    caller_type: str = "ride_booking"  # "ride_booking" | "enterprise_kyron"


@router.post("/calls/simulate")
def simulate_inbound_call(req: SimulateCallRequest):
    """Simulates an incoming customer or client support call."""
    res = call_support_service.simulate_inbound_call(caller_type=req.caller_type)
    return res


@router.post("/calls/end")
def end_active_call():
    """Concludes active call and commits to CRM logs."""
    res = call_support_service.end_active_call()
    return res


# =========================================================================
# 5. AUTONOMOUS SUPER-ACTIONS (PAN, PASSPORT, TICKETS, FORM FILLER)
# =========================================================================

@router.get("/actions/catalog")
def get_autonomous_actions_catalog():
    """Returns the list of autonomous super-power actions."""
    return {
        "success": True,
        "catalog": autonomous_actions_service.get_actions_catalog()
    }


class ExecuteActionRequest(BaseModel):
    action_type: str  # "pan_card" | "passport" | "ticket_booking" | "universal_form"
    params: Optional[Dict[str, Any]] = None


@router.post("/actions/execute")
def execute_autonomous_action(req: ExecuteActionRequest):
    """
    Executes an autonomous action using master profile & document vault.
    """
    atype = req.action_type.lower().strip()
    if atype in ["pan_status", "pan_check", "pan_status_check"]:
        return autonomous_actions_service.check_existing_pan_status()
    elif atype in ["pan_requirements", "pan_requirements_check", "pan_verify"]:
        return autonomous_actions_service.check_pan_requirements_and_readiness()
    elif atype in ["pan_live", "pan_browser", "pan_live_automation", "start_pan"]:
        return autonomous_actions_service.start_live_pan_browser_automation()
    elif atype in ["pan_card", "pan", "form49a"]:
        return autonomous_actions_service.execute_pan_card(req.params)
    elif atype in ["passport", "passport_seva", "fresh_passport"]:
        return autonomous_actions_service.execute_passport(req.params)
    elif atype in ["ticket_booking", "ticket", "train_ticket", "flight_ticket"]:
        return autonomous_actions_service.execute_ticket_booking(req.params)
    elif atype in ["universal_form", "form_filler"]:
        return autonomous_actions_service.execute_universal_form(req.params)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action type: {req.action_type}")
