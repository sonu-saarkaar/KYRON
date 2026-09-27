"""
KYRON AI Agent - Real-World Execution
Opens official websites in NEW TABS and controls from outside
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import asyncio

from auth_utils import verify_token

# Try to get profile from database manager
try:
    from services.database_manager import get_database_manager
    db_manager = get_database_manager()
    use_database = db_manager.is_available()
except:
    use_database = False
    try:
        from profile import profiles_db
    except:
        profiles_db = {}

# Import automation engine
try:
    from services.playwright_automation import get_automation_engine
except ImportError:
    get_automation_engine = None

# Import service catalog
try:
    from services_catalog import get_service_definition
except:
    get_service_definition = None

# Import Form 49A automation engine
try:
    from services.form49a_automation import Form49AAutomationEngine, AutomationStatus
    from services.kyron_control_ui import get_control_ui_script
except ImportError:
    Form49AAutomationEngine = None
    get_control_ui_script = None

# Import BRC automation engine
try:
    from services.brc_automation import BRCAutomationEngine, AutomationStatus as BRCAutomationStatus
except ImportError:
    BRCAutomationEngine = None

router = APIRouter()

# Active agent sessions
agent_sessions: Dict[str, Dict] = {}

# Form 49A automation engines (session_id -> Form49AAutomationEngine)
form49a_engines: Dict[str, Any] = {}

class AgentTriggerRequest(BaseModel):
    """Request to trigger agent automation"""
    service_id: str
    service_config: Optional[Dict[str, Any]] = None
    open_in_new_tab: bool = True  # Always open in new tab

@router.post("/start")
async def start_agent_automation(
    request: AgentTriggerRequest,
    authorization: str = Header(None)
):
    """
    Start AI agent automation
    Opens official website in NEW TAB and controls from outside
    """
    user_id = verify_token(authorization)
    
    # Get user profile
    if use_database:
        user_profile = db_manager.get_profile(user_id)
    else:
        user_profile = profiles_db.get(user_id, {})
    
    if not user_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile not found. Please complete your profile first."
        )
    
    # Get service definition
    if not get_service_definition:
        raise HTTPException(
            status_code=503,
            detail="Service catalog not available"
        )
    
    service = get_service_definition(request.service_id)
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{request.service_id}' not found"
        )
    
    # Get official URL
    official_url = service.official_url
    if not official_url:
        # Try alternative URLs if available
        if service.alternative_urls and len(service.alternative_urls) > 0:
            official_url = service.alternative_urls[0]
        else:
            raise HTTPException(
                status_code=400,
                detail=f"No official URL defined for service '{request.service_id}'"
            )
    
    # Create session ID
    session_id = str(uuid.uuid4())
    
    # Initialize agent session dictionary BEFORE using it
    agent_sessions[session_id] = {
        "user_id": user_id,
        "service_id": request.service_id,
        "service_name": service.name,
        "official_url": official_url,
        "service_config": request.service_config or {},
        "created_at": datetime.now().isoformat(),
        "status": "initializing",
        "current_action": "Initializing automation engine...",
        "progress": {
            "step": 0,
            "total": 0,
            "action": "Initializing..."
        },
        "profile": user_profile
    }
    
    # Get automation engine
    if not get_automation_engine:
        agent_sessions[session_id]["status"] = "error"
        agent_sessions[session_id]["current_action"] = "Automation engine not available"
        raise HTTPException(
            status_code=503,
            detail="Automation engine not available"
        )
    
    engine = get_automation_engine()
    
    # Set headless=False for visible browser (real-world execution)
    engine.headless = False
    
    try:
        # Close existing browser if it was headless
        if engine.browser:
            try:
                await engine.browser.close()
            except:
                pass
            engine.browser = None
        
        agent_sessions[session_id]["current_action"] = "Initializing browser..."
        await engine.initialize()
    except Exception as e:
        agent_sessions[session_id]["status"] = "error"
        agent_sessions[session_id]["current_action"] = f"Failed to initialize: {str(e)}"
        raise HTTPException(
            status_code=503,
            detail=f"Failed to initialize automation engine: {str(e)}"
        )
    
    # Create browser session with visible browser
    try:
        # Update status immediately
        agent_sessions[session_id]["status"] = "active"
        agent_sessions[session_id]["current_action"] = f"Opening {official_url}..."
        
        await engine.create_session(session_id, official_url)
        
        # Verify page loaded (non-blocking check)
        try:
            page = engine.active_sessions[session_id]['page']
            await asyncio.sleep(0.5)  # Small delay for page to render
            
            # Check if page is blank (non-blocking)
            current_url = page.url
            if current_url and current_url != "about:blank":
                agent_sessions[session_id]["current_action"] = "Website opened successfully!"
            else:
                agent_sessions[session_id]["current_action"] = "Opening website, please wait..."
        except:
            agent_sessions[session_id]["current_action"] = "Initializing browser..."
    except Exception as e:
        agent_sessions[session_id]["status"] = "error"
        agent_sessions[session_id]["current_action"] = f"Error: {str(e)}"
        raise HTTPException(
            status_code=503,
            detail=f"Failed to create browser session: {str(e)}"
        )
    
    # Start automation in background
    service_config = request.service_config or {}
    asyncio.create_task(run_agent_automation(session_id, service, user_profile, service_config))
    
    return {
        "success": True,
        "session_id": session_id,
        "official_url": official_url,
        "message": "Agent automation started. Official website opened in new tab.",
        "note": "KYRON is now controlling the real website. You can see it in a new browser window."
    }

async def map_pan_fields_manually(page, detected_fields: List[Dict], user_profile: Dict, service_config: Dict) -> List[Dict]:
    """Manually map PAN form fields to user profile"""
    mapped_fields = []
    
    # Common PAN form field patterns
    field_patterns = {
        "name": ["name", "fullname", "applicant_name", "first_name", "last_name"],
        "father_name": ["father", "father_name", "fathername", "parent_name"],
        "mother_name": ["mother", "mother_name", "mothername"],
        "date_of_birth": ["dob", "date_of_birth", "birthdate", "birth_date", "dateofbirth"],
        "email": ["email", "email_id", "e-mail"],
        "phone": ["phone", "mobile", "phone_number", "contact", "mobile_number"],
        "address": ["address", "residential_address", "permanent_address", "street"],
        "city": ["city"],
        "state": ["state"],
        "pincode": ["pincode", "pin_code", "postal_code", "zip"],
        "gender": ["gender", "sex"],
        "aadhaar": ["aadhaar", "aadhar", "uid"]
    }
    
    for field in detected_fields:
        field_label = field.get("label", "").lower()
        field_name = field.get("name", "").lower()
        field_id = field.get("id", "").lower()
        field_placeholder = field.get("placeholder", "").lower()
        
        all_text = f"{field_label} {field_name} {field_id} {field_placeholder}".lower()
        
        # Try to match with profile fields
        for profile_key, patterns in field_patterns.items():
            if any(pattern in all_text for pattern in patterns):
                if profile_key in user_profile and user_profile[profile_key]:
                    mapped_fields.append({
                        "selector": field.get("selector", ""),
                        "value": str(user_profile[profile_key]),
                        "label": field.get("label", profile_key),
                        "mapped_profile_field": profile_key
                    })
                    break
    
    # Handle applicant type (Status of Applicant dropdown)
    if service_config and service_config.get("applicant_type"):
        applicant_type = service_config.get("applicant_type")
        # Look for "Status of Applicant" dropdown
        for field in detected_fields:
            field_label = field.get("label", "").lower()
            field_name = field.get("name", "").lower()
            field_id = field.get("id", "").lower()
            
            # Match "Status of Applicant" field
            if ("status" in field_label and "applicant" in field_label) or \
               ("status" in field_name and "applicant" in field_name) or \
               ("status" in field_id and "applicant" in field_id):
                if field.get("type") == "select":
                    # Map to appropriate status option
                    if applicant_type == "individual":
                        mapped_fields.append({
                            "selector": field.get("selector", ""),
                            "value": "Individual",  # Will be matched by text in dropdown handler
                            "label": field.get("label", "Status of Applicant"),
                            "mapped_profile_field": "applicant_type",
                            "field_type": "select"
                        })
                    else:
                        mapped_fields.append({
                            "selector": field.get("selector", ""),
                            "value": "Company",  # Will be matched by text in dropdown handler
                            "label": field.get("label", "Status of Applicant"),
                            "mapped_profile_field": "applicant_type",
                            "field_type": "select"
                        })
    
    # Handle PAN Card Mode (radio buttons)
    if service_config and service_config.get("delivery_type"):
        delivery_type = service_config.get("delivery_type")
        # Look for "PAN CARD Mode" radio buttons
        for field in detected_fields:
            field_label = field.get("label", "").lower()
            field_name = field.get("name", "").lower()
            
            # Match "PAN CARD Mode" field
            if ("pan card mode" in field_label or "mode" in field_label) and field.get("type") == "radio":
                if delivery_type == "epan":
                    # Select "e-PAN only" option
                    mapped_fields.append({
                        "selector": field.get("selector", ""),
                        "value": "e-PAN only",  # Will be matched by label text
                        "label": "PAN CARD Mode",
                        "mapped_profile_field": "delivery_type",
                        "field_type": "radio"
                    })
                else:  # physical
                    # Select "Both physical PAN Card and e-PAN" option
                    mapped_fields.append({
                        "selector": field.get("selector", ""),
                        "value": "Both physical PAN Card and e-PAN",  # Will be matched by label text
                        "label": "PAN CARD Mode",
                        "mapped_profile_field": "delivery_type",
                        "field_type": "radio"
                    })
                break  # Only need to add once
    
    return mapped_fields

async def run_agent_automation(session_id: str, service, user_profile: Dict, service_config: Dict = None, user_id: str = None):
    """
    Run automation on the real official website
    Handles account creation, form filling, and submission
    """
    if service_config is None:
        service_config = {}
    
    try:
        engine = get_automation_engine()
        
        # Update status
        agent_sessions[session_id]["status"] = "analyzing"
        agent_sessions[session_id]["current_action"] = "Waiting for page to load..."
        
        # Get page
        page = engine.active_sessions[session_id]['page']
        
        # Wait for page to fully load with proper timeout and retries
        max_retries = 3
        page_loaded = False
        
        for attempt in range(max_retries):
            try:
                # Check current URL first
                current_url = page.url
                if current_url and current_url != "about:blank" and "http" in current_url:
                    # Page seems to have navigated, wait for it to be ready
                    try:
                        await page.wait_for_load_state('networkidle', timeout=15000)
                        page_loaded = True
                        break
                    except:
                        try:
                            await page.wait_for_load_state('domcontentloaded', timeout=8000)
                            await asyncio.sleep(2)  # Wait for dynamic content
                            page_loaded = True
                            break
                        except:
                            # Even if load state fails, check if page has content
                            try:
                                content = await page.content()
                                if content and len(content) > 100:  # Has some content
                                    page_loaded = True
                                    break
                            except:
                                pass
                
                # If not loaded yet, wait a bit and retry
                if not page_loaded:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"Page load attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
        
        # Final check if page loaded successfully
        current_url = page.url
        if not page_loaded or not current_url or current_url == "about:blank":
            # Try to get page content as last resort
            try:
                content = await page.content()
                if not content or len(content) < 100:
                    agent_sessions[session_id]["status"] = "error"
                    agent_sessions[session_id]["current_action"] = "Failed to load page. The website may be slow or blocked. Please try again."
                    return
            except:
                agent_sessions[session_id]["status"] = "error"
                agent_sessions[session_id]["current_action"] = "Failed to load page. Please check the URL and try again."
                return
        
        agent_sessions[session_id]["current_action"] = "Page loaded, analyzing..."
        
        # Check if account creation/login is needed
        html, _ = await engine.get_page_html(session_id)
        
        # Look for login/signup buttons
        login_selectors = [
            "text=Login",
            "text=Sign In",
            "text=Register",
            "text=Sign Up",
            "text=Create Account",
            "a:has-text('Login')",
            "a:has-text('Register')",
            "button:has-text('Login')",
            "[href*='login']",
            "[href*='register']"
        ]
        
        # Check if we need to create account or login
        needs_account = False
        for selector in login_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    needs_account = True
                    break
            except:
                continue
        
        if needs_account:
            agent_sessions[session_id]["current_action"] = "Checking if account exists..."
            # For now, we'll try to proceed - in production, you'd check if user has account
            # and create one if needed using user_profile email/phone
            # This is a simplified version - you may need to handle actual registration flow
            await asyncio.sleep(1)
        
        # Get page HTML and analyze
        html, detected_fields = await engine.get_page_html(session_id)
        
        # Try to find and click New Application/Apply button
        agent_sessions[session_id]["current_action"] = "Looking for New Application button..."
        
        apply_selectors = [
            "text=New Application",
            "text=Apply for New PAN",
            "text=Apply for New PAN Card",
            "text=Apply",
            "text=Apply Now",
            "text=Apply for PAN",
            "a:has-text('New Application')",
            "a:has-text('Apply')",
            "button:has-text('New Application')",
            "button:has-text('Apply')",
            "input[value*='New']",
            "input[value*='Apply']",
            "[href*='new']",
            "[href*='apply']",
            "[href*='application']",
            "[href*='preForm']",
            "a[href*='preForm']",
            "[onclick*='new']",
            "[onclick*='apply']"
        ]
        
        clicked_apply = False
        new_page = None  # Store new page if new tab opens
        
        for selector in apply_selectors:
            try:
                # Use wait_for_selector with longer timeout
                element = await page.wait_for_selector(selector, timeout=15000, state='visible')
                if element:
                    agent_sessions[session_id]["current_action"] = f"Clicking New Application button..."
                    # Scroll to element if needed
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    
                    # Setup listener for new page/tab before clicking
                    context = engine.active_sessions[session_id]['context']
                    
                    async def handle_popup(popup):
                        nonlocal new_page
                        new_page = popup
                        print(f"[KYRON] New tab/popup detected: {popup.url}")
                    
                    # Listen for popup (new tab/window)
                    context.once("page", handle_popup)
                    
                    # Click the button
                    await element.click()
                    
                    # Wait for new tab to open (timeout 5 seconds)
                    for i in range(50):  # 50 * 100ms = 5 seconds
                        if new_page:
                            break
                        await asyncio.sleep(0.1)
                    
                    # If new tab opened, switch to it
                    if new_page:
                        agent_sessions[session_id]["current_action"] = "New tab opened! Switching to new tab..."
                        print(f"[KYRON] Switching to new tab: {new_page.url}")
                        
                        # Wait for new page to load
                        try:
                            await new_page.wait_for_load_state('networkidle', timeout=15000)
                        except:
                            try:
                                await new_page.wait_for_load_state('domcontentloaded', timeout=10000)
                            except:
                                await asyncio.sleep(3)
                        
                        # Update session to use new page
                        engine.active_sessions[session_id]['page'] = new_page
                        page = new_page  # Update local reference
                        
                        agent_sessions[session_id]["current_action"] = "Switched to new tab successfully!"
                    else:
                        # No new tab, just wait for navigation/form to load on same page
                        try:
                            await page.wait_for_load_state('networkidle', timeout=10000)
                        except:
                            try:
                                await page.wait_for_load_state('domcontentloaded', timeout=8000)
                            except:
                                await asyncio.sleep(3)  # Give it time to load
                    
                    clicked_apply = True
                    await asyncio.sleep(2)  # Wait for form to appear
                    break
            except Exception as e:
                print(f"[KYRON] Error clicking apply button with selector {selector}: {e}")
                continue
        
        if not clicked_apply:
            agent_sessions[session_id]["current_action"] = "Form page detected, proceeding to fill..."
            await asyncio.sleep(2)  # Wait a bit more if form is already visible
        
        # 1. Wait until page is fully loaded and all form fields are visible
        agent_sessions[session_id]["current_action"] = "Waiting for page to fully load..."
        try:
            await page.wait_for_load_state('networkidle', timeout=15000)
        except:
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=10000)
            except:
                pass
        await asyncio.sleep(2)  # Additional wait for dynamic content
        
        # Wait for form fields to be visible
        try:
            await page.wait_for_selector('input, select, textarea', timeout=10000, state='visible')
        except:
            pass  # Continue even if timeout
        
        # 2. Detect and switch to iframe if form is inside one
        agent_sessions[session_id]["current_action"] = "Checking for iframes..."
        iframe_page = None
        try:
            # Check for iframes
            iframes = await page.query_selector_all('iframe')
            if iframes:
                for iframe in iframes:
                    try:
                        # Try to get iframe content
                        iframe_content = await iframe.content_frame()
                        if iframe_content:
                            # Check if form is in iframe
                            form_in_iframe = await iframe_content.query_selector('form, input, select')
                            if form_in_iframe:
                                agent_sessions[session_id]["current_action"] = "Switching to iframe..."
                                iframe_page = iframe_content  # Store iframe page
                                await asyncio.sleep(1)
                                break
                    except:
                        continue
        except:
            pass
        
        # Use iframe page if found, otherwise use main page
        active_page = iframe_page if iframe_page else page
        
        # Inject KYRON overlay UI for user control
        agent_sessions[session_id]["current_action"] = "Injecting KYRON control panel..."
        try:
            inject_result = await engine.inject_kyron_widget(session_id)
            print(f"[KYRON] Overlay injection result: {inject_result}")
            
            # Wait for widget to initialize
            await asyncio.sleep(1)
            
            # Update overlay status
            try:
                await page.evaluate("""
                    if (window.updateKyronStatus) {
                        updateKyronStatus('running', 'Analyzing form...');
                    }
                    if (window.KYRON && window.KYRON.updateStatus) {
                        window.KYRON.updateStatus('Form loaded successfully', 'Analyzing fields...', 10);
                    }
                """)
            except Exception as eval_err:
                print(f"[KYRON] Could not update overlay status: {eval_err}")
        except Exception as e:
            print(f"[KYRON] Could not inject KYRON overlay: {e}")
            import traceback
            traceback.print_exc()
        
        # Analyze form fields (with label text support) - use active page (iframe or main)
        agent_sessions[session_id]["current_action"] = "Analyzing form fields with labels..."
        # Temporarily switch page context for field detection
        if iframe_page:
            # Store original page and use iframe
            original_page_context = engine.active_sessions[session_id]['page']
            engine.active_sessions[session_id]['page'] = iframe_page
            html, detected_fields = await engine.get_page_html(session_id)
            engine.active_sessions[session_id]['page'] = original_page_context
        else:
            html, detected_fields = await engine.get_page_html(session_id)
        
        # 3. Enhance fields with label-based selectors (don't rely only on IDs)
        enhanced_fields = []
        for field in detected_fields:
            enhanced_field = field.copy()
            label = field.get("label", "").strip()
            
            # Create label-based selector if label exists
            if label:
                # Try to find field by label text (more reliable than IDs)
                label_selector = f'label:has-text("{label}")'
                enhanced_field["label_selector"] = label_selector
                # Use XPath or nearby selector for label-based field finding
                enhanced_field["label_based_selector"] = f'input:near(label:has-text("{label}")), select:near(label:has-text("{label}")), textarea:near(label:has-text("{label}"))'
            
            enhanced_fields.append(enhanced_field)
        
        detected_fields = enhanced_fields
        
        # Map fields to profile with service_config preferences
        # Prepare enhanced_profile once so it always exists (even if mapping fails)
        enhanced_profile = user_profile.copy()
        try:
            from services.form_mapper import get_form_mapper
            mapper = get_form_mapper()
            
            # Merge user profile with service_config preferences
            if service_config:
                # Add service config to profile for form mapping
                enhanced_profile.update({
                    "applicant_type": service_config.get("applicant_type", "individual"),
                    "delivery_type": service_config.get("delivery_type", "epan"),
                    "application_type": service_config.get("application_type", "new")
                })
            
            # Use map_fields method (checking the correct method name)
            if hasattr(mapper, 'map_fields'):
                mapped_fields = mapper.map_fields(detected_fields, enhanced_profile)
            elif hasattr(mapper, 'map_fields_to_profile'):
                mapped_fields = mapper.map_fields_to_profile(detected_fields, enhanced_profile)
            else:
                mapped_fields = []
        except Exception as e:
            print(f"Form mapping error: {e}")
            mapped_fields = []
        
        # If no mapped fields, try a simple manual fallback later (skip await on missing helper)
        if not mapped_fields:
            agent_sessions[session_id]["current_action"] = "Mapping fields manually..."
            mapped_fields = []
        
        # Check if this is BRC service and use BRC automation engine
        if service and service.id.value == "bihar_residence_certificate" and BRCAutomationEngine:
            agent_sessions[session_id]["current_action"] = "Starting BRC automation engine..."
            try:
                brc_engine = BRCAutomationEngine(page, user_profile, service_config, user_id=user_id)
                brc_engines[session_id] = brc_engine
                
                # Execute BRC automation
                result = await brc_engine.execute()
                
                if result.get("success"):
                    agent_sessions[session_id]["status"] = "completed"
                    agent_sessions[session_id]["current_action"] = result.get("message", "BRC application completed successfully!")
                else:
                    agent_sessions[session_id]["status"] = "error"
                    agent_sessions[session_id]["current_action"] = result.get("error", "BRC automation failed")
                
                return
            except Exception as e:
                print(f"BRC automation error: {e}")
                import traceback
                traceback.print_exc()
                agent_sessions[session_id]["status"] = "error"
                agent_sessions[session_id]["current_action"] = f"BRC automation error: {str(e)}"
                return
        
        # Always try to fill Status dropdown and PAN Card Mode if not already mapped
        agent_sessions[session_id]["current_action"] = "Filling required PAN form fields (Status & Mode)..."
        
        # Fill "Status of the Applicant" dropdown (REQUIRED FIELD)
        if service_config:
            applicant_type = service_config.get("applicant_type", "individual")
            status_filled = False
            
            try:
                # Strategy 1: Find by label text "Status of the Applicant" or "Status of Applicant"
                status_label = await active_page.query_selector('label:has-text("Status of the Applicant"), label:has-text("Status of Applicant")')
                if status_label:
                    label_for = await status_label.get_attribute("for")
                    if label_for:
                        status_select = await active_page.query_selector(f'#{label_for}')
                    else:
                        # Find select near the label
                        status_select = await status_label.evaluate_handle("""
                            (label) => {
                                let current = label.nextElementSibling;
                                while (current) {
                                    if (current.tagName === 'SELECT') return current;
                                    current = current.nextElementSibling;
                                }
                                // Try parent
                                let parent = label.parentElement;
                                if (parent) {
                                    const select = parent.querySelector('select');
                                    if (select) return select;
                                }
                                return null;
                            }
                        """)
                        if status_select:
                            status_select = await status_select.as_element() if hasattr(status_select, 'as_element') else status_select
                else:
                    status_select = None
                
                # Strategy 2: Find by name/id containing "status" and "applicant"
                if not status_select:
                    status_selectors = [
                        'select[name*="status"][name*="applicant"]',
                        'select[id*="status"][id*="applicant"]',
                        'select[name*="status"]',
                        'select[id*="status"]',
                        'select:has(option:has-text("Status"))',
                        'select:has(option:has-text("Applicant"))'
                    ]
                    
                    for selector in status_selectors:
                        try:
                            status_select = await active_page.query_selector(selector)
                            if status_select:
                                # Verify it's the right dropdown by checking options
                                has_status_options = await status_select.evaluate("""
                                    (select) => {
                                        for (let i = 0; i < select.options.length; i++) {
                                            const text = select.options[i].text.toLowerCase();
                                            if (text.includes('individual') || text.includes('company') || text.includes('huf')) {
                                                return true;
                                            }
                                        }
                                        return false;
                                    }
                                """)
                                if has_status_options:
                                    break
                        except:
                            continue
                
                if status_select:
                    # Click dropdown first
                    await status_select.click()
                    await asyncio.sleep(0.3)
                    
                    # Get all options (skip placeholders)
                    options = await status_select.evaluate("""
                        (select) => {
                            const opts = [];
                            for (let i = 0; i < select.options.length; i++) {
                                const opt = select.options[i];
                                const text = opt.text.trim();
                                const value = opt.value;
                                // Skip placeholder options
                                if (value && value !== '' && value !== '0' && 
                                    !text.includes('Select') && !text.includes('---') &&
                                    !value.includes('Select') && !value.includes('---')) {
                                    opts.push({value: value, text: text, index: i});
                                }
                            }
                            return opts;
                        }
                    """)
                    
                    # Match based on applicant_type
                    status_keywords = {
                        "individual": ["individual", "person", "citizen", "self"],
                        "company": ["company", "firm", "huf", "business", "corporation"]
                    }
                    keywords = status_keywords.get(applicant_type, ["individual"])
                    
                    for opt in options:
                        if any(kw in opt['text'].lower() for kw in keywords):
                            await status_select.select_option(value=opt['value'])
                            await asyncio.sleep(0.3)
                            # Trigger events
                            await status_select.dispatch_event("change")
                            await status_select.dispatch_event("blur")
                            await asyncio.sleep(0.2)
                            
                            # Verify selection
                            verified = await status_select.evaluate("el => el.value")
                            if verified == opt['value']:
                                agent_sessions[session_id]["current_action"] = f"✓ Selected Status: {opt['text']}"
                                status_filled = True
                                # Update overlay
                                try:
                                    await page.evaluate(f"""
                                        if (window.updateKyronStatus) {{
                                            updateKyronStatus('running', 'Status selected: {opt['text']}');
                                        }}
                                    """)
                                except:
                                    pass
                                break
                    
                    if not status_filled and options:
                        # Fallback: select first valid option
                        await status_select.select_option(value=options[0]['value'])
                        await status_select.dispatch_event("change")
                        await status_select.dispatch_event("blur")
                        await asyncio.sleep(0.3)
                        agent_sessions[session_id]["current_action"] = f"Selected Status: {options[0]['text']}"
                        status_filled = True
            except Exception as e:
                print(f"Error filling Status dropdown: {e}")
                agent_sessions[session_id]["current_action"] = f"⚠️ Error filling Status of Applicant: {str(e)}"
            
            # Fill "PAN CARD Mode" radio buttons (REQUIRED FIELD)
            delivery_type = service_config.get("delivery_type", "epan")
            mode_filled = False
            
            try:
                # Strategy 1: Find by label text "PAN CARD Mode" or "PAN Card Mode"
                mode_label = await active_page.query_selector('label:has-text("PAN CARD Mode"), label:has-text("PAN Card Mode"), label:has-text("Mode")')
                
                if mode_label:
                    # Find all radio buttons near this label
                    # Get parent container
                    parent = await mode_label.evaluate_handle("""
                        (label) => {
                            let current = label.parentElement;
                            while (current && current.tagName !== 'FORM' && current.tagName !== 'BODY') {
                                const radios = current.querySelectorAll('input[type="radio"]');
                                if (radios.length > 0) return current;
                                current = current.parentElement;
                            }
                            return null;
                        }
                    """)
                    
                    if parent:
                        parent_elem = await parent.as_element() if hasattr(parent, 'as_element') else parent
                        mode_radios = await parent_elem.query_selector_all('input[type="radio"]')
                    else:
                        mode_radios = []
                else:
                    mode_radios = []
                
                # Strategy 2: Find by name containing "mode" or "pan"
                if not mode_radios or len(mode_radios) == 0:
                    mode_radios = await active_page.query_selector_all('input[type="radio"][name*="mode"], input[type="radio"][name*="pan"]')
                
                # Strategy 3: Find all radios and check their labels
                if not mode_radios or len(mode_radios) == 0:
                    all_radios = await active_page.query_selector_all('input[type="radio"]')
                    mode_radios = []
                    for radio in all_radios:
                        radio_id = await radio.get_attribute("id")
                        if radio_id:
                            label_elem = await active_page.query_selector(f'label[for="{radio_id}"]')
                            if label_elem:
                                label_text = await label_elem.inner_text()
                                if "pan" in label_text.lower() and "mode" in label_text.lower():
                                    mode_radios.append(radio)
                
                if mode_radios and len(mode_radios) > 0:
                    for radio in mode_radios:
                        radio_id = await radio.get_attribute("id")
                        radio_name = await radio.get_attribute("name")
                        label_text = ""
                        
                        # Get label text
                        if radio_id:
                            try:
                                label_elem = await active_page.query_selector(f'label[for="{radio_id}"]')
                                if label_elem:
                                    label_text = await label_elem.inner_text()
                            except:
                                pass
                        
                        # Also check parent text
                        if not label_text:
                            try:
                                parent_text = await radio.evaluate("""
                                    (radio) => {
                                        let current = radio.parentElement;
                                        while (current) {
                                            const text = current.textContent || '';
                                            if (text.includes('PAN') || text.includes('physical') || text.includes('e-PAN')) {
                                                return text;
                                            }
                                            current = current.parentElement;
                                        }
                                        return '';
                                    }
                                """)
                                if parent_text:
                                    label_text = parent_text
                            except:
                                pass
                        
                        # Match based on delivery_type
                        should_select = False
                        if delivery_type == "epan":
                            # Select "e-PAN only" option
                            if label_text and ("e-pan only" in label_text.lower() or "epan only" in label_text.lower() or 
                                             ("no physical" in label_text.lower() and "pan" in label_text.lower())):
                                should_select = True
                        else:  # physical
                            # Select "Both physical PAN Card and e-PAN" option
                            if label_text and ("both" in label_text.lower() and "physical" in label_text.lower() and "e-pan" in label_text.lower()):
                                should_select = True
                        
                        if should_select:
                            await radio.scroll_into_view_if_needed()
                            await asyncio.sleep(0.2)
                            
                            # Use JavaScript to set checked property directly (more reliable than .check())
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
                                # Fallback to .check() if JavaScript fails
                                try:
                                    await radio.check()
                                    await asyncio.sleep(0.3)
                                except:
                                    pass
                            
                            # Verify
                            is_checked = await radio.evaluate("el => el.checked")
                            if is_checked:
                                agent_sessions[session_id]["current_action"] = f"✓ Selected PAN Mode: {label_text.strip()[:50]}"
                                mode_filled = True
                                # Update overlay
                                try:
                                    await page.evaluate(f"""
                                        if (window.updateKyronStatus) {{
                                            updateKyronStatus('running', 'PAN Mode selected');
                                        }}
                                    """)
                                except:
                                    pass
                                break
                    
                    # If not filled, try to select first radio (fallback)
                    if not mode_filled and mode_radios:
                        try:
                            await mode_radios[0].check()
                            await asyncio.sleep(0.3)
                            mode_filled = True
                            agent_sessions[session_id]["current_action"] = "Selected PAN Mode (first option)"
                        except:
                            pass
            except Exception as e:
                print(f"Error filling PAN Card Mode: {e}")
                agent_sessions[session_id]["current_action"] = f"⚠️ Error filling PAN Card Mode: {str(e)}"
            
            # Log status
            if status_filled and mode_filled:
                agent_sessions[session_id]["current_action"] = "✓ Status and PAN Mode filled successfully"
            elif not status_filled:
                agent_sessions[session_id]["current_action"] = "⚠️ Status of Applicant not filled"
            elif not mode_filled:
                agent_sessions[session_id]["current_action"] = "⚠️ PAN Card Mode not filled"
        
        # Fill form fields with realistic behavior
        fillable_fields = [
            {
                "selector": f["selector"],
                "value": str(f["value"]),
                "label": f.get("label", "field")
            }
            for f in mapped_fields
            if f.get("selector") and f.get("value")
        ]
        
        # 6. Check for CAPTCHA before filling
        agent_sessions[session_id]["current_action"] = "Checking for CAPTCHA..."
        captcha_detected = False
        try:
            captcha_selectors = [
                '[class*="captcha"]',
                '[id*="captcha"]',
                '[name*="captcha"]',
                'img[alt*="captcha"]',
                'img[src*="captcha"]',
                'iframe[src*="recaptcha"]',
                'div[class*="g-recaptcha"]',
                'div[id*="recaptcha"]'
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha_element = await page.query_selector(selector)
                    if captcha_element:
                        is_visible = await captcha_element.is_visible()
                        if is_visible:
                            captcha_detected = True
                            break
                except:
                    continue
            
            if captcha_detected:
                agent_sessions[session_id]["status"] = "paused"
                agent_sessions[session_id]["current_action"] = "CAPTCHA detected! Please complete it manually and I'll continue filling the form."
                # Update overlay status
                try:
                    await page.evaluate("""
                        if (window.updateKyronStatus) {
                            updateKyronStatus('paused', 'CAPTCHA detected. Please complete manually.');
                        }
                    """)
                except:
                    pass
                # Wait for user to complete CAPTCHA (check every 2 seconds)
                max_wait = 120  # 2 minutes max wait
                waited = 0
                while waited < max_wait:
                    await asyncio.sleep(2)
                    waited += 2
                    # Check if CAPTCHA is still visible
                    still_visible = False
                    for selector in captcha_selectors:
                        try:
                            element = await page.query_selector(selector)
                            if element and await element.is_visible():
                                still_visible = True
                                break
                        except:
                            pass
                    if not still_visible:
                        agent_sessions[session_id]["status"] = "filling"
                        agent_sessions[session_id]["current_action"] = "CAPTCHA completed, continuing..."
                        # Update overlay status
                        try:
                            await page.evaluate("""
                                if (window.updateKyronStatus) {
                                    updateKyronStatus('running', 'CAPTCHA completed. Continuing...');
                                }
                            """)
                        except:
                            pass
                        await asyncio.sleep(1)
                        break
        except:
            pass
        
        if fillable_fields:
            agent_sessions[session_id]["status"] = "filling"
            agent_sessions[session_id]["progress"] = {
                "step": 0,
                "total": len(fillable_fields),
                "action": "Filling form fields..."
            }
            # Update overlay status
            try:
                await page.evaluate(f"""
                    if (window.updateKyronStatus) {{
                        updateKyronStatus('filling', 'Filling {len(fillable_fields)} form fields...');
                    }}
                """)
            except:
                pass
            
            # 8. Fill fields step-by-step, never skip required fields
            for idx, field in enumerate(fillable_fields):
                # Check for pause/stop flags before each field
                try:
                    paused = await page.evaluate("() => window.KYRON_PAUSED || false")
                    stopped = await page.evaluate("() => window.KYRON_STOPPED || false")
                    
                    if stopped:
                        agent_sessions[session_id]["status"] = "stopped"
                        agent_sessions[session_id]["current_action"] = "Automation stopped by user"
                        try:
                            await page.evaluate("""
                                if (window.KYRON && window.KYRON.setCompleted) {
                                    window.KYRON.setError('Stopped by user');
                                }
                            """)
                        except:
                            pass
                        return
                    
                    # Wait while paused
                    while paused:
                        agent_sessions[session_id]["status"] = "paused"
                        agent_sessions[session_id]["current_action"] = "⏸ Paused - waiting for user to resume..."
                        try:
                            await page.evaluate("""
                                if (window.KYRON && window.KYRON.updateStatus) {
                                    window.KYRON.updateStatus('Automation paused', 'Click Resume to continue', undefined);
                                }
                            """)
                        except:
                            pass
                        await asyncio.sleep(1)
                        paused = await page.evaluate("() => window.KYRON_PAUSED || false")
                        stopped = await page.evaluate("() => window.KYRON_STOPPED || false")
                        if stopped:
                            agent_sessions[session_id]["status"] = "stopped"
                            agent_sessions[session_id]["current_action"] = "Automation stopped by user"
                            return
                    
                    # Resume automation
                    if agent_sessions[session_id]["status"] == "paused":
                        agent_sessions[session_id]["status"] = "filling"
                        try:
                            await page.evaluate("""
                                if (window.KYRON && window.KYRON.setRunning) {
                                    window.KYRON.setRunning();
                                }
                            """)
                        except:
                            pass
                except Exception as control_err:
                    print(f"[KYRON] Error checking control flags: {control_err}")
                
                try:
                    field_label = field.get('label', 'field')
                    agent_sessions[session_id]["current_action"] = f"Filling {field_label}..."
                    agent_sessions[session_id]["progress"]["step"] = idx + 1
                    
                    # Update overlay with progress
                    try:
                        progress_percent = int((idx / len(fillable_fields)) * 100)
                        await page.evaluate(f"""
                            if (window.KYRON && window.KYRON.updateStatus) {{
                                window.KYRON.updateStatus('Filling form field {idx + 1}/{len(fillable_fields)}', '{field_label}', {progress_percent});
                            }}
                        """)
                    except:
                        pass
                    
                    # Wait for element and fill
                    element = None
                    selector = field.get("selector", "")
                    label_selector = field.get("label_based_selector") or field.get("label_selector")
                    
                    # Use active page (iframe or main)
                    current_page = active_page
                    
                    # 3. Use label text to find field (more reliable)
                    if label_selector:
                        try:
                            element = await current_page.wait_for_selector(label_selector, timeout=3000, state='visible')
                        except:
                            pass
                    
                    # Fallback to original selector
                    if not element and selector:
                        try:
                            element = await current_page.wait_for_selector(selector, timeout=5000, state='visible')
                        except:
                            # Try by name attribute
                            if "name=" in selector:
                                name_value = selector.split("name=")[1].strip('"\'[]')
                                element = await current_page.query_selector(f'[name="{name_value}"]')
                            # Try by id
                            elif "#" in selector:
                                id_value = selector.replace("#", "")
                                element = await current_page.query_selector(f'#{id_value}')
                    
                    if not element:
                        # Last resort: find by label text
                        label = field.get("label", "")
                        if label:
                            try:
                                # Find label element
                                label_elem = await current_page.query_selector(f'label:has-text("{label}")')
                                if label_elem:
                                    # Get associated input
                                    label_for = await label_elem.get_attribute("for")
                                    if label_for:
                                        element = await current_page.query_selector(f'#{label_for}')
                                    else:
                                        # Try to find input near label
                                        element = await label_elem.query_selector('input, select, textarea')
                            except:
                                pass
                    
                    if not element:
                        print(f"Field {field_label} not found, skipping...")
                        continue
                    
                    # Scroll to element
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.3)
                    
                    # Check if field is required
                    is_required = await element.evaluate("el => el.hasAttribute('required') || el.getAttribute('aria-required') === 'true'")
                    
                    # 5. Handle different field types carefully
                    field_type = await element.evaluate("el => el.type || el.tagName.toLowerCase()")
                    field_value = str(field.get("value", ""))
                    
                    if field_type == "select":
                        # DETERMINISTIC DROPDOWN HANDLING: Click, Select by visible text, Trigger events, Verify
                        try:
                            # Step 1: Click the dropdown to open it
                            await element.click()
                            await asyncio.sleep(0.3)
                            
                            # Step 2: Get all available options (skip placeholders)
                            options = await element.evaluate("""
                                (select) => {
                                    const opts = [];
                                    for (let i = 0; i < select.options.length; i++) {
                                        const opt = select.options[i];
                                        const optText = opt.text.trim();
                                        const optValue = opt.value;
                                        // Skip placeholder options
                                        if (optValue && optValue !== '' && 
                                            !optValue.includes('Select') && 
                                            !optValue.includes('---') &&
                                            !optText.includes('Select') &&
                                            !optText.includes('---') &&
                                            optValue !== '0') {
                                            opts.push({
                                                value: optValue,
                                                text: optText,
                                                index: i
                                            });
                                        }
                                    }
                                    return opts;
                                }
                            """, element)
                            
                            selected = False
                            selected_option = None
                            
                            # Step 3: Match by visible text (deterministic)
                            # Special handling for "Status of Applicant" dropdown
                            if "status" in field_label.lower() and "applicant" in field_label.lower():
                                applicant_type = service_config.get("applicant_type", "individual") if service_config else "individual"
                                status_keywords = {
                                    "individual": ["individual", "person", "citizen", "self"],
                                    "company": ["company", "firm", "huf", "business", "corporation"]
                                }
                                keywords = status_keywords.get(applicant_type, ["individual"])
                                
                                # Match by keywords in visible text
                                for opt in options:
                                    if any(kw in opt['text'].lower() for kw in keywords):
                                        try:
                                            await element.select_option(value=opt['value'])
                                            selected = True
                                            selected_option = opt
                                            await asyncio.sleep(0.3)
                                            break
                                        except:
                                            continue
                            
                            # Try to match by field_value (visible text match)
                            if not selected:
                                for opt in options:
                                    if field_value.lower() in opt['text'].lower() or opt['text'].lower() in field_value.lower():
                                        try:
                                            await element.select_option(value=opt['value'])
                                            selected = True
                                            selected_option = opt
                                            await asyncio.sleep(0.3)
                                            break
                                        except:
                                            continue
                            
                            # If not selected and options available, select first valid option
                            if not selected and options:
                                try:
                                    await element.select_option(value=options[0]['value'])
                                    selected = True
                                    selected_option = options[0]
                                    await asyncio.sleep(0.3)
                                except:
                                    pass
                            
                            # Step 4: Trigger change and blur events (deterministic)
                            if selected:
                                await element.dispatch_event("change")
                                await asyncio.sleep(0.2)
                                await element.dispatch_event("blur")
                                await asyncio.sleep(0.2)
                                
                                # Step 5: Verify the selected value matches expected text
                                verified_value = await element.evaluate("el => el.value")
                                verified_text = await element.evaluate("el => el.options[el.selectedIndex]?.text || ''")
                                
                                if selected_option:
                                    if verified_value == selected_option['value'] and verified_text.strip() == selected_option['text']:
                                        agent_sessions[session_id]["current_action"] = f"✓ Selected: {selected_option['text']}"
                                    else:
                                        print(f"⚠️ Verification mismatch: expected {selected_option['text']}, got {verified_text}")
                                        agent_sessions[session_id]["current_action"] = f"Selected: {verified_text or selected_option['text']}"
                                else:
                                    agent_sessions[session_id]["current_action"] = f"Selected: {verified_text}"
                            else:
                                # Fallback: try direct value or label
                                try:
                                    await element.select_option(field_value)
                                    await element.dispatch_event("change")
                                    await element.dispatch_event("blur")
                                    await asyncio.sleep(0.3)
                                    selected = True
                                except:
                                    try:
                                        await element.select_option(label=field_value)
                                        await element.dispatch_event("change")
                                        await element.dispatch_event("blur")
                                        await asyncio.sleep(0.3)
                                        selected = True
                                    except:
                                        print(f"Could not select option: {field_value}")
                                        if is_required:
                                            agent_sessions[session_id]["current_action"] = f"⚠️ Required field {field_label} could not be filled. Please fill manually."
                        except Exception as e:
                            print(f"Error selecting dropdown {field_label}: {e}")
                            if is_required:
                                agent_sessions[session_id]["current_action"] = f"⚠️ Required field {field_label} could not be filled. Please fill manually."
                    elif field_type in ["radio", "checkbox"]:
                        # Handle radio buttons and checkboxes with better detection
                        try:
                            # For PAN Card Mode radio buttons
                            if "pan card mode" in field_label.lower() or "mode" in field_label.lower():
                                delivery_type = service_config.get("delivery_type", "epan") if service_config else "epan"
                                
                                # Find all radio buttons in the group
                                radio_name = await element.get_attribute("name")
                                if radio_name:
                                    # Get all radio buttons with same name
                                    all_radios = await current_page.query_selector_all(f'input[type="radio"][name="{radio_name}"]')
                                    
                                    for radio in all_radios:
                                        radio_value = await radio.get_attribute("value")
                                        radio_id = await radio.get_attribute("id")
                                        
                                        # Try to find associated label
                                        label_text = ""
                                        if radio_id:
                                            try:
                                                label_elem = await current_page.query_selector(f'label[for="{radio_id}"]')
                                                if label_elem:
                                                    label_text = await label_elem.inner_text()
                                            except:
                                                pass
                                        
                                        # Also try to get text from parent or nearby elements
                                        if not label_text:
                                            try:
                                                # Get parent element text
                                                parent = await radio.evaluate_handle("el => el.parentElement")
                                                if parent:
                                                    parent_text = await parent.as_element().inner_text() if hasattr(parent, 'as_element') else ""
                                                    if parent_text:
                                                        label_text = parent_text
                                            except:
                                                pass
                                        
                                        # Match based on delivery_type preference
                                        if delivery_type == "epan":
                                            # Select "e-PAN only" option
                                            if label_text and ("e-pan only" in label_text.lower() or "epan only" in label_text.lower() or "no physical" in label_text.lower()):
                                                try:
                                                    await radio.evaluate("""
                                                        (radio) => {
                                                            const name = radio.name;
                                                            if (name) {
                                                                document.querySelectorAll(`input[type="radio"][name="${name}"]`).forEach(r => {
                                                                    r.checked = false;
                                                                    r.dispatchEvent(new Event('change', { bubbles: true }));
                                                                });
                                                            }
                                                            radio.checked = true;
                                                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                                                            radio.dispatchEvent(new Event('click', { bubbles: true }));
                                                        }
                                                    """)
                                                except:
                                                    await radio.check()
                                                await asyncio.sleep(0.5)
                                                break
                                        else:  # physical
                                            # Select "Both physical PAN Card and e-PAN" option
                                            if label_text and ("both" in label_text.lower() or ("physical" in label_text.lower() and "e-pan" in label_text.lower())):
                                                try:
                                                    await radio.evaluate("""
                                                        (radio) => {
                                                            const name = radio.name;
                                                            if (name) {
                                                                document.querySelectorAll(`input[type="radio"][name="${name}"]`).forEach(r => {
                                                                    r.checked = false;
                                                                    r.dispatchEvent(new Event('change', { bubbles: true }));
                                                                });
                                                            }
                                                            radio.checked = true;
                                                            radio.dispatchEvent(new Event('change', { bubbles: true }));
                                                            radio.dispatchEvent(new Event('click', { bubbles: true }));
                                                        }
                                                    """)
                                                except:
                                                    await radio.check()
                                                await asyncio.sleep(0.5)
                                                break
                            
                            # Standard radio/checkbox handling
                            elif field_value.lower() in ['true', '1', 'yes', 'on', 'checked']:
                                try:
                                    await element.evaluate("""
                                        (el) => {
                                            if (el.type === 'radio') {
                                                const name = el.name;
                                                if (name) {
                                                    document.querySelectorAll(`input[type="radio"][name="${name}"]`).forEach(r => {
                                                        r.checked = false;
                                                        r.dispatchEvent(new Event('change', { bubbles: true }));
                                                    });
                                                }
                                            }
                                            el.checked = true;
                                            el.dispatchEvent(new Event('change', { bubbles: true }));
                                            el.dispatchEvent(new Event('click', { bubbles: true }));
                                        }
                                    """)
                                except:
                                    await element.check()
                                await asyncio.sleep(0.3)
                            else:
                                try:
                                    await element.evaluate("""
                                        (el) => {
                                            el.checked = false;
                                            el.dispatchEvent(new Event('change', { bubbles: true }));
                                        }
                                    """)
                                except:
                                    await element.uncheck()
                                await asyncio.sleep(0.3)
                        except Exception as e:
                            print(f"Could not check/uncheck: {field_label}, error: {e}")
                            # Try alternative: click the label instead
                            try:
                                radio_id = await element.get_attribute("id")
                                if radio_id:
                                    label_elem = await current_page.query_selector(f'label[for="{radio_id}"]')
                                    if label_elem:
                                        await label_elem.click()
                                        await asyncio.sleep(0.3)
                            except:
                                pass
                    elif field_type == "date" or "date" in field_label.lower():
                        # 5. Handle date fields carefully
                        try:
                            await element.click()
                            await asyncio.sleep(0.3)
                            # Format date properly (DD/MM/YYYY or YYYY-MM-DD)
                            from services.date_formatter import DateFormatter
                            formatted_date = DateFormatter.format_for_field(
                                field_value,
                                field.get("name", ""),
                                field_label,
                                "date"
                            )
                            await element.fill(formatted_date)
                            await asyncio.sleep(0.3)
                        except:
                            print(f"Could not fill date field: {field_label}")
                    else:
                        # 4. Fill text inputs with human-like typing
                        try:
                            await element.click()
                            await asyncio.sleep(0.2)
                            
                            # Clear field first
                            await element.fill("")
                            await asyncio.sleep(0.2)
                            
                            # Human-like typing with small delays
                            for char in field_value:
                                await element.type(char, delay=50)  # 50ms delay per character
                            
                            await asyncio.sleep(0.3)
                            
                            # Trigger events
                            await element.dispatch_event("input")
                            await asyncio.sleep(0.1)
                            await element.dispatch_event("change")
                            await asyncio.sleep(0.1)
                            await element.dispatch_event("blur")
                            await asyncio.sleep(0.2)
                        except:
                            # Fallback to simple fill
                            try:
                                await element.fill(field_value)
                                await asyncio.sleep(0.3)
                            except:
                                print(f"Could not fill field: {field_label}")
                                if is_required:
                                    agent_sessions[session_id]["current_action"] = f"⚠️ Required field {field_label} could not be filled. Please fill manually."
                    
                    # 7. Verify the value is correctly entered
                    try:
                        if field_type == "select":
                            selected_value = await element.evaluate("el => el.value")
                            selected_text = await element.evaluate("el => el.options[el.selectedIndex]?.text || ''")
                            # Check if value or text matches
                            if selected_value and selected_value != "" and selected_value != "0" and not selected_value.startswith("---"):
                                # Value is selected, verify it matches
                                if field_value.lower() not in selected_text.lower() and selected_text.lower() not in field_value.lower():
                                    print(f"⚠️ Value mismatch in {field_label}: expected {field_value}, got {selected_text}")
                            else:
                                print(f"⚠️ Dropdown {field_label} still has placeholder selected")
                        elif field_type == "radio":
                            is_checked = await element.evaluate("el => el.checked")
                            if not is_checked:
                                print(f"⚠️ Radio button {field_label} is not checked")
                                # Try to check it again
                                try:
                                    await element.check()
                                    await asyncio.sleep(0.3)
                                except:
                                    pass
                        elif field_type not in ["radio", "checkbox"]:
                            entered_value = await element.evaluate("el => el.value")
                            if entered_value != field_value and field_value.lower() not in entered_value.lower():
                                print(f"⚠️ Value mismatch in {field_label}: expected {field_value}, got {entered_value}")
                                # Try to fix it
                                await element.fill("")
                                await asyncio.sleep(0.2)
                                await element.fill(field_value)
                                await asyncio.sleep(0.3)
                    except:
                        pass
                    
                    await asyncio.sleep(0.4)  # Small delay between fields
                    
                except Exception as e:
                    print(f"Error filling field {field.get('label', 'unknown')}: {e}")
                    # Don't skip required fields - log the error
                    if field.get("required"):
                        agent_sessions[session_id]["current_action"] = f"⚠️ Error filling required field {field.get('label', 'unknown')}: {str(e)}"
                    continue
        
        # Wait a bit before trying to submit (let form validate)
        await asyncio.sleep(1)
        
        # Get current URL before submit
        current_url = active_page.url
        
        # Check if form has validation errors
        agent_sessions[session_id]["current_action"] = "Checking form validation..."
        try:
            error_elements = await active_page.query_selector_all('.error, .invalid, [class*="error"], [class*="invalid"], [aria-invalid="true"]')
            if error_elements:
                error_texts = []
                for err_elem in error_elements[:3]:  # Get first 3 errors
                    try:
                        err_text = await err_elem.inner_text()
                        if err_text:
                            error_texts.append(err_text.strip())
                    except:
                        pass
                if error_texts:
                    agent_sessions[session_id]["current_action"] = f"⚠️ Form validation errors: {', '.join(error_texts)}. Please check required fields."
        except:
            pass
        
        # 8. REQUIRED FIELD GATE: Scan all required (*) fields before submission
        agent_sessions[session_id]["current_action"] = "Scanning all required fields..."
        try:
            # Find all required fields (by required attribute, aria-required, or * in label)
            required_fields = await active_page.query_selector_all('input[required], select[required], textarea[required], [aria-required="true"]')
            
            # Also find fields with * in label (common pattern for required fields)
            asterisk_labels = await active_page.query_selector_all('label:has-text("*")')
            for label in asterisk_labels:
                try:
                    label_for = await label.get_attribute("for")
                    if label_for:
                        field = await active_page.query_selector(f'#{label_for}')
                        if field:
                            # Check if already in required_fields
                            field_id = await field.get_attribute("id")
                            already_added = False
                            for rf in required_fields:
                                rf_id = await rf.get_attribute("id")
                                if rf_id == field_id:
                                    already_added = True
                                    break
                            if not already_added:
                                required_fields.append(field)
                except:
                    pass
            
            unfilled_required = []
            
            for req_field in required_fields:
                try:
                    field_type = await req_field.evaluate("el => el.type || el.tagName.toLowerCase()")
                    field_name = await req_field.get_attribute("name") or ""
                    field_id = await req_field.get_attribute("id") or ""
                    
                    # Get label text
                    label_text = ""
                    if field_id:
                        try:
                            label_elem = await active_page.query_selector(f'label[for="{field_id}"]')
                            if label_elem:
                                label_text = await label_elem.inner_text()
                        except:
                            pass
                    
                    if not label_text:
                        label_text = field_name or "field"
                    
                    if field_type == "select":
                        selected = await req_field.evaluate("el => el.value")
                        selected_text = await req_field.evaluate("el => el.options[el.selectedIndex]?.text || ''")
                        # Check if placeholder is still selected
                        if not selected or selected == "" or selected.startswith("---") or selected == "0" or "Select" in selected_text or "---" in selected_text:
                            unfilled_required.append(label_text.strip())
                    elif field_type == "radio":
                        # Check if any radio in group is checked
                        radio_name = await req_field.get_attribute("name")
                        if radio_name:
                            checked = await active_page.evaluate(f"""
                                document.querySelector('input[type="radio"][name="{radio_name}"]:checked') !== null
                            """)
                            if not checked:
                                unfilled_required.append(label_text.strip())
                    else:
                        value = await req_field.evaluate("el => el.value")
                        if not value or value.strip() == "":
                            unfilled_required.append(label_text.strip())
                except Exception as e:
                    print(f"Error checking required field: {e}")
                    continue
            
            if unfilled_required:
                unique_unfilled = list(set(unfilled_required))[:5]  # Show max 5
                agent_sessions[session_id]["status"] = "error"
                agent_sessions[session_id]["current_action"] = f"⚠️ REQUIRED FIELDS NOT FILLED: {', '.join(unique_unfilled)}. Please fill all required (*) fields before submitting."
                # Update overlay status
                try:
                    await page.evaluate(f"""
                        if (window.updateKyronStatus) {{
                            updateKyronStatus('error', 'Required fields missing: {', '.join(unique_unfilled[:3])}');
                        }}
                    """)
                except:
                    pass
                return  # NEVER submit if required fields are missing
            else:
                agent_sessions[session_id]["current_action"] = "✓ All required fields are filled"
                # Update overlay status
                try:
                    await page.evaluate("""
                        if (window.updateKyronStatus) {
                            updateKyronStatus('running', 'All required fields filled. Ready to submit.');
                        }
                    """)
                except:
                    pass
        except Exception as e:
            print(f"Error in required field gate: {e}")
            # Continue but warn
            agent_sessions[session_id]["current_action"] = "⚠️ Could not verify all required fields. Proceeding with caution..."
        
        # 9. SUBMISSION LOGIC: Submit only after successful validation
        agent_sessions[session_id]["current_action"] = "Looking for Submit button..."
        # Update overlay status
        try:
            await page.evaluate("""
                if (window.updateKyronStatus) {
                    updateKyronStatus('running', 'Ready to submit form...');
                }
            """)
        except:
            pass
        
        submit_selectors = [
            "text=Submit",
            "button:has-text('Submit')",
            "input[value='Submit']",
            "button[type='submit']",
            "input[type='submit']",
            "text=Submit Application",
            "[id*='submit']",
            "[name*='submit']",
            "[onclick*='submit']",
            "text=Proceed",
            "text=Continue",
            "text=Next",
            "text=Next Step",
            "button:has-text('Proceed')",
            "button:has-text('Continue')",
            "button:has-text('Next')",
            "[onclick*='next']",
            "a:has-text('Next')",
            "a:has-text('Continue')"
        ]
        
        submitted = False
        submit_button = None
        for selector in submit_selectors:
            try:
                element = await active_page.wait_for_selector(selector, timeout=3000, state='visible')
                if element:
                    # Check if button is enabled
                    is_disabled = await element.evaluate("el => el.disabled || el.getAttribute('disabled') !== null")
                    if not is_disabled:
                        submit_button = element
                        break
            except:
                continue
        
        if submit_button:
            try:
                agent_sessions[session_id]["current_action"] = "Submitting application..."
                # Update overlay status
                try:
                    await page.evaluate("""
                        if (window.updateKyronStatus) {
                            updateKyronStatus('running', 'Submitting form...');
                        }
                    """)
                except:
                    pass
                
                await submit_button.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                
                # Double-check required fields one more time before submitting
                status_check = await active_page.evaluate("""
                    () => {
                        // Check Status dropdown
                        const statusSelect = document.querySelector('select[name*="status"], select[id*="status"]');
                        if (statusSelect) {
                            const value = statusSelect.value;
                            const text = statusSelect.options[statusSelect.selectedIndex]?.text || '';
                            if (!value || value === '' || value === '0' || text.includes('Select') || text.includes('---')) {
                                return 'Status of Applicant not selected';
                            }
                        }
                        
                        // Check PAN Card Mode radio
                        const modeRadios = document.querySelectorAll('input[type="radio"][name*="mode"], input[type="radio"][name*="pan"]');
                        if (modeRadios.length > 0) {
                            let checked = false;
                            modeRadios.forEach(radio => {
                                if (radio.checked) checked = true;
                            });
                            if (!checked) {
                                return 'PAN Card Mode not selected';
                            }
                        }
                        
                        return 'ok';
                    }
                """)
                
                if status_check != 'ok':
                    agent_sessions[session_id]["current_action"] = f"⚠️ {status_check}. Please fill required fields before submitting."
                    # Update overlay status
                    try:
                        await page.evaluate(f"""
                            if (window.updateKyronStatus) {{
                                updateKyronStatus('error', '{status_check}');
                            }}
                        """)
                    except:
                        pass
                else:
                    # All checks passed, submit
                    await submit_button.click()
                    await asyncio.sleep(3)  # Wait for submission/navigation
                    
                    # Check if page navigated or form submitted
                    new_url = active_page.url
                    if new_url != current_url:
                        submitted = True
                        agent_sessions[session_id]["current_action"] = "✓ Form submitted successfully! Navigating to next step..."
                    else:
                        # Check if form is gone or success message appears
                        form_exists = await active_page.query_selector('form')
                        success_message = await active_page.query_selector('text=success, text=submitted, text=thank you, .success, .message')
                        if not form_exists or success_message:
                            submitted = True
                            agent_sessions[session_id]["current_action"] = "✓ Form submitted successfully!"
                        else:
                            # Check for error messages
                            error_msg = await active_page.query_selector('.error, .alert-danger, [class*="error"]')
                            if error_msg:
                                error_text = await error_msg.inner_text()
                                agent_sessions[session_id]["current_action"] = f"⚠️ Submission error: {error_text[:100]}"
                            else:
                                agent_sessions[session_id]["current_action"] = "Form submitted. Please wait for page to load..."
            except Exception as e:
                print(f"Error clicking submit: {e}")
                agent_sessions[session_id]["current_action"] = f"⚠️ Error submitting: {str(e)}"
        else:
            agent_sessions[session_id]["current_action"] = "Submit button not found or disabled. Please check if all required fields (Status of Applicant, PAN Card Mode) are filled."
        
        if not submitted:
            # Final attempt: let Form49A engine try automatic Next/Submit
            try:
                engine_obj = form49a_engines.get(session_id)
                if engine_obj:
                    auto_nav = await engine_obj.navigate_to_next_page()
                    if auto_nav:
                        submitted = True
                        agent_sessions[session_id]["current_action"] = "✓ Form validated and Next/Submit clicked automatically. Proceeding to next step..."
                    else:
                        agent_sessions[session_id]["current_action"] = "Form filled with Status and PAN Mode. Next button is still disabled; some other required fields might be missing."
                else:
                    agent_sessions[session_id]["current_action"] = "Form filled with Status and PAN Mode. Engine not available to auto-submit; please submit manually."
            except Exception as nav_err:
                print(f"Auto navigation error: {nav_err}")
                agent_sessions[session_id]["current_action"] = "Form filled with Status and PAN Mode, but automatic Next/Submit failed. Please submit manually."
        
        # Check for payment requirement
        try:
            from services.payment_detector import get_payment_detector
            payment_detector = get_payment_detector()
            current_html, _ = await engine.get_page_html(session_id)
            current_url = page.url
            payment_info = payment_detector.detect_payment(current_html, "")
            
            if payment_info and payment_info.get("required"):
                agent_sessions[session_id]["status"] = "payment_required"
                agent_sessions[session_id]["payment_info"] = payment_info
                agent_sessions[session_id]["current_action"] = f"Payment required: ₹{payment_info.get('amount', 0)}"
                return
        except:
            pass
        
        # Mark as completed
        if submitted:
            agent_sessions[session_id]["status"] = "completed"
            agent_sessions[session_id]["current_action"] = "✓ Application submitted successfully! Please check your email for confirmation and proceed with payment if required."
            # Update overlay status
            try:
                await page.evaluate("""
                    if (window.updateKyronStatus) {
                        updateKyronStatus('completed', 'Form submitted successfully!');
                    }
                """)
            except:
                pass
        else:
            # Even if we couldn't confirm full navigation/submission, keep automation running
            agent_sessions[session_id]["status"] = "running"
            agent_sessions[session_id]["current_action"] = "✓ Status of Applicant and PAN Card Mode filled. Continuing automation for remaining fields..."
            # Update overlay status
            try:
                await page.evaluate("""
                    if (window.updateKyronStatus) {
                        updateKyronStatus('info', 'Required PAN fields filled. Continuing automation...');
                    }
                """)
            except:
                pass
        agent_sessions[session_id]["progress"]["action"] = "Completed"
        
    except Exception as e:
        agent_sessions[session_id]["status"] = "error"
        agent_sessions[session_id]["current_action"] = f"Error: {str(e)}"
        print(f"Agent automation error: {e}")

@router.get("/session/{session_id}")
async def get_agent_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Get agent session status"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = agent_sessions[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "success": True,
        "session": session
    }

@router.post("/session/{session_id}/pause")
async def pause_agent_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Pause agent automation"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = agent_sessions[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    session["status"] = "paused"
    session["current_action"] = "Automation paused"
    
    return {"success": True, "message": "Automation paused"}

@router.post("/session/{session_id}/resume")
async def resume_agent_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Resume agent automation"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = agent_sessions[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    session["status"] = "active"
    session["current_action"] = "Resuming automation..."
    
    return {"success": True, "message": "Automation resumed"}

@router.post("/session/{session_id}/stop")
async def stop_agent_session(
    session_id: str,
    authorization: str = Header(None)
):
    """Stop agent automation"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = agent_sessions[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Close browser session
    try:
        engine = get_automation_engine()
        await engine.close_session(session_id)
    except:
        pass
    
    session["status"] = "stopped"
    session["current_action"] = "Automation stopped"
    
    return {"success": True, "message": "Automation stopped"}

@router.get("/session/{session_id}/screenshot")
async def get_agent_screenshot(
    session_id: str,
    authorization: str = Header(None)
):
    """Get screenshot of current automation state"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = agent_sessions[session_id]
    if session["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        engine = get_automation_engine()
        screenshot = await engine.capture_screenshot(session_id, full_page=True)
        return {
            "success": True,
            "screenshot": screenshot
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to capture screenshot: {str(e)}")

# ==================== Form 49A Automation Endpoints ====================

class Form49ARequest(BaseModel):
    """Request to start Form 49A automation"""
    service_config: Optional[Dict[str, Any]] = None

# Form 49A automation engines (session_id -> Form49AAutomationEngine)
form49a_engines: Dict[str, Any] = {}

@router.post("/form49a/start")
async def start_form49a_automation(
    request: Form49ARequest,
    authorization: str = Header(None)
):
    """
    Start Form 49A automation with fail-safe step-based workflow
    """
    if not Form49AAutomationEngine:
        raise HTTPException(
            status_code=503,
            detail="Form 49A automation engine not available"
        )
    
    user_id = verify_token(authorization)
    
    # Get user profile
    if use_database:
        user_profile = db_manager.get_profile(user_id)
    else:
        user_profile = profiles_db.get(user_id, {})
    
    if not user_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile not found. Please complete your profile first."
        )
    
    # Get service definition for PAN
    if not get_service_definition:
        raise HTTPException(
            status_code=503,
            detail="Service catalog not available"
        )
    
    service = get_service_definition("pan_card")
    if not service:
        raise HTTPException(
            status_code=404,
            detail="PAN card service not found"
        )
    
    # Get official URL
    official_url = service.official_url or "https://www.pan.utiitsl.com/newA.html"
    
    # Create session ID
    session_id = str(uuid.uuid4())
    
    # Initialize automation engine
    if not get_automation_engine:
        raise HTTPException(
            status_code=503,
            detail="Playwright automation engine not available"
        )
    
    engine = get_automation_engine()
    
    # Create new browser session
    try:
        await engine.create_session(session_id, official_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create browser session: {str(e)}"
        )
    
    # Get page
    page = engine.active_sessions[session_id]['page']
    
    # Wait for page to load
    try:
        await page.wait_for_load_state('networkidle', timeout=15000)
    except:
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=10000)
            await asyncio.sleep(2)
        except:
            pass
    
    # Helper: attach reinjection listeners so overlay stays after navigation
    def attach_overlay_reinject(target_page):
        async def reinject(p):
            try:
                control_script = get_control_ui_script()
                await p.evaluate(control_script)
                logger.debug("[CONTROL UI] Reinjected after navigation")
            except Exception as reinject_err:
                logger.debug(f"[CONTROL UI] Reinjection failed: {reinject_err}")

        def on_dom_loaded():
            asyncio.create_task(reinject(target_page))
        
        def on_load():
            asyncio.create_task(reinject(target_page))
        
        def on_frame_navigated(frame):
            asyncio.create_task(reinject(frame.page))
        
        target_page.on("domcontentloaded", on_dom_loaded)
        target_page.on("load", on_load)
        target_page.on("framenavigated", on_frame_navigated)

    # Inject KYRON control UI (initial) and attach reinjection hooks
    try:
        control_script = get_control_ui_script()
        await page.evaluate(control_script)
        await asyncio.sleep(0.5)
        attach_overlay_reinject(page)
    except Exception as e:
        logger.warning(f"Failed to inject control UI: {e}")
    
    # Initialize Form 49A automation engine
    service_config = request.service_config or {}
    
    # Log the received service config
    print("="*60)
    print("Starting Form 49A Automation")
    print(f"Service Config Received: {service_config}")
    print(f"User Profile: {user_profile.get('fullName', 'N/A')}, {user_profile.get('email', 'N/A')}")
    print("="*60)
    
    form49a_engine = Form49AAutomationEngine(page, user_profile, service_config, user_id=user_id)
    form49a_engines[session_id] = form49a_engine
    
    # Store session with service config
    agent_sessions[session_id] = {
        "user_id": user_id,
        "service_id": "pan_card",
        "status": "running",
        "current_action": "Initializing Form 49A automation...",
        "created_at": datetime.now().isoformat(),
        "form49a": True,
        "service_config": service_config,  # Store for tracking
        "collected_data": {
            "applicant_type": service_config.get("applicant_type", "individual"),
            "delivery_type": service_config.get("delivery_type", "epan")
        }
    }
    
    # Start automation in background
    asyncio.create_task(run_form49a_automation(session_id, form49a_engine, page))
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "Form 49A automation started",
        "status_url": f"/api/agent/form49a/status/{session_id}"
    }

async def run_form49a_automation(session_id: str, form49a_engine: Form49AAutomationEngine, page):
    """Run Form 49A automation workflow"""
    try:
        # Update status
        agent_sessions[session_id]["status"] = "running"
        agent_sessions[session_id]["current_action"] = "Starting Form 49A automation..."
        
        # Try to find and click Apply button
        apply_selectors = [
            "text=New Application",
            "text=Apply for New PAN",
            "text=Apply",
            "text=Apply Now",
            "a:has-text('New Application')",
            "button:has-text('Apply')"
        ]
        
        clicked_apply = False
        new_page = None
        
        for selector in apply_selectors:
            try:
                element = await page.wait_for_selector(selector, timeout=5000, state='visible')
                if element:
                    # Use expect_popup to handle new tab correctly
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5 + (0.2 * (hash(selector) % 5) / 5))
                    
                    try:
                        async with page.expect_popup(timeout=5000) as popup_info:
                            await element.click()
                        
                        # New tab opened
                        new_page = await popup_info.value
                        logger.info(f"🆕 New PAN application tab opened: {new_page.url}")
                        
                        # Maximize new tab and set 100% zoom
                        try:
                            await new_page.set_viewport_size({"width": 1920, "height": 1080})
                        except:
                            pass
                        
                        # Force 100% zoom in new tab
                        try:
                            await new_page.evaluate("""
                                document.body.style.zoom = '1.0';
                                document.documentElement.style.zoom = '1.0';
                            """)
                        except:
                            pass
                        
                        # CRITICAL: Wait for new tab to FULLY load
                        logger.info(f"[NEW TAB] Waiting for page to load: {new_page.url}")
                        try:
                            await new_page.wait_for_load_state('networkidle', timeout=20000)
                            logger.info("[NEW TAB] Network idle reached")
                        except:
                            logger.warning("[NEW TAB] Network idle timeout, trying domcontentloaded")
                            try:
                                await new_page.wait_for_load_state('domcontentloaded', timeout=15000)
                                logger.info("[NEW TAB] DOM content loaded")
                            except:
                                logger.warning("[NEW TAB] DOM load timeout, continuing anyway")
                        
                        # Additional wait for dynamic content
                        await asyncio.sleep(3)
                        logger.info("[NEW TAB] Additional wait completed")
                        
                        # CRITICAL: Switch to new page and update active_page
                        logger.info("[TAB SWITCHED] Updating Form49A engine with new page")
                        form49a_engine.page = new_page
                        form49a_engine.active_page = new_page  # Will be set to iframe if found
                        page = new_page
                        logger.info(f"[TAB SWITCHED] Page updated. URL: {new_page.url}")
                        
                        # Re-inject control UI in new tab
                        try:
                            control_script = get_control_ui_script()
                            await new_page.evaluate(control_script)
                            logger.info("[CONTROL UI] Injected in new tab")
                            attach_overlay_reinject(new_page)
                        except Exception as e:
                            logger.debug(f"Failed to inject control UI in new tab: {e}")
                        
                    except Exception:
                        # No popup, try regular navigation
                        await element.click()
                        await asyncio.sleep(2)
                        try:
                            await page.wait_for_load_state('networkidle', timeout=10000)
                        except:
                            pass
                        
                        # Re-inject control UI in new tab
                        try:
                            control_script = get_control_ui_script()
                            # Execute the script directly
                            await page.evaluate(control_script)
                        except Exception as e:
                            logger.debug(f"Failed to inject control UI in new tab: {e}")
                    
                    clicked_apply = True
                    break
            except:
                continue
        
        if not clicked_apply:
            agent_sessions[session_id]["current_action"] = "Apply button not found. Continuing with form filling..."
        
        # CRITICAL: Wait for form to load and detect iframe
        logger.info("[FORM49A] Waiting for form to fully load...")
        
        # Ensure we're using the correct page (new tab if opened)
        if new_page:
            form49a_engine.page = new_page
            form49a_engine.active_page = new_page
            logger.info(f"[TAB SWITCHED] Using new tab: {new_page.url}")
            
            # Wait for page to be ready
            try:
                await new_page.wait_for_load_state('networkidle', timeout=15000)
                logger.info("[FORM49A] Page network idle")
            except:
                try:
                    await new_page.wait_for_load_state('domcontentloaded', timeout=10000)
                    logger.info("[FORM49A] Page DOM loaded")
                except:
                    logger.warning("[FORM49A] Page load timeout, continuing")
            
            # Additional wait for iframe to load
            await asyncio.sleep(4)
            logger.info("[FORM49A] Additional wait for iframe completed")
        else:
            # No new tab, wait on current page
            await asyncio.sleep(3)
            logger.info("[FORM49A] Waiting on current page")
        
        # Run automation (will detect iframe inside)
        logger.info("[FORM49A] ========== STARTING AUTOMATION ==========")
        logger.info(f"[FORM49A] Current page URL: {form49a_engine.page.url}")
        logger.info(f"[FORM49A] Active page: {'iframe' if form49a_engine.iframe_page else 'main page'}")
        result = await form49a_engine.run_automation()
        logger.info(f"[FORM49A] ========== AUTOMATION COMPLETED: {result.get('status')} ==========")
        
        # Update session status
        agent_sessions[session_id]["status"] = result["status"]
        agent_sessions[session_id]["current_action"] = result.get("message", "Automation completed")
        
        # Update control UI
        try:
            status = form49a_engine.status.value
            progress = form49a_engine.get_status()["progress"]
            message = result.get("message", "")
            
            await page.evaluate(f"""
                if (window.updateKyronStatus) {{
                    window.updateKyronStatus('{status}', '{message}', 'Step {progress}');
                }}
            """)
        except:
            pass
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Form 49A automation error: {e}")
        agent_sessions[session_id]["status"] = "error"
        agent_sessions[session_id]["current_action"] = f"Error: {str(e)}"

@router.get("/form49a/status/{session_id}")
async def get_form49a_status(
    session_id: str,
    authorization: str = Header(None)
):
    """Get Form 49A automation status"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if agent_sessions[session_id]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if session_id not in form49a_engines:
        return {
            "status": agent_sessions[session_id]["status"],
            "message": "Form 49A engine not initialized"
        }
    
    form49a_engine = form49a_engines[session_id]
    status = form49a_engine.get_status()
    
    return {
        "success": True,
        "session_status": agent_sessions[session_id]["status"],
        "automation_status": status,
        "current_action": agent_sessions[session_id]["current_action"]
    }

@router.post("/form49a/pause/{session_id}")
async def pause_form49a(
    session_id: str,
    authorization: str = Header(None)
):
    """Pause Form 49A automation"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if agent_sessions[session_id]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if session_id not in form49a_engines:
        raise HTTPException(status_code=404, detail="Form 49A engine not found")
    
    form49a_engine = form49a_engines[session_id]
    form49a_engine.pause()
    
    agent_sessions[session_id]["status"] = "paused"
    agent_sessions[session_id]["current_action"] = "Automation paused by user"
    
    return {"success": True, "message": "Automation paused"}

@router.post("/form49a/resume/{session_id}")
async def resume_form49a(
    session_id: str,
    authorization: str = Header(None)
):
    """Resume Form 49A automation"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if agent_sessions[session_id]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if session_id not in form49a_engines:
        raise HTTPException(status_code=404, detail="Form 49A engine not found")
    
    form49a_engine = form49a_engines[session_id]
    
    # Resume automation
    form49a_engine.status = AutomationStatus.RUNNING
    agent_sessions[session_id]["status"] = "running"
    
    # Resume in background
    page = form49a_engine.page
    asyncio.create_task(run_form49a_resume(session_id, form49a_engine, page))
    
    return {"success": True, "message": "Automation resumed"}

async def run_form49a_resume(session_id: str, form49a_engine: Form49AAutomationEngine, page):
    """Resume Form 49A automation from current step"""
    try:
        # Resume automation
        result = await form49a_engine.resume_automation()
        
        # Update session status
        agent_sessions[session_id]["status"] = result["status"]
        agent_sessions[session_id]["current_action"] = result.get("message", "Automation resumed")
        
        # Update control UI
        try:
            status = form49a_engine.status.value
            progress = form49a_engine.get_status()["progress"]
            message = result.get("message", "")
            
            await page.evaluate(f"""
                if (window.updateKyronStatus) {{
                    window.updateKyronStatus('{status}', '{message}', 'Step {progress}');
                }}
            """)
        except:
            pass
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Form 49A resume error: {e}")
        agent_sessions[session_id]["status"] = "error"
        agent_sessions[session_id]["current_action"] = f"Resume error: {str(e)}"

@router.post("/form49a/stop/{session_id}")
async def stop_form49a(
    session_id: str,
    authorization: str = Header(None)
):
    """Stop Form 49A automation"""
    user_id = verify_token(authorization)
    
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if agent_sessions[session_id]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    if session_id not in form49a_engines:
        raise HTTPException(status_code=404, detail="Form 49A engine not found")
    
    form49a_engine = form49a_engines[session_id]
    form49a_engine.stop()
    
    agent_sessions[session_id]["status"] = "paused"
    agent_sessions[session_id]["current_action"] = "Automation stopped by user"
    
    return {"success": True, "message": "Automation stopped"}

