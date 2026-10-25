"""
KYRON - NVIDIA Brev & Agent Toolkit Integration Tests.
"""

import sys
import os
import pytest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from services.brev_nvidia_service import brev_nvidia_service
from services.dograh_voice_engine import dograh_voice_engine


def test_brev_cli_installation():
    status = brev_nvidia_service.get_status()
    assert status["success"] is True
    assert status["cli_installed"] is True
    assert "v0.6" in status["cli_version"]
    assert status["launchables_count"] >= 6
    print(f" [PASS] Brev CLI verified: {status['cli_version']} at {status['cli_path']}")


def test_brev_launchables_catalog():
    launchables = brev_nvidia_service.get_launchables()
    keys = [item["key"] for item in launchables]
    assert "nemoclaw" in keys
    assert "hermes" in keys
    assert "isaac_sim" in keys
    assert "video_summarizer" in keys
    print(f" [PASS] 6 Launchables verified in catalog: {keys}")


def test_nemoclaw_sandbox_execution():
    code = "import math\nprint(math.factorial(5))"
    res = brev_nvidia_service.execute_in_sandbox(code)
    assert res["success"] is True
    assert "120" in res["stdout"]
    assert res["elapsed_ms"] < 200
    print(f" [PASS] NemoClaw sandbox execution verified in {res['elapsed_ms']}ms")


def test_dograh_brev_voice_directive():
    res = dograh_voice_engine.process_voice_directive("NVIDIA Brev status check karo")
    assert res["success"] is True
    assert res["action"] == "BREV_STATUS"
    assert "NVIDIA Brev" in res["voice_vocalization"]
    print(f" [PASS] Voice directive vocalized: '{res['voice_vocalization']}'")


if __name__ == "__main__":
    test_brev_cli_installation()
    test_brev_launchables_catalog()
    test_nemoclaw_sandbox_execution()
    test_dograh_brev_voice_directive()
    print("ALL BREV & NVIDIA INTEGRATION TESTS PASSED!")
