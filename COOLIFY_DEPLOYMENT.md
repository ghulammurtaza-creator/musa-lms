# Coolify Deployment Guide

This guide will help you deploy Musa LMS on Coolify using Docker Compose.

## Prerequisites

- Coolify instance running and accessible
- GitHub repository connected to Coolify
- Domain names ready (optional but recommended)

## Deployment Steps

### 1. Create New Project in Coolify

1. Login to your Coolify dashboard
2. Click **+ New** → **Project**
3. Give it a name like `Musa LMS`

### 2. Add Docker Compose Service

1. Inside your project, click **+ New** → **Resource**
2. Select **Docker Compose**
3. Choose your GitHub repository
4. Select the `develop` branch
5. Coolify will auto-detect `docker-compose.yml`

### 3. Configure Environment Variables

In the Coolify service settings, add these environment variables:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-db-password-here
POSTGRES_DB=academy_db

# Backend Security
SECRET_KEY=generate-a-random-32-char-string-here-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth & Calendar
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_WEBHOOK_SECRET=your-webhook-secret-for-calendar

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# URLs (Set after deployment)
FRONTEND_URL=https://your-frontend-domain.com
BACKEND_URL=https://your-backend-domain.com

# Admin Auto-creation
CREATE_ADMIN=true
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourSecurePassword123!
ADMIN_NAME=System Administrator

# MinIO Storage
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=generate-strong-password-here
MINIO_BUCKET_NAME=academy-assignments
```

### 4. Configure Service Domains

Coolify will assign domains to your services. You need to expose:

#### Backend (app service)
- **Port:** 8000
- **Domain:** Set a custom domain like `api.yourdomain.com`
- **SSL:** Enable automatic SSL certificate

#### MinIO Console (optional)
- **Port:** 9001
- **Domain:** Set a custom domain like `storage.yourdomain.com`
- **SSL:** Enable automatic SSL certificate

### 5. Deploy

1. Click **Deploy** button
2. Wait for Coolify to build and start all services
3. Monitor logs for any errors

### 6. Verify Deployment

After deployment, check:

1. **Backend API:** Visit `https://api.yourdomain.com/docs`
   - You should see FastAPI Swagger documentation

2. **Health Check:** Visit `https://api.yourdomain.com/health`
   - Should return: `{"status": "healthy"}`

3. **Admin Login:**
   - Deploy frontend (Next.js) separately
   - Login with the admin credentials you set

### 7. Deploy Frontend

The frontend should be deployed separately on:
- **Vercel** (recommended for Next.js)
- **Netlify**
- **Another Coolify service** (static site or Node.js)

#### Frontend Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

### 8. Update Google OAuth Redirect URIs

In Google Cloud Console → APIs & Services → Credentials:

Add authorized redirect URI:
```
https://api.yourdomain.com/api/oauth/callback
```

## Important Notes

### Port Configuration
- Docker Compose uses `expose` instead of `ports` to avoid conflicts
- Coolify handles external port routing automatically
- Services communicate internally via Docker network

### Persistent Data
Volumes are automatically managed by Coolify:
- `postgres_data` - Database storage
- `minio_data` - File uploads storage

### Database Migrations
Database migrations run automatically on startup via `fly-entrypoint.sh`

### Admin User
Admin user is auto-created on first startup if `CREATE_ADMIN=true`

## Troubleshooting

### Service won't start
1. Check Coolify deployment logs
2. Verify all environment variables are set
3. Check database connection: `docker exec academy_backend env | grep DATABASE_URL`

### Database connection errors
1. Ensure `db` service is healthy before `app` starts
2. Check DATABASE_URL uses correct credentials
3. Verify postgres service is running: `docker ps`

### MinIO access issues
1. Check MINIO_ENDPOINT uses internal service name: `minio:9000`
2. Verify MINIO_ACCESS_KEY and MINIO_SECRET_KEY match between services
3. Check bucket is created (MinIO console)

### OAuth not working
1. Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct
2. Check redirect URI in Google Console matches your domain
3. Ensure BACKEND_URL and FRONTEND_URL are set correctly

## Environment Variable Generation

Generate secure values:

```bash
# SECRET_KEY (32 chars minimum)
openssl rand -hex 32

# Database password
openssl rand -base64 24

# MinIO secret key
openssl rand -base64 24

# Webhook secret
openssl rand -hex 16
```

## Updating Deployment

To update your deployment:

1. Push changes to GitHub `develop` branch
2. Coolify auto-deploys on git push (if enabled)
3. Or manually click **Deploy** in Coolify

## Monitoring

Monitor your services in Coolify:
- **Logs:** Real-time container logs
- **Resources:** CPU, memory usage
- **Health:** Service status and uptime

## Backup

Coolify provides backup options for volumes:
1. Go to project settings
2. Configure automated backups for `postgres_data` volume
3. Set backup schedule and retention

---

For local development, use `local-start.sh` (Linux/Mac) or `local-start.bat` (Windows).
