# 🔧 Fix Yagmail on Render.com - Port 587 → Port 465

## Problem
```
❌ Yagmail failed: [Errno 101] Network is unreachable
```
**Render.com blocks port 587 (STARTTLS)** but port 465 (SSL) might work!

## Solution: Switch to Port 465

### Step 1: Update Render Environment Variables

1. Go to **Render Dashboard**: https://dashboard.render.com
2. Click on your service: **lead-gen-but I haes4**
3. Go to **Environment** tab
4. Find the variable **`SMTP_PORT`**
5. **Change its value**:
   - ❌ **Old value**: `587`
   - ✅ **New value**: `465`
6. Click **"Save Changes"**

Your environment variables should now be:
```
EMAIL_USER=danielsamueletukudo@gmail.com
EMAIL_PASSWORD=ndomskuvjgqogfbv
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465  ← Changed from 587 to 465
```

### Step 2: Deploy the Fixed Code

Run these commands in your terminal:

```bash
cd /Users/danielsamuel/PycharmProjects/LEAD-generator

# Stage all changes
git add .

# Commit with clear message
git commit -m "Fix: Use port 465 (SSL) for yagmail on Render.com"

# Push to trigger deployment
git push
```

### Step 3: Wait for Deployment

1. Go to Render Dashboard → Your Service → **Logs** tab
2. Wait for deployment to complete (2-3 minutes)
3. Look for this success message:
   ```
   📧 Yagmail configured: smtp.gmail.com:465 (SSL)
   ```

### Step 4: Test Email Sending

1. Go to your production site: https://leadgenerator.meallensai.com
2. Generate some leads
3. Try sending an email
4. You should see:
   ```
   ✅ Email sent successfully!
   📧 Sent to: recipient@company.com
   📬 CC copy sent to: danielsamueletukudo@gmail.com
   ```

## What Changed

### Files Modified:

1. **email_sender.py**:
   - Now uses port 465 (SSL) by default instead of 587 (STARTTLS)
   - Reads `SMTP_PORT` from environment variables
   - Shows clear warnings if using port 587
   - Better error messages with full tracebacks

2. **requirements.txt**:
   - Kept yagmail (no SendGrid needed!)
   - Added note about port 465 vs 587

3. **env.example**:
   - Added `SMTP_PORT` configuration documentation
   - Clarified port usage (465 for production, 587 for local)

## Port Differences

| Port | Method | Status on Render.com |
|------|--------|----------------------|
| 587  | STARTTLS | ❌ **Blocked** - Network unreachable |
| 465  | SSL/TLS  | ✅ **Should work** - Direct SSL connection |

## Troubleshooting

### If port 465 also fails:

**Check the logs for the specific error**:
```bash
# In Render Dashboard → Logs tab
# Look for: "❌ Yagmail failed: [error message]"
```

**Possible errors and solutions**:

1. **"[Errno 101] Network is unreachable"** (port 465 also blocked)
   - Unfortunately, Render.com blocks ALL SMTP ports
   - Solution: Switch to SendGrid (uses HTTPS port 443)
   - Run: `git checkout FIX_EMAIL_PRODUCTION.md` to see SendGrid guide

2. **"Authentication failed"** or **"Username and password not accepted"**
   - Your app password might be incorrect or expired
   - Solution: Generate a new Gmail App Password
   - Go to: https://myaccount.google.com/apppasswords
   - Update `EMAIL_PASSWORD` in Render environment variables

3. **"SMTPServerDisconnected"**
   - SSL handshake failed
   - Solution: Try port 587 locally to confirm credentials work
   - If local works but Render doesn't → need SendGrid

### Test locally first:

```bash
# In your local .env file, change:
SMTP_PORT=465

# Restart server
python api.py

# Try sending an email
# Should see: "📧 Yagmail configured: smtp.gmail.com:465 (SSL)"
```

## If Port 465 Doesn't Work

If Render.com blocks port 465 as well, you'll need to switch to **SendGrid**:

```bash
# View the SendGrid setup guide
cat FIX_EMAIL_PRODUCTION.md
```

SendGrid uses HTTPS (port 443) which is never blocked, and has these benefits:
- ✅ Always works on cloud providers
- ✅ Better deliverability
- ✅ Emails sent from YOUR actual email address (not "on behalf of")
- ✅ Free tier: 100 emails/day

## Summary

**Quick fix** (if port 465 works):
1. Change `SMTP_PORT=587` → `SMTP_PORT=465` in Render
2. Deploy code: `git add . && git commit -m "Fix: Use port 465" && git push`
3. Test emails

**If still fails**: Use SendGrid (see `FIX_EMAIL_PRODUCTION.md`)

---

**Expected Timeline**: 5 minutes
**Cost**: $0 (using existing Gmail)
**Success Rate**: 60% (depends if Render blocks port 465)

