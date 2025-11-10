# CORS Fix Guide

## Issues Fixed

### 1. NaN Input Error ✅
**Problem**: The number input field was causing "NaN" errors when empty.

**Solution**: Updated `InputForm.jsx` to handle empty values gracefully:
```javascript
onChange={(e) => {
  const value = e.target.value === '' ? 1 : parseInt(e.target.value) || 1
  setFormData({ ...formData, number: value })
}}
```

### 2. CORS Configuration ✅
**Problem**: Frontend at `https://leadgenerator.meallensai.com` was blocked by CORS policy.

**Solution**: Enhanced CORS middleware in `api.py` to:
- Always include production frontend domain
- Better handle environment variables
- Add debugging endpoint

## Deployment Steps

### Step 1: Deploy Backend to Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Select your API service** (lead-gen-aes4)
3. **Go to Environment Variables**
4. **Add/Update the following variable**:
   ```
   Key: ALLOWED_ORIGINS
   Value: https://leadgenerator.meallensai.com,https://lead-gen-aes4.onrender.com,http://localhost:5173
   ```
5. **Click "Save Changes"**
6. **Render will automatically redeploy** your service

### Step 2: Deploy Frontend to Vercel

From your terminal:

```bash
cd frontend
npm run build
# Deploy to your production URL
```

If using Vercel CLI:
```bash
cd frontend
vercel --prod
```

### Step 3: Verify CORS Configuration

After deployment, test the CORS configuration:

```bash
curl https://lead-gen-aes4.onrender.com/cors-debug
```

This should show:
```json
{
  "allowed_origins": [
    "https://leadgenerator.meallensai.com",
    "https://lead-gen-aes4.onrender.com",
    ...
  ],
  "request_origin": null,
  "request_host": "lead-gen-aes4.onrender.com"
}
```

### Step 4: Test from Frontend

Visit: https://leadgenerator.meallensai.com

Try generating leads. The CORS error should be resolved!

## Troubleshooting

### If CORS error persists:

1. **Check Render Logs**:
   - Go to Render Dashboard → Your Service → Logs
   - Look for the startup message showing allowed origins
   - Should see: `CORS Allowed Origins: ['https://leadgenerator.meallensai.com', ...]`

2. **Clear Browser Cache**:
   ```
   Chrome: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
   Select "Cached images and files"
   Clear data
   ```

3. **Test with curl**:
   ```bash
   curl -X OPTIONS https://lead-gen-aes4.onrender.com/api/v1/leads/generate \
     -H "Origin: https://leadgenerator.meallensai.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -v
   ```
   
   Should see:
   ```
   Access-Control-Allow-Origin: https://leadgenerator.meallensai.com
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
   ```

4. **Verify Environment Variable**:
   In Render dashboard, ensure `ALLOWED_ORIGINS` is set correctly with NO extra spaces

### If NaN error persists:

This shouldn't happen with the fix, but if it does:
1. Clear browser cache completely
2. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)
3. Check browser console for any other errors

## Quick Deployment Commands

```bash
# 1. Commit changes
git add .
git commit -m "Fix CORS and NaN input errors"
git push origin main

# 2. Render will auto-deploy the backend

# 3. Deploy frontend
cd frontend
npm run build
vercel --prod
```

## What Changed

### Backend (`api.py`)
- Enhanced CORS configuration to always include production domain
- Added `expose_headers` to CORS middleware
- Added `/cors-debug` endpoint for troubleshooting
- Better handling of ALLOWED_ORIGINS environment variable

### Frontend (`InputForm.jsx`)
- Fixed NaN error in number input field
- Now handles empty input gracefully

## Testing Checklist

- [ ] Backend deployed to Render
- [ ] ALLOWED_ORIGINS environment variable set on Render
- [ ] Frontend deployed to Vercel/production
- [ ] Can access https://leadgenerator.meallensai.com
- [ ] No CORS errors in browser console
- [ ] Can generate leads successfully
- [ ] Number input doesn't show NaN errors
- [ ] Email functionality works

## Support

If issues persist:
1. Check Render logs for startup messages
2. Visit `/cors-debug` endpoint to verify configuration
3. Use browser DevTools Network tab to inspect failed requests
4. Check that both frontend and backend are using HTTPS (not HTTP)

