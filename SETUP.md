# Quick Setup Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
# Minimum required changes:
# - SECRET_KEY: Run `openssl rand -hex 32` to generate
# - GEMINI_API_KEY: Get from https://makersuite.google.com/
```

### Step 2: Start with Docker Compose
```bash
# Start all services (PostgreSQL, FastAPI, Next.js)
docker-compose up -d

# Watch the logs
docker-compose logs -f
```

### Step 3: Access the Application
- **Frontend Dashboard**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

### Step 4: Initial Setup
1. Go to http://localhost:3000
2. Navigate to "User Management" tab
3. Add your first family, students, and teachers

## 📋 Common Commands

### Docker Management (Backend Only)
```bash
# Start backend services (Database, API, MinIO)
docker compose up

# Stop services
docker compose down

# View logs
docker compose logs -f app  # Backend logs
docker compose logs -f db   # Database logs

# Restart a service
docker compose restart app

# Rebuild after code changes
docker compose up --build
```

### Frontend Management
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time)
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run production build
npm run start
```

### Database Operations
```bash
# Run migrations
docker compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "Your message"

# Access PostgreSQL directly
docker-compose exec db psql -U postgres -d academy_db
```

### Development Mode

#### Backend (without Docker)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/academy_db
alembic upgrade head
uvicorn main:app --reload
```

#### Frontend (without Docker)
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000/api
npm run dev
```

## 🔍 Verification Steps

1. **Check if all containers are running**:
   ```bash
   docker-compose ps
   ```
   You should see 3 services running: db, app, web

2. **Test API connection**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

3. **Test frontend**:
   Open http://localhost:3000 in browser

4. **Check database**:
   ```bash
   docker-compose exec db psql -U postgres -d academy_db -c "\dt"
   ```
   Should list tables: families, students, teachers, sessions, attendance_logs

## ❗ Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Linux/Mac:
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Failed
```bash
# Ensure PostgreSQL is running
docker-compose up -d db

# Wait for it to be ready
docker-compose logs db

# Restart the app
docker-compose restart app
```

### Frontend Build Errors
```bash
# Clear and reinstall
cd frontend
rm -rf node_modules .next
npm install
docker-compose up -d --build web
```

## 🔐 Production Deployment Checklist

- [ ] Generate strong SECRET_KEY (min 32 characters)
- [ ] Set up proper database credentials
- [ ] Configure CORS for your domain
- [ ] Enable HTTPS/SSL
- [ ] Set up Google Meet webhook
- [ ] Configure Gemini API key
- [ ] Set up backup strategy
- [ ] Configure monitoring/logging
- [ ] Review and update security settings
- [ ] Test all endpoints
- [ ] Set up CI/CD pipeline

## 📊 System Requirements

### Minimum
- 2 CPU cores
- 4 GB RAM
- 20 GB storage
- Docker & Docker Compose

### Recommended for Production
- 4+ CPU cores
- 8+ GB RAM
- 50+ GB storage (SSD preferred)
- Load balancer
- Backup system
- Monitoring solution

## 🎯 Next Steps After Setup

1. **User Management**: Add families, students, and teachers
2. **Test Attendance**: Manually test the webhook endpoint
3. **Generate Reports**: Try the Financial Hub with sample data
4. **Customize**: Adjust rates, add custom fields
5. **Integrate**: Connect Google Meet webhooks
6. **Monitor**: Watch real-time sessions

## 📞 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review API docs at http://localhost:8000/api/docs
- Check logs with `docker-compose logs -f`
- Verify environment variables in `.env`

---

**Ready to go!** 🎉 Your Academy Management System is now running.
