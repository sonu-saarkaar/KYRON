import pytest
import os
import sys

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.dograh_voice_engine import dograh_voice_engine
from services.session_manager import session_manager
from services.mac_system_control import mac_system_control


def test_battery_and_system_status_telemetry():
    """Verify authentic macOS battery health, cycles, volume and apps telemetry."""
    status = mac_system_control.get_system_status()
    assert status["success"] is True
    assert status["platform"] == "macOS"
    assert "battery" in status
    assert "battery_health" in status
    assert "cycle_count" in status
    assert "frontmost_app" in status
    assert "running_apps" in status
    assert isinstance(status["running_apps"], list)


def test_voice_directive_persists_to_session():
    """Verify that every spoken directive and response is saved into session_manager."""
    test_session_id = "sess_test_voice_mirror"

    # 1. Battery Health query
    res_batt = dograh_voice_engine.process_voice_directive(
        "battery health check karo",
        speak_locally=False,
        session_id=test_session_id
    )
    assert res_batt["success"] is True
    assert res_batt["action"] == "SYSTEM_STATUS"
    assert "Battery" in res_batt["voice_vocalization"]

    # 2. Open apps query
    res_apps = dograh_voice_engine.process_voice_directive(
        "kya open hai mac me",
        speak_locally=False,
        session_id=test_session_id
    )
    assert res_apps["success"] is True
    assert res_apps["action"] == "RUNNING_APPS"
    assert "apps chal rahe hain" in res_apps["voice_vocalization"]

    # 3. NVIDIA Brev status query
    res_nvidia = dograh_voice_engine.process_voice_directive(
        "nvidia status batao",
        speak_locally=False,
        session_id=test_session_id
    )
    assert res_nvidia["success"] is True
    assert res_nvidia["action"] == "BREV_STATUS"
    assert "NVIDIA Brev" in res_nvidia["voice_vocalization"]

    # Verify session manager has captured all interactions
    sess = session_manager.get_session(test_session_id)
    assert sess is not None
    messages = sess["messages"]
    assert len(messages) >= 6  # 3 user directives + 3 bot replies

    # Check bot messages have proper metadata
    actions = [m["metadata"].get("action") for m in messages if m["role"] == "assistant"]
    assert "SYSTEM_STATUS" in actions
    assert "RUNNING_APPS" in actions
    assert "BREV_STATUS" in actions

    # Check live events ring buffer
    events = session_manager.get_live_events(limit=10)
    assert len(events) >= 3


def test_standalone_speech_mirrors_to_session():
    """Verify that standalone dograh speak_instant records to active session."""
    test_session_id = "sess_test_standalone_speech"
    dograh_voice_engine.speak_instant(
        "KYRON live hardware status vocalized",
        session_id=test_session_id
    )
    sess = session_manager.get_session(test_session_id)
    assert sess is not None
    assert len(sess["messages"]) >= 1
    last_msg = sess["messages"][-1]
    assert last_msg["role"] == "assistant"
    assert "live hardware status" in last_msg["content"]
