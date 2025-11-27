# 🔧 Fix 404 Error for Website-Based Lead Generation

## Problem
Getting 404 error when trying to use the website-based lead generation endpoint:
```
/api/v1/leads/generate-from-website:1 Failed to load resource: the server responded with a status of 404
```

## Solution

The backend server needs to be **restarted** to register the new endpoint.

### Step 1: Stop the Backend Server

**If running in terminal:**
- Press `Ctrl+C` to stop the server

**If running in background:**
```bash
# Find and kill Python processes
Get-Process python | Stop-Process
```

### Step 2: Restart the Backend

```bash
# Activate virtual environment
venv\Scripts\activate

# Start the server
python api.py
```

You should see:
```
🚀 Lead Generator API Starting...
📚 API Documentation: http://localhost:8000/docs
💚 Health Check: http://localhost:8000/health
```

### Step 3: Verify Endpoint is Available

1. Open http://localhost:8000/docs in your browser
2. Look for `/api/v1/leads/generate-from-website` endpoint
3. It should be listed under "Leads" tag

### Step 4: Test the Endpoint

Try generating leads from website again in the frontend.

## Alternative: Quick Restart Script

Create a file `restart-backend.bat`:

```batch
@echo off
echo Stopping backend...
Get-Process python -ErrorAction SilentlyContinue | Stop-Process
timeout /t 2 /nobreak >nul
echo Starting backend...
call venv\Scripts\activate.bat
python api.py
```

Then run:
```bash
restart-backend.bat
```

## Why This Happens

When you add new endpoints to `api.py`, FastAPI needs to reload the application to register them. If the server was started before the new code was added, it won't have the new endpoint registered.

## Prevention

- Always restart the backend after making changes to `api.py`
- Use `uvicorn` with `--reload` flag for auto-reload in development:
  ```bash
  uvicorn api:app --reload --host 0.0.0.0 --port 8000
  ```

## Still Getting 404?

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check endpoint exists in docs:**
   - Visit http://localhost:8000/docs
   - Search for "generate-from-website"

3. **Check for import errors:**
   ```bash
   python -c "from context_aware_lead_generator import generate_leads_from_website; print('OK')"
   ```

4. **Check API logs:**
   - Look for any error messages when starting the server
   - Check for import errors

5. **Verify frontend proxy:**
   - Check `frontend/vite.config.js` has correct proxy settings
   - Ensure `VITE_API_URL` is not overriding proxy

## Quick Test

After restarting, test the endpoint directly:

```bash
curl -X POST http://localhost:8000/api/v1/leads/generate-from-website \
  -H "Content-Type: application/json" \
  -d '{"website_url": "https://example.com", "number": 5}'
```

If this works, the endpoint is registered correctly!

