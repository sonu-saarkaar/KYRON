"""
KYRON Brain - Intelligence Integration

Integrates OTP, Payment, and Multi-Tab intelligence into the brain
"""

from typing import Dict, Optional, Any, Tuple
import logging

from ..intelligence import OTPHandler, PaymentIntelligence, MultiTabManager

logger = logging.getLogger(__name__)

class IntelligenceIntegration:
    """
    Integrates all intelligence modules into KYRON brain
    """
    
    def __init__(self):
        self.otp_handler = OTPHandler()
        self.payment_intelligence = PaymentIntelligence()
        self.multi_tab_manager = MultiTabManager()
        logger.info("Intelligence modules initialized")
    
    async def check_and_handle_otp(
        self,
        page,
        execution_controller: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Check for OTP page and handle if detected
        
        Returns:
            Tuple of (otp_detected, message)
        """
        is_otp, context = await self.otp_handler.detect_otp_page(page)
        
        if is_otp:
            logger.info("OTP page detected, handling OTP flow")
            success, message = await self.otp_handler.handle_otp_flow(
                page,
                execution_controller
            )
            return (True, message)
        
        return (False, None)
    
    async def check_and_handle_payment(
        self,
        page,
        session_id: str,
        execution_controller: Any
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check for payment page and handle if detected
        
        Returns:
            Tuple of (payment_detected, payment_result)
        """
        is_payment, context = await self.payment_intelligence.detect_payment_page(
            page,
            session_id
        )
        
        if is_payment:
            logger.info("Payment page detected, handling payment flow")
            success, result = await self.payment_intelligence.handle_payment_flow(
                page,
                session_id,
                execution_controller
            )
            return (True, result)
        
        return (False, None)
    
    async def handle_new_tab(
        self,
        browser_context,
        session_id: str,
        execution_state: Any
    ) -> Optional[Any]:
        """
        Handle new tab that opened (e.g., after clicking Apply)
        
        Returns:
            Page object for new tab
        """
        new_page = await self.multi_tab_manager.handle_popup_tab(
            browser_context,
            session_id,
            execution_state
        )
        
        if new_page:
            logger.info(f"Switched to new tab: {new_page.url}")
        
        return new_page
    
    async def detect_and_switch_tabs(
        self,
        browser_context,
        session_id: str
    ) -> List[Any]:
        """
        Detect all new tabs and return them
        
        Returns:
            List of new page objects
        """
        new_pages = await self.multi_tab_manager.detect_new_tabs(
            browser_context,
            session_id,
            None
        )
        return new_pages
    
    def get_payment_context(self, session_id: str) -> Optional[Any]:
        """Get payment context for session"""
        return self.payment_intelligence.get_payment_context(session_id)
    
    def get_active_tab(self) -> Optional[Any]:
        """Get active tab context"""
        return self.multi_tab_manager.get_active_tab()

