#!/bin/bash

# Fly.io Deployment Quick Start Script
# This script helps you deploy the backend to Fly.io

echo "🚀 Musa LMS - Fly.io Deployment"
echo "================================"
echo ""

# Check if flyctl is installed
if ! command -v fly &> /dev/null; then
    echo "❌ Flyctl is not installed."
    echo ""
    echo "Please install it first:"
    echo "  Windows: powershell -Command \"iwr https://fly.io/install.ps1 -useb | iex\""
    echo "  Mac/Linux: curl -L https://fly.io/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ Flyctl is installed"
echo ""

# Check if logged in
if ! fly auth whoami &> /dev/null; then
    echo "🔐 Please log in to Fly.io:"
    fly auth login
fi

echo "✅ Authenticated with Fly.io"
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend"

echo "📋 Deployment Checklist:"
echo ""
echo "Have you:"
echo "  1. Created a Google Cloud project with OAuth credentials?"
echo "  2. Obtained a Google Gemini API key?"
echo "  3. Chosen a strong admin password?"
echo "  4. Prepared your frontend URL?"
echo ""

read -p "Ready to proceed? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Prompt for app name
echo ""
read -p "Enter your app name (default: musa-lms-backend): " APP_NAME
APP_NAME=${APP_NAME:-musa-lms-backend}

# Check if app exists
if fly apps list | grep -q "$APP_NAME"; then
    echo "ℹ️  App '$APP_NAME' already exists. Will deploy to existing app."
else
    echo "📦 Creating new app..."
    fly launch --name "$APP_NAME" --no-deploy --region iad
fi

echo ""
echo "🗄️  Setting up PostgreSQL database..."
DB_NAME="${APP_NAME}-db"

# Check if database exists
if fly postgres list | grep -q "$DB_NAME"; then
    echo "ℹ️  Database '$DB_NAME' already exists."
else
    echo "Creating PostgreSQL database..."
    fly postgres create --name "$DB_NAME" --region iad
    fly postgres attach "$DB_NAME" --app "$APP_NAME"
fi

echo ""
echo "🔐 Setting up secrets..."
echo ""

# Generate SECRET_KEY if not already set
SECRET_KEY=$(openssl rand -hex 32)
WEBHOOK_SECRET=$(openssl rand -hex 32)

# Collect other secrets
read -p "Google Client ID: " GOOGLE_CLIENT_ID
read -p "Google Client Secret: " GOOGLE_CLIENT_SECRET
read -p "Gemini API Key: " GEMINI_API_KEY
read -p "Admin Email: " ADMIN_EMAIL
read -sp "Admin Password: " ADMIN_PASSWORD
echo ""
read -p "Admin Name (default: System Administrator): " ADMIN_NAME
ADMIN_NAME=${ADMIN_NAME:-System Administrator}
read -p "Frontend URL (e.g., https://your-app.vercel.app): " FRONTEND_URL

BACKEND_URL="https://${APP_NAME}.fly.dev"

echo ""
echo "Setting secrets..."

fly secrets set \
  SECRET_KEY="$SECRET_KEY" \
  GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
  GOOGLE_CLIENT_SECRET="$GOOGLE_CLIENT_SECRET" \
  GOOGLE_WEBHOOK_SECRET="$WEBHOOK_SECRET" \
  GEMINI_API_KEY="$GEMINI_API_KEY" \
  ADMIN_EMAIL="$ADMIN_EMAIL" \
  ADMIN_PASSWORD="$ADMIN_PASSWORD" \
  ADMIN_NAME="$ADMIN_NAME" \
  FRONTEND_URL="$FRONTEND_URL" \
  BACKEND_URL="$BACKEND_URL" \
  --app "$APP_NAME"

echo ""
echo "✅ Secrets configured"
echo ""

# Deploy
echo "🚀 Deploying application..."
fly deploy --app "$APP_NAME"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Your backend is available at:"
echo "   $BACKEND_URL"
echo ""
echo "📚 API Documentation:"
echo "   ${BACKEND_URL}/api/docs"
echo ""
echo "🔐 Admin credentials:"
echo "   Email: $ADMIN_EMAIL"
echo "   Password: $ADMIN_PASSWORD"
echo "   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!"
echo ""
echo "📝 Next steps:"
echo "   1. Update Google OAuth redirect URIs:"
echo "      Add: ${BACKEND_URL}/api/oauth/callback"
echo "   2. Update frontend .env with:"
echo "      NEXT_PUBLIC_API_URL=${BACKEND_URL}/api"
echo "   3. Test the API: ${BACKEND_URL}/api/docs"
echo ""
echo "📊 View logs: fly logs --app $APP_NAME"
echo "🔍 Monitor: fly dashboard --app $APP_NAME"
echo ""
