"""
KYRON Bihar Residence Certificate (BRC) Automation Engine
Automates RTPS Bihar portal for Residence Certificate application
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

class BRCStep:
    """Represents a single step in BRC workflow"""
    
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

class BRCAutomationEngine:
    """
    Fail-safe BRC automation engine with step-based workflow for RTPS Bihar portal
    """
    
    def __init__(self, page, user_profile: Dict, service_config: Dict = None, user_id: str = None):
        self.page = page
        self.active_page = page
        self.user_profile = user_profile
        self.service_config = service_config or {}
        self.user_id = user_id
        self.current_step_index = 0
        self.status = AutomationStatus.RUNNING
        self.steps: List[BRCStep] = []
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
        
        logger.info("="*60)
        logger.info("BRC Automation Engine Initialized")
        logger.info(f"Service Config (Request Data): {self.service_config}")
        logger.info(f"User Profile Keys: {list(self.user_profile.keys())}")
        if self.data_aggregator:
            unified = self.data_aggregator.get_unified_data()
            logger.info(f"Unified Data (Request + Master + Documents): {len([k for k in unified.keys() if not k.startswith('_')])} fields")
        logger.info(f"Initial Page URL: {page.url if page else 'None'}")
        logger.info("="*60)
        
        # Initialize BRC steps
        self._initialize_steps()

    def _initialize_steps(self):
        """Initialize BRC application steps"""
        self.steps = [
            BRCStep(
                step_id="navigate_to_rtps",
                step_name="Navigate to RTPS Bihar Portal",
                required=True,
                selectors=["a:has-text('Residence Certificate')", "a:has-text('निवास प्रमाण पत्र')"]
            ),
            BRCStep(
                step_id="applicant_name",
                step_name="Applicant Full Name",
                required=True,
                profile_field="full_name",
                selectors=[
                    "input[name*='name' i]",
                    "input[id*='name' i]",
                    "input[placeholder*='name' i]",
                    "//label[contains(text(), 'Name') or contains(text(), 'नाम')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="father_name",
                step_name="Father's Name",
                required=True,
                profile_field="father_name",
                selectors=[
                    "input[name*='father' i]",
                    "input[id*='father' i]",
                    "//label[contains(text(), 'Father') or contains(text(), 'पिता')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="mother_name",
                step_name="Mother's Name",
                required=True,
                profile_field="mother_name",
                selectors=[
                    "input[name*='mother' i]",
                    "input[id*='mother' i]",
                    "//label[contains(text(), 'Mother') or contains(text(), 'माता')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="date_of_birth",
                step_name="Date of Birth",
                required=True,
                profile_field="date_of_birth",
                selectors=[
                    "input[name*='dob' i]",
                    "input[name*='birth' i]",
                    "input[type='date']",
                    "//label[contains(text(), 'Date of Birth') or contains(text(), 'जन्म तिथि')]/following::input[1]"
                ],
                field_type="date"
            ),
            BRCStep(
                step_id="gender",
                step_name="Gender",
                required=True,
                profile_field="gender",
                selectors=[
                    "select[name*='gender' i]",
                    "select[id*='gender' i]",
                    "//label[contains(text(), 'Gender') or contains(text(), 'लिंग')]/following::select[1]"
                ],
                field_type="select"
            ),
            BRCStep(
                step_id="mobile_number",
                step_name="Mobile Number",
                required=True,
                profile_field="mobile_number",
                selectors=[
                    "input[name*='mobile' i]",
                    "input[name*='phone' i]",
                    "input[type='tel']",
                    "//label[contains(text(), 'Mobile') or contains(text(), 'मोबाइल')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="aadhaar_number",
                step_name="Aadhaar Number",
                required=True,
                profile_field="aadhaar_number",
                selectors=[
                    "input[name*='aadhaar' i]",
                    "input[name*='aadhar' i]",
                    "input[id*='aadhaar' i]",
                    "//label[contains(text(), 'Aadhaar') or contains(text(), 'आधार')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="permanent_address",
                step_name="Permanent Address",
                required=True,
                profile_field="permanent_address",
                selectors=[
                    "textarea[name*='address' i]",
                    "textarea[id*='address' i]",
                    "input[name*='address' i]",
                    "//label[contains(text(), 'Address') or contains(text(), 'पता')]/following::textarea[1]",
                    "//label[contains(text(), 'Address') or contains(text(), 'पता')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="district",
                step_name="District",
                required=True,
                profile_field="district",
                selectors=[
                    "select[name*='district' i]",
                    "select[id*='district' i]",
                    "//label[contains(text(), 'District') or contains(text(), 'जिला')]/following::select[1]"
                ],
                field_type="select"
            ),
            BRCStep(
                step_id="block_circle",
                step_name="Block / Circle",
                required=True,
                profile_field="block_circle",
                selectors=[
                    "input[name*='block' i]",
                    "input[name*='circle' i]",
                    "select[name*='block' i]",
                    "//label[contains(text(), 'Block') or contains(text(), 'ब्लॉक')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="panchayat_ward",
                step_name="Panchayat / Ward",
                required=True,
                profile_field="panchayat_ward",
                selectors=[
                    "input[name*='panchayat' i]",
                    "input[name*='ward' i]",
                    "//label[contains(text(), 'Panchayat') or contains(text(), 'पंचायत')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="post_office",
                step_name="Post Office",
                required=True,
                profile_field="post_office",
                selectors=[
                    "input[name*='post' i]",
                    "input[name*='postoffice' i]",
                    "//label[contains(text(), 'Post Office') or contains(text(), 'डाकघर')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="pin_code",
                step_name="Pin Code",
                required=True,
                profile_field="pin_code",
                selectors=[
                    "input[name*='pin' i]",
                    "input[name*='pincode' i]",
                    "input[name*='zip' i]",
                    "//label[contains(text(), 'Pin') or contains(text(), 'पिन')]/following::input[1]"
                ],
                field_type="text"
            ),
            BRCStep(
                step_id="purpose",
                step_name="Purpose of Certificate",
                required=True,
                profile_field="purpose",
                selectors=[
                    "select[name*='purpose' i]",
                    "select[id*='purpose' i]",
                    "//label[contains(text(), 'Purpose') or contains(text(), 'उद्देश्य')]/following::select[1]"
                ],
                field_type="select"
            ),
            BRCStep(
                step_id="upload_documents",
                step_name="Upload Documents",
                required=True,
                selectors=[
                    "input[type='file']",
                    "input[name*='document' i]",
                    "input[name*='file' i]"
                ],
                field_type="file"
            ),
            BRCStep(
                step_id="submit_application",
                step_name="Submit Application",
                required=True,
                selectors=[
                    "button:has-text('Submit')",
                    "button:has-text('Submit Application')",
                    "button:has-text('Apply')",
                    "button[type='submit']",
                    "input[type='submit']",
                    "//button[contains(text(), 'Submit') or contains(text(), 'आवेदन करें')]"
                ],
                field_type="button"
            )
        ]

    async def execute(self) -> Dict[str, Any]:
        """Execute the complete BRC automation workflow"""
        try:
            logger.info("Starting BRC automation execution...")
            
            # Wait for page to be ready
            await self.active_page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            # Execute each step
            for i, step in enumerate(self.steps):
                if self.status == AutomationStatus.STOPPED or self.status == AutomationStatus.ERROR:
                    break
                
                if self.status == AutomationStatus.PAUSED:
                    await self._wait_for_resume()
                
                self.current_step_index = i
                logger.info(f"Executing step {i+1}/{len(self.steps)}: {step.step_name}")
                
                try:
                    success, error = await self._execute_step(step)
                    if success:
                        step.status = StepStatus.COMPLETED
                        step.completed_at = datetime.now().isoformat()
                        logger.info(f"✅ Step {step.step_name} completed successfully")
                    else:
                        step.status = StepStatus.ERROR
                        step.error_message = error
                        logger.error(f"❌ Step {step.step_name} failed: {error}")
                        
                        # If required step fails, stop automation
                        if step.required:
                            self.status = AutomationStatus.ERROR
                            return {
                                "success": False,
                                "error": f"Required step '{step.step_name}' failed: {error}",
                                "completed_steps": i,
                                "total_steps": len(self.steps)
                            }
                except Exception as e:
                    logger.error(f"Exception in step {step.step_name}: {str(e)}")
                    step.status = StepStatus.ERROR
                    step.error_message = str(e)
                    
                    if step.required:
                        self.status = AutomationStatus.ERROR
                        return {
                            "success": False,
                            "error": f"Exception in step '{step.step_name}': {str(e)}",
                            "completed_steps": i,
                            "total_steps": len(self.steps)
                        }
                
                # Small delay between steps
                await asyncio.sleep(1)
            
            # All steps completed
            if self.status != AutomationStatus.ERROR:
                self.status = AutomationStatus.COMPLETED
                return {
                    "success": True,
                    "message": "BRC application submitted successfully",
                    "completed_steps": len(self.steps),
                    "total_steps": len(self.steps)
                }
            else:
                return {
                    "success": False,
                    "error": "Automation stopped due to errors",
                    "completed_steps": self.current_step_index,
                    "total_steps": len(self.steps)
                }
                
        except Exception as e:
            logger.error(f"Fatal error in BRC automation: {str(e)}")
            self.status = AutomationStatus.ERROR
            return {
                "success": False,
                "error": f"Fatal error: {str(e)}",
                "completed_steps": self.current_step_index,
                "total_steps": len(self.steps)
            }

    async def _execute_step(self, step: BRCStep) -> Tuple[bool, Optional[str]]:
        """Execute a single step"""
        try:
            if step.step_id == "navigate_to_rtps":
                return await self._navigate_to_service()
            elif step.step_id == "submit_application":
                return await self._submit_application(step)
            elif step.field_type == "file":
                return await self._upload_document(step)
            elif step.field_type == "select":
                return await self._fill_select_field(step)
            elif step.field_type == "text" or step.field_type == "date":
                return await self._fill_text_field(step)
            else:
                return await self._fill_field(step)
        except Exception as e:
            return False, str(e)

    async def _navigate_to_service(self) -> Tuple[bool, Optional[str]]:
        """Navigate to Residence Certificate service on RTPS portal"""
        try:
            # Wait for page to load
            await self.active_page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            # Try to find and click Residence Certificate link
            for selector in [
                "a:has-text('Residence Certificate')",
                "a:has-text('निवास प्रमाण पत्र')",
                "a[href*='residence' i]",
                "//a[contains(text(), 'Residence') or contains(text(), 'निवास')]"
            ]:
                try:
                    element = await self.active_page.query_selector(selector)
                    if element:
                        await element.click()
                        await asyncio.sleep(3)
                        await self.active_page.wait_for_load_state("networkidle", timeout=30000)
                        logger.info("✅ Navigated to Residence Certificate service")
                        return True, None
                except:
                    continue
            
            # If direct link not found, try to find "Apply" or "New Application" button
            for selector in [
                "button:has-text('Apply')",
                "button:has-text('New Application')",
                "a:has-text('Apply')",
                "//button[contains(text(), 'Apply') or contains(text(), 'आवेदन')]"
            ]:
                try:
                    element = await self.active_page.query_selector(selector)
                    if element:
                        await element.click()
                        await asyncio.sleep(3)
                        await self.active_page.wait_for_load_state("networkidle", timeout=30000)
                        logger.info("✅ Clicked Apply button")
                        return True, None
                except:
                    continue
            
            return False, "Could not find Residence Certificate service link"
        except Exception as e:
            return False, f"Navigation error: {str(e)}"

    async def _fill_text_field(self, step: BRCStep) -> Tuple[bool, Optional[str]]:
        """Fill a text input field"""
        try:
            value = self._get_profile_value(step.profile_field)
            if not value:
                return False, f"No value found for field: {step.profile_field}"
            
            # Try each selector
            for selector in step.selectors:
                try:
                    if selector.startswith("//"):
                        # XPath selector
                        element = await self.active_page.query_selector(f"xpath={selector}")
                    else:
                        element = await self.active_page.query_selector(selector)
                    
                    if element:
                        # Clear and fill
                        await element.fill("")
                        await element.fill(str(value))
                        
                        # Trigger events
                        await element.dispatch_event("input")
                        await element.dispatch_event("change")
                        await element.dispatch_event("blur")
                        
                        await asyncio.sleep(0.5)
                        
                        # Verify
                        filled_value = await element.input_value()
                        if str(value) in filled_value or filled_value == str(value):
                            logger.info(f"✅ Filled {step.step_name}: {value}")
                            return True, None
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            return False, f"Could not find or fill field: {step.step_name}"
        except Exception as e:
            return False, f"Error filling text field: {str(e)}"

    async def _fill_select_field(self, step: BRCStep) -> Tuple[bool, Optional[str]]:
        """Fill a select dropdown field"""
        try:
            value = self._get_profile_value(step.profile_field)
            if not value:
                return False, f"No value found for field: {step.profile_field}"
            
            # Try each selector
            for selector in step.selectors:
                try:
                    if selector.startswith("//"):
                        element = await self.active_page.query_selector(f"xpath={selector}")
                    else:
                        element = await self.active_page.query_selector(selector)
                    
                    if element:
                        # Try select by value first, then by label
                        try:
                            await element.select_option(value=str(value))
                        except:
                            try:
                                await element.select_option(label=str(value))
                            except:
                                # Try case-insensitive match
                                options = await element.query_selector_all("option")
                                for opt in options:
                                    opt_text = await opt.inner_text()
                                    if str(value).lower() in opt_text.lower():
                                        await element.select_option(value=await opt.get_attribute("value"))
                                        break
                        
                        await asyncio.sleep(0.5)
                        
                        # Verify
                        selected_value = await element.evaluate("el => el.value")
                        if selected_value:
                            logger.info(f"✅ Selected {step.step_name}: {value}")
                            return True, None
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            return False, f"Could not find or select field: {step.step_name}"
        except Exception as e:
            return False, f"Error filling select field: {str(e)}"

    async def _upload_document(self, step: BRCStep) -> Tuple[bool, Optional[str]]:
        """Upload document file"""
        try:
            # Get document path from profile or service config
            doc_path = self.service_config.get("document_path") or self.user_profile.get("document_path")
            if not doc_path:
                return False, "No document path provided"
            
            # Try each selector
            for selector in step.selectors:
                try:
                    element = await self.active_page.query_selector(selector)
                    if element:
                        await element.set_input_files(doc_path)
                        await asyncio.sleep(2)
                        logger.info(f"✅ Uploaded document: {doc_path}")
                        return True, None
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            return False, "Could not find file upload field"
        except Exception as e:
            return False, f"Error uploading document: {str(e)}"

    async def _submit_application(self, step: BRCStep) -> Tuple[bool, Optional[str]]:
        """Submit the application"""
        try:
            # Wait for form to be ready
            await asyncio.sleep(2)
            
            # Try each selector
            for selector in step.selectors:
                try:
                    if selector.startswith("//"):
                        element = await self.active_page.query_selector(f"xpath={selector}")
                    else:
                        element = await self.active_page.query_selector(selector)
                    
                    if element:
                        # Check if button is enabled
                        is_disabled = await element.get_attribute("disabled")
                        if is_disabled:
                            return False, "Submit button is disabled"
                        
                        # Click submit
                        await element.click()
                        await asyncio.sleep(3)
                        
                        # Wait for navigation or success message
                        try:
                            await self.active_page.wait_for_load_state("networkidle", timeout=10000)
                        except:
                            pass
                        
                        logger.info("✅ Application submitted")
                        return True, None
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {str(e)}")
                    continue
            
            return False, "Could not find submit button"
        except Exception as e:
            return False, f"Error submitting application: {str(e)}"

    async def _fill_field(self, step: BRCStep) -> Tuple[bool, Optional[str]]:
        """Generic field filler"""
        return await self._fill_text_field(step)

    def _get_profile_value(self, field_name: str) -> Optional[str]:
        """
        Get value using intelligent data aggregation
        Priority: Request Data > Master Profile > Document Vault > Defaults
        """
        # Use Data Aggregator if available
        if self.data_aggregator:
            value = self.data_aggregator.get_field_value(field_name)
            if value:
                source = self.data_aggregator.get_data_source(field_name)
                logger.debug(f"[BRC] Field '{field_name}' = '{value}' (source: {source})")
                return str(value)
        
        # Fallback to old method if Data Aggregator not available
        # Check service config first (user-provided data)
        if field_name in self.service_config:
            return str(self.service_config[field_name])
        
        # Check user profile
        if field_name in self.user_profile:
            return str(self.user_profile[field_name])
        
        # Try common field name variations
        variations = {
            "full_name": ["name", "full_name", "applicant_name", "fullName", "applicant_name"],
            "date_of_birth": ["dob", "date_of_birth", "birth_date", "dateOfBirth"],
            "mobile_number": ["mobile", "phone", "mobile_number", "phone_number", "phone"],
            "aadhaar_number": ["aadhaar", "aadhar", "aadhaar_number", "aadhaarNumber"],
            "permanent_address": ["address", "permanent_address", "residential_address", "address", "permanentAddress"],
            "father_name": ["fatherName", "father_name", "fathername"],
            "mother_name": ["motherName", "mother_name", "mothername"],
            "gender": ["gender", "sex"],
            "district": ["district"],
            "block_circle": ["block", "block_circle", "blockCircle"],
            "panchayat_ward": ["panchayat", "panchayat_ward", "panchayatWard"],
            "post_office": ["postOffice", "post_office", "postoffice"],
            "pin_code": ["pincode", "pin_code", "pincode"]
        }
        
        if field_name in variations:
            for var in variations[field_name]:
                if var in self.service_config:
                    return str(self.service_config[var])
                if var in self.user_profile:
                    return str(self.user_profile[var])
        
        return None

    async def _wait_for_resume(self):
        """Wait for automation to be resumed"""
        while self.status == AutomationStatus.PAUSED:
            await asyncio.sleep(1)

    def pause(self):
        """Pause automation"""
        self.status = AutomationStatus.PAUSED
        logger.info("Automation paused")

    def resume(self):
        """Resume automation"""
        if self.status == AutomationStatus.PAUSED:
            self.status = AutomationStatus.RUNNING
            logger.info("Automation resumed")

    def stop(self):
        """Stop automation"""
        self.status = AutomationStatus.STOPPED
        logger.info("Automation stopped")

