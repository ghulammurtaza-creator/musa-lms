# Quick Start Guide - Separated Frontend/Backend

This guide explains how to run the application with the backend in Docker and the frontend locally with npm.

## Setup

### Backend (Docker)

1. **Start the backend services:**
```bash
docker compose up --build
```

This will start:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- MinIO storage (ports 9000, 9001)

2. **Verify backend is running:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

### Frontend (npm)

1. **Navigate to the frontend directory:**
```bash
cd frontend
```

2. **Install dependencies (first time only):**
```bash
npm install
```

3. **Configure the API base URL:**

The frontend is already configured with `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

If you need to change the API URL, edit this file.

4. **Start the development server:**
```bash
npm run dev
```

5. **Access the application:**
- Frontend: http://localhost:3000

## Environment Variables

### Frontend (.env.local)

- `NEXT_PUBLIC_API_URL`: The backend API base URL
  - Default: `http://localhost:8000/api`
  - All API calls in the frontend use this base URL
  - Defined in `frontend/src/lib/api.ts`

### Backend (.env in root directory)

See the main `.env` file for backend configuration including:
- Database credentials
- Google OAuth credentials
- MinIO settings
- Admin user settings

## Development Workflow

### Starting Everything

```bash
# Terminal 1: Start backend
docker compose up

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### Stopping Services

```bash
# Frontend: Press Ctrl+C in the terminal running npm

# Backend:
docker compose down
```

## API Integration

The frontend uses axios with a configured base URL. All API functions are in `frontend/src/lib/api.ts`:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

All API endpoints are relative to this base URL:
- `api.get('/students')` → `http://localhost:8000/api/students`
- `api.post('/assignments')` → `http://localhost:8000/api/assignments`
- etc.

## Troubleshooting

### Frontend can't connect to backend

1. Ensure backend is running: `docker compose ps`
2. Check API URL in `.env.local`
3. Verify backend is accessible: http://localhost:8000/docs

### Port conflicts

- Backend uses port 8000 (change in docker-compose.yml if needed)
- Frontend uses port 3000 (Next.js default, can be changed with `-p` flag)
- Database uses port 5432
- MinIO uses ports 9000 and 9001

### CORS issues

The backend is configured to allow requests from `http://localhost:3000` (FRONTEND_URL in docker-compose.yml).

## Production Build

To build the frontend for production:

```bash
cd frontend
npm run build
npm run start  # Runs production server on port 3000
```

## Benefits of This Setup

1. **Fast Development**: Frontend hot-reloading without Docker overhead
2. **Easy Debugging**: Direct access to Next.js dev tools and error messages
3. **Flexible**: Can easily switch API endpoints or run multiple frontend instances
4. **Consistent Backend**: Backend environment matches production (Docker)
