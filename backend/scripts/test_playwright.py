"""Test Playwright initialization"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

async def test_playwright():
    try:
        from services.playwright_automation import get_automation_engine
        
        print("Getting automation engine...")
        engine = get_automation_engine()
        
        print("Initializing...")
        await engine.initialize()
        
        print(f"Browser initialized: {engine.browser is not None}")
        print(f"Playwright initialized: {engine.playwright is not None}")
        
        if engine.browser is None:
            print("❌ ERROR: Browser is None!")
            return False
        
        # Test creating a context
        print("Testing browser context creation...")
        test_context = await engine.browser.new_context()
        print("✅ Context created successfully!")
        await test_context.close()
        
        print("Cleaning up...")
        await engine.close()
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_playwright())
    sys.exit(0 if result else 1)

