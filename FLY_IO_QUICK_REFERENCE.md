# Fly.io Backend Deployment - Quick Reference

## 🚀 Quick Deploy (Windows)

```powershell
# Run the automated deployment script
.\deploy-to-fly.ps1
```

## 🚀 Quick Deploy (Mac/Linux)

```bash
# Make script executable
chmod +x deploy-to-fly.sh

# Run the automated deployment script
./deploy-to-fly.sh
```

## 📋 Manual Deployment Steps

### 1. Install Flyctl

**Windows:**
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Authenticate

```bash
fly auth login
```

### 3. Create App & Database

```bash
cd backend

# Create app
fly launch --name musa-lms-backend --no-deploy --region iad

# Create PostgreSQL
fly postgres create --name musa-lms-db --region iad
fly postgres attach musa-lms-db --app musa-lms-backend
```

### 4. Set Secrets

```bash
fly secrets set \
  SECRET_KEY="$(openssl rand -hex 32)" \
  GOOGLE_CLIENT_ID="your-client-id" \
  GOOGLE_CLIENT_SECRET="your-client-secret" \
  GOOGLE_WEBHOOK_SECRET="$(openssl rand -hex 32)" \
  GEMINI_API_KEY="your-gemini-key" \
  ADMIN_EMAIL="admin@example.com" \
  ADMIN_PASSWORD="YourSecurePass123!" \
  ADMIN_NAME="System Administrator" \
  FRONTEND_URL="https://your-frontend.vercel.app" \
  BACKEND_URL="https://musa-lms-backend.fly.dev"
```

### 5. Deploy

```bash
fly deploy
```

### 6. Verify

```bash
fly open /api/docs
fly logs
fly status
```

## 🔧 Common Commands

```bash
# View logs
fly logs

# SSH into app
fly ssh console

# View secrets
fly secrets list

# Update a secret
fly secrets set KEY=value

# Scale memory
fly scale memory 1024

# Restart app
fly apps restart

# View status
fly status

# Open dashboard
fly dashboard

# View releases
fly releases

# Rollback
fly releases rollback
```

## 🗄️ Database Commands

```bash
# Connect to database
fly postgres connect -a musa-lms-db

# View database info
fly postgres db list -a musa-lms-db

# Create backup
fly postgres backup create -a musa-lms-db

# View backups
fly postgres backup list -a musa-lms-db
```

## 📍 Important URLs

After deployment, you'll have:

- **Backend API**: `https://musa-lms-backend.fly.dev`
- **API Docs**: `https://musa-lms-backend.fly.dev/api/docs`
- **Dashboard**: `https://fly.io/apps/musa-lms-backend`

## 🔐 Required Secrets

| Secret | How to Get |
|--------|------------|
| SECRET_KEY | `openssl rand -hex 32` |
| GOOGLE_CLIENT_ID | Google Cloud Console |
| GOOGLE_CLIENT_SECRET | Google Cloud Console |
| GOOGLE_WEBHOOK_SECRET | `openssl rand -hex 32` |
| GEMINI_API_KEY | Google AI Studio |
| ADMIN_EMAIL | Your choice |
| ADMIN_PASSWORD | Strong password (change after first login!) |
| FRONTEND_URL | Your deployed frontend URL |
| BACKEND_URL | `https://YOUR-APP.fly.dev` |

## ⚙️ Post-Deployment Setup

### 1. Update Google OAuth

Add to **Authorized redirect URIs** in Google Cloud Console:
```
https://musa-lms-backend.fly.dev/api/oauth/callback
```

### 2. Update Frontend Environment

```env
NEXT_PUBLIC_API_URL=https://musa-lms-backend.fly.dev/api
```

### 3. Test the Deployment

1. Visit `https://musa-lms-backend.fly.dev/api/docs`
2. Try the `/api/auth/login` endpoint with admin credentials
3. Connect Google Calendar from admin settings

## 🐛 Troubleshooting

### App won't start
```bash
fly logs
fly ssh console
```

### Database issues
```bash
fly secrets list  # Check DATABASE_URL is set
fly postgres connect -a musa-lms-db
```

### Memory errors
```bash
fly scale memory 1024
```

### Migration issues
```bash
fly ssh console
cd /app
alembic upgrade head
```

### Check environment
```bash
fly ssh console
printenv | grep -E 'DATABASE|SECRET|GOOGLE'
```

## 💰 Cost (Free Tier)

Fly.io free tier includes:
- ✅ 3 shared-cpu-1x VMs (256MB RAM)
- ✅ 160GB bandwidth/month
- ✅ PostgreSQL (3GB storage)

**Your setup uses:**
- 1 VM (512MB) - auto-scales to 0 when idle
- PostgreSQL Development tier

**Stays free if:**
- You use auto-stop (already configured)
- Stay under 160GB bandwidth
- Use single VM

## 📊 Monitoring

```bash
# Real-time logs
fly logs

# Metrics dashboard
fly dashboard

# App status
fly status

# Check health
fly checks list
```

## 🔄 Updates

After making code changes:

```bash
cd backend
git pull  # if using git
fly deploy
```

Or set up auto-deploy with GitHub Actions (see FLY_IO_DEPLOYMENT.md).

## 🆘 Support

- **Fly.io Docs**: https://fly.io/docs/
- **Community**: https://community.fly.io/
- **Status**: https://status.flyio.net/

## ✅ Deployment Checklist

- [ ] Installed flyctl
- [ ] Authenticated with Fly.io
- [ ] Created app
- [ ] Created PostgreSQL database
- [ ] Set all required secrets
- [ ] Deployed successfully
- [ ] Updated Google OAuth redirect URIs
- [ ] Updated frontend environment variables
- [ ] Tested API endpoints
- [ ] Changed admin password
- [ ] Set up monitoring

## 📱 Next: Deploy Frontend

Consider these options for frontend:
- **Vercel** (recommended for Next.js)
- **Netlify**
- **Fly.io** (same platform as backend)

See frontend deployment guides for each platform.
