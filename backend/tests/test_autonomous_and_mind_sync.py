"""
Tests for Autonomous Actions (PAN Card, Passport, Ticket) and Mind Markdown Synchronization
"""

import pytest
import os
import sys
import json
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from services.profile_mind_service import profile_mind_service
from services.autonomous_actions_service import autonomous_actions_service
from routes.chat import process_user_message


def test_autonomous_pan_card_execution():
    res = autonomous_actions_service.execute_pan_card()
    assert res["success"] is True
    assert res["action_id"] == "pan_card"
    assert "Form 49A" in res["data"]["form_type"]
    assert "Asif Aslam" in res["data"]["applicant_details"]["full_name"]
    assert len(res["data"]["attached_assets"]) >= 2
    assert "Done Boss" in res["voice_vocalization"]


def test_autonomous_passport_execution():
    res = autonomous_actions_service.execute_passport()
    assert res["success"] is True
    assert res["action_id"] == "passport"
    assert "Fresh Passport" in res["data"]["service_type"]
    assert "413 x 531 px" in str(res["data"]["attached_assets"])
    assert "RPO Patna" in res["data"]["rpo_jurisdiction"]


def test_autonomous_ticket_execution():
    res = autonomous_actions_service.execute_ticket_booking({"from_city": "Patna", "to_city": "Delhi"})
    assert res["success"] is True
    assert res["action_id"] == "ticket_booking"
    assert "Patna ➔ Delhi" in res["data"]["route"]
    assert "Asif Aslam" in res["data"]["primary_passenger"]["name"]
    assert "Lower" in res["data"]["primary_passenger"]["berth_preference"]


def test_mind_markdown_parser_and_sync():
    custom_md = """# Personal Profile
**Identity**: Asif Aslam (Sonu Sarkar)
**Role**: Founder & Chief AI Systems Architect
**Location**: Motihari, Bihar

## Personal Life
Automating workflows, high-agency building, late-night deep work sessions.

## Technical Knowledge & Skills
- Python 3.12 (Expert)
- React 18 & TailwindCSS
- Autonomous Multi-Agent Orchestration

## Business & Ventures
- **KYRON AGI**: Autonomous Agentic OS
- **BookMyGaadi**: Regional Taxi Fleet Platform
"""
    success = profile_mind_service.update_mind_markdown(custom_md)
    assert success is True

    profile = profile_mind_service.get_profile()
    assert profile["identity"]["full_name"] == "Asif Aslam"
    assert profile["identity"]["alias"] == "Sonu Sarkar"
    assert "Python 3.12 (Expert)" in profile["technical_knowledge_and_skills"]["programming_languages"]


@pytest.mark.asyncio
async def test_chat_autonomous_pan_trigger():
    chat_resp = await process_user_message(
        text="mera pan card bana do please",
        language="hi",
        user_id="test_user_auto"
    )
    assert "PAN Card" in chat_resp.text or "Form 49A" in chat_resp.text
    assert chat_resp.actions is not None
    assert chat_resp.actions[0]["action_id"] == "pan_card"


@pytest.mark.asyncio
async def test_chat_phonetic_stt_pan_triggers():
    # Verify common speech-to-text slips: "panka", "panka bana sakte ho", "pan cake"
    slips = [
        "ek Hi Mere liye Panka Bana sakte Ho",
        "Main bol Rahoon Panka Bana sakte Ho Mere liye",
        "panka bana do",
        "pan cake bana sakte ho"
    ]
    for phrase in slips:
        chat_resp = await process_user_message(
            text=phrase,
            language="hi",
            user_id="test_user_phonetic"
        )
        assert chat_resp.actions is not None, f"Failed on: {phrase}"
        assert chat_resp.actions[0]["action_id"] == "pan_card", f"Failed action_id on: {phrase}"
        assert "Form 49A" in chat_resp.text or "PAN Card" in chat_resp.text


@pytest.mark.asyncio
async def test_interactive_3_stage_pan_workflow():
    user_id = "test_user_interactive_3_stage"
    
    # 1. Capability check (User asks "tum mere liye pan card bana sakte ho")
    resp1 = await process_user_message("tum Mere liye pan card Bana sakte Ho", "hi", user_id)
    assert "already verified PAN Card maujood hai" in resp1.text or "BXXXX8849F" in resp1.text
    assert "ASIF ASLAM" in resp1.text

    # 2. User confirms ("theek hai apply karo")
    resp2 = await process_user_message("theek hai apply karo", "hi", user_id)
    assert "saari details aur documents completely verified hain" in resp2.text.lower()

    # 3. User approves live automation ("start karo")
    resp3 = await process_user_message("start karo", "hi", user_id)
    assert "Protean" in resp3.text or "cursor" in resp3.text

    # 4. Error troubleshooting check
    resp_err = await process_user_message("eah error aa rha pan card bananee mee", "hi", "test_user_err")
    assert "Safari Can't Find the Server" in resp_err.text or "Protean" in resp_err.text

    # 5. Popup & full cursor control troubleshooting check
    resp_pop = await process_user_message(
        "bhai open ho rha webiste bt pop open kr de rha full cursor control nhi kr paa rha isko fix kro",
        "hi",
        "test_user_pop"
    )
    assert "Popup Kyun Aaya Tha" in resp_pop.text or "Continue" in resp_pop.text
    assert "Full Cursor & Keyboard" in resp_pop.text or "onlineservices.proteantech.in" in resp_pop.text

    # 6. Application Type & CAPTCHA customization check
    resp_type = await process_user_message(
        "application type user se pucho kis user ko kis type ka pan banwan hai jo khud se desgine nhi lo sath hi captore fill nhi kr paoge kya isko bhi fill kro aur age badhoo",
        "hi",
        "test_user_type"
    )
    assert "Application Type Selection" in resp_type.text or "Form 49A" in resp_type.text
    assert "CAPTCHA" in resp_type.text or "reCAPTCHA" in resp_type.text

    # 7. Multi-turn Name Change & Session Context Memory Persistence
    sess_id = "test_sess_memory_flow"
    r1 = await process_user_message("Maine Bhola Mere pan card mein naam change Karna Hai", "hi", "test_user_mem", session_id=sess_id)
    assert "Name Change" in r1.text or "CR" in r1.text

    # Turn 2: User says "Okay go ahead carry on" -> must NOT lose PAN name change context!
    r2 = await process_user_message("Okay go ahead carry on", "hi", "test_user_mem", session_id=sess_id)
    assert "CR" in r2.text or "Protean" in r2.text or "Name Change" in r2.text
    assert "BookMyGaadi" not in r2.text

    # Turn 3: User says "strat kroo name change krnii h" (with typo 'strat')
    r3 = await process_user_message("strat kroo name change krnii h", "hi", "test_user_mem", session_id=sess_id)
    assert "CR" in r3.text or "Name Change" in r3.text or "Protean" in r3.text

    # Turn 4: User says "PAN Card mee"
    r4 = await process_user_message("PAN Card mee", "hi", "test_user_mem", session_id=sess_id)
    assert "Name Change" in r4.text or "CR" in r4.text

    # Turn 5: Memory complaint check
    r5 = await process_user_message("piche ka context yaad nhi rakh paa rha session wise start kro", "hi", "test_user_mem", session_id=sess_id)
    assert "persistent memory" in r5.text.lower() or "name change" in r5.text.lower()


@pytest.mark.asyncio
async def test_chat_autonomous_passport_trigger():
    chat_resp = await process_user_message(
        text="passport bana do",
        language="hi",
        user_id="test_user_auto"
    )
    assert "Passport" in chat_resp.text
    assert chat_resp.actions is not None
    assert chat_resp.actions[0]["action_id"] == "passport"


@pytest.mark.asyncio
async def test_chat_autonomous_ticket_trigger():
    chat_resp = await process_user_message(
        text="ticket kato",
        language="hi",
        user_id="test_user_auto"
    )
    assert "ticket" in chat_resp.text.lower()
    assert chat_resp.actions is not None
    assert chat_resp.actions[0]["action_id"] == "ticket_booking"
