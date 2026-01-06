"""
KYRON Backend Runner
Simple script to run the backend with proper error handling
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    
    if missing:
        print("Missing dependencies:", ", ".join(missing))
        print("Attempting to install automatically...")
        
        # Try to install missing dependencies
        import subprocess
        import sys
        
        try:
            # Try pip
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("Dependencies installed successfully!")
            return True
        except:
            print("Auto-install failed. Please run manually:")
            print("   pip install -r requirements_minimal.txt")
            return False
    
    return True

def main():
    """Main entry point"""
    print("Starting KYRON Backend...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run
    try:
        import uvicorn
        
        # First verify app can be imported
        try:
            from main import app
            print("Backend loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not import app directly: {e}")
            print("   Using import string instead...")
        
        print("Starting server on http://127.0.0.1:8000")
        print("API Docs: http://127.0.0.1:8000/docs")
        print("\nPress CTRL+C to stop\n")
        
        # Use import string for reload to work properly
        # On Windows, disable reload to avoid subprocess import issues
        import sys
        import platform
        
        # Disable reload on Windows by default (avoids subprocess import errors)
        if "--no-reload" in sys.argv:
            reload_enabled = False
        elif platform.system() == "Windows":
            reload_enabled = False
            print("Auto-reload disabled on Windows (to avoid subprocess issues)")
        else:
            reload_enabled = True
        
        uvicorn.run(
            "main:app",  # Import string format for reload
            host="127.0.0.1",
            port=8000,
            reload=reload_enabled,
            reload_dirs=[os.getcwd()] if reload_enabled else None,
            reload_includes=["*.py"] if reload_enabled else None
        )
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please check if all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

