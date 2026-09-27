"""
KYRON Intelligence - Payment Intelligence

Enhanced payment detection and handling
Integrates with payment_detector
Handles payment flow with state preservation
"""

from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

from services.payment_detector import PaymentDetector

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Payment status"""
    NOT_DETECTED = "not_detected"
    DETECTED = "detected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PaymentContext:
    """Payment context information"""
    payment_url: str = ""
    payment_gateway: str = ""  # razorpay, payu, paytm, etc.
    amount: str = ""
    payment_elements: list = None
    status: PaymentStatus = PaymentStatus.NOT_DETECTED
    detected_at: Optional[float] = None
    application_number: Optional[str] = None
    reference_id: Optional[str] = None

class PaymentIntelligence:
    """
    Enhanced payment intelligence with state management
    """
    
    def __init__(self):
        self.payment_detector = PaymentDetector()
        self.active_payments: Dict[str, PaymentContext] = {}
    
    async def detect_payment_page(
        self,
        page,
        session_id: str
    ) -> Tuple[bool, Optional[PaymentContext]]:
        """
        Detect payment page with enhanced intelligence
        
        Returns:
            Tuple of (is_payment_page, PaymentContext)
        """
        try:
            url = page.url
            title = await page.title()
            content = (await page.text_content() or "").lower()
            
            # Use payment detector
            is_payment = self.payment_detector.is_payment_page(url, title, content)
            
            if not is_payment:
                return (False, None)
            
            # Build payment context
            context = PaymentContext()
            context.payment_url = url
            context.status = PaymentStatus.DETECTED
            context.detected_at = asyncio.get_event_loop().time()
            
            # Detect payment gateway
            url_lower = url.lower()
            if "razorpay" in url_lower:
                context.payment_gateway = "razorpay"
            elif "payu" in url_lower:
                context.payment_gateway = "payu"
            elif "paytm" in url_lower:
                context.payment_gateway = "paytm"
            elif "phonepe" in url_lower:
                context.payment_gateway = "phonepe"
            elif "googlepay" in url_lower or "gpay" in url_lower:
                context.payment_gateway = "googlepay"
            else:
                context.payment_gateway = "unknown"
            
            # Extract amount
            try:
                amount_patterns = [
                    r'₹\s*(\d+(?:\.\d{2})?)',
                    r'rs\.?\s*(\d+(?:\.\d{2})?)',
                    r'amount[:\s]*₹?\s*(\d+(?:\.\d{2})?)',
                    r'total[:\s]*₹?\s*(\d+(?:\.\d{2})?)'
                ]
                import re
                for pattern in amount_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        context.amount = match.group(1)
                        break
            except:
                pass
            
            # Get payment elements
            payment_elements = await self.payment_detector.detect_payment_elements(page)
            context.payment_elements = payment_elements
            
            # Store context
            self.active_payments[session_id] = context
            
            logger.info(f"Payment page detected: {context.payment_gateway}, Amount: {context.amount}")
            return (True, context)
            
        except Exception as e:
            logger.error(f"Error detecting payment page: {e}")
            return (False, None)
    
    async def handle_payment_flow(
        self,
        page,
        session_id: str,
        execution_controller: Any,
        timeout: int = 600
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Handle complete payment flow with state preservation
        
        Returns:
            Tuple of (success, payment_result)
        """
        # Detect payment page
        is_payment, context = await self.detect_payment_page(page, session_id)
        
        if not is_payment or not context:
            return (False, None)
        
        # Update status
        context.status = PaymentStatus.IN_PROGRESS
        
        # Pause execution
        await execution_controller.pause("Payment page detected - waiting for payment completion")
        await execution_controller.wait_for_user(
            f"Please complete payment of ₹{context.amount or 'N/A'} using {context.payment_gateway or 'payment gateway'}",
            "payment"
        )
        
        # Wait for payment completion
        payment_result = await self.payment_detector.wait_for_payment_completion(page, timeout)
        
        if payment_result and payment_result.get("status") == "success":
            context.status = PaymentStatus.COMPLETED
            context.application_number = payment_result.get("application_number")
            context.reference_id = payment_result.get("reference_id")
            
            # Resume execution
            await execution_controller.resume()
            
            result = {
                "status": "success",
                "application_number": context.application_number,
                "reference_id": context.reference_id,
                "payment_gateway": context.payment_gateway,
                "amount": context.amount
            }
            
            logger.info(f"Payment completed: {result}")
            return (True, result)
        else:
            context.status = PaymentStatus.FAILED
            await execution_controller.error("Payment failed or cancelled")
            
            result = {
                "status": "failed",
                "message": payment_result.get("message", "Payment failed") if payment_result else "Payment timeout"
            }
            
            return (False, result)
    
    def get_payment_context(self, session_id: str) -> Optional[PaymentContext]:
        """Get payment context for session"""
        return self.active_payments.get(session_id)
    
    def clear_payment_context(self, session_id: str):
        """Clear payment context"""
        if session_id in self.active_payments:
            del self.active_payments[session_id]

