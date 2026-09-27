# Fix "No pyvenv.cfg file" Error

## Quick Fix

If you get the error `No pyvenv.cfg file` when running `python -m uvicorn main:app`, follow these steps:

### Option 1: Use the Batch Script (Easiest)
```cmd
cd backend
.\scripts\QUICK_FIX.bat
```

### Option 2: Manual Fix

1. **Activate the virtual environment first:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   ```

2. **Verify Python is from venv:**
   ```powershell
   python --version
   where.exe python
   ```
   Should show: `C:\Users\Sonu Bhai\Desktop\Project\KYRON\backend\venv\Scripts\python.exe`

3. **Run the backend:**
   ```powershell
   python run.py
   ```
   OR
   ```powershell
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

### Option 3: Use START Scripts

**Recommended:** Use the provided startup scripts:
```powershell
cd backend
.\scripts\START.ps1
```

Or the simple version:
```powershell
cd backend
.\scripts\START_SIMPLE.ps1
```

## Why This Happens

The error occurs when:
- Virtual environment is not activated
- Python is using system Python instead of venv Python
- The venv was created incorrectly

## Solution

Always activate the venv before running Python commands:
```powershell
.\venv\Scripts\Activate.ps1
```

Then run:
```powershell
python run.py
```

---

**Note:** The `START.ps1` script automatically handles venv activation and path resolution.

