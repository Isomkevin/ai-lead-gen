# ⚡ Quick Start - Localhost Preview

Get your AI Lead Generator running on localhost in 5 minutes!

## 🎯 Prerequisites Check

✅ **Python 3.13.2** - Installed  
✅ **Node.js v22.17.0** - Installed

You're all set! Let's continue.

## 🚀 Quick Setup (3 Steps)

### Step 1: Initial Setup (One-time)

Run the setup script:

```bash
# Windows (double-click or run in PowerShell)
setup-localhost.bat

# OR manually:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

### Step 2: Configure API Key

1. Create `.env` file in project root (copy from `env.example`)
2. Add your Gemini API key:

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

**Get API key from:** https://aistudio.google.com/app/apikey

### Step 3: Start Both Servers

**Terminal 1 - Backend:**
```bash
# Windows
start-backend.bat

# OR manually:
venv\Scripts\activate
python api.py
```

**Terminal 2 - Frontend:**
```bash
# Windows
start-frontend.bat

# OR manually:
cd frontend
npm run dev
```

## 🌐 Access Your Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## ✅ Verify It's Working

1. Open http://localhost:3000 in your browser
2. Fill in the form:
   - Industry: `technology`
   - Number: `5`
   - Country: `USA`
3. Click "Generate Leads"
4. Wait for results!

## 🐛 Troubleshooting

### Backend won't start
- ✅ Check `.env` file exists and has `GEMINI_API_KEY`
- ✅ Virtual environment activated? (`venv\Scripts\activate`)
- ✅ Dependencies installed? (`pip install -r requirements.txt`)

### Frontend won't start
- ✅ In `frontend` directory?
- ✅ Dependencies installed? (`npm install`)
- ✅ Backend running on port 8000?

### Can't connect to API
- ✅ Backend running? Check http://localhost:8000/health
- ✅ Check browser console for errors
- ✅ CORS configured? Check `ALLOWED_ORIGINS` in `.env`

## 📝 Manual Setup (If Scripts Don't Work)

### Backend:
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key

# 5. Start server
python api.py
```

### Frontend:
```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

## 🎉 You're Done!

Your application is now running locally. Start generating leads!

---

**Need help?** Check `LOCALHOST_SETUP.md` for detailed instructions.

