"""
KYRON CORE BRAIN - Perception Layer (Digital Senses)

KYRON must "see" the page like a human:
- Analyze DOM structure
- Understand labels, placeholders, aria attributes
- Group fields logically
- Detect dynamic content loading
- Detect content in tabs, popups, modals, iframes
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PageType(Enum):
    """Types of pages"""
    FORM = "form"
    LOGIN = "login"
    PAYMENT = "payment"
    CONFIRMATION = "confirmation"
    ERROR = "error"
    LOADING = "loading"
    UNKNOWN = "unknown"

class FieldType(Enum):
    """Types of form fields"""
    TEXT = "text"
    EMAIL = "email"
    TEL = "tel"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    FILE = "file"
    BUTTON = "button"
    SUBMIT = "submit"

@dataclass
class FieldMetadata:
    """Metadata about a form field"""
    field_id: str
    field_type: FieldType
    label: str = ""
    placeholder: str = ""
    name: str = ""
    aria_label: str = ""
    aria_describedby: str = ""
    required: bool = False
    value: str = ""
    options: List[Dict[str, str]] = field(default_factory=list)  # For select/radio
    semantic_meaning: str = ""  # e.g., "first_name", "email", "date_of_birth"
    confidence: float = 0.0  # Confidence in semantic meaning
    selectors: List[str] = field(default_factory=list)  # Multiple selector options
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PageMetadata:
    """Complete metadata about a page"""
    url: str
    title: str
    page_type: PageType
    fields: List[FieldMetadata] = field(default_factory=list)
    buttons: List[Dict[str, Any]] = field(default_factory=list)
    forms: List[Dict[str, Any]] = field(default_factory=list)
    iframes: List[Dict[str, Any]] = field(default_factory=list)
    popups: List[Dict[str, Any]] = field(default_factory=list)
    tabs: List[Dict[str, Any]] = field(default_factory=list)
    is_loaded: bool = False
    has_dynamic_content: bool = False
    loading_indicators: List[str] = field(default_factory=list)

class PerceptionLayer:
    """
    KYRON's Digital Senses - Perception Layer
    
    Observes and understands page structure without assumptions
    """
    
    def __init__(self):
        self.semantic_mappings = self._initialize_semantic_mappings()
    
    def _initialize_semantic_mappings(self) -> Dict[str, List[str]]:
        """Initialize semantic meaning mappings"""
        return {
            "first_name": ["first name", "firstname", "fname", "given name", "forename"],
            "last_name": ["last name", "lastname", "lname", "surname", "family name"],
            "full_name": ["full name", "name", "applicant name", "your name"],
            "date_of_birth": ["date of birth", "dob", "birth date", "birthdate", "date of birth (dd/mm/yyyy)"],
            "email": ["email", "email address", "e-mail", "email id", "mail"],
            "phone": ["phone", "mobile", "phone number", "mobile number", "contact number", "telephone"],
            "address": ["address", "street address", "residential address", "permanent address"],
            "city": ["city", "town"],
            "state": ["state", "province"],
            "pincode": ["pincode", "pin code", "postal code", "zip code", "zip"],
            "father_name": ["father name", "father's name", "fathername", "father"],
            "mother_name": ["mother name", "mother's name", "mothername", "mother"],
            "aadhaar": ["aadhaar", "aadhar", "uid", "aadhaar number", "aadhar number"],
            "pan": ["pan", "pan number", "pan card number", "permanent account number"],
            "gender": ["gender", "sex"],
            "occupation": ["occupation", "profession", "income source", "employment"]
        }
    
    async def analyze_page(self, page) -> PageMetadata:
        """
        Analyze page and extract complete metadata
        
        Args:
            page: Playwright page object
            
        Returns:
            PageMetadata with all page information
        """
        try:
            # Get basic page info
            url = page.url
            title = await page.title()
            
            # Detect page type
            page_type = await self._detect_page_type(page, url, title)
            
            # Extract fields
            fields = await self._extract_fields(page)
            
            # Extract buttons
            buttons = await self._extract_buttons(page)
            
            # Extract forms
            forms = await self._extract_forms(page)
            
            # Detect iframes
            iframes = await self._extract_iframes(page)
            
            # Detect popups/modals
            popups = await self._detect_popups(page)
            
            # Detect tabs
            tabs = await self._detect_tabs(page)
            
            # Check for dynamic content
            has_dynamic_content = await self._check_dynamic_content(page)
            
            # Check loading state
            is_loaded = await self._check_page_loaded(page)
            
            metadata = PageMetadata(
                url=url,
                title=title,
                page_type=page_type,
                fields=fields,
                buttons=buttons,
                forms=forms,
                iframes=iframes,
                popups=popups,
                tabs=tabs,
                is_loaded=is_loaded,
                has_dynamic_content=has_dynamic_content
            )
            
            logger.info(f"Analyzed page: {page_type.value}, {len(fields)} fields, {len(buttons)} buttons")
            return metadata
            
        except Exception as e:
            logger.error(f"Error analyzing page: {e}")
            return PageMetadata(
                url=page.url if page else "",
                title="",
                page_type=PageType.UNKNOWN
            )
    
    async def _detect_page_type(self, page, url: str, title: str) -> PageType:
        """Detect type of page"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Check for payment
        if any(keyword in url_lower or keyword in title_lower for keyword in ["payment", "pay", "gateway", "checkout"]):
            return PageType.PAYMENT
        
        # Check for login
        if any(keyword in url_lower or keyword in title_lower for keyword in ["login", "sign in", "authenticate"]):
            return PageType.LOGIN
        
        # Check for confirmation
        if any(keyword in url_lower or keyword in title_lower for keyword in ["success", "confirmation", "acknowledgement", "thank you"]):
            return PageType.CONFIRMATION
        
        # Check for error
        if any(keyword in url_lower or keyword in title_lower for keyword in ["error", "failed", "invalid"]):
            return PageType.ERROR
        
        # Check for form
        try:
            forms = await page.query_selector_all('form')
            if forms:
                return PageType.FORM
        except:
            pass
        
        return PageType.UNKNOWN
    
    async def _extract_fields(self, page) -> List[FieldMetadata]:
        """Extract all form fields from page"""
        fields = []
        
        try:
            # Get all input elements
            inputs = await page.query_selector_all('input, select, textarea')
            
            for idx, element in enumerate(inputs):
                try:
                    field_meta = await self._analyze_field(element, page, idx)
                    if field_meta:
                        fields.append(field_meta)
                except Exception as e:
                    logger.debug(f"Error analyzing field {idx}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error extracting fields: {e}")
        
        return fields
    
    async def _analyze_field(self, element, page, index: int) -> Optional[FieldMetadata]:
        """Analyze a single field element"""
        try:
            # Get basic attributes
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            field_type_attr = await element.get_attribute('type') or ""
            field_id = await element.get_attribute('id') or f"field_{index}"
            field_name = await element.get_attribute('name') or ""
            placeholder = await element.get_attribute('placeholder') or ""
            aria_label = await element.get_attribute('aria-label') or ""
            required = await element.evaluate("el => el.required || el.hasAttribute('required')")
            value = await element.input_value() if tag_name != "select" else ""
            
            # Determine field type
            if tag_name == "select":
                field_type = FieldType.SELECT
                # Get options
                options = []
                option_elements = await element.query_selector_all('option')
                for opt in option_elements:
                    opt_text = await opt.text_content() or ""
                    opt_value = await opt.get_attribute('value') or opt_text
                    options.append({"text": opt_text, "value": opt_value})
            elif tag_name == "textarea":
                field_type = FieldType.TEXTAREA
                options = []
            elif field_type_attr == "radio":
                field_type = FieldType.RADIO
                options = []
            elif field_type_attr == "checkbox":
                field_type = FieldType.CHECKBOX
                options = []
            elif field_type_attr == "file":
                field_type = FieldType.FILE
                options = []
            elif field_type_attr == "email":
                field_type = FieldType.EMAIL
                options = []
            elif field_type_attr == "tel":
                field_type = FieldType.TEL
                options = []
            elif field_type_attr == "number":
                field_type = FieldType.NUMBER
                options = []
            elif field_type_attr == "date":
                field_type = FieldType.DATE
                options = []
            else:
                field_type = FieldType.TEXT
                options = []
            
            # Find label
            label = ""
            if field_id:
                label_elem = await page.query_selector(f'label[for="{field_id}"]')
                if label_elem:
                    label = await label_elem.text_content() or ""
            
            # If no label found, try parent label
            if not label:
                parent = await element.evaluate_handle("el => el.closest('label')")
                if parent:
                    label = await parent.text_content() or ""
            
            # Determine semantic meaning
            semantic_meaning, confidence = self._determine_semantic_meaning(
                label, placeholder, field_name, field_id
            )
            
            # Generate selectors
            selectors = self._generate_selectors(field_id, field_name, field_type, label)
            
            return FieldMetadata(
                field_id=field_id,
                field_type=field_type,
                label=label.strip(),
                placeholder=placeholder,
                name=field_name,
                aria_label=aria_label,
                required=required,
                value=value,
                options=options,
                semantic_meaning=semantic_meaning,
                confidence=confidence,
                selectors=selectors
            )
        except Exception as e:
            logger.debug(f"Error analyzing field: {e}")
            return None
    
    def _determine_semantic_meaning(self, label: str, placeholder: str, name: str, field_id: str) -> Tuple[str, float]:
        """
        Determine semantic meaning of a field
        
        Returns:
            Tuple of (semantic_meaning, confidence)
        """
        text = f"{label} {placeholder} {name} {field_id}".lower()
        
        best_match = None
        best_confidence = 0.0
        
        for semantic, keywords in self.semantic_mappings.items():
            matches = sum(1 for keyword in keywords if keyword in text)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = semantic
        
        return (best_match or "", best_confidence)
    
    def _generate_selectors(self, field_id: str, field_name: str, field_type: FieldType, label: str) -> List[str]:
        """Generate multiple selector options for a field"""
        selectors = []
        
        # ID selector (highest priority)
        if field_id:
            selectors.append(f"#{field_id}")
        
        # Name selector
        if field_name:
            selectors.append(f'[name="{field_name}"]')
        
        # Label-based selector
        if label:
            # Try exact label match
            selectors.append(f'label:has-text("{label}")')
            # Try input near label
            selectors.append(f'input:near(label:has-text("{label}"))')
        
        # Type-based selectors
        if field_type == FieldType.EMAIL:
            selectors.append('input[type="email"]')
        elif field_type == FieldType.TEL:
            selectors.append('input[type="tel"]')
        elif field_type == FieldType.DATE:
            selectors.append('input[type="date"]')
        elif field_type == FieldType.SELECT:
            selectors.append('select')
        
        return selectors
    
    async def _extract_buttons(self, page) -> List[Dict[str, Any]]:
        """Extract all buttons from page"""
        buttons = []
        
        try:
            button_elements = await page.query_selector_all('button, input[type="submit"], input[type="button"], a[role="button"]')
            
            for btn in button_elements:
                try:
                    text = await btn.text_content() or ""
                    btn_type = await btn.get_attribute('type') or ""
                    btn_id = await btn.get_attribute('id') or ""
                    btn_class = await btn.get_attribute('class') or ""
                    is_disabled = await btn.evaluate("el => el.disabled")
                    
                    buttons.append({
                        "text": text.strip(),
                        "type": btn_type,
                        "id": btn_id,
                        "class": btn_class,
                        "disabled": is_disabled,
                        "selector": f"#{btn_id}" if btn_id else f'button:has-text("{text}")'
                    })
                except:
                    continue
        except Exception as e:
            logger.error(f"Error extracting buttons: {e}")
        
        return buttons
    
    async def _extract_forms(self, page) -> List[Dict[str, Any]]:
        """Extract all forms from page"""
        forms = []
        
        try:
            form_elements = await page.query_selector_all('form')
            
            for form in form_elements:
                try:
                    form_id = await form.get_attribute('id') or ""
                    form_action = await form.get_attribute('action') or ""
                    form_method = await form.get_attribute('method') or "get"
                    
                    forms.append({
                        "id": form_id,
                        "action": form_action,
                        "method": form_method
                    })
                except:
                    continue
        except Exception as e:
            logger.error(f"Error extracting forms: {e}")
        
        return forms
    
    async def _extract_iframes(self, page) -> List[Dict[str, Any]]:
        """Extract all iframes from page"""
        iframes = []
        
        try:
            iframe_elements = await page.query_selector_all('iframe')
            
            for iframe in iframe_elements:
                try:
                    iframe_src = await iframe.get_attribute('src') or ""
                    iframe_id = await iframe.get_attribute('id') or ""
                    
                    iframes.append({
                        "id": iframe_id,
                        "src": iframe_src
                    })
                except:
                    continue
        except Exception as e:
            logger.error(f"Error extracting iframes: {e}")
        
        return iframes
    
    async def _detect_popups(self, page) -> List[Dict[str, Any]]:
        """Detect popups and modals"""
        popups = []
        
        try:
            # Check for common modal/popup patterns
            modal_selectors = [
                '[role="dialog"]',
                '.modal',
                '.popup',
                '[class*="modal"]',
                '[class*="popup"]',
                '[id*="modal"]',
                '[id*="popup"]'
            ]
            
            for selector in modal_selectors:
                elements = await page.query_selector_all(selector)
                for elem in elements:
                    try:
                        is_visible = await elem.is_visible()
                        if is_visible:
                            text = await elem.text_content() or ""
                            popups.append({
                                "selector": selector,
                                "text": text[:100],
                                "visible": is_visible
                            })
                    except:
                        continue
        except Exception as e:
            logger.error(f"Error detecting popups: {e}")
        
        return popups
    
    async def _detect_tabs(self, page) -> List[Dict[str, Any]]:
        """Detect browser tabs"""
        # This would be handled by the browser context
        # Return empty for now, actual tab detection is in execution layer
        return []
    
    async def _check_dynamic_content(self, page) -> bool:
        """Check if page has dynamic content loading"""
        try:
            # Check for common loading indicators
            loading_selectors = [
                '[class*="loading"]',
                '[class*="spinner"]',
                '[id*="loading"]',
                '[aria-busy="true"]'
            ]
            
            for selector in loading_selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    return True
            
            return False
        except:
            return False
    
    async def _check_page_loaded(self, page) -> bool:
        """Check if page is fully loaded"""
        try:
            # Wait for network idle
            await page.wait_for_load_state('networkidle', timeout=5000)
            return True
        except:
            return False

