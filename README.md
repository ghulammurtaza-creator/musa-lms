# Academy Management System

A production-ready **Automated Academy Management System** designed to replace manual data entry for tuition academies. This system automatically tracks student and teacher attendance by fetching Join/Exit events via Google Meet APIs, processes complex billing (family-based) and payroll (teacher-based) calculations, and provides a comprehensive dashboard for real-time monitoring and financial management.

## 🚀 Features

### Core Functionality
- **Automated Attendance Tracking**: Captures Join/Exit events from Google Meet sessions
- **Duration Calculation Engine**: Stitches multiple join/exit events to handle internet disconnections
- **Family-Based Billing**: Aggregates charges for all students under the same family
- **Teacher Payroll**: Calculates teacher compensation based on actual teaching hours
- **AI-Powered Summaries**: Generates lesson summaries using Google Gemini API
- **Real-Time Monitoring**: Live dashboard showing active sessions and participants

### Technical Highlights
- **Async/Await Architecture**: High-performance async operations throughout
- **Type Safety**: Full TypeScript frontend and Pydantic validation on backend
- **RESTful API**: Well-documented FastAPI endpoints
- **Database Migrations**: Alembic for version-controlled schema changes
- **Dockerized Deployment**: Complete containerization for easy deployment

## 📁 Project Structure

```
Musa LMS/
├── backend/                    # FastAPI Backend
│   ├── alembic/               # Database migrations
│   │   └── versions/          # Migration scripts
│   ├── app/
│   │   ├── core/              # Config, database setup
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   └── services/          # Business logic
│   ├── main.py                # FastAPI application entry
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container
│   └── alembic.ini            # Alembic configuration
├── frontend/                   # Next.js Frontend
│   ├── src/
│   │   ├── app/               # Next.js 14 app directory
│   │   ├── components/        # React components
│   │   │   ├── ui/            # Shadcn/UI components
│   │   │   ├── ActiveSessionsView.tsx
│   │   │   ├── AttendanceLogsView.tsx
│   │   │   ├── FinancialHubView.tsx
│   │   │   └── UserManagementView.tsx
│   │   └── lib/               # Utilities and API client
│   ├── package.json           # Node dependencies
│   ├── tailwind.config.js     # Tailwind CSS config
│   └── Dockerfile             # Frontend container
├── docker-compose.yml         # Docker orchestration
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**: Modern Python with async support
- **FastAPI**: High-performance async web framework
- **SQLAlchemy 2.0**: Async ORM for database operations
- **PostgreSQL**: Production-grade relational database
- **Alembic**: Database migration tool
- **Google Gemini API**: AI-powered lesson summaries
- **Pydantic**: Data validation and settings management

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/UI**: High-quality React components
- **Axios**: HTTP client for API calls
- **Lucide React**: Beautiful icon library

### DevOps
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **PostgreSQL 15**: Containerized database

## 📦 Installation & Setup

### Prerequisites
- Docker & Docker Compose installed
- Git
- (Optional) Node.js 20+ and Python 3.11+ for local development

### Quick Start with Docker

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Musa LMS"
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in your API keys:
   - `SECRET_KEY`: Generate a secure random string (min 32 chars)
   - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - `GOOGLE_WEBHOOK_SECRET`: Secret for webhook authentication
   - `GEMINI_API_KEY`: Your Google Gemini API key

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Local Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

## 🗄️ Database Schema

### Tables Overview

**Families**: Parent/guardian information for billing
- `id`, `family_number` (unique), `parent_name`, `parent_email`

**Students**: Student records linked to families
- `id`, `name`, `email`, `family_id` (FK), `hourly_rate`

**Teachers**: Teacher records with rates
- `id`, `name`, `email`, `hourly_rate`, `subject_specialties`

**Sessions**: Google Meet session records
- `id`, `meeting_id` (unique), `teacher_id` (FK), `start_time`, `end_time`, `ai_summary`

**AttendanceLogs**: Join/exit event tracking
- `id`, `session_id` (FK), `user_email`, `role`, `teacher_id` (FK), `student_id` (FK)
- `join_time`, `exit_time`, `duration_minutes`

### Relationships
- One Family → Many Students
- One Teacher → Many Sessions
- One Session → Many AttendanceLogs
- Cascading deletes for referential integrity

## 🔌 API Endpoints

### CRUD Operations
- `POST /api/families` - Create family
- `GET /api/families` - List all families
- `GET /api/families/{id}` - Get family details
- `PATCH /api/families/{id}` - Update family
- `DELETE /api/families/{id}` - Delete family

*(Similar endpoints for `/api/students` and `/api/teachers`)*

### Webhook & Events
- `POST /api/webhook/google-meet` - Receive Google Meet events
- `POST /api/webhook/sessions/{id}/generate-summary` - Generate AI summary

### Monitoring & Analytics
- `GET /api/monitoring/active-sessions` - Real-time active sessions
- `GET /api/monitoring/attendance-logs` - Query attendance history
- `GET /api/monitoring/billing/families` - Family billing reports
- `GET /api/monitoring/billing/families/{id}` - Single family billing
- `GET /api/monitoring/payroll/teachers` - Teacher payroll reports
- `GET /api/monitoring/payroll/teachers/{id}` - Single teacher payroll

## 💡 Key Features Explained

### Duration Calculation Engine
The system handles complex scenarios like:
- **Internet Disconnections**: Stitches multiple join/exit events within 5 minutes
- **Overlapping Sessions**: Merges consecutive segments intelligently
- **Accurate Time Tracking**: Calculates precise duration in minutes

### Family-Based Billing
- Aggregates hours for all siblings under one family
- Generates consolidated invoices per family
- Individual line items for each student
- Monthly billing cycle support

### Teacher Payroll
- Tracks total teaching hours per teacher
- Applies individual hourly rates
- Monthly payroll summaries
- Export-ready reports

### Real-Time Monitoring
- Live view of active Google Meet sessions
- Participant status (active/disconnected)
- Session duration tracking
- Auto-refresh every 30 seconds

## 🔐 Security Considerations

1. **Webhook Authentication**: Verify `X-Webhook-Secret` header
2. **Environment Variables**: Never commit `.env` files
3. **Database Credentials**: Use strong passwords in production
4. **CORS Configuration**: Restrict origins in production
5. **API Rate Limiting**: Implement rate limiting for production

## 🚀 Deployment

### Production Deployment with Docker

1. **Update docker-compose.yml for production**:
   - Remove volume mounts for hot-reload
   - Set `restart: always` for services
   - Use production-grade secrets management

2. **Set production environment variables**:
   ```bash
   # Use strong, randomly generated values
   SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Run migrations**:
   ```bash
   docker-compose exec app alembic upgrade head
   ```

4. **Scale services** (optional):
   ```bash
   docker-compose up -d --scale app=3
   ```

### Database Migrations

```bash
# Create a new migration
docker-compose exec app alembic revision --autogenerate -m "Description"

# Apply migrations
docker-compose exec app alembic upgrade head

# Rollback
docker-compose exec app alembic downgrade -1
```

## 📊 Usage Guide

### 1. Setup Users
Navigate to **User Management** tab:
1. Add Families (parent information)
2. Add Students (linked to families)
3. Add Teachers (with hourly rates)

### 2. Monitor Sessions
Navigate to **Real-time Monitoring** tab:
- View active Google Meet sessions
- See who's connected in real-time
- Track session durations

### 3. Review Attendance
Navigate to **Attendance Logs** tab:
- Search by email
- Filter by date range
- Export logs for records

### 4. Generate Financial Reports
Navigate to **Financial Hub** tab:
1. Select month and year
2. Click "Generate Reports"
3. Review family billing and teacher payroll
4. Export reports as needed

## 🔧 Configuration

### Google Meet Integration
To connect Google Meet webhooks:
1. Set up Google Cloud Project
2. Enable Admin SDK API
3. Configure webhook endpoint: `https://your-domain.com/api/webhook/google-meet`
4. Set webhook secret in `.env`

### Google Gemini AI
1. Get API key from [Google AI Studio](https://makersuite.google.com/)
2. Add to `.env` as `GEMINI_API_KEY`
3. AI summaries will be generated automatically

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### API Not Responding
```bash
# Check backend logs
docker-compose logs app

# Restart backend
docker-compose restart app
```

### Frontend Build Issues
```bash
# Clear Next.js cache
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

## 📝 Development Notes

### Adding New Endpoints
1. Create router in `backend/app/routers/`
2. Add schemas in `backend/app/schemas/`
3. Include router in `backend/main.py`

### Adding New Components
1. Create component in `frontend/src/components/`
2. Import in relevant page
3. Follow Shadcn/UI patterns

### Database Changes
```bash
# After modifying models
cd backend
alembic revision --autogenerate -m "Description of change"
alembic upgrade head
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 👥 Support

For issues, questions, or feature requests:
- Create an issue in the repository
- Contact: [Your Contact Information]

## 🎯 Roadmap

- [ ] Email notifications for billing
- [ ] SMS alerts for session start/end
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Calendar integration
- [ ] Automated invoice generation (PDF)
- [ ] Payment gateway integration

---

Built with ❤️ using FastAPI, Next.js, and PostgreSQL
