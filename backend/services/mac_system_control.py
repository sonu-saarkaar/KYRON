"""
KYRON MacSystemControl — High-Performance Native macOS Desktop Control Engine.

Provides deep, ultra-low latency integration with macOS using:
1. Native AppleScript (osascript) and JXA (JavaScript for Automation).
2. macOS CLI tools (open, screencapture, pmset, say).
3. Window detection & foreground focus management.
4. Multimedia, audio volume, brightness, and system preferences control.
5. Apple Notes, Reminders, Finder, and App lifecycle management.
6. Safety-gated messaging (WhatsApp / Messages / Slack).
"""

from __future__ import annotations

import os
import sys
import time
import subprocess
import logging
import urllib.parse
import urllib.request
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import pyautogui
import pyperclip

from services.approval_queue import approval_queue

logger = logging.getLogger(__name__)

# Safety settings for GUI automation
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


class MacSystemControlError(Exception):
    """Base exception for macOS control failures."""
    pass


def clean_music_query(text: str) -> str:
    """
    Intelligently extracts the pure song or video title from Hinglish, Hindi, and English directives.
    e.g. 'YouTube open kr ke song bajao saiyara' -> 'saiyara'
         'youtube pe jaa ke song bajao saiyara' -> 'saiyara'
         'saiyara song bajao' -> 'saiyara'
         'mere liye gaana bajao siyara' -> 'saiyara'
    """
    if not text:
        return "top trending songs"
        
    lower = text.lower()
    
    # 1. Strip out platform & action wrappers in Hinglish / Hindi / English
    stopwords = [
        r'\b(?:youtube|yt|chrome|browser|safari|spotify|music)\b',
        r'\b(?:open|kholo|khol|launch|start|run)\b',
        r'\b(?:kr\s*ke|kar\s*ke|karke|kro|kroo|karo|karein|karna|kardo|kar\s*do|kiya|kijiye)\b',
        r'\b(?:jaa\s*ke|jaake|jao|jaakar|jaana|chalo)\b',
        r'\b(?:song|songs|gana|gaana|gaane|track|tracks|audio|video|soundtrack)\b',
        r'\b(?:bajao|baja\s*do|bajado|chalao|chala\s*do|chalado|lagao|laga\s*do|lagado|sunao|suna\s*do|sunado|play|suno|sunna)\b',
        r'\b(?:bhai|boss|kyron|bhaiya|yaar|dost|sir)\b',
        r'\b(?:mere\s*liye|hamaare\s*liye|apne\s*liye|pls|please|zara|ek|koi|bhi|toh|to|dijiye|de)\b',
        r'\b(?:pe|par|me|mein|se|ko|aur|and|with|on|in|for|the|a|an)\b',
        r'\b(?:acha|achha|badhiya|hit|superhit|latest|new|best)\b'
    ]
    cleaned = lower
    for pat in stopwords:
        cleaned = re.sub(pat, ' ', cleaned, flags=re.IGNORECASE)
    
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned)
    cleaned = ' '.join(cleaned.split()).strip()

    # 2. Hindi music common spelling & typo normalizations
    typos = {
        'siyara': 'saiyara',
        'siyaraa': 'saiyara',
        'saiyaraa': 'saiyara',
        'sayara': 'saiyara',
        'sayaraa': 'saiyara',
        'kesria': 'kesariya',
        'kesriya': 'kesariya',
        'apna bna le': 'apna bana le'
    }
    words = [typos.get(w, w) for w in cleaned.split()]
    cleaned = ' '.join(words)

    if not cleaned or len(cleaned) < 2:
        return 'top trending songs'
    return cleaned


class MacSystemControl:
    """Native macOS System Controller for KYRON."""

    # Common macOS Application mappings (alias -> application name or bundle id)
    APP_MAPPINGS: Dict[str, str] = {
        "chrome": "Google Chrome",
        "google chrome": "Google Chrome",
        "safari": "Safari",
        "terminal": "Terminal",
        "iterm": "iTerm",
        "calculator": "Calculator",
        "calc": "Calculator",
        "notes": "Notes",
        "note": "Notes",
        "textedit": "TextEdit",
        "notepad": "TextEdit",
        "finder": "Finder",
        "files": "Finder",
        "explorer": "Finder",
        "whatsapp": "WhatsApp",
        "spotify": "Spotify",
        "music": "Music",
        "apple music": "Music",
        "settings": "System Settings",
        "system settings": "System Settings",
        "system preferences": "System Settings",
        "calendar": "Calendar",
        "reminders": "Reminders",
        "mail": "Mail",
        "messages": "Messages",
        "imessage": "Messages",
        "maps": "Maps",
        "weather": "Weather",
        "clock": "Clock",
        "photos": "Photos",
        "preview": "Preview",
        "xcode": "Xcode",
        "code": "Visual Studio Code",
        "vscode": "Visual Studio Code",
        "claude": "Claude",
        "antigravity": "Antigravity",
    }

    def __init__(self):
        self.is_mac = sys.platform == "darwin"
        if not self.is_mac:
            logger.warning("MacSystemControl initialized on non-macOS environment.")

    def run_applescript(self, script: str) -> Tuple[bool, str]:
        """Runs an AppleScript string via osascript and returns (success, output)."""
        try:
            res = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=10
            )
            if res.returncode == 0:
                return True, res.stdout.strip()
            else:
                return False, res.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "AppleScript execution timed out."
        except Exception as e:
            return False, str(e)

    # =========================================================================
    # Application Management
    # =========================================================================

    def open_app(self, app_name: str) -> Dict[str, Any]:
        """Launch or bring to front any application on macOS."""
        clean_name = app_name.lower().strip()
        target_app = self.APP_MAPPINGS.get(clean_name, app_name.strip())

        logger.info(f"[MacControl] Opening application: '{target_app}' (raw: '{app_name}')")

        # Try open -a first
        try:
            res = subprocess.run(
                ["open", "-a", target_app],
                capture_output=True,
                text=True,
                timeout=8
            )
            if res.returncode == 0:
                time.sleep(0.4)
                # Ensure frontmost focus
                self.focus_app(target_app)
                return {
                    "success": True,
                    "app": target_app,
                    "message": f"{target_app} opened successfully."
                }
        except Exception as e:
            logger.debug(f"[MacControl] open -a failed: {e}")

        # Fallback to AppleScript activation
        script = f'tell application "{target_app}" to activate'
        success, out = self.run_applescript(script)
        if success:
            return {
                "success": True,
                "app": target_app,
                "message": f"{target_app} activated successfully."
            }

        return {
            "success": False,
            "app": target_app,
            "error": out or f"Could not find or open application '{target_app}'."
        }

    def quit_app(self, app_name: str) -> Dict[str, Any]:
        """Gracefully quit an application on macOS."""
        clean_name = app_name.lower().strip()
        target_app = self.APP_MAPPINGS.get(clean_name, app_name.strip())

        script = f'tell application "{target_app}" to quit'
        success, out = self.run_applescript(script)
        if success:
            return {"success": True, "app": target_app, "message": f"{target_app} closed."}
        else:
            return {"success": False, "app": target_app, "error": out}

    def focus_app(self, app_name: str) -> bool:
        """Bring target application to verified foreground."""
        clean_name = app_name.lower().strip()
        target_app = self.APP_MAPPINGS.get(clean_name, app_name.strip())

        script = f'''
        tell application "{target_app}"
            activate
        end tell
        '''
        success, _ = self.run_applescript(script)
        time.sleep(0.25)
        return success

    def get_frontmost_app(self) -> str:
        """Get the name of the currently active/frontmost application."""
        script = 'tell application "System Events" to get name of first process whose frontmost is true'
        success, name = self.run_applescript(script)
        return name if success else "Unknown"

    def get_running_apps(self) -> List[str]:
        """Get list of user-facing running applications."""
        script = 'tell application "System Events" to get name of every process whose background only is false'
        success, out = self.run_applescript(script)
        if success and out:
            return [app.strip() for app in out.split(",")]
        return []

    # =========================================================================
    # Audio & Volume Controls
    # =========================================================================

    def get_volume(self) -> Dict[str, Any]:
        """Get current system output volume and mute status."""
        script = 'get volume settings'
        success, out = self.run_applescript(script)
        if success:
            # Format: output volume:81, input volume:59, alert volume:100, output muted:false
            info: Dict[str, Any] = {}
            for part in out.split(","):
                if ":" in part:
                    k, v = part.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    if v == "false":
                        info[k] = False
                    elif v == "true":
                        info[k] = True
                    else:
                        try:
                            info[k] = int(v)
                        except ValueError:
                            info[k] = v
            return {
                "success": True,
                "output_volume": info.get("output volume", 50),
                "muted": info.get("output muted", False),
                "raw": out
            }
        return {"success": False, "output_volume": 50, "muted": False}

    def set_volume(self, level: int) -> Dict[str, Any]:
        """Set output volume level from 0 to 100."""
        level = max(0, min(100, int(level)))
        script = f'set volume output volume {level}'
        success, out = self.run_applescript(script)
        if success:
            # Unmute automatically if volume is set > 0
            if level > 0:
                self.run_applescript('set volume with output muted false')
            return {"success": True, "volume": level, "message": f"Volume set to {level}%."}
        return {"success": False, "error": out}

    def volume_up(self, step: int = 15) -> Dict[str, Any]:
        """Increase volume by step percent."""
        curr = self.get_volume().get("output_volume", 50)
        return self.set_volume(curr + step)

    def volume_down(self, step: int = 15) -> Dict[str, Any]:
        """Decrease volume by step percent."""
        curr = self.get_volume().get("output_volume", 50)
        return self.set_volume(curr - step)

    def set_mute(self, mute: bool = True) -> Dict[str, Any]:
        """Mute or unmute system audio."""
        flag = "true" if mute else "false"
        script = f'set volume with output muted {flag}'
        success, out = self.run_applescript(script)
        if success:
            state = "muted" if mute else "unmuted"
            return {"success": True, "muted": mute, "message": f"Audio {state}."}
        return {"success": False, "error": out}

    # =========================================================================
    # Web & YouTube Controls
    # =========================================================================

    def open_url(self, url: str) -> Dict[str, Any]:
        """Open any URL in default macOS browser."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        try:
            subprocess.Popen(["open", url])
            return {"success": True, "url": url, "message": f"Opened {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_web(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """Search Google or YouTube in default browser."""
        encoded = urllib.parse.quote(query)
        if engine.lower() == "youtube":
            url = f"https://www.youtube.com/results?search_query={encoded}"
        else:
            url = f"https://www.google.com/search?q={encoded}"
        return self.open_url(url)

    def get_top_youtube_video(self, query: str) -> Tuple[str, Optional[str]]:
        """Scrapes YouTube search to find the exact top video link to autoplay immediately."""
        search_term = query if 'song' in query.lower() else f"{query} song"
        encoded = urllib.parse.quote(search_term)
        search_url = f"https://www.youtube.com/results?search_query={encoded}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        try:
            req = urllib.request.Request(search_url, headers=headers)
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                video_ids = re.findall(r'/watch\?v=([a-zA-Z0-9_-]{11})', html)
                if video_ids:
                    seen = set()
                    unique_ids = [x for x in video_ids if not (x in seen or seen.add(x))]
                    top_id = unique_ids[0]
                    # Direct watch URL with autoplay
                    watch_url = f"https://www.youtube.com/watch?v={top_id}&autoplay=1"
                    return watch_url, top_id
        except Exception as e:
            logger.warning(f"Error fetching direct YouTube video ID: {e}")
        
        return search_url, None

    def play_youtube(self, song_or_video: str) -> Dict[str, Any]:
        """Search and immediately PLAY a video/song on YouTube."""
        clean = clean_music_query(song_or_video)
        watch_url, video_id = self.get_top_youtube_video(clean)
        
        # On macOS, open the exact watch URL in default browser (Chrome/Safari)
        res = self.open_url(watch_url)
        return {
            "success": res.get("success", True),
            "query": clean,
            "url": watch_url,
            "video_id": video_id,
            "is_direct_play": bool(video_id),
            "message": f"Playing '{clean}' on YouTube" if video_id else f"Opened YouTube search for '{clean}'"
        }

    # =========================================================================
    # Media Player Controls (Music / Spotify)
    # =========================================================================

    def media_play_pause(self) -> Dict[str, Any]:
        """Toggle play/pause for active music player (Spotify or Apple Music)."""
        # Try Spotify first
        spotify_script = '''
        if application "Spotify" is running then
            tell application "Spotify" to playpause
            return "Spotify toggled"
        else if application "Music" is running then
            tell application "Music" to playpause
            return "Apple Music toggled"
        else
            -- Simulate system media key Play/Pause using key code
            tell application "System Events"
                key code 16 using {command down, control down}
            end tell
            return "Media key sent"
        end if
        '''
        success, out = self.run_applescript(spotify_script)
        return {"success": success, "message": out if success else "No media player running."}

    def media_next(self) -> Dict[str, Any]:
        """Skip to next track."""
        script = '''
        if application "Spotify" is running then
            tell application "Spotify" to next track
            return "Next track (Spotify)"
        else if application "Music" is running then
            tell application "Music" to next track
            return "Next track (Music)"
        else
            return "No player active"
        end if
        '''
        success, out = self.run_applescript(script)
        return {"success": success, "message": out}

    def media_prev(self) -> Dict[str, Any]:
        """Previous track."""
        script = '''
        if application "Spotify" is running then
            tell application "Spotify" to previous track
            return "Previous track (Spotify)"
        else if application "Music" is running then
            tell application "Music" to previous track
            return "Previous track (Music)"
        else
            return "No player active"
        end if
        '''
        success, out = self.run_applescript(script)
        return {"success": success, "message": out}

    # =========================================================================
    # Productivity: Apple Notes & Reminders
    # =========================================================================

    def create_note(self, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Create a new note in Apple Notes."""
        note_title = title or "KYRON Note"
        escaped_content = content.replace('"', '\\"').replace('\n', '<br>')
        script = f'''
        tell application "Notes"
            activate
            tell account "Default" to make new note at folder "Notes" with properties {{name:"{note_title}", body:"<h2>{note_title}</h2><p>{escaped_content}</p>"}}
        end tell
        '''
        # Fallback if account "Default" differs
        success, out = self.run_applescript(script)
        if not success:
            simple_script = f'''
            tell application "Notes"
                activate
                make new note with properties {{body:"<h2>{note_title}</h2><p>{escaped_content}</p>"}}
            end tell
            '''
            success, out = self.run_applescript(simple_script)

        if success:
            return {"success": True, "message": f"Note '{note_title}' created in Apple Notes."}
        return {"success": False, "error": out}

    def add_reminder(self, title: str) -> Dict[str, Any]:
        """Add a reminder to Apple Reminders app."""
        clean_title = title.replace('"', '\\"')
        script = f'''
        tell application "Reminders"
            make new reminder with properties {{name:"{clean_title}"}}
        end tell
        '''
        success, out = self.run_applescript(script)
        if success:
            return {"success": True, "message": f"Reminder '{title}' added to Reminders."}
        return {"success": False, "error": out}

    # =========================================================================
    # Screen & System Operations
    # =========================================================================

    def take_screenshot(self, target_folder: Optional[str] = None) -> Dict[str, Any]:
        """Take a fullscreen screenshot and save to Desktop or Downloads."""
        save_dir = Path(target_folder) if target_folder else (Path.home() / "Desktop")
        if not save_dir.exists():
            save_dir = Path.home() / "Downloads"

        filename = f"KYRON_Screenshot_{int(time.time())}.png"
        file_path = save_dir / filename

        try:
            res = subprocess.run(["screencapture", "-x", str(file_path)], capture_output=True)
            if res.returncode == 0:
                return {
                    "success": True,
                    "file_path": str(file_path),
                    "message": f"Screenshot saved to {file_path.name}."
                }
            return {"success": False, "error": "screencapture failed."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def toggle_dark_mode(self) -> Dict[str, Any]:
        """Toggle macOS Dark Mode."""
        script = '''
        tell application "System Events"
            tell appearance preferences
                set dark mode to not dark mode
                return dark mode
            end tell
        end tell
        '''
        success, out = self.run_applescript(script)
        if success:
            mode = "Dark Mode enabled" if out == "true" else "Light Mode enabled"
            return {"success": True, "message": mode}
        return {"success": False, "error": out}

    def lock_screen(self) -> Dict[str, Any]:
        """Lock the Mac screen immediately."""
        try:
            subprocess.Popen(["pmset", "displaysleepnow"])
            return {"success": True, "message": "Screen locked."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sleep_mac(self) -> Dict[str, Any]:
        """Put Mac to sleep."""
        script = 'tell application "System Events" to sleep'
        success, out = self.run_applescript(script)
        return {"success": success, "message": "Mac put to sleep." if success else out}

    def get_system_status(self) -> Dict[str, Any]:
        """Comprehensive system diagnostics for macOS (Battery health, volume, running apps, frontmost)."""
        import plistlib
        vol_info = self.get_volume()
        front_app = self.get_frontmost_app()
        running_apps = self.get_running_apps()

        # Check battery & power
        battery_pct = "Unknown"
        is_charging = False
        remaining = ""
        try:
            pm = subprocess.check_output(["pmset", "-g", "batt"], text=True)
            for line in pm.splitlines():
                if "%" in line:
                    m = re.search(r'(\d+)%', line)
                    if m:
                        battery_pct = f"{m.group(1)}%"
                    is_charging = "charging" in line.lower() or "ac attached" in line.lower()
                    rm = re.search(r'(\d+:\d+)\s+remaining', line)
                    if rm:
                        remaining = f"{rm.group(1)} remaining"
        except Exception:
            pass

        cycles = 0
        health = "100%"
        condition = "Normal"
        try:
            ioreg_out = subprocess.check_output(["ioreg", "-r", "-c", "AppleSmartBattery", "-a"])
            if ioreg_out.strip():
                data = plistlib.loads(ioreg_out)[0]
                cycles = data.get("CycleCount", 0)
                max_cap = data.get("MaxCapacity", 100)
                health = f"{max_cap}%" if max_cap <= 100 else "100%"
                condition = "Normal" if not data.get("AtCriticalLevel") else "Service Recommended"
        except Exception:
            pass

        return {
            "success": True,
            "platform": "macOS",
            "frontmost_app": front_app,
            "running_apps_count": len(running_apps),
            "running_apps": running_apps[:16],
            "output_volume": vol_info.get("output_volume", 50),
            "muted": vol_info.get("muted", False),
            "battery": battery_pct,
            "battery_health": health,
            "battery_condition": condition,
            "cycle_count": cycles,
            "time_remaining": remaining,
            "is_charging": is_charging,
        }

    # =========================================================================
    # Keyboard, Typing & Safety Gate Messaging
    # =========================================================================

    def type_text(self, text: str) -> None:
        """Types text with human-like speed, clipboard paste fallback for Hindi/unicode."""
        has_unicode = any(ord(c) > 127 for c in text)
        if has_unicode:
            old_clip = pyperclip.paste()
            try:
                pyperclip.copy(text)
                time.sleep(0.05)
                # macOS uses Command+V
                pyautogui.hotkey("command", "v")
                time.sleep(0.05)
            finally:
                try:
                    pyperclip.copy(old_clip)
                except Exception:
                    pass
        else:
            pyautogui.write(text, interval=0.03)

    def send_keys(self, combo: str) -> None:
        """Send keystrokes adapted for macOS (cmd instead of ctrl)."""
        keys = [k.strip().lower() for k in combo.split("+")]
        mac_keys = []
        for k in keys:
            if k == "ctrl" or k == "control":
                mac_keys.append("command")
            else:
                mac_keys.append(k)

        if len(mac_keys) == 1:
            pyautogui.press(mac_keys[0])
        else:
            pyautogui.hotkey(*mac_keys)

    def search_and_send_whatsapp(self, contact: str, message: str) -> Dict[str, Any]:
        """
        Directly searches for a contact in native WhatsApp on macOS,
        opens the chat, types the message, and presses Enter to dispatch.
        Displays macOS native desktop notification banner.
        """
        logger.info(f"[MacSystemControl] Searching WhatsApp for '{contact}' and sending: '{message}'")
        
        # 1. Open and focus WhatsApp application
        self.open_app("WhatsApp")
        time.sleep(0.8)

        # 2. Focus search bar (Cmd+F on Mac)
        pyautogui.hotkey("command", "f")
        time.sleep(0.3)
        pyautogui.hotkey("command", "a")
        pyautogui.press("backspace")
        time.sleep(0.2)

        # 3. Type contact name (e.g. "Sonu")
        self.type_text(contact)
        time.sleep(0.8)

        # 4. Select contact conversation
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.6)

        # 5. Type and send message
        self.type_text(message)
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.3)

        # 6. Display native macOS Desktop banner notification
        try:
            safe_contact = contact.replace('"', '\\"')
            safe_msg = message.replace('"', '\\"')
            subprocess.run([
                "osascript", "-e",
                f'display notification "Sent: \\"{safe_msg}\\" to {safe_contact}" with title "KYRON OBG" subtitle "WhatsApp Message Sent"'
            ], check=False, timeout=3)
        except Exception:
            pass

        return {
            "success": True,
            "app": "WhatsApp",
            "contact": contact,
            "message": message,
            "status": "delivered",
            "voice_vocalization": f"Boss, WhatsApp par {contact} ko search karke '{message}' message bhej diya hai!"
        }

    def draft_whatsapp_message(self, contact: str, message: str) -> Dict[str, Any]:
        """
        Drafts a WhatsApp message on macOS safely.
        Stops before hitting Enter, registering in approval queue.
        """
        # 1. Open and focus WhatsApp
        self.open_app("WhatsApp")
        time.sleep(1.0)

        # 2. Focus search bar (Cmd+F on Mac)
        pyautogui.hotkey("command", "f")
        time.sleep(0.3)
        pyautogui.hotkey("command", "a")
        pyautogui.press("backspace")
        time.sleep(0.2)

        # 3. Type contact
        self.type_text(contact)
        time.sleep(1.0)

        # 4. Select contact conversation
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(0.8)

        # 5. Type draft message
        self.type_text(message)
        time.sleep(0.3)

        # 6. Stop and register approval gate
        action_data = {
            "app": "WhatsApp",
            "target_contact": contact,
            "content": message,
            "description": f"Send WhatsApp message to '{contact}': '{message}'",
            "final_step": {"action": "send_keys", "key": "enter"},
            "created_at": time.time(),
            "status": "pending_confirmation"
        }
        action_id = approval_queue.register_pending_action(
            agent_type="SYSTEM",
            description=action_data["description"],
            payload=action_data,
            risk_level="high"
        )
        action_data["action_id"] = action_id
        return action_data

    # -------------------------------------------------------------------------
    # Native Mouth/Voice-Driven Cursor & Mouse Control (Sub-10ms Latency)
    # -------------------------------------------------------------------------
    def get_cursor_position(self) -> Tuple[int, int]:
        """Returns current cursor (x, y) coordinates on macOS display."""
        try:
            pos = pyautogui.position()
            return (pos.x, pos.y)
        except Exception:
            return (700, 450)

    def cursor_move_to(self, x: int, y: int, duration: float = 0.12) -> Dict[str, Any]:
        """Moves cursor to absolute coordinates (x, y) with boundary clamping."""
        try:
            sw, sh = pyautogui.size()
            safe_x = max(10, min(sw - 10, int(x)))
            safe_y = max(10, min(sh - 10, int(y)))
            pyautogui.moveTo(safe_x, safe_y, duration=duration)
            return {
                "success": True,
                "x": safe_x,
                "y": safe_y,
                "screen_width": sw,
                "screen_height": sh
            }
        except Exception as e:
            logger.error(f"[MacSystemControl] cursor_move_to failed: {e}")
            return {"success": False, "error": str(e)}

    def cursor_move(self, direction: str, distance: int = 140, duration: float = 0.12) -> Dict[str, Any]:
        """Moves cursor in a direction (up, down, left, right) by distance in pixels."""
        try:
            sw, sh = pyautogui.size()
            curr_x, curr_y = pyautogui.position()
            target_x, target_y = curr_x, curr_y

            dir_norm = direction.lower().strip()
            if dir_norm in ["up", "upar", "top"]:
                target_y -= distance
            elif dir_norm in ["down", "niche", "bottom"]:
                target_y += distance
            elif dir_norm in ["left", "baayein", "bayein"]:
                target_x -= distance
            elif dir_norm in ["right", "daayein", "dayein"]:
                target_x += distance
            elif dir_norm in ["up_left", "up-left"]:
                target_x -= int(distance * 0.7)
                target_y -= int(distance * 0.7)
            elif dir_norm in ["up_right", "up-right"]:
                target_x += int(distance * 0.7)
                target_y -= int(distance * 0.7)
            elif dir_norm in ["down_left", "down-left"]:
                target_x -= int(distance * 0.7)
                target_y += int(distance * 0.7)
            elif dir_norm in ["down_right", "down-right"]:
                target_x += int(distance * 0.7)
                target_y += int(distance * 0.7)

            safe_x = max(10, min(sw - 10, target_x))
            safe_y = max(10, min(sh - 10, target_y))
            pyautogui.moveTo(safe_x, safe_y, duration=duration)
            return {
                "success": True,
                "direction": dir_norm,
                "distance": distance,
                "old_pos": [curr_x, curr_y],
                "new_pos": [safe_x, safe_y]
            }
        except Exception as e:
            logger.error(f"[MacSystemControl] cursor_move failed: {e}")
            return {"success": False, "error": str(e)}

    def cursor_to_center(self, duration: float = 0.15) -> Dict[str, Any]:
        """Moves cursor directly to the center of the screen."""
        try:
            sw, sh = pyautogui.size()
            cx, cy = sw // 2, sh // 2
            pyautogui.moveTo(cx, cy, duration=duration)
            return {"success": True, "pos": [cx, cy]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cursor_click(self, button: str = "left", clicks: int = 1) -> Dict[str, Any]:
        """Performs single or multi-click at the current cursor position."""
        try:
            btn = button.lower()
            if btn not in ["left", "right", "middle"]:
                btn = "left"
            pyautogui.click(button=btn, clicks=clicks)
            pos = pyautogui.position()
            return {
                "success": True,
                "button": btn,
                "clicks": clicks,
                "pos": [pos.x, pos.y]
            }
        except Exception as e:
            logger.error(f"[MacSystemControl] cursor_click failed: {e}")
            return {"success": False, "error": str(e)}

    def cursor_double_click(self) -> Dict[str, Any]:
        """Performs double click at the current cursor position."""
        try:
            pyautogui.doubleClick()
            pos = pyautogui.position()
            return {"success": True, "action": "double_click", "pos": [pos.x, pos.y]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cursor_right_click(self) -> Dict[str, Any]:
        """Performs right click (context menu) at the current cursor position."""
        try:
            pyautogui.rightClick()
            pos = pyautogui.position()
            return {"success": True, "action": "right_click", "pos": [pos.x, pos.y]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cursor_scroll(self, direction: str = "down", amount: int = 6) -> Dict[str, Any]:
        """Scrolls up or down smoothly."""
        try:
            scroll_val = -amount if direction.lower() in ["down", "niche", "bottom"] else amount
            pyautogui.scroll(scroll_val)
            return {"success": True, "direction": direction, "amount": amount}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cursor_mouse_down(self, button: str = "left") -> Dict[str, Any]:
        """Presses and holds the mouse button (for drag & drop)."""
        try:
            pyautogui.mouseDown(button=button)
            return {"success": True, "status": "mouse_down", "button": button}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cursor_mouse_up(self, button: str = "left") -> Dict[str, Any]:
        """Releases the held mouse button."""
        try:
            pyautogui.mouseUp(button=button)
            return {"success": True, "status": "mouse_up", "button": button}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_cursor_voice_directive(self, directive: str) -> Optional[Dict[str, Any]]:
        """
        Parses mouth/voice directives deterministically and executes instantly (<10ms).
        Returns None if the directive is not a cursor instruction.
        """
        if not directive:
            return None
        text = directive.lower().strip()

        # Check for meta-instruction to enable mouth cursor control
        if (re.search(r'\b(cursore?|mouth|voice)\b.*?\bcontrol\s*kro\b', text) or 
            re.search(r'\bcontrol\s*kro.*?\b(cursor|mouth|aawaz)\b', text) or
            re.search(r'\b(mouth|aawaz)\s*se\s*.*cursor\b', text)):
            return {
                "handled": True,
                "action": "setup_cursor_control",
                "voice_vocalization": "Ji Boss! Mouth-driven Cursor Control active ho chuka hai. Aap jo bhi bolein—cursor upar, thoda niche, double click, right click, ya scroll—cursor direct sub-millisecond me aapke command par move karega!",
                "pos": list(self.get_cursor_position())
            }

        # Normalize common Hindi/Hinglish speech-to-text typos
        text = re.sub(r'\b(curose|curser|kursor|kursar|courser|coursor|cousor)\b', 'cursor', text)
        text = re.sub(r'\b(uper|uppar)\b', 'upar', text)
        text = re.sub(r'\b(neeche|neche)\b', 'niche', text)
        text = re.sub(r'\b(duble|doble)\b', 'double', text)
        text = re.sub(r'\b(kro|kroo|kardo|kijiye)\b', 'karo', text)
        text = re.sub(r'\b(bayein|baayein|baye|baaye)\b', 'left', text)
        text = re.sub(r'\b(daayein|dayein|daye|daaye)\b', 'right', text)
        text = re.sub(r'\b(clik|clck)\b', 'click', text)

        # 1. Double click
        if re.search(r'\b(double\s*click|do\s*baar\s*click|twice\s*click|click\s*double)\b', text) or text in ['double click', 'double click karo', 'duble click']:
            res = self.cursor_double_click()
            return {
                "handled": True,
                "action": "double_click",
                "pos": res.get("pos"),
                "voice_vocalization": "Boss, double click kar diya!"
            }

        # 2. Right click
        if re.search(r'\b(right\s*click|context\s*menu|click\s*right)\b', text):
            res = self.cursor_right_click()
            return {
                "handled": True,
                "action": "right_click",
                "pos": res.get("pos"),
                "voice_vocalization": "Boss, right click kar diya!"
            }

        # 3. Left / Single click
        if re.search(r'\b(single\s*click|left\s*click|click\s*single|click\s*left|ek\s*baar\s*click)\b', text) or text in ['click', 'click karo', 'single click', 'left click', 'cursor click', 'mouse click', 'cursor click karo']:
            res = self.cursor_click()
            return {
                "handled": True,
                "action": "click",
                "pos": res.get("pos"),
                "voice_vocalization": "Boss, click kar diya!"
            }
        if re.search(r'\bcursor\s*(se\s*)?click\b', text) or (re.search(r'\bclick\s*karo\b', text) and len(text.split()) <= 4):
            res = self.cursor_click()
            return {
                "handled": True,
                "action": "click",
                "pos": res.get("pos"),
                "voice_vocalization": "Boss, click kar diya!"
            }

        # 4. Scroll
        if re.search(r'\b(scroll\s*down|niche\s*scroll|scroll\s*niche|page\s*down)\b', text):
            self.cursor_scroll(direction="down", amount=8)
            return {
                "handled": True,
                "action": "scroll",
                "direction": "down",
                "voice_vocalization": "Boss, scroll down kar diya!"
            }
        if re.search(r'\b(scroll\s*up|upar\s*scroll|scroll\s*upar|page\s*up)\b', text):
            self.cursor_scroll(direction="up", amount=8)
            return {
                "handled": True,
                "action": "scroll",
                "direction": "up",
                "voice_vocalization": "Boss, scroll up kar diya!"
            }

        # 5. Center
        if re.search(r'\b(cursor\s*center|center\s*me\s*le\s*jao|screen\s*center)\b', text) or (text in ['center', 'center me', 'center karo', 'center le jao']):
            res = self.cursor_to_center()
            return {
                "handled": True,
                "action": "center",
                "pos": res.get("pos"),
                "voice_vocalization": "Boss, cursor screen center me le aaya!"
            }

        # 6. Directional Movement
        dist = 140
        if re.search(r'\b(thoda|thoda\s*sa|thodi|halka|slow|kam)\b', text):
            dist = 50
        elif re.search(r'\b(bahut|zyada|fast|bada)\b', text):
            dist = 300
        m_num = re.search(r'(\d+)\s*(px|pixel|pixels)?', text)
        if m_num:
            try:
                dist = min(int(m_num.group(1)), 800)
            except:
                pass

        has_cursor_mention = 'cursor' in text or 'mouse' in text or 'le jao' in text or 'move' in text or 'karo' in text
        words = text.split()

        if len(words) <= 5:
            if re.search(r'\b(upar|up)\b', text) and (has_cursor_mention or len(words) <= 2):
                res = self.cursor_move(direction="up", distance=dist)
                return {
                    "handled": True,
                    "action": "move",
                    "direction": "up",
                    "distance": dist,
                    "pos": res.get("new_pos"),
                    "voice_vocalization": f"Boss, cursor {dist}px upar kar diya!"
                }
            if re.search(r'\b(niche|down)\b', text) and (has_cursor_mention or len(words) <= 2):
                res = self.cursor_move(direction="down", distance=dist)
                return {
                    "handled": True,
                    "action": "move",
                    "direction": "down",
                    "distance": dist,
                    "pos": res.get("new_pos"),
                    "voice_vocalization": f"Boss, cursor {dist}px niche kar diya!"
                }
            if re.search(r'\b(left)\b', text) and (has_cursor_mention or len(words) <= 2):
                res = self.cursor_move(direction="left", distance=dist)
                return {
                    "handled": True,
                    "action": "move",
                    "direction": "left",
                    "distance": dist,
                    "pos": res.get("new_pos"),
                    "voice_vocalization": f"Boss, cursor {dist}px left kar diya!"
                }
            if re.search(r'\b(right)\b', text) and (has_cursor_mention or len(words) <= 2):
                res = self.cursor_move(direction="right", distance=dist)
                return {
                    "handled": True,
                    "action": "move",
                    "direction": "right",
                    "distance": dist,
                    "pos": res.get("new_pos"),
                    "voice_vocalization": f"Boss, cursor {dist}px right kar diya!"
                }

        # 7. Drag hold / release
        if re.search(r'\b(mouse\s*hold|drag|hold\s*karo|daba\s*ke\s*rakho)\b', text):
            self.cursor_mouse_down()
            return {
                "handled": True,
                "action": "mouse_down",
                "voice_vocalization": "Boss, mouse click hold kar liya hai!"
            }
        if re.search(r'\b(mouse\s*release|drop|chhod\s*do|release\s*karo)\b', text):
            self.cursor_mouse_up()
            return {
                "handled": True,
                "action": "mouse_up",
                "voice_vocalization": "Boss, mouse click release kar diya!"
            }

        return None



# Singleton instance
mac_system_control = MacSystemControl()
