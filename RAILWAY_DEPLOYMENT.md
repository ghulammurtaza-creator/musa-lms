# Railway Deployment Guide - Musa LMS Backend

Railway is simpler than Fly.io and perfect for this project! Here's how to deploy.

## Why Railway?

- ✅ **Simpler setup** - Auto-detects everything
- ✅ **$5/month free credit** - Enough for small projects
- ✅ **Built-in PostgreSQL** - One-click database
- ✅ **GitHub integration** - Auto-deploy on push
- ✅ **Great dashboard** - Easy monitoring
- ✅ **No credit card** required for free tier

## Prerequisites

1. **Railway Account**: Sign up at https://railway.app (use GitHub login)
2. **GitHub Repository** (recommended) or Railway CLI

## Method 1: Deploy via GitHub (Recommended)

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/musa-lms.git
git push -u origin main
```

### Step 2: Create Project on Railway

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will detect the backend automatically

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically sets `DATABASE_URL` environment variable

### Step 4: Configure Environment Variables

In Railway dashboard, go to your backend service → **Variables** tab:

```env
# Required Variables
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_WEBHOOK_SECRET=your-webhook-secret
GEMINI_API_KEY=your-gemini-api-key

# Admin Settings
CREATE_ADMIN=true
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=YourSecurePassword123!
ADMIN_NAME=System Administrator

# URLs (Railway auto-generates these)
FRONTEND_URL=https://your-frontend-url.vercel.app
BACKEND_URL=${{RAILWAY_PUBLIC_DOMAIN}}

# Algorithm
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Note**: Railway provides `RAILWAY_PUBLIC_DOMAIN` which you can reference as `${{RAILWAY_PUBLIC_DOMAIN}}`

### Step 5: Deploy

1. Click **"Deploy"** or push to GitHub
2. Railway will build and deploy automatically
3. Get your URL from the **"Settings"** → **"Domains"** section

### Step 6: Generate Domain

1. Go to **Settings** → **Domains**
2. Click **"Generate Domain"**
3. You'll get a URL like: `musa-lms-backend.up.railway.app`

## Method 2: Deploy via Railway CLI

### Step 1: Install Railway CLI

**Windows (PowerShell):**
```powershell
iwr https://railway.app/install.ps1 | iex
```

**Mac/Linux:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Step 2: Login

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd backend

# Create new project
railway init

# Link to existing project (if created via web)
railway link
```

### Step 4: Add PostgreSQL

```bash
railway add --database postgresql
```

This automatically:
- Creates a PostgreSQL instance
- Sets `DATABASE_URL` environment variable
- Connects it to your service

### Step 5: Set Environment Variables

```bash
# Set variables one by one
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set GOOGLE_CLIENT_ID="your-client-id"
railway variables set GOOGLE_CLIENT_SECRET="your-client-secret"
railway variables set GOOGLE_WEBHOOK_SECRET="$(openssl rand -hex 32)"
railway variables set GEMINI_API_KEY="your-gemini-key"
railway variables set ADMIN_EMAIL="admin@example.com"
railway variables set ADMIN_PASSWORD="YourSecure123!"
railway variables set ADMIN_NAME="System Administrator"
railway variables set CREATE_ADMIN="true"
railway variables set ALGORITHM="HS256"
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES="30"

# Frontend URL (update later with actual URL)
railway variables set FRONTEND_URL="http://localhost:3000"
```

### Step 6: Deploy

```bash
railway up
```

That's it! Railway will:
- Build your Docker image
- Run database migrations
- Create admin user
- Start the service

### Step 7: Get Your URL

```bash
railway domain
```

Or check in the Railway dashboard.

## Configuration Files

Railway automatically detects:
- ✅ `Dockerfile` in backend directory
- ✅ Python/FastAPI project
- ✅ Port 8000 from Dockerfile
- ✅ Database connection from `DATABASE_URL`

Optional `railway.toml` is already created for custom settings.

## Post-Deployment

### 1. Update Google OAuth

Add to **Authorized redirect URIs** in Google Cloud Console:
```
https://your-app.up.railway.app/api/oauth/callback
```

### 2. Update Frontend Environment

```env
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app/api
```

### 3. Update Backend URL Variable

In Railway dashboard, update:
```env
BACKEND_URL=https://your-app.up.railway.app
```

### 4. Test the API

Visit: `https://your-app.up.railway.app/api/docs`

## Managing Your Deployment

### View Logs

**Dashboard**: Click on your service → **"Deployments"** → Click deployment → **"View Logs"**

**CLI**:
```bash
railway logs
```

### Restart Service

**Dashboard**: Service → **"Settings"** → **"Restart"**

**CLI**:
```bash
railway restart
```

### Update Variables

**Dashboard**: Service → **"Variables"** → Edit

**CLI**:
```bash
railway variables set KEY=value
```

### Rollback

**Dashboard**: **"Deployments"** → Click old deployment → **"Redeploy"**

### Scale/Change Plan

**Dashboard**: Project Settings → **"Usage"** → **"Upgrade"**

## Automatic Deployments

Railway automatically deploys when you:
- Push to your connected GitHub branch
- Manually trigger from dashboard
- Use `railway up` command

To disable auto-deploy:
1. Service → **"Settings"**
2. Toggle **"Automatic Deployments"** off

## Database Management

### Connect to Database

**Get connection string:**
```bash
railway variables get DATABASE_URL
```

**Connect via CLI:**
```bash
railway connect postgres
```

**Connect via GUI tool:**
Use the `DATABASE_URL` from variables in tools like TablePlus, pgAdmin, or DBeaver.

### Backups

Railway Pro plan includes automatic backups. For free tier:
1. Use `railway connect postgres`
2. Run manual backup: `pg_dump > backup.sql`

## Environment Variables Reference

| Variable | Required | Example | Notes |
|----------|----------|---------|-------|
| DATABASE_URL | Auto-set | postgresql://... | Set by Railway PostgreSQL |
| SECRET_KEY | Yes | 64-char hex | `openssl rand -hex 32` |
| GOOGLE_CLIENT_ID | Yes | xxx.apps.googleusercontent.com | From Google Cloud |
| GOOGLE_CLIENT_SECRET | Yes | GOCSPX-xxx | From Google Cloud |
| GOOGLE_WEBHOOK_SECRET | Yes | random string | `openssl rand -hex 32` |
| GEMINI_API_KEY | Yes | AIza... | From Google AI Studio |
| ADMIN_EMAIL | Yes | admin@example.com | Your admin email |
| ADMIN_PASSWORD | Yes | SecurePass123! | Strong password |
| ADMIN_NAME | No | Administrator | Display name |
| FRONTEND_URL | Yes | https://yourapp.vercel.app | Your frontend URL |
| BACKEND_URL | Yes | ${{RAILWAY_PUBLIC_DOMAIN}} | Railway auto-fills |
| CREATE_ADMIN | No | true | Auto-create admin on first deploy |
| ALGORITHM | No | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 30 | Token expiry |

## Cost & Free Tier

**Free Tier (Starter Plan):**
- $5 of usage per month
- ~500 hours of usage
- Perfect for development and small projects
- No credit card required

**Usage Calculation:**
- Backend: ~$0.01/hour = ~$7.20/month (scales to zero when idle)
- PostgreSQL: ~$0.01/hour = ~$7.20/month (always on)

**Tips to Stay Free:**
- Use one service
- Set up auto-sleep (Railway does this automatically)
- Monitor usage in dashboard

**Upgrade if needed:**
- Hobby Plan: $5/month + usage
- Pro Plan: $20/month + usage

## Troubleshooting

### Build Fails

**Check logs:**
```bash
railway logs --deployment
```

**Common issues:**
- Missing `Dockerfile` - Already exists ✓
- Wrong directory - Ensure Railway points to `backend` folder
- Build timeout - Increase in settings if needed

### Database Connection Failed

**Check DATABASE_URL is set:**
```bash
railway variables get DATABASE_URL
```

**Ensure PostgreSQL is running:**
- Dashboard → Database service should be green

### App Won't Start

**Check environment variables:**
```bash
railway variables
```

**Ensure all required variables are set**

**Check start command:**
Should be `/app/fly-entrypoint.sh` or auto-detected from Dockerfile

### Port Issues

Railway auto-detects port 8000 from `EXPOSE 8000` in Dockerfile. No configuration needed.

### Memory Issues

**Upgrade memory:**
- Service → **"Settings"** → **"Resources"**
- Increase memory limit

## Custom Domain (Optional)

1. Buy domain (Namecheap, Google Domains, etc.)
2. Railway → Service → **"Settings"** → **"Domains"**
3. Click **"Custom Domain"**
4. Add your domain
5. Update DNS records as shown

## GitHub Actions (Optional)

Railway auto-deploys from GitHub, but you can add custom actions:

`.github/workflows/railway.yml`:
```yaml
name: Deploy to Railway
on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway
        run: npm i -g @railway/cli
        
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

Get token: `railway login --browserless`

## Monitoring

**Built-in Metrics:**
- Dashboard → Service → **"Metrics"**
- Shows: CPU, Memory, Network

**Logs:**
- Real-time logs in dashboard
- `railway logs` via CLI
- Filter by time, service, level

**Alerts:**
- Pro plan includes usage alerts
- Set up in Project Settings

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Add PostgreSQL database
3. ✅ Set environment variables
4. ✅ Generate domain
5. ✅ Update Google OAuth redirect URIs
6. ✅ Deploy frontend (Vercel recommended)
7. ✅ Update frontend environment variables
8. ✅ Test the integration
9. ✅ Change admin password

## Useful Links

- **Railway Dashboard**: https://railway.app/dashboard
- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway
- **Status Page**: https://status.railway.app/

## Support

- **Documentation**: https://docs.railway.app/
- **Community**: https://discord.gg/railway
- **Examples**: https://railway.app/templates

Railway is simpler and faster than Fly.io - you'll be deployed in minutes! 🚀
