# 🚀 Localhost Setup Guide

Complete guide to run the AI Lead Generator on your local machine.

## 📋 Prerequisites

- **Python 3.11+** (check with `python --version`)
- **Node.js 18+** (check with `node --version`)
- **npm** or **yarn** (comes with Node.js)
- **Git** (for cloning if needed)

## 🔧 Step 1: Backend Setup

### 1.1 Install Python Dependencies

```bash
# Navigate to project root
cd ai-lead-gen

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 1.2 Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example file
cp env.example .env
```

Edit `.env` and add your API keys:

```bash
# REQUIRED: Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# OPTIONAL: Email Configuration (choose one)
# Option 1: SendGrid (Recommended)
# SENDGRID_API_KEY=SG.your_sendgrid_api_key_here

# Option 2: Gmail with Yagmail
# EMAIL_USER=your.email@gmail.com
# EMAIL_PASSWORD=your_16_char_app_password

# OPTIONAL: AI Avatar/Voice (ElevenLabs)
# ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Development Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000
ENVIRONMENT=development
```

**Get API Keys:**
- **Gemini API**: https://aistudio.google.com/app/apikey (Required)
- **ElevenLabs**: https://elevenlabs.io (Optional - for voice features)
- **SendGrid**: https://sendgrid.com (Optional - for email)

### 1.3 Start Backend Server

```bash
# Make sure you're in project root and virtual environment is activated
python api.py
```

Backend will start on: **http://localhost:8000**

You should see:
```
🚀 Lead Generator API Starting...
📚 API Documentation: http://localhost:8000/docs
💚 Health Check: http://localhost:8000/health
```

**Keep this terminal open!**

## 🎨 Step 2: Frontend Setup

### 2.1 Install Node Dependencies

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 2.2 Configure Frontend (Optional)

The frontend is already configured to proxy to `http://localhost:8000` in development.

If you need to change the API URL, create `frontend/.env.local`:

```bash
# frontend/.env.local
VITE_API_URL=http://localhost:8000
```

### 2.3 Start Frontend Development Server

```bash
# Make sure you're in frontend directory
npm run dev
```

Frontend will start on: **http://localhost:3000**

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

## ✅ Step 3: Verify Setup

### 3.1 Check Backend

Open in browser:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 3.2 Check Frontend

Open in browser:
- **Frontend**: http://localhost:3000

### 3.3 Test the Application

1. Go to http://localhost:3000
2. Fill in the form:
   - Industry: `technology`
   - Number: `5`
   - Country: `USA`
   - Enable Web Scraping: ✅
   - Business Intelligence Analysis: ✅
3. Click "Generate Leads"
4. Wait for results (10-30 seconds for AI, 2-5 minutes with scraping)

## 🐛 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Change port in api.py or set environment variable
export PORT=8001
python api.py
```

**Module not found errors:**
```bash
# Make sure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

**GEMINI_API_KEY error:**
- Check `.env` file exists in project root
- Verify API key is correct (no extra spaces)
- Restart backend after changing .env

### Frontend Issues

**Port 3000 already in use:**
```bash
# Vite will automatically use next available port
# Or change in vite.config.js
```

**API connection errors:**
- Make sure backend is running on http://localhost:8000
- Check browser console for errors
- Verify CORS settings in backend

**npm install fails:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Common Issues

**"Cannot connect to API":**
- ✅ Backend running? Check http://localhost:8000/health
- ✅ Frontend proxy configured? Check vite.config.js
- ✅ CORS allowed? Check ALLOWED_ORIGINS in .env

**"GEMINI_API_KEY not configured":**
- ✅ .env file exists in project root?
- ✅ API key is correct?
- ✅ Restarted backend after adding key?

**"Module not found":**
- ✅ Virtual environment activated?
- ✅ Installed requirements.txt?
- ✅ Node modules installed in frontend?

## 📝 Quick Start Commands

### Windows (PowerShell)

```powershell
# Terminal 1 - Backend
cd ai-lead-gen
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python api.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

### Mac/Linux

```bash
# Terminal 1 - Backend
cd ai-lead-gen
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

## 🎯 Development Workflow

1. **Start Backend** (Terminal 1)
   ```bash
   python api.py
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

4. **Make Changes**
   - Backend: Changes auto-reload (if reload enabled)
   - Frontend: Hot module replacement (HMR) enabled

## 🔍 Testing Endpoints

### Using Browser

- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Generate leads (example)
curl -X POST http://localhost:8000/api/v1/leads/generate \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "technology",
    "number": 5,
    "country": "USA",
    "enable_web_scraping": false
  }'
```

## 📦 Project Structure

```
ai-lead-gen/
├── api.py                      # Backend API server
├── business_intelligence.py     # BI analysis module
├── avatar_service.py           # Voice/Avatar service
├── generate_health_insurance.py # AI lead generation
├── web_scraper.py              # Web scraping
├── email_sender.py             # Email service
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── .env.local              # Frontend env (optional)
└── README.md
```

## 🎉 You're Ready!

Your application should now be running:
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:3000
- ✅ API Docs: http://localhost:8000/docs

Start generating leads! 🚀

## 💡 Tips

1. **Keep both terminals open** - Backend and Frontend need to run simultaneously
2. **Check console logs** - Both backend and frontend show helpful error messages
3. **Use API docs** - http://localhost:8000/docs for testing endpoints
4. **Enable Business Intelligence** - Get lead scores and better insights
5. **Start small** - Test with 5 leads first, then scale up

## 🆘 Still Having Issues?

1. Check all prerequisites are installed
2. Verify API keys are correct
3. Check both servers are running
4. Review error messages in console
5. Check firewall isn't blocking ports
6. Try restarting both servers

---

**Happy coding!** 🎊

