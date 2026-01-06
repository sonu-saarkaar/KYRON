"""
KYRON Payment Detection
Detects payment pages and handles payment flow
"""

import re
from typing import Dict, Optional, List

class PaymentDetector:
    """Detects payment pages and payment-related elements"""
    
    # Payment page indicators
    PAYMENT_KEYWORDS = [
        "payment", "pay", "payment gateway", "pay now", "proceed to pay",
        "amount", "fee", "charges", "total", "rupees", "rs.", "₹",
        "upi", "net banking", "card", "debit", "credit", "wallet",
        "razorpay", "payu", "paytm", "phonepe", "google pay"
    ]
    
    # Payment form selectors
    PAYMENT_SELECTORS = [
        'input[name*="payment" i]',
        'input[name*="pay" i]',
        'input[name*="amount" i]',
        'input[name*="fee" i]',
        'button:has-text("Pay")',
        'button:has-text("Payment")',
        'button:has-text("Proceed to Pay")',
        'a:has-text("Pay")',
        'a:has-text("Payment")',
        'iframe[src*="payment"]',
        'iframe[src*="pay"]',
        'iframe[src*="razorpay"]',
        'iframe[src*="payu"]',
        'iframe[src*="paytm"]',
        '[class*="payment"]',
        '[id*="payment"]'
    ]
    
    @staticmethod
    def is_payment_page(page_url: str, page_title: str, page_content: str) -> bool:
        """
        Check if current page is a payment page
        
        Args:
            page_url: Current page URL
            page_title: Page title
            page_content: Page HTML content (lowercase)
            
        Returns:
            True if payment page detected
        """
        url_lower = page_url.lower()
        title_lower = page_title.lower()
        content_lower = page_content.lower()
        
        # Check URL
        if any(keyword in url_lower for keyword in ["payment", "pay", "gateway", "checkout"]):
            return True
        
        # Check title
        if any(keyword in title_lower for keyword in PaymentDetector.PAYMENT_KEYWORDS):
            return True
        
        # Check content
        payment_matches = sum(1 for keyword in PaymentDetector.PAYMENT_KEYWORDS if keyword in content_lower)
        if payment_matches >= 3:  # At least 3 payment keywords
            return True
        
        return False
    
    @staticmethod
    async def detect_payment_elements(page) -> List[Dict]:
        """
        Detect payment-related elements on the page
        
        Returns:
            List of payment element info
        """
        payment_elements = []
        
        try:
            # Check for payment buttons
            pay_buttons = await page.query_selector_all('button, a, input[type="submit"]')
            for btn in pay_buttons:
                try:
                    text = (await btn.text_content() or "").lower()
                    if any(keyword in text for keyword in ["pay", "payment", "proceed to pay"]):
                        payment_elements.append({
                            "type": "button",
                            "text": await btn.text_content(),
                            "selector": await btn.evaluate("el => el.tagName + (el.id ? '#' + el.id : '') + (el.className ? '.' + el.className.split(' ')[0] : '')")
                        })
                except:
                    pass
            
            # Check for payment iframes
            iframes = await page.query_selector_all('iframe')
            for iframe in iframes:
                try:
                    src = await iframe.get_attribute('src') or ""
                    if any(keyword in src.lower() for keyword in ["payment", "pay", "gateway"]):
                        payment_elements.append({
                            "type": "iframe",
                            "src": src
                        })
                except:
                    pass
        except Exception as e:
            print(f"Error detecting payment elements: {e}")
        
        return payment_elements
    
    @staticmethod
    async def wait_for_payment_completion(page, timeout: int = 300) -> Optional[Dict]:
        """
        Wait for payment completion and detect success/failure
        
        Returns:
            Dict with payment status and details, or None if timeout
        """
        try:
            # Wait for URL change or success message
            success_indicators = [
                "success", "successful", "completed", "acknowledgement",
                "application number", "reference", "transaction id"
            ]
            
            failure_indicators = [
                "failed", "error", "declined", "cancelled", "timeout"
            ]
            
            # Monitor page for changes
            for _ in range(timeout // 2):  # Check every 2 seconds
                await page.wait_for_timeout(2000)
                
                # Check URL
                current_url = page.url.lower()
                if any(indicator in current_url for indicator in success_indicators):
                    return {
                        "status": "success",
                        "url": page.url,
                        "detected_at": "url_change"
                    }
                
                # Check page content
                try:
                    page_text = (await page.text_content() or "").lower()
                    if any(indicator in page_text for indicator in success_indicators):
                        return {
                            "status": "success",
                            "url": page.url,
                            "detected_at": "page_content"
                        }
                    elif any(indicator in page_text for indicator in failure_indicators):
                        return {
                            "status": "failed",
                            "url": page.url,
                            "detected_at": "page_content"
                        }
                except:
                    pass
                
                # Check for application number or reference
                try:
                    app_number_pattern = re.compile(r'(application|reference|transaction)[\s#:]*([A-Z0-9]{8,})', re.IGNORECASE)
                    page_text = await page.text_content() or ""
                    match = app_number_pattern.search(page_text)
                    if match:
                        return {
                            "status": "success",
                            "application_number": match.group(2),
                            "url": page.url,
                            "detected_at": "application_number"
                        }
                except:
                    pass
            
            return None  # Timeout
        except Exception as e:
            print(f"Error waiting for payment completion: {e}")
            return None
