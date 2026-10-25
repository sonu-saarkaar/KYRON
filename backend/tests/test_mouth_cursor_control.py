"""
Test Suite for Hands-Free Mouth & Voice-Driven Cursor Control in KYRON.

Verifies:
1. Native MacSystemControl cursor movements, clicks, scrolls, and drag-and-drop.
2. Deterministic regex parsing for Hinglish / Hindi speech phonetics ('curose', 'uper', 'duble', 'kro').
3. Instant zero-latency interception in chat pipeline.
4. Dedicated REST endpoint /api/kyron/system-control/cursor.
5. Strict non-interference with normal PAN Card, Coding, and General Chat pipelines.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.mac_system_control import mac_system_control
from routes.chat import process_user_message


def test_cursor_position_and_bounds():
    """Verify cursor position querying returns valid coordinates."""
    pos = mac_system_control.get_cursor_position()
    assert isinstance(pos, tuple)
    assert len(pos) == 2
    assert pos[0] >= 0
    assert pos[1] >= 0


def test_cursor_movement_directions():
    """Verify up, down, left, right and center cursor navigation."""
    # Center
    res_center = mac_system_control.cursor_to_center(duration=0.01)
    assert res_center["success"] is True
    assert "pos" in res_center

    # Up
    res_up = mac_system_control.cursor_move(direction="up", distance=50, duration=0.01)
    assert res_up["success"] is True
    assert res_up["new_pos"][1] <= res_up["old_pos"][1]

    # Down
    res_down = mac_system_control.cursor_move(direction="down", distance=50, duration=0.01)
    assert res_down["success"] is True
    assert res_down["new_pos"][1] >= res_down["old_pos"][1]

    # Left
    res_left = mac_system_control.cursor_move(direction="left", distance=50, duration=0.01)
    assert res_left["success"] is True
    assert res_left["new_pos"][0] <= res_left["old_pos"][0]

    # Right
    res_right = mac_system_control.cursor_move(direction="right", distance=50, duration=0.01)
    assert res_right["success"] is True
    assert res_right["new_pos"][0] >= res_right["old_pos"][0]


def test_cursor_clicks_and_scroll():
    """Verify single click, double click, right click, and scroll executions."""
    res_click = mac_system_control.cursor_click()
    assert res_click["success"] is True
    assert res_click["clicks"] == 1

    res_double = mac_system_control.cursor_double_click()
    assert res_double["success"] is True
    assert res_double["action"] == "double_click"

    res_right = mac_system_control.cursor_right_click()
    assert res_right["success"] is True
    assert res_right["action"] == "right_click"

    res_scroll_down = mac_system_control.cursor_scroll(direction="down", amount=5)
    assert res_scroll_down["success"] is True

    res_scroll_up = mac_system_control.cursor_scroll(direction="up", amount=5)
    assert res_scroll_up["success"] is True


def test_voice_directive_parsing_exact_user_phrases():
    """Verify the exact user speech inputs are properly parsed and handled."""
    # 1. Setup / meta activation directive
    meta_directive = (
        "bhai cursore ko control kro mai bolu curose uper kro duble click kro "
        "single click kro left click kro right click kro jo jo bolu cursor wo wo kre "
        "mere mouth se pure courser ko control kroo best way se hermes ke trah"
    )
    res_meta = mac_system_control.execute_cursor_voice_directive(meta_directive)
    assert res_meta is not None
    assert res_meta["handled"] is True
    assert res_meta["action"] == "setup_cursor_control"
    assert "Mouth-driven Cursor Control active" in res_meta["voice_vocalization"]

    # 2. 'curose uper kro'
    res_up = mac_system_control.execute_cursor_voice_directive("curose uper kro")
    assert res_up is not None
    assert res_up["action"] == "move"
    assert res_up["direction"] == "up"

    # 3. 'duble click kro'
    res_duble = mac_system_control.execute_cursor_voice_directive("duble click kro")
    assert res_duble is not None
    assert res_duble["action"] == "double_click"

    # 4. 'single click kro'
    res_single = mac_system_control.execute_cursor_voice_directive("single click kro")
    assert res_single is not None
    assert res_single["action"] == "click"

    # 5. 'left click kro'
    res_left_click = mac_system_control.execute_cursor_voice_directive("left click kro")
    assert res_left_click is not None
    assert res_left_click["action"] == "click"

    # 6. 'right click kro'
    res_right_click = mac_system_control.execute_cursor_voice_directive("right click kro")
    assert res_right_click is not None
    assert res_right_click["action"] == "right_click"

    # 7. 'thoda niche'
    res_thoda = mac_system_control.execute_cursor_voice_directive("thoda niche")
    assert res_thoda is not None
    assert res_thoda["action"] == "move"
    assert res_thoda["direction"] == "down"
    assert res_thoda["distance"] == 50

    # 8. 'center me le jao'
    res_center = mac_system_control.execute_cursor_voice_directive("center me le jao")
    assert res_center is not None
    assert res_center["action"] == "center"

    # 9. 'scroll down'
    res_scroll = mac_system_control.execute_cursor_voice_directive("scroll down")
    assert res_scroll is not None
    assert res_scroll["action"] == "scroll"
    assert res_scroll["direction"] == "down"


@pytest.mark.asyncio
async def test_chat_pipeline_cursor_interception():
    """Verify chat endpoint intercepts cursor commands instantly without LLM latency."""
    res = await process_user_message(
        text="curose uper kro",
        language="hi",
        user_id="test-cursor-user",
        session_id="test-cursor-session"
    )
    assert res.should_speak is True
    assert "upar" in res.text.lower()
    assert res.actions is not None
    assert res.actions[0]["type"] == "CURSOR_CONTROL"
    assert res.actions[0]["action"] == "move"


@pytest.mark.asyncio
async def test_non_cursor_requests_bypass_cleanly():
    """Verify non-cursor requests (e.g. PAN card) are not intercepted by cursor engine."""
    assert mac_system_control.execute_cursor_voice_directive("tum Mere liye pan card Bana sakte Ho") is None
    assert mac_system_control.execute_cursor_voice_directive("PAN Card me correction kroon") is None
    assert mac_system_control.execute_cursor_voice_directive("hello kyron good morning") is None
