"""
KYRON Playwright Automation Engine
Handles browser automation, screenshot capture, and form filling
"""

import asyncio
import base64
from typing import Dict, List, Optional, Any, Tuple, Callable
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import json
import logging
import logging

logger = logging.getLogger(__name__)

class PlaywrightAutomationEngine:
    """Playwright-based automation engine for KYRON"""
    
    def __init__(self, headless: bool = False):
        """
        Initialize Playwright automation engine
        
        Args:
            headless: Run browser in headless mode (default: False for visible browser)
        """
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.active_sessions: Dict[str, Dict] = {}
        self.is_paused: bool = False
        self.is_stopped: bool = False  # {session_id: {page, context, ...}}
    
    async def initialize(self):
        """Initialize Playwright and browser"""
        try:
            # Check if playwright is installed
            try:
                from playwright.async_api import async_playwright
            except ImportError:
                raise RuntimeError("Playwright is not installed. Please run: pip install playwright && playwright install chromium")
            
            # Close existing browser if it exists but is invalid
            if self.browser is not None:
                try:
                    # Test if browser is still valid
                    await self.browser.new_context()
                    # If we get here, browser is valid, close the test context
                    # Actually, we shouldn't create a context just to test - let's check differently
                    # Just proceed if browser exists
                    logger.info("Browser already initialized, reusing")
                    return
                except Exception:
                    # Browser is invalid, close it
                    logger.warning("Existing browser is invalid, closing and reinitializing")
                    try:
                        await self.browser.close()
                    except:
                        pass
                    self.browser = None
            
            # Close existing playwright if it exists
            if self.playwright is not None:
                try:
                    await self.playwright.stop()
                except:
                    pass
                self.playwright = None
            
            # Start Playwright
            if self.playwright is None:
                try:
                    self.playwright = await async_playwright().start()
                    logger.info("Playwright started")
                except Exception as e:
                    raise RuntimeError(f"Failed to start Playwright: {str(e)}. Make sure Playwright is installed: pip install playwright && playwright install chromium")
            
            # Launch browser - REAL GOOGLE CHROME (not Chromium)
            if self.browser is None:
                try:
                    self.browser = await self.playwright.chromium.launch(
                        channel="chrome",  # Use real Google Chrome
                        headless=False,  # Always visible for government sites
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-web-security',
                            '--disable-features=IsolateOrigins,site-per-process',
                            '--no-first-run',
                            '--no-default-browser-check',
                            '--disable-infobars',
                            '--start-maximized',  # Start maximized
                            '--window-size=1920,1080',
                            '--force-device-scale-factor=1.0'  # Force 100% zoom
                        ]
                    )
                    logger.info("✅ Google Chrome browser launched (maximized, 100% zoom)")
                except Exception as e:
                    error_msg = str(e)
                    if "Executable doesn't exist" in error_msg or "Browser not found" in error_msg:
                        raise RuntimeError(f"Google Chrome not found: {error_msg}. Please install Google Chrome browser.")
                    raise RuntimeError(f"Failed to launch Google Chrome: {str(e)}. Please install Google Chrome browser.")
            
            # Verify browser is actually initialized
            if self.browser is None:
                raise RuntimeError("Browser object is None after launch. Playwright installation may be incomplete.")
            
            # Test browser by creating a test context
            try:
                test_context = await self.browser.new_context()
                await test_context.close()
                logger.info("Browser context test successful")
            except AttributeError as e:
                if "'NoneType' object has no attribute 'new_context'" in str(e):
                    raise RuntimeError("Browser object is None when creating context. Chromium may not be installed. Please run: playwright install chromium")
                raise RuntimeError(f"Browser context test failed: {str(e)}. Browser may not be properly installed.")
            except Exception as e:
                raise RuntimeError(f"Browser context test failed: {str(e)}. Browser may not be properly installed.")
                
            logger.info("Playwright automation engine initialized successfully")
        except RuntimeError:
            raise  # Re-raise RuntimeError as-is
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}", exc_info=True)
            raise RuntimeError(f"Playwright initialization failed: {str(e)}. Please install Playwright: pip install playwright && playwright install chromium")
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            try:
                await self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                await self.playwright.stop()
            except:
                pass
        logger.info("Playwright automation engine closed")
    
    def pause(self):
        """Pause automation (hook for external control)"""
        self.is_paused = True
        logger.info("⏸️ Automation paused")
    
    def resume(self):
        """Resume automation (hook for external control)"""
        self.is_paused = False
        logger.info("▶️ Automation resumed")
    
    def stop(self):
        """Stop automation (hook for external control)"""
        self.is_stopped = True
        logger.info("⏹️ Automation stopped")
    
    async def wait_if_paused(self):
        """Wait if automation is paused (check hook)"""
        while self.is_paused and not self.is_stopped:
            await asyncio.sleep(0.5)
        return not self.is_stopped
    
    async def create_session(self, session_id: str, url: Optional[str] = None, headless: bool = True) -> Dict[str, Any]:
        """
        Create a new browser session
        
        Args:
            session_id: Unique session identifier
            url: Optional URL to navigate to
            
        Returns:
            Session information
        """
        # Always ensure initialization - don't trust cached state
        try:
            await self.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize in create_session: {e}")
            raise RuntimeError(f"Failed to initialize Playwright: {str(e)}. Please ensure Playwright and Chromium are installed: pip install playwright && playwright install chromium")
        
        # Triple-check browser is initialized and valid
        if self.browser is None:
            logger.error("Browser is None after initialization")
            raise RuntimeError("Browser not initialized after initialize() call. Please install Playwright: pip install playwright && playwright install chromium")
        
        # Verify browser object is actually a Browser instance
        if not hasattr(self.browser, 'new_context'):
            logger.error(f"Browser object is invalid: {type(self.browser)}")
            raise RuntimeError("Browser object is invalid. Please reinstall Playwright: pip install playwright && playwright install chromium")
        
        # Verify browser is still connected
        try:
            # Check if browser is still valid by checking its type
            from playwright.async_api import Browser
            if not isinstance(self.browser, Browser):
                raise RuntimeError("Browser object is not a valid Browser instance")
        except Exception as e:
            logger.error(f"Browser validation failed: {e}")
            # Try to reinitialize
            self.browser = None
            self.playwright = None
            await self.initialize()
        
        # Create new context with realistic settings for government sites
        try:
            context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                viewport=None,  # Use full window size (no fixed viewport)
                locale='en-IN',
                timezone_id='Asia/Kolkata',
                permissions=['geolocation'],
                geolocation={'latitude': 28.6139, 'longitude': 77.2090},
                color_scheme='light',
                accept_downloads=True,
                ignore_https_errors=True,
                java_script_enabled=True,
                device_scale_factor=1.0  # Force 100% zoom
            )
        except AttributeError as e:
            if "'NoneType' object has no attribute 'new_context'" in str(e) or self.browser is None:
                logger.error("Browser is None when trying to create context")
                # Force reinitialize
                self.browser = None
                self.playwright = None
                await self.initialize()
                if self.browser is None:
                    raise RuntimeError("Browser is None after reinitialization. Please install Chromium: playwright install chromium")
                # Try again
                context = await self.browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-IN',
                    timezone_id='Asia/Kolkata',
                    permissions=['geolocation'],
                    geolocation={'latitude': 28.6139, 'longitude': 77.2090},
                    color_scheme='light',
                    accept_downloads=True,
                    ignore_https_errors=True,
                    java_script_enabled=True
                )
            else:
                raise
        except Exception as e:
            logger.error(f"Failed to create browser context: {e}")
            raise RuntimeError(f"Failed to create browser context: {str(e)}. Please ensure Playwright and Chromium are installed: pip install playwright && playwright install chromium")
        
        page = await context.new_page()
        
        # Maximize window and set 100% zoom
        try:
            await page.set_viewport_size({"width": 1920, "height": 1080})
        except:
            pass
        
        # Force 100% zoom via multiple methods
        try:
            await page.evaluate("""
                document.body.style.zoom = '1.0';
                document.documentElement.style.zoom = '1.0';
            """)
            # Also try setting viewport zoom via CDP if available
            try:
                cdp_session = await context.new_cdp_session(page)
                await cdp_session.send('Emulation.setPageScaleFactor', {'pageScaleFactor': 1.0})
            except:
                pass
        except:
            pass
        
        # Navigate if URL provided with better timeout handling and retries
        if url:
            max_retries = 2
            navigation_success = False
            
            for attempt in range(max_retries):
                try:
                    # Try networkidle first (more reliable)
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    navigation_success = True
                    break
                except Exception as e:
                    logger.warning(f"Navigation attempt {attempt + 1} with networkidle failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
            
            if not navigation_success:
                try:
                    # Fallback to domcontentloaded
                    await page.goto(url, wait_until='domcontentloaded', timeout=20000)
                    # Wait a bit more for dynamic content
                    await asyncio.sleep(3)
                    navigation_success = True
                except Exception as e2:
                    logger.warning(f"Navigation with domcontentloaded failed: {e2}")
                    try:
                        # Last resort: just navigate without waiting
                        await page.goto(url, timeout=15000)
                        await asyncio.sleep(3)  # Give it time to load
                    except Exception as e3:
                        logger.error(f"All navigation attempts failed: {e3}")
                        raise RuntimeError(f"Failed to navigate to {url}: {str(e3)}")
        
        self.active_sessions[session_id] = {
            'page': page,
            'context': context,
            'url': url,
            'is_paused': False,
            'is_stopped': False
        }
        
        logger.info(f"Created session {session_id} for URL: {url}")
        
        return {
            "session_id": session_id,
            "url": url,
            "status": "active"
        }
    
    async def navigate(self, session_id: str, url: str) -> Dict[str, Any]:
        """
        Navigate to a URL in an existing session
        
        Args:
            session_id: Session identifier
            url: URL to navigate to
            
        Returns:
            Navigation result
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        page = self.active_sessions[session_id]['page']
        await page.goto(url, wait_until='networkidle')
        
        self.active_sessions[session_id]['url'] = url
        
        return {
            "success": True,
            "url": url,
            "title": await page.title()
        }
    
    async def capture_screenshot(self, session_id: str, full_page: bool = False) -> str:
        """
        Capture screenshot of current page
        
        Args:
            session_id: Session identifier
            full_page: Capture full page or just viewport
            
        Returns:
            Base64 encoded screenshot
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        page = self.active_sessions[session_id]['page']
        screenshot_bytes = await page.screenshot(full_page=full_page, type='png')
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        return screenshot_base64
    
    async def get_page_html(self, session_id: str) -> Tuple[str, Dict]:
        """
        Get HTML content and form field information
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple of (html_content, form_fields_info)
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        page = self.active_sessions[session_id]['page']
        
        # Get HTML content
        html_content = await page.content()
        
        # Extract form field information using JavaScript
        form_fields_info = await page.evaluate("""
            () => {
                const fields = [];
                const inputs = document.querySelectorAll('input, select, textarea');
                
                inputs.forEach(field => {
                    // Skip hidden fields
                    if (field.type === 'hidden') return;
                    
                    const rect = field.getBoundingClientRect();
                    const isVisible = rect.width > 0 && rect.height > 0 && 
                                    window.getComputedStyle(field).display !== 'none';
                    
                    if (!isVisible) return;
                    
                    fields.push({
                        selector: field.id ? `#${field.id}` : 
                                 field.name ? `[name="${field.name}"]` :
                                 field.className ? `.${field.className.split(' ')[0]}` : '',
                        id: field.id || '',
                        name: field.name || '',
                        type: field.type || field.tagName.toLowerCase(),
                        label: (() => {
                            // Try to find associated label
                            if (field.id) {
                                const label = document.querySelector(`label[for="${field.id}"]`);
                                if (label) return label.textContent.trim();
                            }
                            // Try parent label
                            const parentLabel = field.closest('label');
                            if (parentLabel) return parentLabel.textContent.trim();
                            // Try previous sibling
                            const prevSibling = field.previousElementSibling;
                            if (prevSibling && prevSibling.tagName === 'LABEL') {
                                return prevSibling.textContent.trim();
                            }
                            return '';
                        })(),
                        placeholder: field.placeholder || '',
                        value: field.value || '',
                        required: field.hasAttribute('required'),
                        visible: isVisible,
                        position: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        }
                    });
                });
                
                return fields;
            }
        """)
        
        return html_content, form_fields_info
    
    async def fill_field(self, session_id: str, selector: str, value: Any) -> Dict[str, Any]:
        """
        Fill a form field
        
        Args:
            session_id: Session identifier
            selector: CSS selector for the field
            value: Value to fill
            
        Returns:
            Fill result
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        page = self.active_sessions[session_id]['page']
        
        try:
            # Wait for field to be visible (with longer timeout)
            try:
                await page.wait_for_selector(selector, state='visible', timeout=10000)
            except:
                # Try waiting for any input field
                try:
                    await page.wait_for_selector('input, select, textarea', state='visible', timeout=5000)
                except:
                    pass
            
            # Get field info
            field_info = await page.evaluate(f"""
                (selector) => {{
                    try {{
                        const field = document.querySelector(selector);
                        if (!field) return {{exists: false}};
                        return {{
                            exists: true,
                            type: field.type || field.tagName.toLowerCase(),
                            tagName: field.tagName.toLowerCase(),
                            disabled: field.disabled,
                            readonly: field.readOnly
                        }};
                    }} catch(e) {{
                        return {{exists: false, error: e.message}};
                    }}
                }}
            """, selector)
            
            if not field_info.get("exists"):
                return {"success": False, "error": f"Field not found: {selector}"}
            
            if field_info.get("disabled") or field_info.get("readonly"):
                return {"success": False, "error": f"Field is disabled or readonly: {selector}"}
            
            field_type = field_info.get("type", "").lower()
            tag_name = field_info.get("tagName", "").lower()
            
            # Get field label/name for date detection
            field_label = await page.evaluate(f"""
                (selector) => {{
                    try {{
                        const field = document.querySelector(selector);
                        if (!field) return '';
                        const label = field.closest('label')?.textContent || 
                                     field.getAttribute('placeholder') || 
                                     field.getAttribute('title') || '';
                        return label;
                    }} catch(e) {{
                        return '';
                    }}
                }}
            """, selector)
            
            field_name = await page.evaluate(f"""
                (selector) => {{
                    try {{
                        const field = document.querySelector(selector);
                        if (!field) return '';
                        return field.getAttribute('name') || field.getAttribute('id') || '';
                    }} catch(e) {{
                        return '';
                    }}
                }}
            """, selector)
            
            # Format value if it's a date field
            from services.date_formatter import DateFormatter
            formatted_value = DateFormatter.format_for_field(
                str(value), 
                field_name, 
                field_label, 
                field_type
            )
            
            # Fill based on field type
            if tag_name == 'select':
                try:
                    await page.select_option(selector, formatted_value)
                except:
                    # Try by label if value doesn't match
                    await page.select_option(selector, label=formatted_value)
            elif tag_name == 'textarea' or field_type == 'textarea':
                await page.fill(selector, formatted_value)
            elif field_type == 'file':
                return {"success": False, "error": "File uploads require special handling"}
            elif field_type in ['checkbox', 'radio']:
                if str(value).lower() in ['true', '1', 'yes', 'on']:
                    await page.check(selector)
                else:
                    await page.uncheck(selector)
            else:
                # Text input, email, tel, number, date, etc.
                # Clear first
                await page.fill(selector, '')
                await asyncio.sleep(0.2)  # Slight delay for realistic behavior
                
                # For date fields, try clicking first if there's a date picker
                if DateFormatter.is_date_field(field_name, field_label) or field_type == 'date':
                    try:
                        # Try clicking the field to open date picker
                        await page.click(selector)
                        await asyncio.sleep(0.3)
                    except:
                        pass
                
                # Fill the value
                await page.fill(selector, formatted_value)
                await asyncio.sleep(0.2)
                
                # Trigger events for validation
                await page.dispatch_event(selector, 'input')
                await page.dispatch_event(selector, 'change')
                await page.dispatch_event(selector, 'blur')
                
                # Wait a bit to ensure validation completes
                await asyncio.sleep(0.3)
            
            await asyncio.sleep(0.5)
            
            # Verify value
            filled_value = await page.evaluate(f"""
                (selector) => {{
                    const field = document.querySelector(selector);
                    return field ? (field.value || field.textContent || '') : '';
                }}
            """, selector)
            
            return {
                "success": True,
                "selector": selector,
                "value": str(value),
                "filled_value": filled_value
            }
            
        except Exception as e:
            logger.error(f"Error filling field {selector}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "selector": selector
            }
    
    async def fill_form_batch(
        self, 
        session_id: str, 
        field_values: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Fill multiple form fields in sequence
        
        Args:
            session_id: Session identifier
            field_values: List of {selector, value} dictionaries
            
        Returns:
            Batch fill results
        """
        results = []
        successful = 0
        failed = 0
        
        total_fields = len(field_values)
        
        for idx, field_data in enumerate(field_values):
            selector = field_data.get('selector')
            value = field_data.get('value')
            label = field_data.get('label', selector)
            
            if not selector or value is None:
                results.append({
                    "success": False,
                    "error": "Missing selector or value",
                    "field": field_data
                })
                failed += 1
                continue
            
            # Progress callback
            if progress_callback:
                progress_callback({
                    "step": idx + 1,
                    "total": total_fields,
                    "action": f"Filling {label}",
                    "status": "processing"
                })
            
            result = await self.fill_field(session_id, selector, value)
            results.append(result)
            
            if result.get('success'):
                successful += 1
                if progress_callback:
                    progress_callback({
                        "step": idx + 1,
                        "total": total_fields,
                        "action": f"Filled {label}",
                        "status": "success"
                    })
            else:
                failed += 1
                if progress_callback:
                    progress_callback({
                        "step": idx + 1,
                        "total": total_fields,
                        "action": f"Failed to fill {label}",
                        "status": "error",
                        "error": result.get('error')
                    })
            
            # Realistic delay between fields (human-like behavior)
            await asyncio.sleep(0.5)
        
        return {
            "success": True,
            "total": len(field_values),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    async def click_button(self, session_id: str, selector: str) -> Dict[str, Any]:
        """
        Click a button or link
        
        Args:
            session_id: Session identifier
            selector: CSS selector for the button
            
        Returns:
            Click result
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        page = self.active_sessions[session_id]['page']
        
        try:
            await page.wait_for_selector(selector, state='visible', timeout=5000)
            await page.click(selector)
            await asyncio.sleep(1)  # Wait for navigation/updates
            
            return {
                "success": True,
                "selector": selector
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "selector": selector
            }
    
    async def inject_kyron_widget(self, session_id: str) -> Dict[str, Any]:
        """
        Inject comprehensive KYRON overlay UI with control panel
        NOW USING EXTERNAL JS FILE FOR BETTER MAINTAINABILITY
        
        Args:
            session_id: Session identifier
            
        Returns:
            Injection result
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        page = self.active_sessions[session_id]['page']
        
        # Load overlay from external file
        import os
        overlay_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'kyron_overlay.js')
        
        try:
            with open(overlay_path, 'r', encoding='utf-8') as f:
                widget_script = f.read()
        except FileNotFoundError:
            logger.warning(f"Overlay file not found at {overlay_path}, using embedded version")
            # Fallback to embedded version
            widget_script = """
        (function() {
            if (document.getElementById('kyron-overlay')) return;
            
            // Create overlay container
            const overlay = document.createElement('div');
            overlay.id = 'kyron-overlay';
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 999998;
            `;
            
            // Create floating button (bottom-right)
            const floatBtn = document.createElement('div');
            floatBtn.id = 'kyron-float-btn';
            floatBtn.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 60px;
                height: 60px;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                border-radius: 50%;
                cursor: pointer;
                z-index: 999999;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
                transition: transform 0.2s;
                pointer-events: auto;
            `;
            floatBtn.innerHTML = '<span style="color: white; font-weight: bold; font-size: 24px;">K</span>';
            
            // Create control panel
            const panel = document.createElement('div');
            panel.id = 'kyron-panel';
            panel.style.cssText = `
                position: fixed;
                bottom: 90px;
                right: 20px;
                width: 320px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.15);
                padding: 20px;
                z-index: 999999;
                pointer-events: auto;
                display: none;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            `;
            
            panel.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <h3 style="margin: 0; color: #1f2937; font-size: 18px; font-weight: 600;">KYRON Control</h3>
                    <button id="kyron-close-panel" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #6b7280;">×</button>
                </div>
                <div style="margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                        <div id="kyron-status-indicator" style="width: 12px; height: 12px; border-radius: 50%; background: #10b981;"></div>
                        <span id="kyron-status-text" style="color: #6b7280; font-size: 14px;">Running</span>
                    </div>
                    <div id="kyron-current-step" style="color: #1f2937; font-size: 13px; margin-top: 8px; padding: 8px; background: #f3f4f6; border-radius: 6px;">
                        Initializing...
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button id="kyron-pause-btn" style="flex: 1; padding: 10px; background: #f59e0b; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 14px;">Pause</button>
                    <button id="kyron-resume-btn" style="flex: 1; padding: 10px; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 14px; display: none;">Resume</button>
                    <button id="kyron-stop-btn" style="flex: 1; padding: 10px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; font-size: 14px;">Stop</button>
                </div>
            `;
            
            // Toggle panel visibility
            let panelVisible = false;
            floatBtn.addEventListener('click', () => {
                panelVisible = !panelVisible;
                panel.style.display = panelVisible ? 'block' : 'none';
            });
            
            document.getElementById('kyron-close-panel')?.addEventListener('click', () => {
                panelVisible = false;
                panel.style.display = 'none';
            });
            
            // Control buttons (will be connected to backend via events)
            document.getElementById('kyron-pause-btn')?.addEventListener('click', () => {
                window.dispatchEvent(new CustomEvent('kyron-pause'));
            });
            
            document.getElementById('kyron-resume-btn')?.addEventListener('click', () => {
                window.dispatchEvent(new CustomEvent('kyron-resume'));
            });
            
            document.getElementById('kyron-stop-btn')?.addEventListener('click', () => {
                window.dispatchEvent(new CustomEvent('kyron-stop'));
            });
            
            // Update status function (called from backend)
            window.updateKyronStatus = function(status, step) {
                const indicator = document.getElementById('kyron-status-indicator');
                const statusText = document.getElementById('kyron-status-text');
                const stepText = document.getElementById('kyron-current-step');
                const pauseBtn = document.getElementById('kyron-pause-btn');
                const resumeBtn = document.getElementById('kyron-resume-btn');
                
                if (indicator && statusText) {
                    if (status === 'running' || status === 'filling') {
                        indicator.style.background = '#10b981';
                        statusText.textContent = 'Running';
                        pauseBtn.style.display = 'block';
                        resumeBtn.style.display = 'none';
                    } else if (status === 'paused') {
                        indicator.style.background = '#f59e0b';
                        statusText.textContent = 'Paused';
                        pauseBtn.style.display = 'none';
                        resumeBtn.style.display = 'block';
                    } else if (status === 'error') {
                        indicator.style.background = '#ef4444';
                        statusText.textContent = 'Error';
                    } else {
                        indicator.style.background = '#6b7280';
                        statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
                    }
                }
                
                if (stepText && step) {
                    stepText.textContent = step;
                }
            };
            
            overlay.appendChild(floatBtn);
            overlay.appendChild(panel);
            document.body.appendChild(overlay);
        })();
        """
        
        try:
            await page.add_init_script(widget_script)
            await page.evaluate(widget_script)
            
            return {
                "success": True,
                "message": "KYRON overlay UI injected"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close_session(self, session_id: str):
        """Close a browser session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            await session['context'].close()
            del self.active_sessions[session_id]
            logger.info(f"Closed session {session_id}")


# Global instance
_automation_engine: Optional[PlaywrightAutomationEngine] = None

def get_automation_engine() -> PlaywrightAutomationEngine:
    """Get or create global automation engine instance"""
    global _automation_engine
    if _automation_engine is None:
        _automation_engine = PlaywrightAutomationEngine(headless=True)
    return _automation_engine

