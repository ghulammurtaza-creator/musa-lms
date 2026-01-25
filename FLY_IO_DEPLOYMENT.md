# Deployment Guide - Fly.io Backend

This guide walks you through deploying the Musa LMS backend to Fly.io.

## Prerequisites

1. **Fly.io Account**: Sign up at https://fly.io/
2. **Flyctl CLI**: Install from https://fly.io/docs/hands-on/install-flyctl/
3. **GitHub Repository** (optional but recommended for CI/CD)

## Step 1: Install and Authenticate

```bash
# Install flyctl (if not already installed)
# Windows (PowerShell):
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Linux/Mac:
curl -L https://fly.io/install.sh | sh

# Authenticate
fly auth login
```

## Step 2: Initialize Fly.io App

```bash
cd backend

# Launch the app (this creates the app on Fly.io)
fly launch --no-deploy

# When prompted:
# - App name: musa-lms-backend (or your preferred name)
# - Region: Choose closest to your users
# - Add PostgreSQL? YES (select Development - Single node)
# - Add Redis? NO
# - Deploy now? NO
```

This creates a `fly.toml` file (we already have one prepared).

## Step 3: Create PostgreSQL Database

If you didn't add PostgreSQL during launch:

```bash
# Create a Postgres database
fly postgres create --name musa-lms-db --region iad

# Attach it to your app
fly postgres attach musa-lms-db --app musa-lms-backend
```

This automatically sets the `DATABASE_URL` secret.

## Step 4: Set Required Secrets

Fly.io uses secrets for sensitive environment variables:

```bash
# Required secrets
fly secrets set SECRET_KEY="$(openssl rand -hex 32)" \
  GOOGLE_CLIENT_ID="your-google-client-id" \
  GOOGLE_CLIENT_SECRET="your-google-client-secret" \
  GOOGLE_WEBHOOK_SECRET="$(openssl rand -hex 32)" \
  GEMINI_API_KEY="your-gemini-api-key" \
  ADMIN_EMAIL="admin@yourdomain.com" \
  ADMIN_PASSWORD="YourSecurePassword123!" \
  ADMIN_NAME="System Administrator" \
  FRONTEND_URL="https://your-frontend-url.com" \
  BACKEND_URL="https://musa-lms-backend.fly.dev"
```

**Important**: Replace:
- `your-google-client-id` with actual Google OAuth Client ID
- `your-google-client-secret` with actual Google OAuth Client Secret
- `your-gemini-api-key` with actual Gemini API key
- `admin@yourdomain.com` with your admin email
- `YourSecurePassword123!` with a strong password
- `https://your-frontend-url.com` with your actual frontend URL

## Step 5: Update Dockerfile for Production

The current Dockerfile uses `--reload` which is for development. Let's create a production version:

```bash
# Already configured in the existing Dockerfile, but verify:
# The CMD should be:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Update the Dockerfile:

```dockerfile
# Use fly-entrypoint.sh for migrations
CMD ["/app/fly-entrypoint.sh"]
```

## Step 6: Update Google OAuth Redirect URIs

Add your Fly.io URL to Google Cloud Console:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to APIs & Services → Credentials
4. Edit your OAuth 2.0 Client ID
5. Add to "Authorized redirect URIs":
   ```
   https://musa-lms-backend.fly.dev/api/oauth/callback
   ```

## Step 7: Handle MinIO/File Storage

Fly.io doesn't include MinIO. You have two options:

### Option A: Use Tigris (Recommended - Fly.io's object storage)

```bash
# Create a Tigris bucket
fly storage create --name musa-lms-storage

# This will set BUCKET_URL automatically
```

Update your code to use Tigris instead of MinIO (or use S3-compatible API).

### Option B: Disable File Uploads Temporarily

Update the secrets to skip MinIO:

```bash
fly secrets set MINIO_ENDPOINT="" \
  MINIO_ACCESS_KEY="" \
  MINIO_SECRET_KEY=""
```

## Step 8: Deploy

```bash
# Deploy the application
fly deploy

# Monitor deployment
fly logs

# Check status
fly status
```

## Step 9: Run Database Migrations

Migrations run automatically via the entrypoint script, but you can run them manually:

```bash
# SSH into the machine
fly ssh console

# Run migrations manually if needed
alembic upgrade head

# Exit
exit
```

## Step 10: Verify Deployment

```bash
# Open your app
fly open

# Should redirect to https://musa-lms-backend.fly.dev

# Check API docs
fly open /api/docs

# View logs
fly logs

# Check app status
fly status
```

## Step 11: Update Frontend Environment

Update your frontend `.env.local` or production environment:

```env
NEXT_PUBLIC_API_URL=https://musa-lms-backend.fly.dev/api
```

## Scaling and Monitoring

### Scale Resources

```bash
# View current scale
fly scale show

# Scale memory
fly scale memory 1024

# Scale to 2 VMs (for high availability)
fly scale count 2

# Auto-scale
fly autoscale set min=1 max=3
```

### Monitor Application

```bash
# View real-time logs
fly logs

# View metrics
fly dashboard

# SSH into app
fly ssh console

# Check database
fly postgres connect -a musa-lms-db
```

## Continuous Deployment (Optional)

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Fly.io
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
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        working-directory: ./backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Get your API token:
```bash
fly tokens create deploy
```

Add it to GitHub Secrets as `FLY_API_TOKEN`.

## Troubleshooting

### App Won't Start

```bash
# Check logs
fly logs

# SSH into the machine
fly ssh console

# Check environment variables
printenv | grep -E 'DATABASE|SECRET|GOOGLE'
```

### Database Connection Issues

```bash
# Verify DATABASE_URL is set
fly secrets list

# Check Postgres status
fly postgres connect -a musa-lms-db
```

### Memory Issues

```bash
# Scale up memory
fly scale memory 1024

# Or use a larger VM
fly scale vm shared-cpu-2x --memory 2048
```

### Migrations Not Running

```bash
# SSH into the app
fly ssh console

# Run migrations manually
cd /app
alembic upgrade head
```

## Cost Optimization

Fly.io free tier includes:
- 3 shared-cpu-1x VMs (256MB RAM each)
- 160GB outbound data transfer
- PostgreSQL: 3GB storage, 1 shared CPU

To stay within free tier:
- Use 1 VM with auto-stop enabled (already configured)
- Use Development Postgres (3GB limit)
- Optimize database queries to reduce transfer

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | Auto-set by Postgres addon |
| SECRET_KEY | Yes | JWT secret (generate with openssl) |
| GOOGLE_CLIENT_ID | Yes | Google OAuth client ID |
| GOOGLE_CLIENT_SECRET | Yes | Google OAuth client secret |
| GOOGLE_WEBHOOK_SECRET | Yes | Webhook validation secret |
| GEMINI_API_KEY | Yes | Google Gemini API key |
| ADMIN_EMAIL | Yes | Initial admin email |
| ADMIN_PASSWORD | Yes | Initial admin password |
| ADMIN_NAME | No | Admin display name |
| FRONTEND_URL | Yes | Your frontend URL |
| BACKEND_URL | Yes | Your backend URL (Fly.io URL) |

## Next Steps

1. Deploy frontend (Vercel, Netlify, or Fly.io)
2. Update CORS settings in `main.py` to allow your frontend domain
3. Set up custom domain (optional)
4. Configure SSL/TLS (automatic with Fly.io)
5. Set up monitoring and alerts

## Custom Domain (Optional)

```bash
# Add custom domain
fly certs create api.yourdomain.com

# Follow DNS instructions
# Add CNAME record: api.yourdomain.com -> musa-lms-backend.fly.dev

# Verify
fly certs show api.yourdomain.com
```

## Useful Commands

```bash
# View all apps
fly apps list

# View app info
fly info

# View secrets
fly secrets list

# Update a secret
fly secrets set KEY=VALUE

# View releases
fly releases

# Rollback to previous release
fly releases rollback

# Restart app
fly apps restart

# Destroy app (careful!)
fly apps destroy musa-lms-backend
```

## Support

- Fly.io Docs: https://fly.io/docs/
- Fly.io Community: https://community.fly.io/
- FastAPI Docs: https://fastapi.tiangolo.com/

## Security Checklist

- [ ] Changed default admin password
- [ ] Set strong SECRET_KEY
- [ ] Updated Google OAuth redirect URIs
- [ ] Set FRONTEND_URL to actual domain
- [ ] Enabled HTTPS (automatic on Fly.io)
- [ ] Reviewed CORS settings
- [ ] Rotated webhook secrets
- [ ] Set up database backups (Fly Postgres includes daily backups)
