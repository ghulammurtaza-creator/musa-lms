# Railway Deployment - Quick Reference

## 🚀 Fastest Way: Deploy via Dashboard

1. **Go to**: https://railway.app/new
2. **Click**: "Deploy from GitHub repo"
3. **Select**: Your repository
4. **Add**: PostgreSQL database (click "+ New" → "Database" → "PostgreSQL")
5. **Set Variables**: (See below)
6. **Generate Domain**: Settings → Domains → "Generate Domain"
7. **Done!** 🎉

## 📋 Required Environment Variables

```env
SECRET_KEY=<run: openssl rand -hex 32>
GOOGLE_CLIENT_ID=<from Google Cloud Console>
GOOGLE_CLIENT_SECRET=<from Google Cloud Console>
GOOGLE_WEBHOOK_SECRET=<run: openssl rand -hex 32>
GEMINI_API_KEY=<from Google AI Studio>
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=YourSecurePassword123!
ADMIN_NAME=System Administrator
FRONTEND_URL=https://your-frontend.vercel.app
BACKEND_URL=${{RAILWAY_PUBLIC_DOMAIN}}
CREATE_ADMIN=true
```

**Note**: `DATABASE_URL` is automatically set by Railway PostgreSQL

## 🔧 CLI Quick Start

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Navigate to backend
cd backend

# Create project
railway init

# Add PostgreSQL
railway add --database postgresql

# Set variables (example)
railway variables set SECRET_KEY="$(openssl rand -hex 32)"
railway variables set ADMIN_EMAIL="admin@example.com"
# ... set all other required variables

# Deploy
railway up

# Get your URL
railway domain
```

## 📊 Common Commands

```bash
# View logs
railway logs

# Restart service
railway restart

# Connect to database
railway connect postgres

# View variables
railway variables

# Set variable
railway variables set KEY=value

# Open in browser
railway open
```

## ✅ Post-Deployment Checklist

- [ ] Backend deployed successfully
- [ ] PostgreSQL database created and connected
- [ ] All environment variables set
- [ ] Domain generated
- [ ] Google OAuth redirect URI updated: `https://YOUR-APP.up.railway.app/api/oauth/callback`
- [ ] Frontend `.env` updated: `NEXT_PUBLIC_API_URL=https://YOUR-APP.up.railway.app/api`
- [ ] Tested API: `https://YOUR-APP.up.railway.app/api/docs`
- [ ] Admin login works
- [ ] Admin password changed

## 💰 Free Tier

- **$5 credit/month** (~500 hours)
- Perfect for development
- No credit card required
- Auto-scales to zero when idle

## 🔗 Important URLs

After deployment:
- **API**: `https://your-app.up.railway.app`
- **API Docs**: `https://your-app.up.railway.app/api/docs`
- **Dashboard**: https://railway.app/dashboard

## 🐛 Quick Troubleshooting

**Build failed?**
```bash
railway logs --deployment
```

**Can't connect to database?**
```bash
railway variables get DATABASE_URL
```

**App won't start?**
- Check all required variables are set
- Check logs: `railway logs`

**Need more memory?**
- Dashboard → Service → Settings → Resources

## 📚 Full Guide

See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for complete instructions.

## 🆚 Railway vs Fly.io

**Railway is better for:**
- ✅ Simpler setup (no complex config files)
- ✅ Better dashboard/UI
- ✅ Easier database management
- ✅ GitHub auto-deploy
- ✅ Faster deployments

**Both are great!** Railway is just easier to get started with.
