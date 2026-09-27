import pytest
import time
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.system_control_agent import SystemControlAgent, AmbiguousContactError
from services.approval_queue import approval_queue
from routes.system_control import execute_system_command, ExecuteSystemCommandRequest

@pytest.mark.asyncio
async def test_ambiguous_contact_error(monkeypatch):
    """
    Test that ambiguous contacts ('Sonu' matching multiple) throws AmbiguousContactError
    instead of pushing anything to the approval queue.
    """
    from services.system_control_agent import system_control_agent
    
    # Mocking pywinauto or search_and_open_contact directly
    def mock_search_contact(contact, app_title="WhatsApp"):
        raise AmbiguousContactError("SAFETY ABORT: Multiple contacts matched")

    monkeypatch.setattr(system_control_agent, "search_and_open_contact", mock_search_contact)
    monkeypatch.setattr(system_control_agent, "open_app", lambda x: {"success": True})
    monkeypatch.setattr(system_control_agent, "find_and_focus_window", lambda title, timeout: True)

    req = ExecuteSystemCommandRequest(command="WhatsApp khol aur Sonu ko 'meeting at 5' bhej")
    res = await execute_system_command(req)
    
    assert res["success"] is False
    assert res["error_type"] == "AMBIGUOUS_CONTACT_ERROR"
    assert "SAFETY ABORT: Multiple contacts matched" in res["message"]
        
    # Ensure no action was registered in the central queue
    for pending in approval_queue.get_all_pending():
        assert pending["payload"].get("target_contact") != "Sonu"

@pytest.mark.asyncio
async def test_whatsapp_message_flow(monkeypatch):
    """
    Test WhatsApp message flow:
    1. Dry-run (pause) registers in central queue.
    2. Execution triggers on explicit confirm_and_execute.
    """
    from services.system_control_agent import system_control_agent
    from routes.system_control import confirm_system_action, ConfirmActionRequest
    
    # Mock OS interactions
    monkeypatch.setattr(system_control_agent, "open_app", lambda x: {"success": True})
    monkeypatch.setattr(system_control_agent, "find_and_focus_window", lambda title, timeout: True)
    monkeypatch.setattr(system_control_agent, "search_and_open_contact", lambda c, app_title="WhatsApp": None)
    monkeypatch.setattr(system_control_agent, "type_text", lambda text, delay, verify_window: None)
    
    # Track keys sent
    keys_sent = []
    monkeypatch.setattr(system_control_agent, "send_keys", lambda keys: keys_sent.append(keys))
    
    # Clean queue
    approval_queue.pending_actions.clear()
    
    # Mock LLM Client to force deterministic fallback parsing
    from services.llm_client import LLMClient
    async def mock_acomplete(*args, **kwargs):
        return {"success": False}
    monkeypatch.setattr(LLMClient, "acomplete", mock_acomplete)

    # Dry-run execution
    req = ExecuteSystemCommandRequest(command="WhatsApp khol aur papa ko 'I am coming home' bhej")
    res = await execute_system_command(req)
    
    assert res["requires_confirmation"] is True
    action_id = res["pending_action"]["action_id"]
    
    # Verify it is in the queue
    queued_action = approval_queue.get_action(action_id)
    assert queued_action is not None
    assert queued_action["agent_type"] == "SYSTEM"
    assert queued_action["payload"]["content"] == "I am coming home"
    
    # Confirm
    confirm_req = ConfirmActionRequest(action_id=action_id, confirmed=True)
    confirm_res = confirm_system_action(confirm_req)
    assert confirm_res["status"] == "executed"
    
    # Since it's confirmed, it should have sent 'enter'
    assert keys_sent == ["enter"]
    
    # Action should be removed from pending queue
    assert approval_queue.get_action(action_id) is None

