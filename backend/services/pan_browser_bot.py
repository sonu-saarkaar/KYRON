"""
KYRON PAN Browser Bot — Full Human-Like Browser, Cursor, Keyboard & CAPTCHA Automation Engine.

Features:
1. User-Driven Application Type Selection:
   - 49A : New PAN - Indian Citizen (Form No. 93)
   - CR  : Changes or Correction in PAN Data / Reprint of PAN Card
   - 49AA: New PAN - Foreign Citizen (Form No. 95)
2. Intelligent Popup & Announcement Modal Dismissal (Protean Upgrade Banner, Cookie Consent, Alert dialogs).
3. Official Protean Form 49A Direct Navigation (https://onlineservices.proteantech.in/paam/endUserRegisterContact.html).
4. Human-like Cursor Gliding (smooth bezier/multi-step mouse movement).
5. Realistic Keyboard Input (realistic typing intervals into First Name, Last Name, DOB, Mobile, Email).
6. Google reCAPTCHA Auto-Clicker & Auto-Submit Pipeline:
   - Automatically navigates cursor to reCAPTCHA iframe
   - Clicks "I am not a robot" checkbox
   - If verified (green checkmark), automatically clicks Submit button to proceed to Part 2!
   - If visual challenge appears, keeps browser foregrounded for user tap while standing by.
7. Non-blocking Background Execution with persistent visible Chrome display.
"""

import time
import logging
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PanBrowserBot:
    """Automates Form 49A / CR application on the official Protean portal."""

    APPLICATION_TYPES = {
        "49A": {
            "value": "49A",
            "name": "New PAN - Form No. 93 (Indian Citizen)",
            "category": "P"
        },
        "CR": {
            "value": "CR",
            "name": "Changes or Correction in existing PAN Data / Reprint of PAN Card",
            "category": "P"
        },
        "49AA": {
            "value": "49AA",
            "name": "New PAN - Form No. 95 (Foreign Citizen)",
            "category": "P"
        }
    }

    @staticmethod
    def run_in_background(applicant_data: Optional[Dict[str, Any]] = None):
        """Launches the bot in a background thread to prevent blocking the API response."""
        thread = threading.Thread(
            target=PanBrowserBot._execute_automation,
            args=(applicant_data,),
            daemon=True
        )
        thread.start()
        return thread

    @staticmethod
    def _execute_automation(applicant_data: Optional[Dict[str, Any]] = None):
        if not applicant_data:
            applicant_data = {
                "application_type": "49A",
                "first_name": "Asif",
                "last_name": "Aslam",
                "dob": "15/08/2000",
                "email": "sonu.saarkaar@gmail.com",
                "mobile": "9297989994",
                "father_name": "Md Aslam",
                "address": "Main Road, Ward No. 12, Motihari, Bihar - 845401",
                "aadhaar": "984210929942"
            }

        app_type_key = applicant_data.get("application_type", "49A").upper()
        type_config = PanBrowserBot.APPLICATION_TYPES.get(app_type_key, PanBrowserBot.APPLICATION_TYPES["49A"])

        logger.info(f"[PanBrowserBot] Starting automation for Application Type: {type_config['name']}...")

        # Optional OS-level PyAutoGUI smooth cursor movement
        try:
            import pyautogui
            sw, sh = pyautogui.size()
            pyautogui.moveTo(int(sw * 0.5), int(sh * 0.4), duration=0.6)
        except Exception as e:
            logger.debug(f"[PanBrowserBot] PyAutoGUI initial move notice: {e}")

        # Attempt Playwright native Chrome execution
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = None
                for channel in ["chrome", None]:
                    try:
                        kwargs = {"headless": False}
                        if channel:
                            kwargs["channel"] = channel
                        browser = p.chromium.launch(**kwargs)
                        logger.info(f"[PanBrowserBot] Launched Chromium browser (channel={channel})")
                        break
                    except Exception as launch_err:
                        logger.debug(f"[PanBrowserBot] Launch attempt with channel={channel} failed: {launch_err}")

                if not browser:
                    logger.warning("[PanBrowserBot] Playwright launch failed. Falling back to OS browser.")
                    PanBrowserBot._os_browser_fallback(applicant_data)
                    return

                context = browser.new_context(
                    viewport={"width": 1280, "height": 850},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = context.new_page()

                # Auto-accept all browser alert dialogs
                page.on("dialog", lambda dialog: dialog.accept())

                # 1. Step 1: Navigating to Protean Portal & Dismissing Popups
                logger.info("[PanBrowserBot] Step 1: Navigating to Protean Portal...")
                try:
                    page.goto("https://tinpan.proteantech.in/", timeout=25000)
                    time.sleep(1.2)

                    # Look for announcement popup / continue button
                    popup_selectors = [
                        'button:has-text("Continue")',
                        'button.bg-orange-500',
                        'button:has-text("Accept")',
                        'button:has-text("Close")',
                        '#gotrust-cookie-banner button'
                    ]
                    for sel in popup_selectors:
                        try:
                            btn = page.query_selector(sel)
                            if btn and btn.is_visible():
                                box = btn.bounding_box()
                                if box:
                                    # Smooth mouse movement to the popup dismiss button
                                    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=10)
                                    time.sleep(0.3)
                                btn.click()
                                logger.info(f"[PanBrowserBot] Successfully dismissed popup with: {sel}")
                                time.sleep(0.5)
                                break
                        except Exception:
                            pass
                except Exception as e:
                    logger.debug(f"[PanBrowserBot] Portal navigation notice: {e}")

                # 2. Step 2: Navigate to official Form 49A registration
                form_url = "https://onlineservices.proteantech.in/paam/endUserRegisterContact.html"
                logger.info(f"[PanBrowserBot] Step 2: Navigating to Form 49A: {form_url}")
                page.goto(form_url, timeout=30000)
                time.sleep(1.5)

                # 3. Step 3: Application Type (User's choice) & Category
                target_type = type_config["value"]
                target_category = type_config["category"]
                logger.info(f"[PanBrowserBot] Step 3: Selecting Application Type '{target_type}' & Category '{target_category}'...")
                
                # Move cursor to Application Type dropdown
                sel_type_el = page.query_selector('select#type')
                if sel_type_el and sel_type_el.is_visible():
                    box = sel_type_el.bounding_box()
                    if box:
                        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=8)
                        time.sleep(0.2)

                page.evaluate(f"""() => {{
                    const selType = document.querySelector('select#type');
                    if (selType) {{
                        selType.value = '{target_type}';
                        selType.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                    const selCat = document.querySelector('select#cat_applicant1');
                    if (selCat) {{
                        selCat.value = '{target_category}';
                        selCat.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        if (typeof checktype === 'function') checktype();
                    }}
                }}""")
                time.sleep(0.8)

                # 4. Step 4: Typing Applicant Name with Human Keystroke Simulation
                logger.info("[PanBrowserBot] Step 4: Typing Applicant Names...")
                l_name = page.query_selector('input#l_name_end')
                if l_name and l_name.is_visible():
                    box = l_name.bounding_box()
                    if box:
                        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=8)
                        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    page.type('input#l_name_end', applicant_data.get("last_name", "Aslam"), delay=55)

                time.sleep(0.3)
                f_name = page.query_selector('input#f_name_end')
                if f_name and f_name.is_visible():
                    box = f_name.bounding_box()
                    if box:
                        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=8)
                        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    page.type('input#f_name_end', applicant_data.get("first_name", "Asif"), delay=55)

                time.sleep(0.3)

                # 5. Step 5: Typing Date of Birth
                logger.info("[PanBrowserBot] Step 5: Typing Date of Birth...")
                dob_field = page.query_selector('input#date_of_birth_reg')
                if dob_field and dob_field.is_visible():
                    box = dob_field.bounding_box()
                    if box:
                        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=6)
                        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    page.type('input#date_of_birth_reg', applicant_data.get("dob", "15/08/2000"), delay=45)

                time.sleep(0.3)

                # 6. Step 6: Typing Contact Info (Email & Mobile)
                logger.info("[PanBrowserBot] Step 6: Typing Email & Mobile Number...")
                page.type('input#email_id2', applicant_data.get("email", "sonu.saarkaar@gmail.com"), delay=35)
                time.sleep(0.2)
                page.type('input#rvContactNo', applicant_data.get("mobile", "9297989994"), delay=35)

                time.sleep(0.3)

                # 7. Step 7: Consent Checkbox & Citizenship Radio
                logger.info("[PanBrowserBot] Step 7: Checking Consent Box...")
                page.evaluate("""() => {
                    const consent = document.querySelector('input#consent');
                    if (consent) {
                        consent.checked = true;
                        consent.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                    const cit = document.querySelector('input#citizenCr1');
                    if (cit) {
                        cit.checked = true;
                        cit.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }""")
                time.sleep(0.4)

                # 8. Step 8: Scroll down to reveal reCAPTCHA section
                logger.info("[PanBrowserBot] Step 8: Scrolling to CAPTCHA section...")
                page.mouse.wheel(0, 420)
                time.sleep(1.0)

                # 9. Step 9: reCAPTCHA Auto-Clicker & Auto-Submit Pipeline
                logger.info("[PanBrowserBot] Step 9: Moving cursor to reCAPTCHA checkbox...")
                try:
                    frames = page.frames
                    recaptcha_frame = None
                    for f in frames:
                        if "recaptcha/enterprise/anchor" in f.url or "recaptcha" in f.url:
                            recaptcha_frame = f
                            break

                    if recaptcha_frame:
                        anchor = recaptcha_frame.wait_for_selector("#recaptcha-anchor", timeout=4000)
                        if anchor:
                            box = anchor.bounding_box()
                            if box:
                                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=8)
                                time.sleep(0.3)
                            anchor.click()
                            logger.info("[PanBrowserBot] Successfully clicked 'I am not a robot' reCAPTCHA checkbox!")
                            time.sleep(2.0)

                            # Check if verified with green checkmark
                            checked = recaptcha_frame.evaluate("""() => {
                                const el = document.querySelector('#recaptcha-anchor');
                                return el ? el.getAttribute('aria-checked') : null;
                            }""")
                            logger.info(f"[PanBrowserBot] reCAPTCHA checkmark status: {checked}")

                            if checked == "true":
                                logger.info("[PanBrowserBot] CAPTCHA verified! Auto-clicking Submit button to advance form...")
                                submit_btn = page.query_selector("button#submitForm")
                                if submit_btn and submit_btn.is_visible():
                                    box = submit_btn.bounding_box()
                                    if box:
                                        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=6)
                                        time.sleep(0.2)
                                    submit_btn.click()
                                    logger.info("[PanBrowserBot] Clicked Submit! Form advanced to Part 2 token registration.")
                            else:
                                logger.info("[PanBrowserBot] reCAPTCHA challenge displayed. Browser window open for physical confirmation.")
                except Exception as cap_err:
                    logger.debug(f"[PanBrowserBot] CAPTCHA automation notice: {cap_err}")

                logger.info("[PanBrowserBot] Form fill cycle completed. Keeping window open on screen.")
                time.sleep(300)

        except Exception as e:
            logger.error(f"[PanBrowserBot] Execution error: {e}", exc_info=True)
            PanBrowserBot._os_browser_fallback(applicant_data)

    @staticmethod
    def _os_browser_fallback(applicant_data: Dict[str, Any]):
        """Fallback to macOS system browser with PyAutoGUI cursor actions."""
        try:
            import subprocess
            import pyautogui
            url = "https://onlineservices.proteantech.in/paam/endUserRegisterContact.html"
            subprocess.Popen(["open", url])
            time.sleep(2.0)
            sw, sh = pyautogui.size()
            pyautogui.moveTo(int(sw * 0.5), int(sh * 0.4), duration=0.8)
            pyautogui.click()
            time.sleep(0.3)
            pyautogui.press("esc")
            time.sleep(0.3)
            pyautogui.scroll(-3)
        except Exception as ex:
            logger.debug(f"[PanBrowserBot] OS fallback notice: {ex}")


pan_browser_bot = PanBrowserBot()
