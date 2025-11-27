# ⚡ Quick Fix for 404 Error

## The Problem
The endpoint `/api/v1/leads/generate-from-website` returns 404 because the backend server was started **before** the new endpoint was added.

## ✅ Solution: Restart Backend Server

### Option 1: Use the Restart Script (Easiest)

1. **Stop the current backend** (if running in terminal, press `Ctrl+C`)

2. **Run the restart script:**
   ```bash
   restart-backend.bat
   ```

### Option 2: Manual Restart

1. **Stop the backend:**
   - If running in terminal: Press `Ctrl+C`
   - Or kill Python processes:
     ```powershell
     Get-Process python | Stop-Process
     ```

2. **Start the backend:**
   ```bash
   venv\Scripts\activate
   python api.py
   ```

3. **Verify it's working:**
   - Check http://localhost:8000/docs
   - Look for `/api/v1/leads/generate-from-website` in the endpoints list

### Option 3: Enable Auto-Reload (For Development)

The backend already has auto-reload enabled in development mode. If it's not working, make sure:

1. `ENVIRONMENT` is NOT set to `production` in `.env`
2. Or modify `api.py` to always use reload:
   ```python
   reload=True  # Always reload in development
   ```

## Verify the Fix

After restarting:

1. **Check the endpoint exists:**
   - Visit http://localhost:8000/docs
   - Search for "generate-from-website"
   - It should appear under "Leads" tag

2. **Test in frontend:**
   - Go to http://localhost:3000
   - Select "From Website" mode
   - Enter a website URL
   - Click "Generate Leads"
   - Should work now! ✅

## Why This Happens

FastAPI registers endpoints when the application starts. If you:
1. Start the server
2. Then add a new endpoint to the code
3. The server won't know about the new endpoint until you restart it

## Prevention

- Always restart the backend after adding new endpoints
- Use auto-reload in development (already enabled)
- Check http://localhost:8000/docs after making changes

---

**After restarting, the 404 error should be fixed!** 🎉

