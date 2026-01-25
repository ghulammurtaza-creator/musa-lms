# Fly.io Deployment Quick Start Script (Windows)
# This script helps you deploy the backend to Fly.io

Write-Host "🚀 Musa LMS - Fly.io Deployment" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if flyctl is installed
if (-not (Get-Command fly -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Flyctl is not installed." -ForegroundColor Red
    Write-Host ""
    Write-Host "Install it with:" -ForegroundColor Yellow
    Write-Host "  powershell -Command `"iwr https://fly.io/install.ps1 -useb | iex`"" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Flyctl is installed" -ForegroundColor Green
Write-Host ""

# Check if logged in
try {
    fly auth whoami 2>&1 | Out-Null
    Write-Host "✅ Authenticated with Fly.io" -ForegroundColor Green
} catch {
    Write-Host "🔐 Please log in to Fly.io:" -ForegroundColor Yellow
    fly auth login
}

Write-Host ""

# Navigate to backend directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptPath\backend"

Write-Host "📋 Deployment Checklist:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Have you:"
Write-Host "  1. Created a Google Cloud project with OAuth credentials?"
Write-Host "  2. Obtained a Google Gemini API key?"
Write-Host "  3. Chosen a strong admin password?"
Write-Host "  4. Prepared your frontend URL?"
Write-Host ""

$proceed = Read-Host "Ready to proceed? (y/n)"
if ($proceed -ne "y" -and $proceed -ne "Y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Prompt for app name
Write-Host ""
$appName = Read-Host "Enter your app name (default: musa-lms-backend)"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = "musa-lms-backend"
}

# Check if app exists
$appList = fly apps list 2>&1 | Out-String
if ($appList -match $appName) {
    Write-Host "ℹ️  App '$appName' already exists. Will deploy to existing app." -ForegroundColor Yellow
} else {
    Write-Host "📦 Creating new app..." -ForegroundColor Cyan
    fly launch --name $appName --no-deploy --region iad
}

Write-Host ""
Write-Host "🗄️  Setting up PostgreSQL database..." -ForegroundColor Cyan
$dbName = "$appName-db"

# Check if database exists
$dbList = fly postgres list 2>&1 | Out-String
if ($dbList -match $dbName) {
    Write-Host "ℹ️  Database '$dbName' already exists." -ForegroundColor Yellow
} else {
    Write-Host "Creating PostgreSQL database..." -ForegroundColor Cyan
    fly postgres create --name $dbName --region iad
    fly postgres attach $dbName --app $appName
}

Write-Host ""
Write-Host "🔐 Setting up secrets..." -ForegroundColor Cyan
Write-Host ""

# Generate SECRET_KEY
$secretKey = -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })
$webhookSecret = -join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })

# Collect other secrets
$googleClientId = Read-Host "Google Client ID"
$googleClientSecret = Read-Host "Google Client Secret"
$geminiApiKey = Read-Host "Gemini API Key"
$adminEmail = Read-Host "Admin Email"
$adminPassword = Read-Host "Admin Password" -AsSecureString
$adminPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($adminPassword))
$adminName = Read-Host "Admin Name (default: System Administrator)"
if ([string]::IsNullOrWhiteSpace($adminName)) {
    $adminName = "System Administrator"
}
$frontendUrl = Read-Host "Frontend URL (e.g., https://your-app.vercel.app)"

$backendUrl = "https://$appName.fly.dev"

Write-Host ""
Write-Host "Setting secrets..." -ForegroundColor Cyan

fly secrets set `
  "SECRET_KEY=$secretKey" `
  "GOOGLE_CLIENT_ID=$googleClientId" `
  "GOOGLE_CLIENT_SECRET=$googleClientSecret" `
  "GOOGLE_WEBHOOK_SECRET=$webhookSecret" `
  "GEMINI_API_KEY=$geminiApiKey" `
  "ADMIN_EMAIL=$adminEmail" `
  "ADMIN_PASSWORD=$adminPasswordPlain" `
  "ADMIN_NAME=$adminName" `
  "FRONTEND_URL=$frontendUrl" `
  "BACKEND_URL=$backendUrl" `
  --app $appName

Write-Host ""
Write-Host "✅ Secrets configured" -ForegroundColor Green
Write-Host ""

# Deploy
Write-Host "🚀 Deploying application..." -ForegroundColor Cyan
fly deploy --app $appName

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Your backend is available at:" -ForegroundColor Cyan
Write-Host "   $backendUrl" -ForegroundColor White
Write-Host ""
Write-Host "📚 API Documentation:" -ForegroundColor Cyan
Write-Host "   $backendUrl/api/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Admin credentials:" -ForegroundColor Cyan
Write-Host "   Email: $adminEmail" -ForegroundColor White
Write-Host "   Password: $adminPasswordPlain" -ForegroundColor White
Write-Host "   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!" -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Update Google OAuth redirect URIs:"
Write-Host "      Add: $backendUrl/api/oauth/callback"
Write-Host "   2. Update frontend .env with:"
Write-Host "      NEXT_PUBLIC_API_URL=$backendUrl/api"
Write-Host "   3. Test the API: $backendUrl/api/docs"
Write-Host ""
Write-Host "📊 View logs: fly logs --app $appName" -ForegroundColor Cyan
Write-Host "🔍 Monitor: fly dashboard --app $appName" -ForegroundColor Cyan
Write-Host ""
