# Docker Quick Start Guide

## One-Command Setup with Admin User

### Option 1: Auto-Create Admin User (Recommended for Testing)

Create a `.env` file with admin credentials:

```bash
# Copy example and edit
cp .env.example .env
```

Then add to your `.env`:
```env
CREATE_ADMIN=true
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=changeme123
ADMIN_NAME=System Administrator
```

Now run:
```bash
docker compose up --build
```

**That's it!** Everything will be set up automatically:
- ✅ PostgreSQL database created
- ✅ Database migrations run
- ✅ Admin user created
- ✅ Backend started on http://localhost:8000
- ✅ Frontend started on http://localhost:3000

### Option 2: Create Admin User Manually

If you don't want to auto-create the admin user, run:

```bash
# Start everything
docker compose up --build

# In another terminal, create admin user interactively
docker exec -it academy_backend python create_users.py
```

## What Each Command Does

```bash
docker compose up --build
```

This single command:
1. **Builds** the Docker images for backend and frontend
2. **Starts** PostgreSQL database
3. **Waits** for database to be ready
4. **Runs** `alembic upgrade head` (database migrations)
5. **Creates** admin user (if `CREATE_ADMIN=true`)
6. **Starts** FastAPI backend on port 8000
7. **Starts** Next.js frontend on port 3000

## Environment Variables

### Required for Basic Operation
```env
SECRET_KEY=your-secret-key-min-32-characters
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GEMINI_API_KEY=your-gemini-api-key
```

### Optional for Admin Auto-Creation
```env
CREATE_ADMIN=true                          # Enable auto-creation
ADMIN_EMAIL=admin@example.com              # Admin email
ADMIN_PASSWORD=changeme123                 # Admin password
ADMIN_NAME=System Administrator            # Admin full name
```

## Access the Application

Once running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Database**: localhost:5432 (postgres/postgres)

## Login

Use the credentials you set in `.env`:
- Email: `admin@example.com` (or your ADMIN_EMAIL)
- Password: `changeme123` (or your ADMIN_PASSWORD)

⚠️ **Important**: Change the default password after first login!

## Useful Docker Commands

```bash
# Stop all services
docker compose down

# Stop and remove volumes (reset database)
docker compose down -v

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f app

# Restart a service
docker compose restart app

# Execute commands in running container
docker exec -it academy_backend python create_users.py

# Access database
docker exec -it academy_db psql -U postgres -d academy_db

# Rebuild and restart
docker compose up --build --force-recreate
```

## Troubleshooting

### Admin User Not Created

Check logs:
```bash
docker compose logs app | grep -i admin
```

Manually create:
```bash
docker exec -it academy_backend python create_users.py
```

### Database Connection Errors

Ensure database is ready:
```bash
docker compose ps
```

All services should show "Up" status.

### Port Already in Use

If ports 3000, 5432, or 8000 are in use:

Edit `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Use different external port
```

### Clear Everything and Start Fresh

```bash
docker compose down -v
docker compose up --build
```

## Development Mode

The `docker-compose.yml` is configured for development with hot-reload:
- Backend: Changes to Python files reload automatically
- Frontend: Changes to TypeScript/React files reload automatically

## Production Mode

For production:

1. **Change environment variables**:
   ```env
   CREATE_ADMIN=false  # Don't auto-create in production
   SECRET_KEY=<generate-strong-random-key>
   ACCESS_TOKEN_EXPIRE_MINUTES=10080
   ```

2. **Remove volume mounts** in `docker-compose.yml`:
   ```yaml
   # Comment out this line for production:
   # volumes:
   #   - ./backend:/app
   ```

3. **Use production build** for frontend

4. **Set up HTTPS** with nginx/traefik

## Comparison: Docker vs Manual Setup

| Task | Docker | Manual |
|------|--------|--------|
| Database setup | Automatic | Manual PostgreSQL install |
| Migrations | Automatic | `alembic upgrade head` |
| Admin user | Auto (optional) | `python create_users.py` |
| Start backend | Automatic | `python main.py` |
| Start frontend | Automatic | `npm run dev` |
| Dependencies | Pre-installed | Manual install |
| **Total commands** | **1** | **4-5** |

## Summary

✅ **With Docker**: One command does everything
```bash
docker compose up --build
```

✅ **With Admin Auto-Creation**: Set `CREATE_ADMIN=true` in `.env` and you're done!

✅ **Without Docker**: You need to run 4-5 commands manually as shown in the Quick Start guide.

Choose Docker for:
- Quick setup and testing
- Consistent environments
- Easy reset/cleanup
- Team development

Choose Manual for:
- More control over each step
- Lighter resource usage
- Direct access to tools
- Learning/debugging
