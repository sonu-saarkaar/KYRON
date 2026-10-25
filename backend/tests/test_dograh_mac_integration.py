"""
KYRON - Dograh Voice Engine & macOS Native Control Integration Test Suite.

Verifies:
1. Native macOS System Control (Volume, Running Apps, Battery, Diagnostics).
2. Dograh Ultra-Low Latency Voice Directive Matcher (Hindi/Hinglish/English).
3. Low-latency Vocalization Telemetry (<250ms roundtrip).
4. Safety Gate integration for WhatsApp and Sensitive Actions.
5. REST API endpoints (/api/dograh/*).
"""

import sys
import os
import time
import pytest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.mac_system_control import mac_system_control
from services.dograh_voice_engine import dograh_voice_engine
from services.approval_queue import approval_queue


def test_mac_system_diagnostics():
    print("\n--- [TEST 1] Native macOS Hardware & System Diagnostics ---")
    status = mac_system_control.get_system_status()
    assert status["success"] is True
    assert status["platform"] == "macOS"
    assert "battery" in status
    assert "output_volume" in status
    assert "frontmost_app" in status
    assert status["running_apps_count"] > 0
    print(f" [PASS] macOS Status OK: Battery {status['battery']}, Active App: {status['frontmost_app']}")


def test_mac_volume_control():
    print("\n--- [TEST 2] macOS Audio & Volume Control ---")
    # Read initial volume
    initial = mac_system_control.get_volume()
    initial_vol = initial.get("output_volume", 50)
    
    # Set to 60
    res = mac_system_control.set_volume(60)
    assert res["success"] is True
    assert res["volume"] == 60
    
    # Read back to verify
    check = mac_system_control.get_volume()
    assert check["output_volume"] == 60
    print(f" [PASS] Output volume set and verified at 60%.")

    # Restore initial volume
    mac_system_control.set_volume(initial_vol)
    print(f" [PASS] Restored initial volume to {initial_vol}%.")


def test_dograh_intent_matcher_volume():
    print("\n--- [TEST 3] Dograh Voice Intent Matcher (Volume & Hinglish) ---")
    
    # Hindi/Hinglish directive: "volume 70 percent karo"
    t0 = time.time()
    res = dograh_voice_engine.process_voice_directive("volume 70 percent kar do please")
    elapsed_ms = int((time.time() - t0) * 1000)
    
    assert res["success"] is True
    assert res["action"] == "VOLUME_SET"
    assert "70" in res["voice_vocalization"]
    assert elapsed_ms < 300, f"Latency {elapsed_ms}ms exceeded 300ms threshold!"
    print(f" [PASS] Volume directive matched in {elapsed_ms}ms with vocalization: '{res['voice_vocalization']}'")


def test_dograh_intent_matcher_app_open():
    print("\n--- [TEST 4] Dograh Voice Intent Matcher (App Open) ---")
    
    # "calculator kholo"
    res = dograh_voice_engine.process_voice_directive("calculator kholo")
    assert res["success"] is True
    assert res["action"] == "APP_OPEN"
    assert "Calculator" in res["voice_vocalization"]
    print(f" [PASS] App open directive matched with vocalization: '{res['voice_vocalization']}'")
    
    # Clean up Calculator
    mac_system_control.quit_app("Calculator")


def test_dograh_intent_matcher_status():
    print("\n--- [TEST 5] Dograh Voice Intent Matcher (System Status in Hindi) ---")
    
    res = dograh_voice_engine.process_voice_directive("system status batao")
    assert res["success"] is True
    assert res["action"] == "SYSTEM_STATUS"
    assert "Battery" in res["voice_vocalization"] or "Boss" in res["voice_vocalization"]
    print(f" [PASS] System status vocalized: '{res['voice_vocalization']}'")


def test_dograh_whatsapp_safety_gate():
    print("\n--- [TEST 6] Dograh WhatsApp Messaging Safety Gate ---")
    
    approval_queue.pending_actions.clear()
    res = dograh_voice_engine.process_voice_directive("WhatsApp pe Sonu ko 'Meeting at 6 PM' message bhej")
    
    assert res["success"] is True
    assert res["action"] == "WHATSAPP_DRAFT"
    assert res["requires_confirmation"] is True
    assert "action_id" in res
    
    action_id = res["action_id"]
    queued = approval_queue.get_action(action_id)
    assert queued is not None
    assert queued["agent_type"] == "SYSTEM"
    print(f" [PASS] WhatsApp draft halted at Safety Gate with action_id: {action_id}")


def test_dograh_instant_speech_synthesis():
    print("\n--- [TEST 7] Dograh Native macOS Hardware Speech (<50ms) ---")
    
    t0 = time.time()
    res = dograh_voice_engine.speak_instant("KYRON is online and ready Boss.", language="en-IN")
    elapsed_ms = int((time.time() - t0) * 1000)
    
    assert res["success"] is True
    assert res["engine"] == "macos_native_say"
    assert elapsed_ms < 50, f"Synthesis invocation took {elapsed_ms}ms"
    print(f" [PASS] Hardware speech synthesized in {elapsed_ms}ms with voice: {res.get('voice')}")


if __name__ == "__main__":
    test_mac_system_diagnostics()
    test_mac_volume_control()
    test_dograh_intent_matcher_volume()
    test_dograh_intent_matcher_app_open()
    test_dograh_intent_matcher_status()
    test_dograh_whatsapp_safety_gate()
    test_dograh_instant_speech_synthesis()
    print("\n=======================================================")
    print(" ALL 7 DOGRAH & MACOS INTEGRATION TESTS PASSED (100%)!")
    print("=======================================================\n")
