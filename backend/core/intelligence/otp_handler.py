"""
KYRON Intelligence - OTP Handler

Handles OTP-based authentication and pauses
Detects OTP input fields
Pauses execution and waits for user input
Resumes after OTP verification
"""

from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging
import re

logger = logging.getLogger(__name__)

class OTPStatus(Enum):
    """OTP status"""
    NOT_DETECTED = "not_detected"
    DETECTED = "detected"
    WAITING_INPUT = "waiting_input"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class OTPContext:
    """OTP context information"""
    otp_field_selector: str = ""
    otp_field_type: str = "text"  # text, number, tel
    otp_length: int = 6  # Expected OTP length
    otp_sent_to: str = ""  # Phone/Email where OTP was sent
    submit_button_selector: str = ""
    resend_button_selector: str = ""
    status: OTPStatus = OTPStatus.NOT_DETECTED
    detected_at: Optional[float] = None

class OTPHandler:
    """
    Handles OTP detection, pause, and verification
    """
    
    def __init__(self):
        self.otp_patterns = [
            r"otp",
            r"one.?time.?password",
            r"verification.?code",
            r"enter.?code",
            r"6.?digit.?code",
            r"verification.?otp"
        ]
        self.otp_field_selectors = [
            'input[name*="otp" i]',
            'input[id*="otp" i]',
            'input[name*="verification" i]',
            'input[id*="verification" i]',
            'input[name*="code" i]',
            'input[id*="code" i]',
            'input[placeholder*="otp" i]',
            'input[placeholder*="code" i]',
            'input[type="tel"][maxlength="6"]',
            'input[type="number"][maxlength="6"]',
            'input[pattern*="[0-9]"]'
        ]
    
    async def detect_otp_page(self, page) -> Tuple[bool, Optional[OTPContext]]:
        """
        Detect if current page is an OTP input page
        
        Returns:
            Tuple of (is_otp_page, OTPContext)
        """
        try:
            # Check page URL and title
            url = page.url.lower()
            title = (await page.title() or "").lower()
            
            # Check for OTP keywords
            is_otp_page = False
            for pattern in self.otp_patterns:
                if re.search(pattern, url) or re.search(pattern, title):
                    is_otp_page = True
                    break
            
            # Check for OTP input fields
            otp_field = None
            for selector in self.otp_field_selectors:
                try:
                    field = await page.query_selector(selector)
                    if field:
                        is_visible = await field.is_visible()
                        if is_visible:
                            otp_field = field
                            is_otp_page = True
                            break
                except:
                    continue
            
            if not is_otp_page:
                return (False, None)
            
            # Build OTP context
            context = OTPContext()
            context.status = OTPStatus.DETECTED
            
            if otp_field:
                field_id = await otp_field.get_attribute('id') or ""
                field_name = await otp_field.get_attribute('name') or ""
                field_type = await otp_field.get_attribute('type') or "text"
                maxlength = await otp_field.get_attribute('maxlength') or "6"
                placeholder = (await otp_field.get_attribute('placeholder') or "").lower()
                
                context.otp_field_selector = f"#{field_id}" if field_id else f'[name="{field_name}"]'
                context.otp_field_type = field_type
                context.otp_length = int(maxlength) if maxlength.isdigit() else 6
                
                # Try to find where OTP was sent
                page_text = (await page.text_content() or "").lower()
                if "phone" in page_text or "mobile" in page_text:
                    context.otp_sent_to = "phone"
                elif "email" in page_text or "mail" in page_text:
                    context.otp_sent_to = "email"
                
                # Find submit button
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Verify")',
                    'button:has-text("Submit")',
                    'button:has-text("Continue")',
                    'button:has-text("Confirm")'
                ]
                
                for selector in submit_selectors:
                    try:
                        btn = await page.query_selector(selector)
                        if btn and await btn.is_visible():
                            btn_id = await btn.get_attribute('id') or ""
                            context.submit_button_selector = f"#{btn_id}" if btn_id else selector
                            break
                    except:
                        continue
                
                # Find resend button
                resend_selectors = [
                    'button:has-text("Resend")',
                    'a:has-text("Resend")',
                    'button:has-text("Resend OTP")',
                    'a:has-text("Resend OTP")'
                ]
                
                for selector in resend_selectors:
                    try:
                        btn = await page.query_selector(selector)
                        if btn:
                            btn_id = await btn.get_attribute('id') or ""
                            context.resend_button_selector = f"#{btn_id}" if btn_id else selector
                            break
                    except:
                        continue
            
            context.detected_at = asyncio.get_event_loop().time()
            logger.info(f"OTP page detected: {context.otp_field_selector}")
            return (True, context)
            
        except Exception as e:
            logger.error(f"Error detecting OTP page: {e}")
            return (False, None)
    
    async def wait_for_otp_input(
        self,
        page,
        context: OTPContext,
        timeout: int = 300
    ) -> Tuple[bool, Optional[str]]:
        """
        Wait for user to enter OTP
        
        Returns:
            Tuple of (success, otp_value or error_message)
        """
        try:
            context.status = OTPStatus.WAITING_INPUT
            
            # Monitor OTP field for input
            start_time = asyncio.get_event_loop().time()
            
            while True:
                # Check timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout:
                    context.status = OTPStatus.EXPIRED
                    return (False, "OTP input timeout")
                
                # Check if OTP field has value
                try:
                    otp_field = await page.query_selector(context.otp_field_selector)
                    if otp_field:
                        otp_value = await otp_field.input_value()
                        if otp_value and len(otp_value.strip()) >= context.otp_length:
                            # OTP entered
                            context.status = OTPStatus.VERIFIED
                            logger.info(f"OTP entered: {len(otp_value)} digits")
                            return (True, otp_value.strip())
                except:
                    pass
                
                # Check if page changed (user might have submitted)
                try:
                    current_url = page.url
                    if "success" in current_url.lower() or "verified" in current_url.lower():
                        context.status = OTPStatus.VERIFIED
                        return (True, "verified")
                except:
                    pass
                
                # Wait before next check
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error waiting for OTP input: {e}")
            context.status = OTPStatus.FAILED
            return (False, str(e))
    
    async def verify_otp_submission(
        self,
        page,
        context: OTPContext
    ) -> Tuple[bool, Optional[str]]:
        """
        Verify OTP submission was successful
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Wait for page change or success message
            await asyncio.sleep(2)
            
            # Check URL
            url = page.url.lower()
            if "success" in url or "verified" in url or "confirmed" in url:
                context.status = OTPStatus.VERIFIED
                return (True, "OTP verified successfully")
            
            # Check page content
            page_text = (await page.text_content() or "").lower()
            success_indicators = [
                "verified",
                "success",
                "confirmed",
                "authentication successful"
            ]
            
            for indicator in success_indicators:
                if indicator in page_text:
                    context.status = OTPStatus.VERIFIED
                    return (True, f"OTP verified: {indicator}")
            
            # Check for error messages
            error_indicators = [
                "invalid",
                "incorrect",
                "wrong",
                "expired",
                "failed"
            ]
            
            for indicator in error_indicators:
                if indicator in page_text:
                    context.status = OTPStatus.FAILED
                    return (False, f"OTP verification failed: {indicator}")
            
            # If no clear indication, assume success if we're on a different page
            if context.detected_at:
                # Page likely changed
                context.status = OTPStatus.VERIFIED
                return (True, "OTP likely verified (page changed)")
            
            return (False, "Could not verify OTP status")
            
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return (False, str(e))
    
    async def handle_otp_flow(
        self,
        page,
        execution_controller: Any,
        timeout: int = 300
    ) -> Tuple[bool, Optional[str]]:
        """
        Complete OTP flow: detect, pause, wait, verify
        
        Returns:
            Tuple of (success, message)
        """
        # Detect OTP page
        is_otp_page, context = await self.detect_otp_page(page)
        
        if not is_otp_page or not context:
            return (False, "OTP page not detected")
        
        # Pause execution
        await execution_controller.pause("OTP input required")
        await execution_controller.wait_for_user(
            f"Please enter the {context.otp_length}-digit OTP sent to your {context.otp_sent_to or 'phone/email'}",
            "otp"
        )
        
        # Wait for user to enter OTP
        success, result = await self.wait_for_otp_input(page, context, timeout)
        
        if not success:
            await execution_controller.error(f"OTP input failed: {result}")
            return (False, result)
        
        # If OTP was entered, wait for submission
        if result and result != "verified":
            # Wait a bit for auto-submit or user to click submit
            await asyncio.sleep(2)
        
        # Verify OTP submission
        verify_success, verify_message = await self.verify_otp_submission(page, context)
        
        if verify_success:
            # Resume execution
            await execution_controller.resume()
            logger.info("OTP verified, execution resumed")
            return (True, verify_message)
        else:
            await execution_controller.error(f"OTP verification failed: {verify_message}")
            return (False, verify_message)

