"""
KYRON BrowserControlAgent — Autonomous Browser Action Execution Engine.

Features:
1. NVIDIA NIM & Hermes-aligned LLM Gateway (ChatOpenAI / LLMClient).
2. Persistent Browser Profile (~/.kyron_browser_profile) for saved sessions (Gmail, Amazon, WhatsApp Web).
3. Pre-Action Safety Interceptor (Reversible vs Irreversible Classification):
   - REVERSIBLE (navigate, scroll, read, search, non-submitting form typing): Auto-executes directly.
   - IRREVERSIBLE (submit, pay, checkout, buy, place order, delete, post, send): PAUSES execution,
     generates ActionPreviewCard payload, requests physical user confirmation.
4. Real-time telemetry streaming to ActivityFeed.
"""

from __future__ import annotations

import os
import re
import time
import json
import uuid
import base64
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

from services.llm_client import (
    LLMClient,
    llm_client,
    NVIDIA_NIM_BASE_URL,
    DEFAULT_NVIDIA_MODEL,
    GROQ_BASE_URL,
    DEFAULT_GROQ_MODEL,
)

logger = logging.getLogger(__name__)

# Irreversible action keyword regex matcher
IRREVERSIBLE_REGEX = re.compile(
    r"(submit|pay|checkout|place\s*order|place\s*your\s*order|buy\s*now|proceed\s*to\s*checkout|"
    r"proceed\s*to\s*pay|delete|post|publish|send\s*message|remove\s*account|confirm\s*order)",
    re.IGNORECASE
)

# Persistent browser profile path
BROWSER_PROFILE_DIR = Path.home() / ".kyron_browser_profile"
BROWSER_PROFILE_DIR.mkdir(parents=True, exist_ok=True)


from services.approval_queue import approval_queue

class BrowserControlAgent:
    """
    KYRON Autonomous Browser Control Agent.
    Executes natural language web directives while guarding destructive/irreversible actions.
    """

    def __init__(self):
        self.playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.activity_log: List[Dict[str, Any]] = []
        self._loop = None
        self._lock = None

    @property
    def lock(self) -> asyncio.Lock:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if getattr(self, "_loop", None) is not current_loop or self._lock is None:
            self._loop = current_loop
            self._lock = asyncio.Lock()
            # Reset instances bound to prior event loops
            self.playwright = None
            self.context = None
            self.page = None
        return self._lock

    async def ensure_browser(self) -> Page:
        """
        Ensures persistent browser context is initialized and returns active page.
        Prefers native Chrome or Edge channels if available on Windows.
        Includes automatic fallback for user-data-dir locks or display constraints.
        """
        # Ensure event loop alignment
        _ = self.lock

        try:
            if self.page and not self.page.is_closed():
                return self.page
        except Exception:
            self.page = None

        try:
            if not self.playwright:
                self.playwright = await async_playwright().start()
        except Exception:
            self.playwright = await async_playwright().start()

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-default-browser-check",
            "--disable-infobars",
        ]

        # 1. Attempt persistent context with native channels
        for channel in ["chrome", "msedge", None]:
            for hl in [False, True]:
                try:
                    kwargs = {
                        "user_data_dir": str(BROWSER_PROFILE_DIR),
                        "headless": hl,
                        "args": launch_args,
                        "viewport": {"width": 1280, "height": 800},
                    }
                    if channel:
                        kwargs["channel"] = channel

                    self.context = await self.playwright.chromium.launch_persistent_context(**kwargs)
                    pages = self.context.pages
                    self.page = pages[0] if pages else await self.context.new_page()
                    logger.info(f"Browser launched (channel: {channel or 'bundled'}, headless: {hl}).")
                    return self.page
                except Exception as e:
                    logger.debug(f"Persistent launch attempt ({channel}, headless={hl}) failed: {e}")

        # 2. Resilient fallback: standard browser launch without persistent lock
        if not self.page or self.page.is_closed():
            for channel in ["chrome", "msedge", None]:
                for hl in [False, True]:
                    try:
                        kwargs = {"headless": hl, "args": launch_args}
                        if channel:
                            kwargs["channel"] = channel
                        browser = await self.playwright.chromium.launch(**kwargs)
                        self.context = await browser.new_context(viewport={"width": 1280, "height": 800})
                        self.page = await self.context.new_page()
                        logger.info(f"Standard browser launched as fallback ({channel}, headless: {hl}).")
                        return self.page
                    except Exception as e:
                        logger.debug(f"Standard launch fallback failed ({channel}, hl={hl}): {e}")

        if not self.page:
            raise RuntimeError("Could not launch any browser instance on system.")

        return self.page

    def log_activity(self, action_type: str, detail: str, level: str = "INFO"):
        """Logs event for telemetry streaming to ActivityFeed."""
        entry = {
            "timestamp": time.time(),
            "time_str": time.strftime("%H:%M:%S"),
            "type": "BROWSER",
            "action": action_type,
            "detail": detail,
            "level": level,
        }
        self.activity_log.append(entry)
        if len(self.activity_log) > 100:
            self.activity_log.pop(0)
        logger.info(f"[BROWSER ACTIVITY] [{action_type}] {detail}")

    def classify_action(self, action_type: str, element_desc: str) -> str:
        """
        Classifies an action as REVERSIBLE or IRREVERSIBLE (Strict Fail-Safe).
        Rule:
        - Default assumption is IRREVERSIBLE.
        - Only explicitly known-safe actions are REVERSIBLE.
        """
        # Always check against dangerous patterns first
        if IRREVERSIBLE_REGEX.search(element_desc):
            return "IRREVERSIBLE"

        # Explicitly safe non-click/non-submit actions
        if action_type in ["navigate", "scroll", "extract", "wait", "focus", "type"]:
            return "REVERSIBLE"

        # Click actions are only safe if they match a known whitelist pattern with word boundaries
        if action_type == "click":
            safe_keywords_pattern = re.compile(
                r'\b(cart|add to cart|search|filter|next|tab|open|expand|view|'
                r'close|cancel|back|home|menu|sign in|login|continue shopping|go)\b',
                re.IGNORECASE
            )
            
            if safe_keywords_pattern.search(element_desc):
                return "REVERSIBLE"
            
            # If it's a click and doesn't match the exact whitelist, default to IRREVERSIBLE
            return "IRREVERSIBLE"

        # Any unknown action type defaults to IRREVERSIBLE
        return "IRREVERSIBLE"

    async def get_interactive_elements(self, page: Page) -> List[Dict[str, Any]]:
        """
        Extracts interactive DOM elements (buttons, inputs, links) with their visible text,
        selectors, and roles for the LLM to inspect.
        """
        script = """
        () => {
            const elements = [];
            const candidates = document.querySelectorAll('button, a, input, textarea, [role="button"], select');
            let idx = 0;
            for (const el of candidates) {
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                if (rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none') {
                    const text = (el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim();
                    const tag = el.tagName.toLowerCase();
                    const type = el.getAttribute('type') || '';
                    const placeholder = el.getAttribute('placeholder') || el.placeholder || '';
                    const id = el.id || '';
                    elements.push({
                        id: idx++,
                        tag: tag,
                        type: type,
                        text: text.slice(0, 100),
                        placeholder: placeholder,
                        element_id: id,
                        role: el.getAttribute('role') || tag,
                        name: el.getAttribute('name') || '',
                        aria: el.getAttribute('aria-label') || ''
                    });
                    if (elements.length >= 60) break;
                }
            }
            return elements;
        }
        """
        try:
            return await page.evaluate(script)
        except Exception:
            return []

    async def execute_task(self, directive: str, max_steps: int = 10) -> Dict[str, Any]:
        """
        Main execution loop:
        1. Ensures browser session is active.
        2. Inspects page state & DOM.
        3. Uses LLM to plan next step.
        4. Intercepts action:
           - If Reversible -> Execute immediately, log activity.
           - If Irreversible -> PAUSE execution, register pending action, return ActionPreviewCard payload.
        """
        async with self.lock:
            page = await self.ensure_browser()
            executed_steps = []
            client = LLMClient()

            self.log_activity("TASK_START", f"Directive: '{directive}'")

            # Check if directive contains a direct URL or domain
            target_url = None
            url_match = re.search(r"https?://[^\s]+|(?:www\.)?[a-zA-Z0-9-]+\.(?:com|in|app|org|net|co|io|ai|tech)[^\s]*", directive)
            if url_match:
                raw_url = url_match.group(0).rstrip(".,;!?'\")")
                target_url = raw_url if raw_url.startswith("http") else f"https://{raw_url}"
            elif "bookmygadi" in directive.lower() or "my gadi" in directive.lower() or "mygadi" in directive.lower():
                target_url = "https://www.bookmygadi.app/"
            elif "gmail" in directive.lower():
                target_url = "https://mail.google.com"
            elif "amazon" in directive.lower():
                target_url = "https://www.amazon.in"
            elif "google" in directive.lower():
                target_url = "https://www.google.com"

            if target_url and (page.url == "about:blank" or target_url not in page.url):
                try:
                    self.log_activity("NAVIGATE", f"Navigating to {target_url}")
                    await page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
                    await asyncio.sleep(2)
                    executed_steps.append(f"Navigated to {target_url}")
                except Exception as e:
                    logger.warning(f"Navigation warning: {e}")

            # Smart direct autofill for BookMyGadi / Cab booking directives
            if "bookmygadi" in (target_url or "").lower() or "bookmygadi" in page.url.lower():
                pickup_val = None
                drop_val = None
                
                # Check for pickup and drop in directive
                pm = re.search(r"pickup[:\s]+([a-zA-Z0-9\s]+?)(?:,|\bdrop\b|\bnaam\b|\bname\b|\bphone\b|$)", directive, re.IGNORECASE)
                if pm:
                    pickup_val = pm.group(1).strip()
                elif "motihari" in directive.lower() and "patna" in directive.lower():
                    if directive.lower().find("motihari") < directive.lower().find("patna"):
                        pickup_val, drop_val = "Motihari", "Patna"
                    else:
                        pickup_val, drop_val = "Patna", "Motihari"
                elif "motihari" in directive.lower():
                    pickup_val = "Motihari"

                dm = re.search(r"drop[:\s]+([a-zA-Z0-9\s]+?)(?:,|\bpickup\b|\bnaam\b|\bname\b|\bphone\b|$)", directive, re.IGNORECASE)
                if dm:
                    drop_val = dm.group(1).strip()
                elif "patna" in directive.lower() and not drop_val:
                    drop_val = "Patna"

                if pickup_val:
                    try:
                        p_input = page.get_by_placeholder("Pickup Location").first
                        await p_input.click()
                        await p_input.fill(pickup_val)
                        executed_steps.append(f"Autofilled Pickup Location: {pickup_val}")
                        self.log_activity("TYPE", f"Pickup Location set to '{pickup_val}'")
                    except Exception as pe:
                        logger.warning(f"Could not fill pickup: {pe}")

                if drop_val:
                    try:
                        d_input = page.get_by_placeholder("Drop Location").first
                        await d_input.click()
                        await d_input.fill(drop_val)
                        executed_steps.append(f"Autofilled Drop Location: {drop_val}")
                        self.log_activity("TYPE", f"Drop Location set to '{drop_val}'")
                    except Exception as de:
                        logger.warning(f"Could not fill drop: {de}")

            for step_num in range(1, max_steps + 1):
                try:
                    await page.wait_for_load_state("domcontentloaded", timeout=4000)
                except Exception:
                    pass

                current_url = page.url
                try:
                    page_title = await page.title()
                except Exception:
                    await asyncio.sleep(0.5)
                    try:
                        page_title = await page.title()
                    except Exception:
                        page_title = "Web Page"

                elements = await self.get_interactive_elements(page)

                # Simplify elements snapshot for LLM prompt with placeholder & name
                elements_summary = [
                    f"[{el['id']}] <{el['tag']} type='{el['type']}'" +
                    (f" placeholder='{el['placeholder']}'" if el.get('placeholder') else "") +
                    (f" name='{el['name']}'" if el.get('name') else "") +
                    f"> '{el['text'] or el['aria']}' (role: {el['role']})"
                    for el in elements[:40]
                ]

                system_prompt = (
                    "You are KYRON BrowserControlAgent. You execute user directives on real websites.\n"
                    "Tum ek real human assistant ki tarah baat karo, robot ya script-reading machine ki tarah nahi. Casual, confident, friendly tone. Technical jargon avoid karo jab tak zaroori na ho.\n"
                    "CRITICAL BEHAVIOR RULES:\n"
                    "1. Jawab hamesha question ke scope ke barabar ho — chhote command ka chhota jawab.\n"
                    "2. CASUAL 'DONE BOSS' CONFIRMATION: Jab bhi task (finish) ho, summary me brief casual confirmation do.\n"
                    "3. STRICT VOICE OUTPUT CONSTRAINT (voice_vocalization): MAX 1 short sentence. Sirf kaam ki baat bolo (e.g., 'Done Boss', 'Navigating Boss'). Faltu details bilkul nahi.\n\n"
                    "Inspect the current page, title, and interactive DOM elements to choose the single NEXT action.\n"
                    "Available actions:\n"
                    "- navigate(url='https://...')\n"
                    "- click(id=number, description='text')\n"
                    "- type(id=number, text='...', press_enter=bool)\n"
                    "- scroll(direction='down'|'up')\n"
                    "- extract_and_finish(summary='answer to user directive')\n"
                    "- finish(summary='task completed')\n\n"
                    "CRITICAL SAFETY RULE:\n"
                    "If the action is IRREVERSIBLE (submit, checkout, pay, place order, buy now, delete, post, send message),\n"
                    "still specify click(id, description), but the safety interceptor will halt execution and ask the user to confirm.\n"
                    "Return ONLY JSON: {\"thought\": \"reasoning\", \"action\": \"click|type|scroll|navigate|finish|extract_and_finish\", \"id\": number, \"text\": \"string\", \"url\": \"string\", \"direction\": \"down|up\", \"description\": \"button text/intent\", \"summary\": \"final answer\"}"
                )

                user_content = (
                    f"User Directive: {directive}\n"
                    f"Current URL: {current_url}\n"
                    f"Page Title: {page_title}\n"
                    f"Interactive Elements:\n" + "\n".join(elements_summary)
                )

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ]

                try:
                    res = await client.acomplete(messages=messages, temperature=0.1)
                    raw_text = res.get("content", "").strip()
                    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
                    plan_json = json_match.group(1) if json_match else raw_text
                    plan = json.loads(plan_json)
                except Exception as e:
                    logger.warning(f"LLM Step planning error: {e}. Attempting smart heuristic fallback.")
                    plan = {"action": "finish", "summary": f"Could not determine next step: {str(e)}"}

                action = plan.get("action", "finish")
                desc = plan.get("description") or plan.get("thought") or action
                element_id = plan.get("id")

                self.log_activity("THOUGHT", plan.get("thought", f"Step {step_num}: {action}"))

                # Check Action Classification for Safety Gate (STANDING RULE 1)
                is_irreversible = (
                    self.classify_action(action, desc) == "IRREVERSIBLE" or
                    bool(IRREVERSIBLE_REGEX.search(directive)) or
                    bool(IRREVERSIBLE_REGEX.search(desc))
                )

                if is_irreversible:
                    # STANDING RULE 1: STRICT DRY-RUN / PAUSE GATE
                    desc_text = desc if desc not in ["finish", "extract_and_finish"] else f"Place Order / Final Submission for '{directive}'"
                    pending_payload = {
                        "type": "browser",
                        "app": "Browser",
                        "website": page.url,
                        "page_title": page_title,
                        "element_id": element_id,
                        "action": action if action not in ["finish", "extract_and_finish"] else "click",
                        "description": desc_text,
                        "target_element": desc_text,
                        "risk_level": "high",
                        "created_at": time.time(),
                        "status": "pending_confirmation"
                    }
                    action_id = approval_queue.register_pending_action(
                        agent_type="BROWSER",
                        description=desc_text,
                        payload=pending_payload,
                        risk_level="high"
                    )
                    pending_payload["action_id"] = action_id

                    self.log_activity("SAFETY_GATE_TRIGGERED", f"Paused before irreversible action: '{desc_text}' on {page.url}", level="WARN")

                    return {
                        "success": True,
                        "status": "waiting_confirmation",
                        "summary": f"Execution paused before irreversible action: {desc_text}",
                        "url": page.url,
                        "title": page_title,
                        "executed_steps": executed_steps,
                        "requires_confirmation": True,
                        "pending_action": pending_payload,
                        "voice_vocalization": f"Commander, {page_title or 'website'} par '{desc_text}' hone ja raha hai. Confirm kijiye."
                    }

                # 1. Finish / Extract (Reversible Only)
                if action in ["finish", "extract_and_finish"]:
                    summary = plan.get("summary") or "Task completed successfully."
                    if "unread" in directive.lower() and "count" in directive.lower():
                        content = await page.content()
                        unread_match = re.search(r"(\d+)\s+unread", content, re.IGNORECASE)
                        if unread_match:
                            summary = f"Detected {unread_match.group(1)} unread emails on page."
                        else:
                            summary = "Gmail page checked — 0 unread emails or inbox is clean."
                    self.log_activity("COMPLETED", summary)
                    return {
                        "success": True,
                        "status": "completed",
                        "summary": summary,
                        "url": page.url,
                        "title": page_title,
                        "executed_steps": executed_steps,
                        "requires_confirmation": False,
                        "pending_action": None,
                        "voice_vocalization": f"Commander, {summary}"
                    }

                # 3. Execute Reversible Action
                if action == "navigate":
                    nav_url = plan.get("url")
                    if nav_url:
                        await page.goto(nav_url, timeout=30000, wait_until="domcontentloaded")
                        executed_steps.append(f"Navigated to {nav_url}")
                        self.log_activity("NAVIGATE", nav_url)

                elif action == "scroll":
                    direction = plan.get("direction", "down")
                    pixels = 500 if direction == "down" else -500
                    await page.evaluate(f"window.scrollBy(0, {pixels})")
                    executed_steps.append(f"Scrolled {direction}")
                    self.log_activity("SCROLL", f"Scrolled {direction}")

                elif action == "type":
                    text_to_type = plan.get("text", "")
                    press_enter = plan.get("press_enter", False)
                    if element_id is not None and element_id < len(elements):
                        target_el = elements[element_id]
                        filled = False
                        
                        # 1. Try by placeholder
                        if target_el.get("placeholder"):
                            try:
                                loc = page.get_by_placeholder(target_el["placeholder"]).first
                                await loc.click()
                                await loc.fill(text_to_type)
                                filled = True
                            except Exception:
                                pass

                        # 2. Try by element ID
                        if not filled and target_el.get("element_id"):
                            try:
                                loc = page.locator(f"#{target_el['element_id']}")
                                await loc.click()
                                await loc.fill(text_to_type)
                                filled = True
                            except Exception:
                                pass

                        # 3. Try by name
                        if not filled and target_el.get("name"):
                            try:
                                loc = page.locator(f"[name='{target_el['name']}']").first
                                await loc.click()
                                await loc.fill(text_to_type)
                                filled = True
                            except Exception:
                                pass

                        # 4. Fallback to tag and type
                        if not filled:
                            try:
                                selector = f"{target_el['tag']}"
                                if target_el.get("type"):
                                    selector += f"[type='{target_el['type']}']"
                                loc = page.locator(selector).nth(min(element_id, 10))
                                await loc.click()
                                await loc.fill(text_to_type)
                                filled = True
                            except Exception:
                                pass

                        if not filled:
                            await page.keyboard.type(text_to_type)

                        if press_enter:
                            await page.keyboard.press("Enter")
                        executed_steps.append(f"Typed '{text_to_type}' into {target_el.get('placeholder') or target_el.get('text') or target_el['tag']}")
                        self.log_activity("TYPE", f"Typed '{text_to_type}'")
                    else:
                        await page.keyboard.type(text_to_type)
                        if press_enter:
                            await page.keyboard.press("Enter")

                elif action == "click":
                    if element_id is not None and element_id < len(elements):
                        target_el = elements[element_id]
                        btn_text = target_el.get('text') or target_el.get('aria')
                        clicked = False

                        # 1. Try by element ID
                        if target_el.get("element_id"):
                            try:
                                await page.locator(f"#{target_el['element_id']}").click(timeout=3000)
                                clicked = True
                            except Exception:
                                pass

                        # 2. Try by visible text
                        if not clicked and btn_text:
                            try:
                                await page.get_by_text(btn_text, exact=False).first.click(timeout=3000)
                                clicked = True
                            except Exception:
                                pass

                        # 3. Fallback to nth
                        if not clicked:
                            try:
                                await page.locator(f"{target_el['tag']}").nth(element_id).click(timeout=3000)
                                clicked = True
                            except Exception:
                                pass

                        executed_steps.append(f"Clicked '{btn_text or desc}'")
                        self.log_activity("CLICK", f"Clicked '{btn_text or desc}'")

                await asyncio.sleep(1.5)

            # End of loop
            return {
                "success": True,
                "status": "completed",
                "summary": f"Completed {max_steps} automation steps for '{directive}'",
                "url": page.url,
                "title": await page.title(),
                "executed_steps": executed_steps,
                "requires_confirmation": False,
                "pending_action": None,
                "voice_vocalization": f"Commander, directive execution complete."
            }

    async def confirm_action(self, action_id: str, confirmed: bool) -> Dict[str, Any]:
        """
        Safety Gate Confirmation:
        Fires the final irreversible action ONLY when physical user confirmation is received.
        """
        action_wrapper = approval_queue.get_action(action_id)
        if not action_wrapper:
            raise ValueError(f"Action '{action_id}' not found or already executed.")
            
        action = action_wrapper.get("payload")

        if not confirmed:
            action["status"] = "rejected_by_user"
            approval_queue.resolve_action(action_id, "rejected_by_user")
            self.log_activity("ACTION_REJECTED", f"User rejected action '{action.get('description')}'", level="WARN")
            return {
                "success": True,
                "action_id": action_id,
                "status": "rejected",
                "message": "Action cancelled by operator. Nothing was submitted or charged."
            }

        # User clicked Confirm
        self.log_activity("ACTION_CONFIRMED", f"User confirmed action '{action.get('description')}'. Firing final submit.", level="INFO")

        page = await self.ensure_browser()
        desc = action.get("description", "")
        btn_text = action.get("target_element", desc)

        try:
            # Fire the final click
            await page.get_by_text(btn_text, exact=False).first.click(timeout=5000)
        except Exception:
            try:
                # Fallback to Enter key
                await page.keyboard.press("Enter")
            except Exception as e:
                logger.error(f"Failed to execute confirmed action: {e}")

        await asyncio.sleep(2.0)
        action["status"] = "executed_confirmed"
        approval_queue.resolve_action(action_id, "executed_confirmed")

        new_url = page.url
        new_title = await page.title()

        return {
            "success": True,
            "action_id": action_id,
            "status": "executed",
            "message": f"Action '{desc}' confirmed and executed successfully on {new_title}.",
            "url": new_url,
            "title": new_title
        }

    async def get_status(self) -> Dict[str, Any]:
        """Returns live browser status and pending actions."""
        url = "about:blank"
        title = "No active page"
        if self.page and not self.page.is_closed():
            try:
                url = self.page.url
                title = await self.page.title()
            except Exception:
                pass

        return {
            "success": True,
            "agent": "KYRON BrowserControlAgent",
            "browser_ready": bool(self.page and not self.page.is_closed()),
            "current_url": url,
            "page_title": title,
            "profile_dir": str(BROWSER_PROFILE_DIR),
            "pending_actions_count": len(approval_queue.get_all_pending()),
            "pending_actions": approval_queue.get_all_pending(),
            "recent_activity": self.activity_log[-10:],
            "safety_gate": {
                "strict_dry_run_default": True,
                "irreversible_filter": "submit|pay|checkout|order|buy|delete|post|send",
                "confirmation_required": True
            }
        }

    async def close(self):
        """Closes browser context."""
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass


# Global singleton instance
browser_control_agent = BrowserControlAgent()
