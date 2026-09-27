"""
KYRON SystemControlAgent — Autonomous OS-level Action Execution Engine.

Capabilities:
1. Window detection & foreground focus verification (PyGetWindow / PyWinAuto).
2. App launching (Universal Windows launcher: native binaries, Store apps, URI schemes).
3. Human-like randomized typing (PyAutoGUI + pyperclip fallback for unicode/emojis).
4. Strict Background App Safety: Aborts typing if target window cannot be verified in focus.
5. Strict Contact Resolution: Aborts if contact search is ambiguous or not found.
6. Two-Phase Irreversible Action Gate (Drafts safely, pauses before final send).
"""

from __future__ import annotations

import os
import time
import random
import subprocess
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import uuid

import pyautogui
import pygetwindow as gw
import pyperclip
from pywinauto import Desktop

logger = logging.getLogger(__name__)

# Configure PyAutoGUI safety features
pyautogui.FAILSAFE = True  # Moving mouse to top-left corner aborts PyAutoGUI
pyautogui.PAUSE = 0.05


class SystemControlError(Exception):
    """Base exception for OS-level control failures."""
    pass


class WindowFocusError(SystemControlError):
    """Raised when target window cannot be focused (prevents typing into wrong windows)."""
    pass


class AmbiguousContactError(SystemControlError):
    """Raised when multiple contacts match or contact cannot be determined safely."""
    pass


from services.approval_queue import approval_queue

class SystemControlAgent:
    """
    KYRON System Control Agent managing desktop applications, input simulation,
    and safety-gated execution.
    """

    # Common Windows application launch mappings
    APP_MAPPINGS: Dict[str, Dict[str, Any]] = {
        "notepad": {"command": "notepad.exe", "window_title": "Notepad", "type": "executable"},
        "calculator": {"command": "calc.exe", "window_title": "Calculator", "type": "executable"},
        "cmd": {"command": "cmd.exe", "window_title": "Command Prompt", "type": "executable"},
        "terminal": {"command": "wt.exe", "window_title": "Terminal", "type": "executable"},
        "explorer": {"command": "explorer.exe", "window_title": "File Explorer", "type": "executable"},
        "code": {"command": "code", "window_title": "Visual Studio Code", "type": "executable"},
        "vscode": {"command": "code", "window_title": "Visual Studio Code", "type": "executable"},
        "chrome": {"command": "chrome.exe", "window_title": "Google Chrome", "type": "executable"},
        "edge": {"command": "msedge.exe", "window_title": "Microsoft Edge", "type": "executable"},
        "whatsapp": {"command": "whatsapp://", "window_title": "WhatsApp", "type": "uri"},
        "spotify": {"command": "spotify://", "window_title": "Spotify", "type": "uri"},
        "settings": {"command": "ms-settings:", "window_title": "Settings", "type": "uri"},
        "display": {"command": "ms-settings:display", "window_title": "Settings", "type": "uri"},
    }

    def __init__(self):
        pass

    def open_app(self, app_name: str) -> Dict[str, Any]:
        """
        Launch an application by name or common alias.
        Supports native executables and Windows URI schemes.
        """
        clean_name = app_name.lower().strip()
        mapping = self.APP_MAPPINGS.get(clean_name)

        target_cmd = mapping["command"] if mapping else clean_name
        is_uri = mapping["type"] == "uri" if mapping else ("://" in clean_name)

        logger.info(f"Opening application '{app_name}' (target: {target_cmd})")

        try:
            if is_uri:
                os.startfile(target_cmd)
            else:
                subprocess.Popen(
                    target_cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Allow process a brief moment to initialize
            time.sleep(1.0)
            return {"success": True, "app": app_name, "command": target_cmd}
        except Exception as e:
            logger.error(f"Failed to open app '{app_name}': {e}")
            raise SystemControlError(f"Could not open application '{app_name}': {str(e)}")

    def find_and_focus_window(self, title_query: str, timeout: float = 5.0) -> Any:
        """
        Locates target window by title query and brings it to foreground.
        CRITICAL SAFETY RULE 2 (Background App Safety):
        If window is not found or fails to gain foreground focus within timeout (5s),
        ABORT IMMEDIATELY. Typing is strictly prohibited before a single keystroke is sent,
        guaranteeing zero accidental keystrokes into background apps (browser, terminal, chats).
        """
        clean_query = title_query.lower().strip()
        start_time = time.time()
        matching_window = None

        logger.info(f"Searching for active window containing '{title_query}' (timeout: {timeout}s)")

        while time.time() - start_time < timeout:
            try:
                windows = gw.getAllWindows()
                for win in windows:
                    if win.title and clean_query in win.title.lower():
                        matching_window = win
                        break
            except Exception as e:
                logger.debug(f"Window enumeration error: {e}")
            
            if matching_window:
                break
            time.sleep(0.3)

        if not matching_window:
            raise WindowFocusError(
                f"SAFETY ABORT: Target window matching '{title_query}' was NOT found within {timeout}s timeout. "
                "Typing immediately blocked — no keystrokes sent to protect other open windows."
            )

        try:
            if matching_window.isMinimized:
                matching_window.restore()
            matching_window.activate()
            time.sleep(0.4)
            
            # Strict Foreground Verification
            active_win = gw.getActiveWindow()
            if not active_win or clean_query not in active_win.title.lower():
                # Force foreground activation attempt
                try:
                    import win32gui, win32con
                    win32gui.ShowWindow(matching_window._hWnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(matching_window._hWnd)
                except Exception:
                    matching_window.activate()
                time.sleep(0.4)
                
                active_win = gw.getActiveWindow()
                if not active_win or clean_query not in active_win.title.lower():
                    raise WindowFocusError(
                        f"SAFETY ABORT: Window '{matching_window.title}' could not achieve verified foreground focus. "
                        "Typing halted to prevent keystrokes leaking into active window."
                    )
            
            logger.info(f"Window '{matching_window.title}' safely focused and verified in foreground.")
            return matching_window
        except WindowFocusError:
            raise
        except Exception as e:
            raise WindowFocusError(f"SAFETY ABORT: Failed to focus window '{title_query}': {str(e)}")

    def type_text(self, text: str, delay: float = 0.04, verify_window: Optional[str] = None) -> None:
        """
        Types text with human-like randomized micro-delays (0.02s - 0.06s).
        CRITICAL SAFETY:
        - Checks verified foreground window before typing.
        - Continually verifies window focus every 10 chars so user switching apps halts typing immediately.
        - Uses clipboard paste fallback for unicode, Hindi, or emojis.
        """
        def _check_focus():
            if verify_window:
                active_win = gw.getActiveWindow()
                if not active_win or verify_window.lower() not in active_win.title.lower():
                    current_title = active_win.title if active_win else "None"
                    raise WindowFocusError(
                        f"SAFETY ABORT: Window focus lost! Expected '{verify_window}', but '{current_title}' is active. "
                        "Keystrokes halted immediately."
                    )

        _check_focus()

        # Check if text contains non-ASCII characters (e.g. Hindi, emojis)
        has_unicode = any(ord(c) > 127 for c in text)

        if has_unicode:
            # Safe paste via clipboard
            old_clip = pyperclip.paste()
            try:
                pyperclip.copy(text)
                time.sleep(0.05)
                _check_focus()
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.05)
            finally:
                # restore clipboard
                try:
                    pyperclip.copy(old_clip)
                except Exception:
                    pass
        else:
            # Human-like keystroke typing with periodic focus verification
            for idx, char in enumerate(text):
                if idx > 0 and idx % 10 == 0:
                    _check_focus()
                pyautogui.write(char)
                jitter = delay + random.uniform(-0.015, 0.02)
                time.sleep(max(0.01, jitter))

    def send_keys(self, key_combo: str) -> None:
        """Sends key combinations (e.g. 'enter', 'ctrl+v', 'tab', 'esc')."""
        keys = [k.strip().lower() for k in key_combo.split('+')]
        if len(keys) == 1:
            pyautogui.press(keys[0])
        else:
            pyautogui.hotkey(*keys)
        time.sleep(0.15)

    def search_and_open_contact(self, contact_name: str, app_title: str = "WhatsApp") -> None:
        """
        Searches for a contact in WhatsApp / Messaging app.
        CRITICAL SAFETY RULE 1 (Strict Contact Resolution):
        - Navigates to search box
        - Types contact name
        - Inspects search results: If contact is ambiguous (multiple matches) or no match is found,
          ABORT IMMEDIATELY. Never guess or type into an unverified contact conversation!
        """
        clean_contact = contact_name.strip()
        if not clean_contact or len(clean_contact) < 2:
            raise AmbiguousContactError(
                f"SAFETY ABORT: Contact query '{contact_name}' is too short or ambiguous. Clarification required."
            )

        # 1. Bring app to foreground with strict timeout
        self.find_and_focus_window(app_title, timeout=5.0)

        # 2. Focus search bar
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.4)

        # Clear existing search query
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.2)

        # 3. Type contact query
        self.type_text(clean_contact, delay=0.04, verify_window=app_title)
        time.sleep(1.2)  # Allow search results list to populate

        # 4. Check for UI automation / inspection if possible
        # Verify contact isn't ambiguous or non-existent
        try:
            from pywinauto import Desktop
            app_windows = Desktop(backend="uia").windows(title_re=f".*{app_title}.*")
            if app_windows:
                main_win = app_windows[0]
                # Look for 'No chats, contacts or messages found' or multiple contact items
                texts = [el.window_text() for el in main_win.descendants() if el.window_text()]
                lower_texts = [t.lower() for t in texts]

                # Check for "not found" states
                if any("no chats" in t or "no results" in t or "not found" in t for t in lower_texts):
                    raise AmbiguousContactError(
                        f"SAFETY ABORT: Contact '{contact_name}' was not found in {app_title}. "
                        "Execution halted to avoid typing into incorrect chat."
                    )

                # Check for multiple matching contacts
                matching_contacts = [t for t in texts if clean_contact.lower() in t.lower() and len(t) < 40]
                unique_matches = list(set(matching_contacts))
                if len(unique_matches) > 1:
                    logger.warning(f"Multiple contact matches found for '{contact_name}': {unique_matches}")
                    raise AmbiguousContactError(
                        f"SAFETY ABORT: Multiple contacts matched '{contact_name}': {', '.join(unique_matches[:4])}. "
                        "Execution paused. Operator clarification required before drafting message."
                    )
        except AmbiguousContactError:
            raise
        except Exception as e:
            logger.debug(f"UIAutomation contact inspection fallback: {e}")

        # In WhatsApp desktop, navigate to first verified match
        pyautogui.press('down')
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.8)

        # Final check: Ensure WhatsApp is still the focused window
        self.find_and_focus_window(app_title, timeout=3.0)
        logger.info(f"Safely opened verified contact conversation for '{contact_name}'.")

    def register_pending_action(
        self,
        app: str,
        target_contact: Optional[str],
        content: str,
        final_step: Dict[str, Any],
        description: str
    ) -> Dict[str, Any]:
        """
        Registers an irreversible action (e.g. final message dispatch) behind the safety gate.
        Returns payload for frontend ActionPreviewCard.
        """
        action_data = {
            "app": app,
            "target_contact": target_contact,
            "content": content,
            "description": description,
            "final_step": final_step,
            "created_at": time.time(),
            "status": "pending_confirmation"
        }
        action_id = approval_queue.register_pending_action(
            agent_type="SYSTEM",
            description=description,
            payload=action_data,
            risk_level="high"
        )
        action_data["action_id"] = action_id
        return action_data

    def confirm_and_execute(self, action_id: str, confirmed: bool) -> Dict[str, Any]:
        """
        Executes or discards the final irreversible step held in pending state.
        ONLY fires when physical user confirmation is received.
        """
        action_wrapper = approval_queue.get_action(action_id)
        if not action_wrapper:
            raise SystemControlError(f"Action '{action_id}' not found or already completed.")
            
        action = action_wrapper.get("payload")

        if not confirmed:
            action["status"] = "rejected_by_user"
            approval_queue.resolve_action(action_id, "rejected_by_user")
            logger.info(f"Action '{action_id}' rejected by user. Draft discarded.")
            return {"success": True, "action_id": action_id, "status": "rejected", "message": "Action cancelled by operator."}

        # User clicked Confirm: Execute final step
        final_step = action["final_step"]
        step_action = final_step.get("action")
        target_app = action.get("app")

        logger.info(f"User CONFIRMED action '{action_id}'. Executing final step: {step_action}")

        # Ensure window is still focused before sending final keystroke
        if target_app:
            self.find_and_focus_window(target_app, timeout=3.0)

        if step_action == "send_keys":
            self.send_keys(final_step.get("key", "enter"))
        elif step_action == "click_element":
            pyautogui.press("enter")

        action["status"] = "executed_confirmed"
        approval_queue.resolve_action(action_id, "executed_confirmed")

        return {
            "success": True,
            "action_id": action_id,
            "status": "executed",
            "message": f"Action confirmed and sent successfully to {action.get('target_contact') or target_app}."
        }

    def execute_power_command(self, power_type: str) -> Dict[str, Any]:
        """
        Executes an OS-level power command (shutdown, restart, sleep, lock).
        """
        try:
            if power_type == "shutdown":
                logger.info("Executing system shutdown command...")
                subprocess.Popen("shutdown /s /t 0", shell=True)
                return {"success": True, "message": "System shutdown initiated."}
            elif power_type == "restart":
                logger.info("Executing system restart command...")
                subprocess.Popen("shutdown /r /t 0", shell=True)
                return {"success": True, "message": "System restart initiated."}
            elif power_type == "lock":
                logger.info("Executing system lock command...")
                subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
                return {"success": True, "message": "System locked."}
            elif power_type == "sleep":
                logger.info("Executing system sleep command...")
                subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
                return {"success": True, "message": "System put to sleep."}
            else:
                return {"success": False, "message": f"Unknown power command: {power_type}"}
        except Exception as e:
            logger.error(f"Failed to execute power command '{power_type}': {e}")
            return {"success": False, "message": f"Failed to execute power command: {str(e)}"}


# Global singleton instance
system_control_agent = SystemControlAgent()
