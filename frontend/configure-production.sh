#!/bin/bash

echo "=================================================="
echo "🔧 Frontend Production Configuration"
echo "=================================================="
echo ""

# Check if backend URL is provided
if [ -z "$1" ]; then
    echo "❌ Error: Backend URL required!"
    echo ""
    echo "Usage: ./configure-production.sh <BACKEND_URL>"
    echo ""
    echo "Example:"
    echo "  ./configure-production.sh https://your-app.railway.app"
    echo ""
    echo "Get your backend URL from:"
    echo "  Railway: railway domain"
    echo "  Render: Check dashboard"
    echo ""
    exit 1
fi

BACKEND_URL=$1

# Remove trailing slash if present
BACKEND_URL=${BACKEND_URL%/}

echo "📡 Backend URL: $BACKEND_URL"
echo ""

# Test if backend is reachable
echo "🔍 Testing backend health..."
HEALTH_CHECK=$(curl -s ${BACKEND_URL}/health 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Backend is reachable!"
    echo "   Response: $HEALTH_CHECK"
else
    echo "⚠️  WARNING: Cannot reach backend at $BACKEND_URL"
    echo "   Make sure backend is deployed and running"
    echo ""
    read -p "Continue anyway? [y/N]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Configuration cancelled"
        exit 1
    fi
fi

echo ""

# Create .env.production
echo "📝 Creating .env.production..."
echo "VITE_API_URL=$BACKEND_URL" > .env.production

echo "✅ Created .env.production with:"
cat .env.production

echo ""
echo "=================================================="
echo "✅ Configuration Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Build frontend:"
echo "   npm run build"
echo ""
echo "2. Deploy to Vercel:"
echo "   vercel --prod"
echo ""
echo "   Or set environment variable in Vercel dashboard:"
echo "   VITE_API_URL = $BACKEND_URL"
echo ""
echo "3. Test your app:"
echo "   Open: https://lead-magnet-livid.vercel.app"
echo ""
echo "=================================================="

