"""
KYRON Form 49A Automation Engine
Fail-safe step-based automation with pause/resume and missing data handling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    COMPLETED = "completed"
    WAITING_USER = "waiting_user"
    SKIPPED = "skipped"
    ERROR = "error"

class AutomationStatus(Enum):
    """Overall automation status"""
    RUNNING = "running"
    WAITING_FOR_USER = "waiting_for_user"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"

class Form49AStep:
    """Represents a single step in Form 49A workflow"""
    
    def __init__(
        self,
        step_id: str,
        step_name: str,
        required: bool = True,
        profile_field: Optional[str] = None,
        selectors: List[str] = None,
        field_type: str = "text",
        validation_func: Optional[callable] = None
    ):
        self.step_id = step_id
        self.step_name = step_name
        self.required = required
        self.profile_field = profile_field
        self.selectors = selectors or []
        self.field_type = field_type
        self.validation_func = validation_func
        
        self.status = StepStatus.PENDING
        self.retry_count = 0
        self.error_message = None
        self.filled_value = None
        self.completed_at = None

class Form49AAutomationEngine:
    """
    Fail-safe Form 49A automation engine with step-based workflow
    """
    
    def __init__(self, page, user_profile: Dict, service_config: Dict = None, user_id: str = None):
        self.page = page
        self.active_page = page  # Will be set to iframe if found, otherwise main page
        self.iframe_page = None  # Store iframe reference if form is in iframe
        self.user_profile = user_profile
        self.service_config = service_config or {}
        self.user_id = user_id
        self.current_step_index = 0
        self.status = AutomationStatus.RUNNING
        self.steps: List[Form49AStep] = []
        self.waiting_for_field = None
        self.session_data = {}
        
        # Initialize Data Aggregator for intelligent data combination
        try:
            from services.data_aggregator import DataAggregator
            self.data_aggregator = DataAggregator(user_id) if user_id else None
            if self.data_aggregator:
                self.data_aggregator.load_master_profile()
                self.data_aggregator.load_document_vault()
                self.data_aggregator.set_request_data(service_config)
        except Exception as e:
            logger.warning(f"Could not initialize Data Aggregator: {e}")
            self.data_aggregator = None
        
        # Log received data for debugging
        logger.info("="*60)
        logger.info("Form 49A Automation Engine Initialized")
        logger.info(f"Service Config (Request Data): {self.service_config}")
        logger.info(f"User Profile Keys: {list(self.user_profile.keys())}")
        if self.data_aggregator:
            unified = self.data_aggregator.get_unified_data()
            logger.info(f"Unified Data (Request + Master + Documents): {len([k for k in unified.keys() if not k.startswith('_')])} fields")
        logger.info(f"Initial Page URL: {page.url if page else 'None'}")
        logger.info("="*60)
        
        # Initialize Form 49A steps
        self._initialize_steps()

    async def _force_first_page_defaults(self):
        """
        Some portals ignore generic mapping. Force-select safest defaults on first page:
        - Delivery: Based on user's delivery_type preference (Digital/ePAN or Physical)
        - Applicant Status: Individual (NOT Artificial Judicial Person)
        - PAN Card Mode: Based on delivery_type (e-PAN only for Digital, Both for Physical)
        
        CRITICAL: This function respects user choices from service_config/user_profile
        """
        page = self.active_page or self.page
        if not page:
            return
        
        # Get user's delivery type preference
        delivery_type = self.get_profile_value("delivery_type")
        delivery_str = str(delivery_type).lower() if delivery_type else "digital"
        logger.info(f"[FORCE DEFAULTS] User's delivery_type preference: {delivery_str}")

        async def safe_click(selectors: List[str]):
            for sel in selectors:
                try:
                    el = await page.query_selector(sel)
                    if el:
                        await el.click()
                        await asyncio.sleep(0.3)
                        return True
                except Exception:
                    continue
            return False

        async def select_dropdown(selectors: List[str], option_text_targets: List[str]):
            for sel in selectors:
                try:
                    el = await page.query_selector(sel)
                    if not el:
                        continue
                    options = await el.query_selector_all("option")
                    for opt in options:
                        text = (await opt.inner_text() or "").strip().lower()
                        val = (await opt.get_attribute("value") or "").strip().lower()
                        for target in option_text_targets:
                            if target in text or target in val:
                                await el.select_option(value=await opt.get_attribute("value"))
                                await asyncio.sleep(0.3)
                                return True
                except Exception:
                    continue
            return False

        # Delivery mode: Based on user preference (Digital/ePAN or Physical)
        if "physical" in delivery_str:
            logger.info("[FORCE DEFAULTS] Selecting Physical Mode (user preference)")
            await safe_click([
                "text=Physical Mode",
                "label:has-text('Physical Mode')",
                "label:has-text('Physical')",
                "input[type='radio'][value*='physical' i]",
                "input[type='radio'][id*='physical' i]",
            ])
        else:
            # Default to Digital/ePAN
            logger.info("[FORCE DEFAULTS] Selecting Digital Mode (user preference or default)")
            await safe_click([
                "text=Digital Mode",
                "label:has-text('Digital Mode')",
                "label:has-text('Digital')",
                "label:has-text('e-PAN')",
                "input[type='radio'][value*='digital' i]",
                "input[type='radio'][value*='epan' i]",
                "input[type='radio'][id*='digital' i]",
                "input[type='radio'][id*='epan' i]",
            ])

        # Applicant status: Individual (JS fallback if select_option fails)
        # CRITICAL: Must select exact "Individual", NOT "Artificial Judicial Person"
        try:
            await page.evaluate("""
                (() => {
                    const selects = Array.from(document.querySelectorAll('select'));
                    for (const sel of selects) {
                        const html = (sel.outerHTML || '').toLowerCase();
                        if (html.includes('status') || html.includes('applicant')) {
                            // First, try exact match "Individual"
                            for (const opt of Array.from(sel.options)) {
                                const t = (opt.textContent || '').trim().toLowerCase();
                                if (t === 'individual') {
                                    sel.value = opt.value;
                                    sel.dispatchEvent(new Event('change', {bubbles:true}));
                                    return;
                                }
                            }
                            // If no exact match, try "Individual" that doesn't contain "artificial" or "judicial"
                            for (const opt of Array.from(sel.options)) {
                                const t = (opt.textContent || '').trim().toLowerCase();
                                if (t.startsWith('individual') && 
                                    !t.includes('artificial') && 
                                    !t.includes('judicial')) {
                                    sel.value = opt.value;
                                    sel.dispatchEvent(new Event('change', {bubbles:true}));
                                    return;
                                }
                            }
                        }
                    }
                })();
            """)
        except:
            await select_dropdown(
                [
                    "select[name*='status' i]",
                    "select[id*='status' i]",
                    "select:has(option:has-text('Individual'))",
                ],
                ["individual"]
            )

        # PAN card mode: Based on delivery_type preference
        if "physical" in delivery_str:
            logger.info("[FORCE DEFAULTS] Selecting 'Both physical PAN Card and e-PAN' (Physical mode)")
            await safe_click([
                "label:has-text('Both physical PAN Card and e-PAN')",
                "label:has-text('Both')",
                "text=Both physical PAN Card and e-PAN",
                "input[type='radio'][value*='both' i]",
            ])
        else:
            # Digital/ePAN mode: select e-PAN only
            logger.info("[FORCE DEFAULTS] Selecting 'e-PAN only' (Digital mode)")
            await safe_click([
                "label:has-text('e-PAN only')",
                "label:has-text('No physical PAN Card')",
                "label:has-text('e-PAN only, No physical PAN Card')",
                "label:has-text('e-PAN')",
                "text=e-PAN only",
                "input[type='radio'][value*='epan' i]",
                "input[type='radio'][id*='epan' i]",
            ])
    
    def _initialize_steps(self):
        """Initialize all Form 49A steps"""
        
        # STEP_01: PAN Type (Digital / Physical) - Physical Mode by default
        self.steps.append(Form49AStep(
            step_id="STEP_01",
            step_name="PAN Type Selection",
            required=True,
            profile_field="delivery_type",
            selectors=[
                'input[type="radio"][value*="physical" i]',
                'input[type="radio"][value*="Physical" i]',
                'label:has-text("Physical Mode")',
                'label:has-text("Physical")',
                'input[type="radio"]:near(label:has-text("Physical"))',
                'input[type="radio"][name*="mode" i]',
                'input[type="radio"][name*="pan" i]',
                'input[type="radio"][id*="physical" i]',
                'input[type="radio"][id*="digital" i]'
            ],
            field_type="radio"
        ))
        
        # STEP_01B: Digital Mode Sub-options (only if Digital Mode selected)
        # This step will be conditionally executed
        self.steps.append(Form49AStep(
            step_id="STEP_01B",
            step_name="Digital Mode Option",
            required=False,
            profile_field="digital_mode_option",
            selectors=[
                'input[type="radio"][value*="ekyc" i]',
                'input[type="radio"][value*="esign" i]',
                'input[type="radio"][value*="dsc" i]',
                'label:has-text("Aadhaar based e-KYC")',
                'label:has-text("eSign Mode")',
                'label:has-text("DSC Mode")',
                'input[type="radio"][name*="digital" i]',
                'input[type="radio"][id*="ekyc" i]',
                'input[type="radio"][id*="esign" i]',
                'input[type="radio"][id*="dsc" i]'
            ],
            field_type="radio"
        ))
        
        # STEP_02: Applicant Type (Individual / Company) - Must be Individual
        # CRITICAL: Do NOT include "Artificial Judicial Person" in selectors - it might match first
        self.steps.append(Form49AStep(
            step_id="STEP_02",
            step_name="Status of the Applicant",
            required=True,
            profile_field="applicant_type",
            selectors=[
                'select[name*="status" i]',
                'select[id*="status" i]',
                'select:has(option:has-text("Individual"))',
                'select:has(option:has-text("individual"))',
                'select[name*="applicant" i]',
                'select[id*="applicant" i]',
                'select[name*="category" i]',
                'select[id*="category" i]',
                'select[title*="Status" i]',
                'select[title*="Applicant" i]'
            ],
            field_type="select"
        ))
        
        # STEP_02B: PAN CARD Mode (Both physical PAN Card and e-PAN / e-PAN only)
        self.steps.append(Form49AStep(
            step_id="STEP_02B",
            step_name="PAN CARD Mode",
            required=True,
            profile_field="pan_card_mode",
            selectors=[
                'input[type="radio"][value*="both" i]',
                'input[type="radio"][value*="epan" i]',
                'input[type="radio"][value*="physical" i]',
                'label:has-text("Both physical PAN Card and e-PAN")',
                'label:has-text("e-PAN only")',
                'label:has-text("No physical PAN Card")',
                'input[type="radio"][name*="pan.*mode" i]',
                'input[type="radio"][id*="pan.*mode" i]',
                'input[type="radio"][name*="epan" i]',
                'input[type="radio"][id*="epan" i]'
            ],
            field_type="radio"
        ))
        
        # STEP_03: Name Title (Mr/Mrs/Ms)
        self.steps.append(Form49AStep(
            step_id="STEP_03",
            step_name="Name Title",
            required=True,
            profile_field="nameTitle",
            selectors=[
                'select[name*="title" i]',
                'select[id*="title" i]',
                'select[name*="salutation" i]',
                'option:has-text("Mr")',
                'option:has-text("Mrs")',
                'option:has-text("Ms")'
            ],
            field_type="select"
        ))
        
        # STEP_03A: First Name
        self.steps.append(Form49AStep(
            step_id="STEP_03A",
            step_name="First Name",
            required=True,
            profile_field="firstName",
            selectors=[
                'input[name*="first" i][name*="name" i]',
                'input[id*="first" i][id*="name" i]',
                'input[name*="firstname" i]',
                'input[id*="firstname" i]',
                'input[placeholder*="first name" i]',
                'input[placeholder*="First Name" i]'
            ],
            field_type="text"
        ))
        
        # STEP_03B: Middle Name (optional)
        self.steps.append(Form49AStep(
            step_id="STEP_03B",
            step_name="Middle Name",
            required=False,
            profile_field="middleName",
            selectors=[
                'input[name*="middle" i][name*="name" i]',
                'input[id*="middle" i][id*="name" i]',
                'input[name*="middlename" i]',
                'input[id*="middlename" i]',
                'input[placeholder*="middle name" i]'
            ],
            field_type="text"
        ))
        
        # STEP_03C: Last Name/Surname
        self.steps.append(Form49AStep(
            step_id="STEP_03C",
            step_name="Last Name",
            required=True,
            profile_field="lastName",
            selectors=[
                'input[name*="last" i][name*="name" i]',
                'input[name*="surname" i]',
                'input[id*="last" i][id*="name" i]',
                'input[id*="surname" i]',
                'input[placeholder*="last name" i]',
                'input[placeholder*="surname" i]'
            ],
            field_type="text"
        ))
        
        # STEP_04: Parent Selection (Father / Mother)
        self.steps.append(Form49AStep(
            step_id="STEP_04",
            step_name="Parent Name Selection",
            required=True,
            profile_field="fatherName",
            selectors=[
                'input[type="radio"][name*="parent"]',
                'input[type="radio"][name*="father"]',
                'input[type="radio"][name*="mother"]',
                'label:has-text("Father")',
                'label:has-text("Mother")'
            ],
            field_type="radio"
        ))
        
        # STEP_05: Parent Name
        self.steps.append(Form49AStep(
            step_id="STEP_05",
            step_name="Parent Name",
            required=True,
            profile_field="fatherName",
            selectors=[
                'input[name*="father"]',
                'input[name*="mother"]',
                'input[name*="parent"]',
                'input[id*="father"]',
                'input[id*="mother"]',
                'input[id*="parent"]'
            ],
            field_type="text"
        ))
        
        # STEP_06: Date of Birth
        self.steps.append(Form49AStep(
            step_id="STEP_06",
            step_name="Date of Birth",
            required=True,
            profile_field="dateOfBirth",
            selectors=[
                'input[name*="dob"]',
                'input[name*="birth"]',
                'input[id*="dob"]',
                'input[id*="birth"]',
                'input[type="date"]'
            ],
            field_type="date"
        ))
        
        # STEP_07: Aadhaar / KYC
        self.steps.append(Form49AStep(
            step_id="STEP_07",
            step_name="Aadhaar Number",
            required=False,
            profile_field="aadhaarNumber",
            selectors=[
                'input[name*="aadhaar"]',
                'input[name*="aadhar"]',
                'input[name*="uid"]',
                'input[id*="aadhaar"]',
                'input[id*="aadhar"]'
            ],
            field_type="text"
        ))
        
        # STEP_08: Income Source
        self.steps.append(Form49AStep(
            step_id="STEP_08",
            step_name="Income Source",
            required=True,
            profile_field="occupation",
            selectors=[
                'select[name*="income"]',
                'select[name*="source"]',
                'select[id*="income"]',
                'select[id*="source"]',
                'input[name*="income"]',
                'input[name*="source"]'
            ],
            field_type="select"
        ))
        
        # STEP_09: Email
        self.steps.append(Form49AStep(
            step_id="STEP_09",
            step_name="Email Address",
            required=True,
            profile_field="email",
            selectors=[
                'input[type="email"]',
                'input[name*="email"]',
                'input[id*="email"]',
                'input[placeholder*="email" i]'
            ],
            field_type="email"
        ))
        
        # STEP_10: Phone
        self.steps.append(Form49AStep(
            step_id="STEP_10",
            step_name="Phone Number",
            required=True,
            profile_field="phone",
            selectors=[
                'input[type="tel"]',
                'input[name*="phone"]',
                'input[name*="mobile"]',
                'input[id*="phone"]',
                'input[id*="mobile"]'
            ],
            field_type="tel"
        ))
        
        # STEP_11: Address
        self.steps.append(Form49AStep(
            step_id="STEP_11",
            step_name="Address",
            required=True,
            profile_field="address",
            selectors=[
                'textarea[name*="address"]',
                'input[name*="address"]',
                'textarea[id*="address"]',
                'input[id*="address"]'
            ],
            field_type="textarea"
        ))
        
        # STEP_12: City
        self.steps.append(Form49AStep(
            step_id="STEP_12",
            step_name="City",
            required=True,
            profile_field="city",
            selectors=[
                'input[name*="city"]',
                'select[name*="city"]',
                'input[id*="city"]',
                'select[id*="city"]'
            ],
            field_type="text"
        ))
        
        # STEP_13: State
        self.steps.append(Form49AStep(
            step_id="STEP_13",
            step_name="State",
            required=True,
            profile_field="state",
            selectors=[
                'select[name*="state"]',
                'input[name*="state"]',
                'select[id*="state"]',
                'input[id*="state"]'
            ],
            field_type="select"
        ))
        
        # STEP_14: Pincode
        self.steps.append(Form49AStep(
            step_id="STEP_14",
            step_name="Pincode",
            required=True,
            profile_field="pincode",
            selectors=[
                'input[name*="pin"]',
                'input[name*="postal"]',
                'input[id*="pin"]',
                'input[id*="postal"]'
            ],
            field_type="text"
        ))
        
        # STEP_15: Document Upload (Photo)
        self.steps.append(Form49AStep(
            step_id="STEP_15",
            step_name="Photo Upload",
            required=False,
            profile_field="photoUrl",
            selectors=[
                'input[type="file"][name*="photo"]',
                'input[type="file"][name*="image"]',
                'input[type="file"][id*="photo"]',
                'input[type="file"][id*="image"]'
            ],
            field_type="file"
        ))
        
        # STEP_16: Document Upload (Signature)
        self.steps.append(Form49AStep(
            step_id="STEP_16",
            step_name="Signature Upload",
            required=False,
            profile_field="signatureUrl",
            selectors=[
                'input[type="file"][name*="signature"]',
                'input[type="file"][name*="sign"]',
                'input[type="file"][id*="signature"]',
                'input[type="file"][id*="sign"]'
            ],
            field_type="file"
        ))
    
    def get_current_step(self) -> Optional[Form49AStep]:
        """Get current step"""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def get_step_by_id(self, step_id: str) -> Optional[Form49AStep]:
        """Get step by ID"""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_profile_value(self, field_name: str) -> Optional[Any]:
        """
        Get value using intelligent data aggregation
        Priority: Request Data > Master Profile > Document Vault > Defaults
        """
        # Use Data Aggregator if available (preferred method)
        if self.data_aggregator:
            value = self.data_aggregator.get_field_value(field_name)
            if value:
                source = self.data_aggregator.get_data_source(field_name)
                logger.debug(f"[Form49A] Field '{field_name}' = '{value}' (source: {source})")
                return value
        
        # Fallback to old method if Data Aggregator not available
        # Special handling for delivery_type (PAN mode)
        if field_name == "delivery_type" or field_name == "deliveryType":
            # Prefer service_config (chat data), then profile, default to DIGITAL/ePAN
            value = (self.service_config.get("delivery_type") or 
                    self.service_config.get("deliveryType") or
                    self.user_profile.get("delivery_type") or 
                    self.user_profile.get("deliveryType") or "epan")
            value_str = str(value).lower().strip()
            
            # CRITICAL: Normalize values - chat stores "epan" but form needs "digital"
            # Also handle "online" as synonym for digital/epan
            if "phy" in value_str or value_str == "physical":
                logger.info(f"[DELIVERY_TYPE] Normalized '{value}' to 'physical'")
                return "physical"
            elif "epan" in value_str or "digital" in value_str or "online" in value_str or value_str == "e-pan":
                logger.info(f"[DELIVERY_TYPE] Normalized '{value}' to 'digital'")
                return "digital"
            else:
                # Default to digital/epan
                logger.warning(f"[DELIVERY_TYPE] Unrecognized value '{value_str}', defaulting to 'digital'")
                return "digital"
        
        # Special handling for digital_mode_option
        if field_name == "digital_mode_option" or field_name == "digitalModeOption":
            value = (self.service_config.get("digital_mode_option") or
                    self.service_config.get("digitalModeOption") or
                    self.user_profile.get("digital_mode_option") or
                    self.user_profile.get("digitalModeOption") or "ekyc")
            value_str = str(value).lower()
            if "esign" in value_str:
                return "esign"
            elif "dsc" in value_str:
                return "dsc"
            return "ekyc"  # Default to e-KYC
        
        # Special handling for pan_card_mode
        if field_name == "pan_card_mode" or field_name == "panCardMode":
            # CRITICAL: Check delivery_type first - if Digital/ePAN, force e-PAN only
            delivery_type = self.get_profile_value("delivery_type")
            delivery_str = str(delivery_type).lower() if delivery_type else ""
            
            # If user selected Digital/ePAN, always return e-PAN only (not both)
            if "digital" in delivery_str or "epan" in delivery_str:
                logger.info(f"[PAN_CARD_MODE] Delivery type is Digital/ePAN, forcing 'epan_only'")
                return "epan_only"
            
            # Otherwise, check the pan_card_mode value
            value = (self.service_config.get("pan_card_mode") or
                    self.service_config.get("panCardMode") or
                    self.user_profile.get("pan_card_mode") or
                    self.user_profile.get("panCardMode") or "epan_only")
            value_str = str(value).lower()
            if "both" in value_str:
                return "both"
            if "physical" in value_str:
                return "both"  # physical implies card + epan
            return "epan_only"
        
        # Special handling for applicant_type
        if field_name == "applicant_type" or field_name == "applicantType":
            # Get value from service_config (chat data) first, then profile
            value = (self.service_config.get("applicant_type") or
                    self.service_config.get("applicantType") or
                    self.user_profile.get("applicant_type") or 
                    self.user_profile.get("applicantType") or "individual")
            value_str = str(value).strip()
            value_lower = value_str.lower()
            
            # CRITICAL: Normalize to expected dropdown labels
            # Chat stores "individual" (lowercase), form needs "Individual" (capitalized)
            if value_lower == "individual" or value_lower.startswith("ind"):
                logger.info(f"[APPLICANT_TYPE] Normalized '{value_str}' to 'Individual'")
                return "Individual"
            elif value_lower == "company" or value_lower.startswith("comp") or value_lower.startswith("huf"):
                return "Company"
            else:
                # Default to Individual if unrecognized
                logger.warning(f"[APPLICANT_TYPE] Unrecognized value '{value_str}', defaulting to 'Individual'")
                return "Individual"
        
        # Special handling for name fields
        if field_name == "firstName" or field_name == "first_name":
            # Extract first name from fullName
            full_name = self.user_profile.get("fullName") or self.user_profile.get("full_name") or ""
            if full_name:
                parts = str(full_name).strip().split()
                if len(parts) > 0:
                    return parts[0]
        
        if field_name == "lastName" or field_name == "last_name":
            # Extract last name from fullName
            full_name = self.user_profile.get("fullName") or self.user_profile.get("full_name") or ""
            if full_name:
                parts = str(full_name).strip().split()
                if len(parts) > 1:
                    return parts[-1]  # Last part is surname
                elif len(parts) == 1:
                    return ""  # No surname if only one word
        
        if field_name == "middleName" or field_name == "middle_name":
            # Extract middle name from fullName
            full_name = self.user_profile.get("fullName") or self.user_profile.get("full_name") or ""
            if full_name:
                parts = str(full_name).strip().split()
                if len(parts) > 2:
                    return " ".join(parts[1:-1])  # Middle parts
            return None  # Optional field
        
        if field_name == "nameTitle" or field_name == "name_title":
            # Default to "Mr" if not specified
            return self.user_profile.get("nameTitle") or self.user_profile.get("name_title") or "Mr"
        
        # Try camelCase first
        if field_name in self.user_profile:
            value = self.user_profile[field_name]
            if value and str(value).strip():
                return value
        
        # Try snake_case
        snake_case = ''.join(['_' + c.lower() if c.isupper() else c for c in field_name]).lstrip('_')
        if snake_case in self.user_profile:
            value = self.user_profile[snake_case]
            if value and str(value).strip():
                return value
        
        # Try direct match (case insensitive)
        for key, value in self.user_profile.items():
            if key.lower() == field_name.lower() and value and str(value).strip():
                return value
        
        return None
    
    def has_required_data(self, step: Form49AStep) -> Tuple[bool, Optional[str]]:
        """Check if required data exists for step"""
        if not step.required:
            return True, None
        
        if not step.profile_field:
            return True, None
        
        value = self.get_profile_value(step.profile_field)
        
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, step.profile_field
        
        return True, None
    
    async def detect_and_switch_to_iframe(self) -> bool:
        """
        Detect iframe containing Form 49A and switch context
        RETRIES MULTIPLE TIMES with increasing wait times
        
        Returns:
            True if iframe found and switched, False otherwise
        """
        max_retries = 5
        retry_delay = 2
        
        for retry in range(max_retries):
            try:
                logger.info(f"[IFRAME DETECTION] Attempt {retry + 1}/{max_retries} - Starting iframe detection...")
                
                # Wait for page to be ready
                try:
                    await self.page.wait_for_load_state('domcontentloaded', timeout=10000)
                except:
                    pass
                
                await asyncio.sleep(retry_delay)
                
                # Find all iframes
                iframes = await self.page.query_selector_all('iframe')
                logger.info(f"[IFRAME DETECTION] Found {len(iframes)} iframe(s) on attempt {retry + 1}")
                
                if not iframes:
                    if retry < max_retries - 1:
                        logger.info(f"[IFRAME DETECTION] No iframes found, retrying in {retry_delay}s...")
                        continue
                    else:
                        logger.info("[IFRAME DETECTION] No iframes found after all retries, using main page")
                        self.active_page = self.page
                        return False
                
                # Try each iframe
                for idx, iframe in enumerate(iframes):
                    try:
                        # Get iframe content frame
                        iframe_frame = await iframe.content_frame()
                        if not iframe_frame:
                            logger.debug(f"[IFRAME DETECTION] Iframe {idx} has no content frame")
                            continue
                        
                        # Wait for iframe to load (longer timeout)
                        try:
                            await iframe_frame.wait_for_load_state('domcontentloaded', timeout=10000)
                            await asyncio.sleep(1)
                        except:
                            logger.debug(f"[IFRAME DETECTION] Iframe {idx} load timeout, trying anyway")
                            await asyncio.sleep(1)
                        
                        # Check if form elements exist in iframe
                        form_elements = await iframe_frame.query_selector_all('form, input, select, textarea')
                        logger.info(f"[IFRAME DETECTION] Iframe {idx} has {len(form_elements)} form elements")
                        
                        if len(form_elements) > 0:
                            # Check for Form 49A specific elements (more comprehensive)
                            has_pan_fields = False
                            test_selectors = [
                                'input[name*="name" i]',
                                'select[name*="status" i]',
                                'input[type="radio"]',
                                'input[name*="pan" i]',
                                'select',
                                'input[type="text"]',
                                'textarea'
                            ]
                            
                            for test_sel in test_selectors:
                                try:
                                    test_elem = await iframe_frame.query_selector(test_sel)
                                    if test_elem:
                                        has_pan_fields = True
                                        logger.info(f"[IFRAME DETECTION] Found form element with selector: {test_sel}")
                                        break
                                except:
                                    continue
                            
                            # If we have form elements, assume it's the form (even if specific selectors don't match)
                            if has_pan_fields or len(form_elements) >= 3:
                                logger.info(f"[IFRAME FOUND] ✅ Switching to iframe {idx} (has {len(form_elements)} form elements)")
                                self.iframe_page = iframe_frame
                                self.active_page = iframe_frame
                                logger.info(f"[TAB SWITCHED] ✅ Now using iframe context for all operations")
                                
                                # Verify we can access elements in iframe
                                try:
                                    test_input = await iframe_frame.query_selector('input, select')
                                    if test_input:
                                        logger.info("[IFRAME VERIFIED] ✅ Can access elements in iframe")
                                        return True
                                except:
                                    logger.warning("[IFRAME VERIFIED] ⚠️ Cannot access elements, but continuing")
                                    return True
                    except Exception as e:
                        logger.debug(f"[IFRAME DETECTION] Error checking iframe {idx}: {e}")
                        continue
                
                # If we get here, no iframe matched
                if retry < max_retries - 1:
                    logger.info(f"[IFRAME DETECTION] No matching iframe found, retrying in {retry_delay}s...")
                    retry_delay += 1
                else:
                    logger.info("[IFRAME DETECTION] No form iframe found after all retries, using main page")
                    self.active_page = self.page
                    return False
                    
            except Exception as e:
                logger.error(f"[IFRAME DETECTION] Error during iframe detection (attempt {retry + 1}): {e}")
                if retry < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    logger.error("[IFRAME DETECTION] All retries exhausted, using main page")
                    self.active_page = self.page
                    return False
        
        # Final fallback
        logger.info("[IFRAME DETECTION] Using main page as fallback")
        self.active_page = self.page
        return False
    
    async def find_field_element(self, step: Form49AStep) -> Optional[Any]:
        """Find field element using selector set with label/XPath fallback - uses active_page (iframe or main)"""
        search_page = self.active_page
        logger.info(f"[FINDING FIELD] Looking for: {step.step_name} on {'iframe' if self.iframe_page else 'main page'}")

        # Prefer non-ID selectors (UTI page has duplicate IDs)
        sanitized_selectors = [s for s in step.selectors if "[id" not in s and "id=" not in s]
        selectors_to_try = sanitized_selectors or step.selectors

        # Try configured selectors
        for selector in selectors_to_try:
            try:
                element = await search_page.wait_for_selector(selector, timeout=5000, state='visible')
                if element:
                    is_visible = await element.is_visible()
                    is_enabled = await element.is_enabled() if hasattr(element, 'is_enabled') else True
                    if is_visible and is_enabled:
                        logger.info(f"[FIELD FOUND] {step.step_name} using selector: {selector[:50]}")
                        return element
            except Exception as e:
                logger.debug(f"[FIELD SEARCH] Selector failed: {selector[:50]} - {str(e)[:50]}")
                continue

        # Generic selectors (no IDs)
        if step.profile_field:
            field_name_lower = step.profile_field.lower()
            generic_selectors = []
            if 'name' in field_name_lower:
                generic_selectors = [
                    'input[name*="name" i]',
                    'input[placeholder*="name" i]'
                ]
            elif 'email' in field_name_lower:
                generic_selectors = [
                    'input[type="email"]',
                    'input[name*="email" i]'
                ]
            elif 'phone' in field_name_lower or 'mobile' in field_name_lower:
                generic_selectors = [
                    'input[type="tel"]',
                    'input[name*="phone" i]',
                    'input[name*="mobile" i]'
                ]
            elif 'dob' in field_name_lower or 'birth' in field_name_lower:
                generic_selectors = [
                    'input[type="date"]',
                    'input[name*="dob" i]',
                    'input[name*="birth" i]'
                ]
            elif 'address' in field_name_lower:
                generic_selectors = [
                    'textarea[name*="address" i]',
                    'input[name*="address" i]'
                ]

            for selector in generic_selectors:
                try:
                    element = await search_page.wait_for_selector(selector, timeout=3000, state='visible')
                    if element and await element.is_visible():
                        logger.info(f"[FIELD FOUND] {step.step_name} using generic selector")
                        return element
                except Exception:
                    continue

        # Label-based relative XPath fallback
        try:
            label_text = step.step_name.replace("_", " ")
            xpath = f'xpath=//label[contains(normalize-space(), "{label_text}")]/following::*[self::input or self::select or self::textarea][1]'
            element = await search_page.wait_for_selector(xpath, timeout=2000, state='visible')
            if element:
                logger.info(f"[FIELD FOUND] {step.step_name} using label-relative XPath")
                return element
        except Exception:
            pass

        logger.warning(f"[FIELD NOT FOUND] Could not find field: {step.step_name}")
        return None
    
    async def _dispatch_change_events(self, element, value: Optional[Any] = None):
        """Force input/change/blur events to satisfy UTI validation."""
        try:
            await element.evaluate(
                """(el, val) => {
                    if (val !== null && val !== undefined && typeof el.value !== 'undefined') {
                        el.value = val;
                    }
                    ['input','change','blur'].forEach(evt => {
                        el.dispatchEvent(new Event(evt, { bubbles: true }));
                    });
                }""",
                value,
            )
        except Exception as e:
            logger.debug(f"[EVENT DISPATCH] failed: {e}")

    async def _wait_next_enabled(self, timeout_ms: int = 4000):
        """Wait briefly for Next/Submit to become enabled."""
        search_page = self.active_page
        if not search_page:
            return
        candidates = [
            'text=Next', 'text=Continue', 'text=Submit', 'text=Proceed',
            'button:has-text("Next")', 'button:has-text("Continue")', 'button:has-text("Submit")',
            'input[type="submit"]', 'input[type="button"][value*="Next" i]'
        ]
        end = asyncio.get_event_loop().time() + (timeout_ms / 1000)
        while asyncio.get_event_loop().time() < end:
            for sel in candidates:
                try:
                    btn = await search_page.query_selector(sel)
                    if btn:
                        disabled = await btn.evaluate("el => el.disabled || el.getAttribute('disabled') !== null")
                        if not disabled:
                            return
                except Exception:
                    continue
            await asyncio.sleep(0.2)

    async def fill_field(self, step: Form49AStep, value: Any) -> Tuple[bool, Optional[str]]:
        """Fill a form field with value - CRITICAL: Uses active_page (iframe or main)"""
        try:
            logger.info(f"[FILLING FIELD] {step.step_name} with value: {str(value)[:50]}")
            
            element = await self.find_field_element(step)
            if not element:
                error_msg = f"Field not found: {step.step_name}"
                logger.error(f"[FILL FAILED] {error_msg}")
                return False, error_msg
            
            # Wait for element to be ready
            try:
                await element.wait_for_element_state('attached', timeout=3000)
                await element.wait_for_element_state('visible', timeout=3000)
            except:
                pass
            
            # Scroll to element
            await element.scroll_into_view_if_needed()
            await asyncio.sleep(0.3)
            
            # Click to focus (but NOT for radio buttons - they need direct click)
            if step.field_type != "radio":
                try:
                    await element.click()
                    await asyncio.sleep(0.2)
                except:
                    # If click fails, try focus
                    await element.focus()
                    await asyncio.sleep(0.2)
            
            # Fill based on field type
            if step.field_type == "radio":
                # For radio buttons - IMPROVED for Form 49A
                radio_value = str(value).lower()
                logger.info(f"🔘 Selecting radio button: {radio_value}")
                
                try:
                    # CRITICAL: Use active_page (iframe or main) for all operations
                    search_page = self.active_page
                    
                    # Strategy 1: Find by clicking the label with matching text
                    if "physical" in radio_value:
                        # Try to find Physical Mode label
                        label_selectors = [
                            'label:has-text("Physical Mode")',
                            'label:has-text("Physical")',
                            'text=Physical Mode',
                            'text=Physical'
                        ]
                        for selector in label_selectors:
                            try:
                                label = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                                if label:
                                    await label.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await label.click()
                                    await asyncio.sleep(0.5)
                                    logger.info(f"[RADIO CLICKED] Physical Mode label")
                                    await self._dispatch_change_events(label)
                                    await self._wait_next_enabled()
                                    return True, None
                            except:
                                continue
                    
                    elif "digital" in radio_value or "epan" in radio_value:
                        # Try to find Digital Mode label
                        label_selectors = [
                            'label:has-text("Digital Mode")',
                            'label:has-text("Digital")',
                            'text=Digital Mode',
                            'text=Digital'
                        ]
                        for selector in label_selectors:
                            try:
                                label = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                                if label:
                                    await label.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await label.click()
                                    await asyncio.sleep(0.5)
                                    logger.info(f"[RADIO CLICKED] Digital Mode label")
                                    await self._dispatch_change_events(label)
                                    await self._wait_next_enabled()
                                    return True, None
                            except:
                                continue
                    
                    elif "epan_only" in radio_value or "epan only" in radio_value or "epanonly" in radio_value:
                        # PAN CARD Mode: e-PAN only (CRITICAL: This should be selected when Digital mode is chosen)
                        label_selectors = [
                            'label:has-text("e-PAN only")',
                            'label:has-text("No physical PAN Card")',
                            'label:has-text("e-PAN only, No physical PAN Card")',
                            'label:has-text("e-PAN")',
                            'text=e-PAN only',
                            'text=No physical PAN Card',
                            'text=e-PAN only, No physical PAN Card'
                        ]
                        for selector in label_selectors:
                            try:
                                label = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                                if label:
                                    await label.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await label.click()
                                    await asyncio.sleep(0.5)
                                    logger.info(f"✅ [RADIO CLICKED] e-PAN only label")
                                    
                                    # Verify it's actually selected (not "Both")
                                    try:
                                        # Find the associated radio input
                                        label_for = await label.get_attribute('for')
                                        if label_for:
                                            radio_input = await search_page.query_selector(f'input[type="radio"][id="{label_for}"]')
                                            if radio_input:
                                                is_checked = await radio_input.evaluate('el => el.checked')
                                                if not is_checked:
                                                    logger.warning(f"⚠️ Radio not checked after label click, trying direct click")
                                                    await radio_input.click()
                                                    await asyncio.sleep(0.3)
                                    except:
                                        pass
                                    
                                    await self._dispatch_change_events(label)
                                    await self._wait_next_enabled()
                                    
                                    # Final verification
                                    try:
                                        # Check all radio buttons in PAN CARD Mode group
                                        all_pan_radios = await search_page.query_selector_all('input[type="radio"]:visible')
                                        for radio in all_pan_radios:
                                            radio_id = await radio.get_attribute('id') or ""
                                            radio_name = await radio.get_attribute('name') or ""
                                            is_checked = await radio.evaluate('el => el.checked')
                                            if is_checked:
                                                # Get label text
                                                label_elem = await search_page.query_selector(f'label[for="{radio_id}"]')
                                                if label_elem:
                                                    label_text = (await label_elem.text_content() or "").lower()
                                                    if "both" in label_text and "epan only" not in label_text:
                                                        logger.error(f"❌ Wrong option selected: '{label_text}' - should be e-PAN only")
                                                        # Uncheck and try again
                                                        await radio.evaluate('el => el.checked = false')
                                                        await asyncio.sleep(0.2)
                                    except:
                                        pass
                                    
                                    return True, None
                            except:
                                continue
                    
                    elif "both" in radio_value and "epan_only" not in radio_value and "epan only" not in radio_value:
                        # PAN CARD Mode: Both physical and e-PAN (only if explicitly requested, not for Digital mode)
                        # CRITICAL: Check delivery_type - if Digital, don't select "Both"
                        delivery_type = self.get_profile_value("delivery_type")
                        delivery_str = str(delivery_type).lower() if delivery_type else ""
                        if "digital" in delivery_str or "epan" in delivery_str:
                            logger.warning(f"⚠️ Delivery type is Digital/ePAN, skipping 'Both' option - should use e-PAN only")
                            return False, "Cannot select 'Both' when Digital/ePAN mode is selected"
                        
                        label_selectors = [
                            'label:has-text("Both physical PAN Card and e-PAN")',
                            'label:has-text("Both")',
                            'text=Both physical PAN Card and e-PAN'
                        ]
                        for selector in label_selectors:
                            try:
                                label = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                                if label:
                                    await label.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await label.click()
                                    await asyncio.sleep(0.5)
                                    logger.info(f"✅ [RADIO CLICKED] Both physical and e-PAN label")
                                    await self._dispatch_change_events(label)
                                    await self._wait_next_enabled()
                                    return True, None
                            except:
                                continue
                    
                    elif "ekyc" in radio_value or "aadhaar" in radio_value:
                        # Digital Mode Option: Aadhaar based e-KYC
                        label_selectors = [
                            'label:has-text("Aadhaar based e-KYC")',
                            'label:has-text("e-KYC")',
                            'text=Aadhaar based e-KYC'
                        ]
                        for selector in label_selectors:
                            try:
                                label = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                                if label:
                                    await label.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await label.click()
                                    await asyncio.sleep(0.5)
                                    logger.info(f"[RADIO CLICKED] Aadhaar based e-KYC label")
                                    await self._dispatch_change_events(label)
                                    await self._wait_next_enabled()
                                    return True, None
                            except:
                                continue
                    
                    elif "esign" in radio_value:
                        # Digital Mode Option: eSign Mode
                        label_selectors = [
                            'label:has-text("eSign Mode")',
                            'label:has-text("eSignature")',
                            'text=eSign Mode'
                        ]
                        for selector in label_selectors:
                            try:
                                label = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                                if label:
                                    await label.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await label.click()
                                    await asyncio.sleep(0.5)
                                    logger.info(f"[RADIO CLICKED] eSign Mode label")
                                    await self._dispatch_change_events(label)
                                    await self._wait_next_enabled()
                                    return True, None
                            except:
                                continue
                    
                    elif "dsc" in radio_value:
                        # Digital Mode Option: DSC Mode
                        label_selectors = [
                            'label:has-text("DSC Mode")',
                            'label:has-text("DSC")',
                            'text=DSC Mode'
                        ]
                        for selector in label_selectors:
                            try:
                                label = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                                if label:
                                    await label.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await label.click()
                                    await asyncio.sleep(0.5)
                                    logger.info(f"✅ Clicked DSC Mode label")
                                    await self._dispatch_change_events(label)
                                    await self._wait_next_enabled()
                                    return True, None
                            except:
                                continue
                    
                    # Strategy 2: Find radio input and click it directly - use active_page
                    all_radios = await search_page.query_selector_all('input[type="radio"]:visible')
                    logger.info(f"[RADIO SEARCH] Found {len(all_radios)} radio buttons on {'iframe' if self.iframe_page else 'main page'}")
                    
                    for radio in all_radios:
                        try:
                            # Get label text for this radio
                            radio_id = await radio.get_attribute('id')
                            radio_val = (await radio.get_attribute('value') or "").lower()
                            label_text = ""
                            
                            # Try to find associated label - use active_page
                            if radio_id:
                                label = await search_page.query_selector(f'label[for="{radio_id}"]')
                                if label:
                                    label_text = (await label.text_content() or "").lower()
                            
                            # Check if this is the right radio
                            if (radio_value in label_text or 
                                radio_value in radio_val or
                                ("physical" in label_text and "physical" in radio_value) or
                                ("digital" in label_text and "digital" in radio_value) or
                                ("epan" in label_text and "epan" in radio_value) or
                                ("both" in label_text and "both" in radio_value) or
                                ("ekyc" in label_text and "ekyc" in radio_value) or
                                ("esign" in label_text and "esign" in radio_value) or
                                ("dsc" in label_text and "dsc" in radio_value)):
                                
                                await radio.scroll_into_view_if_needed()
                                await asyncio.sleep(0.3)
                                
                                # Use JavaScript to set checked property directly (more reliable)
                                try:
                                    await radio.evaluate("""
                                        (radio) => {
                                            // Uncheck all radios in the same group first
                                            const name = radio.name;
                                            if (name) {
                                                document.querySelectorAll(`input[type="radio"][name="${name}"]`).forEach(r => {
                                                    r.checked = false;
                                                    r.dispatchEvent(new Event('change', { bubbles: true }));
                                                });
                                            }
                                            // Check this radio
                                            radio.checked = true;
                                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                                            radio.dispatchEvent(new Event('click', { bubbles: true }));
                                        }
                                    """)
                                    await asyncio.sleep(0.3)
                                except Exception as js_err:
                                    # Fallback to click if JavaScript fails
                                    try:
                                        await radio.click(force=True)
                                        await asyncio.sleep(0.3)
                                    except:
                                        pass
                                
                                # Verify selection
                                is_checked = await radio.evaluate('el => el.checked')
                                if is_checked:
                                    logger.info(f"✅ Radio button selected successfully: {label_text or radio_val}")
                                    await self._dispatch_change_events(radio)
                                    await self._wait_next_enabled()
                                    return True, None
                        except Exception as e:
                            logger.debug(f"Radio button attempt failed: {e}")
                            continue
                    
                    return False, f"Could not select radio button for '{value}'"
                    
                except Exception as e:
                    logger.error(f"❌ Error selecting radio button: {e}")
                    return False, f"Error: {str(e)}"
            
            elif step.field_type == "select":
                # For dropdowns - CRITICAL: Properly select Individual (not Artificial Judicial Person)
                try:
                    value_str = str(value)
                    value_lower = value_str.lower()
                    logger.info(f"🔽 Selecting dropdown: '{value_str}'")
                    
                    # Get all options
                    options = await element.query_selector_all('option')
                    logger.info(f"Found {len(options)} options in dropdown")
                    
                    # Log all options for debugging
                    for i, option in enumerate(options):
                        try:
                            opt_text = (await option.text_content() or "").strip()
                            opt_value = await option.get_attribute('value') or ""
                            logger.info(f"  Option {i}: '{opt_text}' (value: '{opt_value}')")
                        except:
                            pass
                    
                    # CRITICAL: For "Individual", we need exact match (not "Artificial Judicial Person")
                    selected = False
                    
                    # Sort options: prioritize exact matches, then Individual without Artificial/Judicial
                    sorted_options = []
                    for option in options:
                        try:
                            option_text = (await option.text_content() or "").strip()
                            option_value = (await option.get_attribute('value') or "").strip()
                            option_text_lower = option_text.lower()
                            
                            # Priority scoring for Individual
                            priority = 0
                            if value_str == "Individual" or value_lower == "individual":
                                if option_text.strip() == "Individual":
                                    priority = 100  # Highest priority - exact match
                                elif option_value.strip() == "Individual":
                                    priority = 90
                                elif (option_text_lower.startswith("individual") and 
                                      "artificial" not in option_text_lower and 
                                      "judicial" not in option_text_lower):
                                    priority = 80  # Individual without artificial/judicial
                                elif "individual" in option_text_lower and "artificial" not in option_text_lower:
                                    priority = 70
                                elif "artificial" in option_text_lower or "judicial" in option_text_lower:
                                    priority = 0  # Lowest priority - avoid this
                            
                            sorted_options.append((priority, option, option_text, option_value, option_text_lower))
                        except:
                            continue
                    
                    # Sort by priority (highest first)
                    sorted_options.sort(key=lambda x: x[0], reverse=True)
                    
                    # Try options in priority order - ONLY select high-priority options for Individual
                    for priority, option, option_text, option_value, option_text_lower in sorted_options:
                        try:
                            # CRITICAL: For Individual, skip ALL options with priority 0 (Artificial Judicial Person)
                            if (value_str == "Individual" or value_lower == "individual"):
                                if priority == 0:
                                    logger.debug(f"⏭️ Skipping low-priority option: '{option_text}' (priority: {priority})")
                                    continue
                                # Also skip if it contains artificial/judicial even if priority > 0
                                if "artificial" in option_text_lower or "judicial" in option_text_lower:
                                    logger.debug(f"⏭️ Skipping option with artificial/judicial: '{option_text}'")
                                    continue
                                # Only proceed if priority is high enough (>= 70)
                                if priority < 70:
                                    logger.debug(f"⏭️ Skipping low-priority option: '{option_text}' (priority: {priority})")
                                    continue
                            
                            # Check if this matches
                            is_match = False
                            if value_str == "Individual" or value_lower == "individual":
                                # For Individual, only match if priority is high and text is exactly "Individual" or starts with "Individual"
                                if priority >= 70 and (
                                    option_text.strip() == "Individual" or
                                    (option_text_lower.startswith("individual") and 
                                     "artificial" not in option_text_lower and 
                                     "judicial" not in option_text_lower)
                                ):
                                    is_match = True
                            else:
                                # For other values, use contains match
                                if value_lower in option_text_lower or value_lower in option_value.lower():
                                    is_match = True
                            
                            if is_match:
                                # Select this option
                                logger.info(f"🎯 Selecting: '{option_text}' (value: '{option_value}', priority: {priority})")
                                
                                if option_value:
                                    await element.select_option(value=option_value)
                                else:
                                    await element.select_option(label=option_text)
                                
                                await asyncio.sleep(0.5)
                                await self._dispatch_change_events(element)
                                await self._wait_next_enabled()
                                
                                # Verify selection - CRITICAL: Re-verify to ensure we got the right option
                                selected_value = await element.evaluate("el => el.value")
                                selected_text = await element.evaluate("el => el.options[el.selectedIndex]?.text || ''")
                                
                                logger.info(f"✅ Dropdown selected: '{selected_text}' (value: '{selected_value}')")
                                
                                # CRITICAL: Double-check for Individual - reject if it contains artificial/judicial
                                if (value_str == "Individual" or value_lower == "individual") and selected_text:
                                    selected_text_lower = selected_text.lower()
                                    if "artificial" in selected_text_lower or "judicial" in selected_text_lower:
                                        logger.error(f"❌ Selected wrong option: '{selected_text}' contains artificial/judicial, trying next option...")
                                        # Deselect this option
                                        try:
                                            await element.select_option(value="")
                                            await asyncio.sleep(0.3)
                                        except:
                                            pass
                                        continue  # Try next option
                                    # Also verify it's actually "Individual" or starts with "Individual"
                                    if not (selected_text.strip() == "Individual" or 
                                            (selected_text_lower.startswith("individual") and 
                                             "artificial" not in selected_text_lower and 
                                             "judicial" not in selected_text_lower)):
                                        logger.error(f"❌ Selected option doesn't match Individual: '{selected_text}', trying next option...")
                                        try:
                                            await element.select_option(value="")
                                            await asyncio.sleep(0.3)
                                        except:
                                            pass
                                        continue
                                
                                selected = True
                                return True, None
                        except Exception as e:
                            logger.debug(f"Option selection attempt failed: {e}")
                            continue
                    
                    if not selected:
                        logger.error(f"❌ Could not select '{value_str}' from dropdown")
                        # List available options for debugging
                        available_options = []
                        for opt in options:
                            try:
                                opt_text = await opt.text_content()
                                available_options.append(opt_text.strip())
                            except:
                                pass
                        logger.error(f"Available options were: {available_options}")
                        return False, f"Option '{value_str}' not found. Available: {', '.join(available_options[:5])}"
                    
                except Exception as e:
                    logger.error(f"❌ Error selecting dropdown option: {e}")
                    return False, f"Error selecting option: {str(e)}"
            
            elif step.field_type == "date":
                # For date fields
                date_str = str(value)
                # Convert to DD/MM/YYYY if needed
                if len(date_str) == 10 and '-' in date_str:
                    parts = date_str.split('-')
                    if len(parts) == 3:
                        date_str = f"{parts[2]}/{parts[1]}/{parts[0]}"
                
                await element.fill("")
                await asyncio.sleep(0.2)
                await element.type(date_str, delay=50)
                await asyncio.sleep(0.3)
                await self._dispatch_change_events(element, date_str)
                await self._wait_next_enabled()
            
            elif step.field_type == "file":
                # For file uploads
                if value and isinstance(value, str):
                    # If value is a URL, we'd need to download it first
                    # For now, skip file uploads if URL provided
                    return False, "File upload from URL not yet implemented"
            
            else:
                # For text, email, tel, textarea
                await element.fill("")
                await asyncio.sleep(0.2)
                # Human-like typing
                for char in str(value):
                    await element.type(char, delay=50)
                await asyncio.sleep(0.3)
                await self._dispatch_change_events(element, str(value))
                await self._wait_next_enabled()
            
            # Additional safety events for text-like fields
            if step.field_type in ["text", "email", "tel", "textarea", "date"]:
                await self._dispatch_change_events(element, str(value))
            
            # CRITICAL: Verify value was filled/selected - NO SILENT FAILURES
            verification_passed = False
            verification_error = ""
            
            if step.field_type == "radio":
                # For radio buttons, check if it's checked
                is_checked = await element.evaluate("el => el.checked")
                if is_checked:
                    verification_passed = True
                    logger.info(f"[VERIFIED] Radio button selected: {step.step_name}")
                else:
                    verification_error = f"Radio button not checked after click"
                    logger.error(f"[VERIFY FAILED] {verification_error}: {step.step_name}")
            elif step.field_type == "select":
                # For dropdowns, check selected value
                selected_value = await element.evaluate("el => el.value")
                selected_text = await element.evaluate("el => el.options[el.selectedIndex]?.text || ''")
                if selected_value or selected_text:
                    verification_passed = True
                    step.filled_value = selected_text or selected_value
                    logger.info(f"[VERIFIED] Dropdown selected: {step.step_name} = {selected_text or selected_value}")
                else:
                    verification_error = f"Dropdown value empty after selection"
                    logger.error(f"[VERIFY FAILED] {verification_error}: {step.step_name}")
            else:
                # For text inputs, check filled value
                filled_value = await element.input_value()
                if filled_value and str(filled_value).strip():
                    verification_passed = True
                    step.filled_value = filled_value
                    logger.info(f"[VERIFIED] Field filled: {step.step_name} = {filled_value[:50]}")
                else:
                    verification_error = f"Field empty after fill (expected: {str(value)[:50]})"
                    logger.error(f"[VERIFY FAILED] {verification_error}: {step.step_name}")
            
            if verification_passed:
                return True, None
            else:
                # FAIL LOUDLY - no silent failures
                error_msg = f"Value not filled/selected correctly: {step.step_name}. {verification_error}"
                logger.error(f"[FILL FAILED] {error_msg}")
                return False, error_msg
            
        except Exception as e:
            logger.error(f"Error filling field {step.step_name}: {e}")
            return False, str(e)
    
    async def check_manual_fill(self, step: Form49AStep) -> bool:
        """Check if user manually filled the field"""
        try:
            element = await self.find_field_element(step)
            if element:
                value = await element.input_value()
                if value and str(value).strip():
                    step.filled_value = value
                    return True
        except:
            pass
        return False
    
    async def execute_step(self, step: Form49AStep) -> Dict[str, Any]:
        """Execute a single step"""
        result = {
            "step_id": step.step_id,
            "step_name": step.step_name,
            "status": "pending",
            "message": None,
            "requires_user": False
        }
        
        logger.info(f"[EXECUTE STEP] ========== Executing: {step.step_name} ({step.step_id}) ==========")
        logger.info(f"[EXECUTE STEP] Field type: {step.field_type}")
        logger.info(f"[EXECUTE STEP] Profile field: {step.profile_field}")
        logger.info(f"[EXECUTE STEP] Selectors: {step.selectors[:3] if step.selectors else []}...")
        logger.info(f"[EXECUTE STEP] Using {'iframe' if self.iframe_page else 'main page'}")
        
        # Check if step already completed
        if step.status == StepStatus.COMPLETED:
            logger.info(f"[EXECUTE STEP] ⏭️ Step already completed, skipping")
            result["status"] = "skipped"
            result["message"] = f"{step.step_name} already completed"
            return result
        
        # Conditional step execution: Skip STEP_01B (Digital Mode Option) if Physical Mode is selected
        if step.step_id == "STEP_01B":
            # Check if Physical Mode was selected
            delivery_type = self.get_profile_value("delivery_type")
            if delivery_type and "physical" in str(delivery_type).lower():
                logger.info(f"[EXECUTE STEP] ⏭️ Skipping {step.step_name} - Physical Mode selected")
                step.status = StepStatus.SKIPPED
                result["status"] = "skipped"
                result["message"] = f"{step.step_name} skipped (Physical Mode selected)"
                return result
        
        # Wait for active page (iframe or main) to be ready
        logger.info(f"[EXECUTE STEP] Waiting for {'iframe' if self.iframe_page else 'main page'} to be ready...")
        try:
            await self.active_page.wait_for_load_state('domcontentloaded', timeout=5000)
            logger.info("[EXECUTE STEP] ✅ Page ready")
        except:
            logger.warning("[EXECUTE STEP] ⚠️ Page load timeout, continuing")
        
        # Check if required data exists
        logger.info(f"[EXECUTE STEP] Checking required data for field: {step.profile_field}")
        has_data, missing_field = self.has_required_data(step)
        
        if not has_data:
            # Missing required data - pause automation
            logger.warning(f"[EXECUTE STEP] ❌ Missing required data: {missing_field}")
            step.status = StepStatus.WAITING_USER
            self.status = AutomationStatus.WAITING_FOR_USER
            self.waiting_for_field = missing_field
            
            result["status"] = "waiting_user"
            result["requires_user"] = True
            result["message"] = f"I need '{missing_field}' to continue PAN Form 49A. Please fill it manually or provide it to me."
            
            logger.warning(f"[EXECUTE STEP] ⏸️ Automation paused - missing: {missing_field}")
            return result
        
        # Get value from profile
        value = self.get_profile_value(step.profile_field) if step.profile_field else None
        logger.info(f"[EXECUTE STEP] Got value: '{value}' from profile field '{step.profile_field}'")
        
        # Try to fill the field
        if value:
            logger.info(f"[EXECUTE STEP] Attempting to fill field with value: {str(value)[:50]}")
            success, error = await self.fill_field(step, value)
            if success:
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now()
                result["status"] = "completed"
                result["message"] = f"{step.step_name} filled successfully with '{value}'"
                logger.info(f"[EXECUTE STEP] ✅ {step.step_name} filled successfully")
            else:
                step.status = StepStatus.ERROR
                step.error_message = error
                result["status"] = "error"
                result["message"] = f"Failed to fill {step.step_name}: {error}"
                logger.error(f"[EXECUTE STEP] ❌ Failed to fill {step.step_name}: {error}")
                # Continue to next step even on error (attempt full form)
        else:
            # Optional field with no data - skip
            if not step.required:
                logger.info(f"[EXECUTE STEP] ⏭️ Optional field with no data, skipping")
                step.status = StepStatus.SKIPPED
                result["status"] = "skipped"
                result["message"] = f"{step.step_name} skipped (optional, no data)"
            else:
                # Required but no data - should not happen due to earlier check
                logger.warning(f"[EXECUTE STEP] ⚠️ Required field has no data")
                step.status = StepStatus.WAITING_USER
                self.status = AutomationStatus.WAITING_FOR_USER
                result["status"] = "waiting_user"
                result["requires_user"] = True
                result["message"] = f"Required field {step.step_name} has no data"
        
        logger.info(f"[EXECUTE STEP] ========== Step execution complete: {result['status']} ==========")
        return result
    
    async def _check_if_field_filled(self, step: Form49AStep) -> bool:
        """Check if a field is already filled (for manual progress detection) - uses active_page"""
        try:
            search_page = self.active_page
            for selector in step.selectors:
                try:
                    element = await search_page.wait_for_selector(selector, timeout=1000, state='attached')
                    if element:
                        # Check if field has value
                        if step.field_type == "text":
                            value = await element.evaluate("el => el.value")
                            if value and len(value.strip()) > 0:
                                return True
                        elif step.field_type == "radio":
                            is_checked = await element.evaluate("el => el.checked")
                            if is_checked:
                                return True
                        elif step.field_type == "select":
                            value = await element.evaluate("el => el.value")
                            if value and value != "" and value != "0":
                                return True
                        elif step.field_type == "checkbox":
                            is_checked = await element.evaluate("el => el.checked")
                            if is_checked:
                                return True
                except:
                    continue
            return False
        except Exception as e:
            logger.debug(f"Error checking if field filled: {e}")
            return False
    
    async def navigate_to_next_page(self) -> bool:
        """Navigate to next page of the form - CRITICAL: Uses active_page (iframe or main)"""
        try:
            # CRITICAL: Use active_page (iframe or main)
            search_page = self.active_page
            
            # Wait for form to be ready and any animations to complete
            await asyncio.sleep(1.5)
            await search_page.wait_for_load_state('domcontentloaded', timeout=3000)
            
            logger.info(f"[NAVIGATION] Looking for Next/Submit button on {'iframe' if self.iframe_page else 'main page'}...")
            
            # Strategy 1: Find button by text content (most reliable)
            text_selectors = [
                "text=Next",
                "text=Continue",
                "text=Proceed",
                "text=Submit",
                "text=Next Step",
                "text=Continue to Next Step",
                "text=Apply",
                "text=Save and Continue"
            ]
            
            for text_selector in text_selectors:
                try:
                    element = await search_page.wait_for_selector(text_selector, timeout=2000, state='visible')
                    if element:
                        # Check if button is enabled
                        is_disabled = await element.evaluate("""
                            el => {
                                if (el.disabled) return true;
                                if (el.getAttribute('disabled') !== null) return true;
                                if (el.style.display === 'none') return false; // visibility check separate
                                if (el.style.visibility === 'hidden') return false;
                                if (el.offsetParent === null) return false; // not visible
                                return false;
                            }
                        """)
                        
                        if not is_disabled:
                            await element.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            
                            # Try multiple click strategies
                            try:
                                # Strategy A: Normal click
                                await element.click(timeout=2000)
                                logger.info(f"✅ Clicked button (normal): {text_selector}")
                            except:
                                try:
                                    # Strategy B: JavaScript click
                                    await element.evaluate("el => el.click()")
                                    logger.info(f"✅ Clicked button (JS): {text_selector}")
                                except:
                                    # Strategy C: Dispatch click event
                                    await element.dispatch_event("click")
                                    logger.info(f"✅ Clicked button (dispatch): {text_selector}")
                            
                            # Wait for navigation
                            await asyncio.sleep(2)
                            
                            # Check if page changed
                            try:
                                await self.page.wait_for_load_state('networkidle', timeout=8000)
                                logger.info("✅ Page navigation detected (networkidle)")
                            except:
                                # Check if URL changed
                                current_url = self.page.url
                                await asyncio.sleep(1)
                                new_url = self.page.url
                                if current_url != new_url:
                                    logger.info(f"✅ Page navigation detected (URL changed: {current_url} → {new_url})")
                                else:
                                    logger.info("⚠️ Button clicked but page didn't change yet, continuing...")
                            
                            return True
                except Exception as e:
                    logger.debug(f"Text selector {text_selector} failed: {e}")
                    continue
            
            # Strategy 2: Find by CSS selectors
            css_selectors = [
                'button:has-text("Next")',
                'button:has-text("Continue")',
                'button:has-text("Proceed")',
                'button:has-text("Submit")',
                'input[type="submit"][value*="Next" i]',
                'input[type="submit"][value*="Continue" i]',
                'input[type="submit"][value*="Proceed" i]',
                'input[type="button"][value*="Next" i]',
                'input[type="button"][value*="Continue" i]',
                'button[type="submit"]:not([disabled])',
                'input[type="submit"]:not([disabled])',
                'button.next:not([disabled])',
                'button.continue:not([disabled])',
                '#next:not([disabled])',
                '#continue:not([disabled])',
                'button[id*="next" i]:not([disabled])',
                'button[id*="continue" i]:not([disabled])',
                'button[class*="next" i]:not([disabled])',
                'button[class*="continue" i]:not([disabled])',
                'a:has-text("Next")',
                'a:has-text("Continue")'
            ]
            
            for selector in css_selectors:
                try:
                    element = await search_page.wait_for_selector(selector, timeout=2000, state='visible')
                    if element:
                        is_disabled = await element.evaluate("el => el.disabled || el.getAttribute('disabled') !== null")
                        is_visible = await element.is_visible()
                        
                        if not is_disabled and is_visible:
                            await element.scroll_into_view_if_needed()
                            await asyncio.sleep(0.5)
                            
                            try:
                                await element.click(timeout=2000)
                            except:
                                await element.evaluate("el => el.click()")
                            
                            logger.info(f"[NAVIGATION] Clicked button (CSS): {selector}")
                            await asyncio.sleep(2)
                            
                            try:
                                await self.page.wait_for_load_state('networkidle', timeout=8000)
                            except:
                                pass
                            
                            return True
                except Exception as e:
                    logger.debug(f"[NAVIGATION] CSS selector {selector} failed: {e}")
                    continue
            
            # Strategy 3: Find all buttons and check text content - use active_page
            try:
                all_buttons = await search_page.query_selector_all('button, input[type="submit"], input[type="button"], a[href*="#"]')
                logger.info(f"Found {len(all_buttons)} potential buttons")
                
                for btn in all_buttons:
                    try:
                        btn_text = (await btn.text_content() or "").strip()
                        btn_value = await btn.get_attribute('value') or ""
                        btn_type = await btn.get_attribute('type') or ""
                        
                        # Check if button text matches
                        text_lower = (btn_text + " " + btn_value).lower()
                        if any(keyword in text_lower for keyword in ['next', 'continue', 'proceed', 'submit', 'apply']):
                            is_disabled = await btn.evaluate("el => el.disabled || el.getAttribute('disabled') !== null")
                            is_visible = await btn.is_visible()
                            
                            if not is_disabled and is_visible:
                                logger.info(f"🎯 Found matching button: '{btn_text}' (value: '{btn_value}')")
                                await btn.scroll_into_view_if_needed()
                                await asyncio.sleep(0.5)
                                
                                try:
                                    await btn.click(timeout=2000)
                                except:
                                    await btn.evaluate("el => el.click()")
                                
                                logger.info(f"[NAVIGATION] Clicked button: '{btn_text}'")
                                await asyncio.sleep(2)
                                
                                try:
                                    await self.page.wait_for_load_state('networkidle', timeout=8000)
                                except:
                                    pass
                                
                                return True
                    except Exception as e:
                        logger.debug(f"[NAVIGATION] Button check failed: {e}")
                        continue
            except Exception as e:
                logger.debug(f"[NAVIGATION] Button search failed: {e}")
            
            # Strategy 4: Try form submission - use active_page
            try:
                forms = await search_page.query_selector_all('form')
                for form in forms:
                    try:
                        submit_btn = await form.query_selector('button[type="submit"], input[type="submit"]')
                        if submit_btn:
                            is_disabled = await submit_btn.evaluate("el => el.disabled")
                            if not is_disabled:
                                await submit_btn.scroll_into_view_if_needed()
                                await asyncio.sleep(0.5)
                                
                                # Try submitting form directly
                                try:
                                    await form.evaluate("form => form.submit()")
                                    logger.info("✅ Form submitted directly")
                                    await asyncio.sleep(2)
                                    await self.page.wait_for_load_state('networkidle', timeout=8000)
                                    return True
                                except:
                                    await submit_btn.click()
                                    logger.info("✅ Submit button clicked")
                                    await asyncio.sleep(2)
                                    await self.page.wait_for_load_state('networkidle', timeout=8000)
                                    return True
                    except:
                        continue
            except Exception as e:
                logger.debug(f"Form submission failed: {e}")
            
            # Strategy 5: Try pressing Enter on the form - use active_page
            try:
                active_element = await search_page.evaluate("() => document.activeElement")
                if active_element:
                    await search_page.keyboard.press('Enter')
                    logger.info("[NAVIGATION] Pressed Enter key")
                    await asyncio.sleep(2)
                    return True
            except:
                pass
            
            logger.warning("[NAVIGATION FAILED] No Next/Continue/Submit button found or clickable")
            return False
        except Exception as e:
            logger.error(f"[NAVIGATION ERROR] Error navigating to next page: {e}")
            return False
    
    async def run_automation(self) -> Dict[str, Any]:
        """Run the complete automation workflow - fills all pages automatically"""
        results = []
        max_pages = 6  # Form 49A typically has 6 pages
        current_page = 1
        
        logger.info("="*80)
        logger.info("[AUTOMATION START] ========== FORM 49A AUTOMATION STARTING ==========")
        logger.info(f"[AUTOMATION START] Page URL: {self.page.url}")
        logger.info(f"[AUTOMATION START] Total steps: {len(self.steps)}")
        logger.info(f"[AUTOMATION START] Service Config: {self.service_config}")
        logger.info("="*80)
        
        # CRITICAL: Detect and switch to iframe BEFORE starting automation
        logger.info("[AUTOMATION START] Step 1: Detecting iframe...")
        iframe_found = await self.detect_and_switch_to_iframe()
        
        if iframe_found:
            logger.info("[AUTOMATION START] ✅ Using iframe context for form filling")
        else:
            logger.info("[AUTOMATION START] ⚠️ Using main page context for form filling (no iframe found)")
        
        # Wait for page/iframe to be fully ready
        logger.info("[AUTOMATION START] Step 2: Waiting for page/iframe to be ready...")
        try:
            await self.active_page.wait_for_load_state('networkidle', timeout=15000)
            logger.info("[AUTOMATION START] ✅ Network idle reached")
        except:
            logger.warning("[AUTOMATION START] ⚠️ Network idle timeout, trying domcontentloaded")
            try:
                await self.active_page.wait_for_load_state('domcontentloaded', timeout=10000)
                logger.info("[AUTOMATION START] ✅ DOM content loaded")
            except:
                logger.warning("[AUTOMATION START] ⚠️ DOM load timeout, continuing anyway")
        
        await asyncio.sleep(2)  # Additional wait for dynamic content
        logger.info("[AUTOMATION START] Step 3: Starting field filling...")

        # Hard enforcement of first-page defaults to avoid site-side JS ignoring generic fills
        # CRITICAL: This runs BEFORE step-based automation to set initial state
        logger.info("[AUTOMATION START] Forcing first-page defaults based on user preferences...")
        try:
            await self._force_first_page_defaults()
            await asyncio.sleep(1)  # Wait for form to update
        except Exception as e:
            logger.warning(f"[AUTOMATION START] Force defaults failed: {e}")
        
        # CRITICAL: After forcing defaults, verify and correct any wrong selections
        logger.info("[AUTOMATION START] Verifying and correcting first-page selections...")
        try:
            await self._verify_and_correct_first_page()
        except Exception as e:
            logger.warning(f"[AUTOMATION START] Verification failed: {e}")
        
        # Start from current step index
        logger.info(f"[AUTOMATION LOOP] Starting from step {self.current_step_index + 1}/{len(self.steps)}")
        
        while self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            
            logger.info("="*60)
            logger.info(f"[AUTOMATION LOOP] Step {self.current_step_index + 1}/{len(self.steps)}: {step.step_name} ({step.step_id})")
            logger.info(f"[AUTOMATION LOOP] Field type: {step.field_type}, Profile field: {step.profile_field}")
            logger.info("="*60)
            
            # Check if automation is paused or stopped
            if self.status == AutomationStatus.PAUSED:
                logger.info("[AUTOMATION LOOP] ⏸️ Automation paused by user")
                return {
                    "status": "paused",
                    "current_step": step.step_id,
                    "message": "Automation paused by user",
                    "results": results
                }
            
            if self.status == AutomationStatus.STOPPED:
                logger.info("[AUTOMATION LOOP] ⛔ Automation stopped by user")
                return {
                    "status": "stopped",
                    "current_step": step.step_id,
                    "message": "Automation stopped by user",
                    "results": results
                }
            
            # Check if field is already filled (manual progress detection)
            logger.info(f"[AUTOMATION LOOP] Checking if field already filled: {step.step_name}")
            is_filled = await self._check_if_field_filled(step)
            if is_filled:
                logger.info(f"[AUTOMATION LOOP] ⏭️ Field already filled (manual progress): {step.step_name}")
                step.status = StepStatus.SKIPPED
                self.current_step_index += 1
                continue
            
            # Execute step
            logger.info(f"[AUTOMATION LOOP] Executing step: {step.step_name}")
            try:
                result = await self.execute_step(step)
                results.append(result)
                
                logger.info(f"[AUTOMATION LOOP] Step result: {result.get('status')} - {result.get('message', '')}")
                
                # If step requires user input, pause
                if result.get("requires_user"):
                    return {
                        "status": "waiting_for_user",
                        "current_step": step.step_id,
                        "waiting_for_field": self.waiting_for_field,
                        "message": result["message"],
                        "results": results
                    }
                
                # If step had an error but is not critical, log and continue
                if result.get("status") == "error":
                    error_msg = result.get("message", "Unknown error")
                    logger.warning(f"[AUTOMATION LOOP] ⚠️ Step had error but continuing: {error_msg}")
                    # Don't stop automation for non-critical errors - continue to next step
                
            except Exception as step_error:
                logger.error(f"[AUTOMATION LOOP] ❌ Exception during step execution: {step_error}")
                # Log the error but continue to next step (don't stop automation)
                results.append({
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "status": "error",
                    "message": f"Exception: {str(step_error)}",
                    "requires_user": False
                })
            
            # Move to next step (always, even if there was an error)
            self.current_step_index += 1
            
            # After filling a field, check if we need to navigate to next page
            # Form 49A first page typically has: Mode selection, Status, PAN CARD Mode
            # Navigate after first page is complete (after STEP_02B - PAN CARD Mode)
            should_try_navigate = False
            
            # Check current step ID to determine if we should navigate
            current_step_id = step.step_id if step else None
            
            # Navigate after first page fields are filled
            if current_step_id in ["STEP_02B"]:  # After PAN CARD Mode
                should_try_navigate = True
                logger.info(f"[NAVIGATION] Completed first page fields, checking for Submit/Next button...")
            # Also try after key steps on other pages
            elif current_step_id in ["STEP_06", "STEP_10", "STEP_14"]:  # After DOB, Phone, Pincode
                should_try_navigate = True
                logger.info(f"[NAVIGATION] Completed step {current_step_id}, checking for Next button...")
            # Periodic check every few steps
            elif self.current_step_index > 0 and self.current_step_index % 4 == 0:
                should_try_navigate = True
                logger.info(f"[NAVIGATION] Periodic check: step {self.current_step_index}, checking for Next button...")
            
            if should_try_navigate and current_page < max_pages:
                # CRITICAL: Check on active_page (iframe or main)
                try:
                    next_button_exists = await self.active_page.evaluate("""
                        () => {
                            const buttons = document.querySelectorAll('button, input[type="submit"], input[type="button"], a');
                            for (let btn of buttons) {
                                const text = (btn.textContent || btn.value || '').toLowerCase();
                                if (text.includes('next') || text.includes('continue') || text.includes('proceed') || text.includes('submit')) {
                                    if (!btn.disabled && btn.offsetParent !== null) {
                                        return true;
                                    }
                                }
                            }
                            return false;
                        }
                    """)
                    
                    if next_button_exists:
                        logger.info(f"[NAVIGATION] Next button found, attempting navigation...")
                        try:
                            navigated = await self.navigate_to_next_page()
                            if navigated:
                                current_page += 1
                                logger.info(f"[NAVIGATION SUCCESS] ✅ Navigated to page {current_page}")
                                
                                # Re-detect iframe for new page
                                await asyncio.sleep(2)  # Wait for next page to load
                                try:
                                    await self.detect_and_switch_to_iframe()
                                    # Wait for new page to be ready
                                    await self.active_page.wait_for_load_state('domcontentloaded', timeout=10000)
                                    await asyncio.sleep(1)
                                except Exception as iframe_err:
                                    logger.warning(f"[NAVIGATION] Iframe re-detection failed: {iframe_err}, continuing...")
                            else:
                                logger.warning(f"[NAVIGATION FAILED] Next button exists but navigation failed - will retry later")
                                # Don't stop automation - continue filling fields
                        except Exception as nav_error:
                            logger.error(f"[NAVIGATION ERROR] Navigation exception: {nav_error} - continuing automation")
                            # Don't stop automation - continue to next step
                    else:
                        logger.debug(f"[NAVIGATION] No Next button found yet (page {current_page})")
                except Exception as e:
                    logger.error(f"[NAVIGATION ERROR] Error checking for Next button: {e} - continuing automation")
                    # Don't stop automation - continue to next step
            
            # Small delay between steps
            await asyncio.sleep(0.5)
        
        # After filling all fields, try to submit or go to final page
        if self.current_step_index >= len(self.steps):
            logger.info("✅ All fields filled, attempting final submission...")
            # Try to navigate to next page multiple times (for final submission)
            max_submit_attempts = 3
            for attempt in range(max_submit_attempts):
                logger.info(f"Submission attempt {attempt + 1}/{max_submit_attempts}...")
                navigated = await self.navigate_to_next_page()
                if navigated:
                    logger.info("✅ Final submission successful!")
                    break
                else:
                    await asyncio.sleep(2)
                    if attempt < max_submit_attempts - 1:
                        logger.info(f"Retrying submission in 2 seconds...")
            
            await asyncio.sleep(2)
        
        # All steps completed
        self.status = AutomationStatus.COMPLETED
        return {
            "status": "completed",
            "message": "Form 49A automation completed successfully - all pages filled",
            "results": results,
            "pages_completed": current_page
        }
    
    async def resume_automation(self) -> Dict[str, Any]:
        """Resume automation from current step"""
        # Reset status if it was waiting
        if self.status == AutomationStatus.WAITING_FOR_USER:
            # Check if waiting field was manually filled
            if self.waiting_for_field:
                # Find the step that was waiting
                waiting_step = None
                for i, step in enumerate(self.steps):
                    if step.profile_field == self.waiting_for_field and step.status == StepStatus.WAITING_USER:
                        waiting_step = step
                        self.current_step_index = i
                        break
                
                if waiting_step:
                    # Check if manually filled
                    if await self.check_manual_fill(waiting_step):
                        waiting_step.status = StepStatus.COMPLETED
                        waiting_step.completed_at = datetime.now()
                        self.waiting_for_field = None
                        self.status = AutomationStatus.RUNNING
                        # Move to next step
                        self.current_step_index += 1
                    else:
                        # Still waiting - return waiting status
                        return {
                            "status": "waiting_for_user",
                            "current_step": waiting_step.step_id,
                            "waiting_for_field": self.waiting_for_field,
                            "message": f"Still waiting for '{self.waiting_for_field}'. Please fill it manually.",
                            "results": []
                        }
            else:
                # No specific field waiting - just resume
                self.status = AutomationStatus.RUNNING
        
        # Continue automation from current step
        return await self.run_automation()
    
    def pause(self):
        """Pause automation safely"""
        self.status = AutomationStatus.PAUSED
    
    def stop(self):
        """Stop automation"""
        self.status = AutomationStatus.STOPPED
    
    def get_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        current_step = self.get_current_step()
        completed_steps = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        total_steps = len(self.steps)
        
        return {
            "status": self.status.value,
            "current_step": current_step.step_id if current_step else None,
            "current_step_name": current_step.step_name if current_step else None,
            "progress": f"{completed_steps}/{total_steps}",
            "waiting_for_field": self.waiting_for_field,
            "steps": [
                {
                    "step_id": s.step_id,
                    "step_name": s.step_name,
                    "status": s.status.value,
                    "required": s.required
                }
                for s in self.steps
            ]
        }

