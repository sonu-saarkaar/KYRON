"""
This is the main entry point for the KYRON backend API.
It sets up FastAPI and includes all the route modules.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import time
import os

# Debug logging helper
def debug_log(location, message, data, hypothesis_id="A", run_id="run1"):
    log_data = {
        "sessionId": "debug-session",
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000)
    }
    print(f"[DEBUG] {json.dumps(log_data)}")  # Console fallback
    try:
        log_path = r'c:\Users\Sonu Bhai\Desktop\Project\KYRON\.cursor\debug.log'
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_data) + '\n')
    except Exception as log_err:
        print(f"[DEBUG] Log write failed: {log_err}")

# Import existing route modules
from auth import router as auth_router
from profile import router as profile_router
from documents import router as documents_router
from agent_logic import router as agent_router
from service_requests import router as service_requests_router

# Import admin panel routes
from routes.auth import router as admin_auth_router
from routes.admins import router as admin_admins_router
from routes.users import router as admin_users_router
from routes.logs import router as admin_logs_router
from routes.system import router as admin_system_router
from routes.downloads import router as downloads_router

# Import automation routes (Playwright + AI Vision)
# Make imports optional to prevent startup errors
try:
    from routes.automation import router as automation_router
except ImportError as e:
    print(f"Warning: Could not import automation router: {e}")
    automation_router = None

try:
    from routes.automation_standalone import router as automation_standalone_router
except ImportError as e:
    print(f"Warning: Could not import automation_standalone router: {e}")
    automation_standalone_router = None

# Import core config for CORS
from core.config import settings

# Create FastAPI app
app = FastAPI(
    title="KYRON API",
    description="AI Digital Execution Agent Backend with Admin Panel",
    version="1.0.0"
)

# Global exception handler
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # #region agent log
    debug_log("main.py:exception_handler", "global exception caught", {
        "method": request.method,
        "path": str(request.url.path),
        "error": str(exc),
        "errorType": type(exc).__name__
    }, "D")
    # #endregion
    import traceback
    print(f"[GLOBAL ERROR] {type(exc).__name__}: {exc}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # #region agent log
    debug_log("main.py:middleware", "request received", {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "hasAuth": "authorization" in request.headers
    }, "B")
    # #endregion
    try:
        response = await call_next(request)
        # #region agent log
        debug_log("main.py:middleware", "request completed", {
            "method": request.method,
            "path": request.url.path,
            "statusCode": response.status_code
        }, "B")
        # #endregion
        return response
    except Exception as e:
        # #region agent log
        debug_log("main.py:middleware", "request error", {
            "method": request.method,
            "path": request.url.path,
            "error": str(e),
            "errorType": type(e).__name__
        }, "D")
        # #endregion
        raise

# Enable CORS (Cross-Origin Resource Sharing) so frontend can communicate with backend
# In development, allow all origins for easier testing
cors_origins = settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

# Include existing routers (user-facing)
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(profile_router, prefix="/api/profile", tags=["profile"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
app.include_router(service_requests_router, prefix="/api/service", tags=["service"])

# Include admin panel routers
app.include_router(admin_auth_router, prefix="/auth", tags=["admin-auth"])
app.include_router(admin_admins_router, prefix="/admins", tags=["admin-management"])
app.include_router(admin_users_router, prefix="/users", tags=["admin-users"])
app.include_router(admin_logs_router, prefix="/logs", tags=["admin-logs"])
app.include_router(admin_system_router, prefix="/system", tags=["admin-system"])

# Include download routes
app.include_router(downloads_router, prefix="/download", tags=["downloads"])

# Database health route
try:
    from routes.database import router as database_router
    app.include_router(database_router, prefix="/api/database", tags=["database"])
except ImportError:
    pass

# Import and include new feature routes
try:
    from routes.blockchain import router as blockchain_router
    app.include_router(blockchain_router, prefix="/api/blockchain", tags=["blockchain"])
except ImportError as e:
    print(f"Warning: Could not import blockchain router: {e}")

try:
    from routes.voice import router as voice_router
    app.include_router(voice_router, prefix="/api/voice", tags=["voice"])
except ImportError as e:
    print(f"Warning: Could not import voice router: {e}")

try:
    from routes.screen_share import router as screen_share_router
    app.include_router(screen_share_router, prefix="/api/screen-share", tags=["screen-share"])
except ImportError as e:
    print(f"Warning: Could not import screen_share router: {e}")

# Import and include chat routes
try:
    # #region agent log
    debug_log("main.py:161", "attempting to import chat router", {}, "A")
    # #endregion
    from routes.chat import router as chat_router
    # #region agent log
    debug_log("main.py:161", "chat router imported successfully", {"routerExists": chat_router is not None}, "A")
    # #endregion
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    # #region agent log
    debug_log("main.py:161", "chat router registered", {"prefix": "/api/chat"}, "A")
    # #endregion
except ImportError as e:
    # #region agent log
    debug_log("main.py:161", "chat router import failed", {"error": str(e)}, "A")
    # #endregion
    print(f"Warning: Could not import chat router: {e}")

# Import and include agent routes (real-world execution)
try:
    from routes.automation_agent import router as agent_router
    app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
except ImportError as e:
    print(f"Warning: Could not import agent router: {e}")

# Include automation routes (Playwright + AI Vision)
if automation_router:
    app.include_router(automation_router, prefix="/api/automation", tags=["automation"])
# Standalone automation (no Chrome extension required)
if automation_standalone_router:
    app.include_router(automation_standalone_router, prefix="/api/automation/standalone", tags=["automation-standalone"])

# Root endpoint
@app.get("/")
def read_root():
    # #region agent log
    debug_log("main.py:127", "root endpoint hit", {}, "A")
    # #endregion
    return {
        "message": "KYRON API is running",
        "version": "1.0.0"
    }

# Test debug endpoint
@app.get("/test-debug")
def test_debug():
    # #region agent log
    debug_log("main.py:test-debug", "test debug endpoint", {"test": True}, "A")
    # #endregion
    return {"status": "debug logging test", "logPath": r'c:\Users\Sonu Bhai\Desktop\Project\KYRON\.cursor\debug.log'}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Run the server (for development)
if __name__ == "__main__":
    import uvicorn
    # Use import string for reload to work
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

