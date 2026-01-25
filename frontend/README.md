# Musa LMS - Frontend

Next.js frontend application for the Musa Learning Management System.

## Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend running on Docker (see main README)

### Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**

The `.env.local` file is already configured:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Development

**Start the development server:**
```bash
npm run dev
```

The application will be available at http://localhost:3000

### Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

Create or edit `.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Note:** All environment variables that should be accessible in the browser must be prefixed with `NEXT_PUBLIC_`.

## API Integration

The frontend uses axios with a centralized API configuration in `src/lib/api.ts`. All API calls use the base URL from `NEXT_PUBLIC_API_URL`.

Example:
```typescript
import { api } from '@/lib/api';

// This calls http://localhost:8000/api/students
const response = await api.get('/students');
```

## Project Structure

```
src/
├── app/              # Next.js app router pages
├── components/       # React components
│   └── ui/          # Reusable UI components
├── contexts/        # React contexts (Auth, etc.)
└── lib/             # Utilities and API client
    └── api.ts       # Axios instance and API functions
```

## Development Workflow

1. Ensure backend is running:
   ```bash
   # In the project root
   docker compose up
   ```

2. Start frontend development server:
   ```bash
   # In the frontend directory
   npm run dev
   ```

3. Make changes - the app will hot-reload automatically

## Building for Production

```bash
npm run build
npm run start
```

## Common Issues

### Can't connect to backend
- Ensure backend is running: http://localhost:8000/docs
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify no CORS errors in browser console

### Port 3000 already in use
```bash
# Use a different port
npm run dev -- -p 3001
```

### Environment variables not updating
- Restart the dev server after changing `.env.local`
- Clear `.next` folder: `rm -rf .next` (or `rmdir /s .next` on Windows)

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI
- **HTTP Client:** Axios
- **Date Handling:** date-fns
