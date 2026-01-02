# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ACADEMY MANAGEMENT SYSTEM                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SYSTEMS                                  │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌────────────────┐         ┌────────────────┐         ┌────────────────┐   │
│  │  Google Meet   │         │ Google Admin   │         │  Google Gemini │   │
│  │    Sessions    │────────▶│  SDK / Reports │────────▶│   AI API       │   │
│  │                │         │     API        │         │                │   │
│  └────────────────┘         └────────────────┘         └────────────────┘   │
│         │                            │                         │              │
│         │ Join/Exit Events           │ Webhook                 │ Summaries    │
│         └────────────────────────────┼─────────────────────────┘              │
└──────────────────────────────────────┼────────────────────────────────────────┘
                                       │
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                                 │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                         API LAYER (Routers)                           │    │
│  ├──────────────────────────────────────────────────────────────────────┤    │
│  │                                                                        │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐│    │
│  │  │ Families │  │ Students │  │ Teachers │  │ Webhook  │  │Monitoring││    │
│  │  │  Router  │  │  Router  │  │  Router  │  │  Router  │  │ Router  ││    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └─────────┘│    │
│  │       │              │              │              │            │     │    │
│  └───────┼──────────────┼──────────────┼──────────────┼────────────┼─────┘    │
│          │              │              │              │            │           │
│          ▼              ▼              ▼              ▼            ▼           │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                      SERVICES LAYER (Business Logic)                  │    │
│  ├──────────────────────────────────────────────────────────────────────┤    │
│  │                                                                        │    │
│  │  ┌─────────────────────────┐  ┌────────────────────────────────┐    │    │
│  │  │ Duration Calculation    │  │      Billing Service           │    │    │
│  │  │       Engine            │  │  ┌──────────────────────────┐ │    │    │
│  │  │ ┌─────────────────────┐ │  │  │  Family-Based Billing    │ │    │    │
│  │  │ │ - Stitch Join/Exit  │ │  │  │  - Aggregate students    │ │    │    │
│  │  │ │ - Handle Gaps       │ │  │  │  - Calculate totals      │ │    │    │
│  │  │ │ - Merge Segments    │ │  │  └──────────────────────────┘ │    │    │
│  │  │ │ - Calculate Minutes │ │  │  ┌──────────────────────────┐ │    │    │
│  │  │ └─────────────────────┘ │  │  │   Teacher Payroll        │ │    │    │
│  │  └─────────────────────────┘  │  │  - Track teaching hours  │ │    │    │
│  │                                │  │  - Apply rates           │ │    │    │
│  │  ┌─────────────────────────┐  │  └──────────────────────────┘ │    │    │
│  │  │     AI Service          │  └────────────────────────────────┘    │    │
│  │  │  (Google Gemini)        │                                        │    │
│  │  │ ┌─────────────────────┐ │                                        │    │
│  │  │ │ - Lesson Summaries  │ │                                        │    │
│  │  │ │ - Session Notes     │ │                                        │    │
│  │  │ └─────────────────────┘ │                                        │    │
│  │  └─────────────────────────┘                                        │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│          │                                                                     │
│          ▼                                                                     │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                      DATA LAYER (SQLAlchemy)                          │    │
│  ├──────────────────────────────────────────────────────────────────────┤    │
│  │                                                                        │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  │    │
│  │  │Families │  │Students │  │Teachers │  │Sessions │  │Attendance│  │    │
│  │  │  Model  │  │  Model  │  │  Model  │  │  Model  │  │   Logs   │  │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └──────────┘  │    │
│  │       │            │            │            │               │        │    │
│  └───────┼────────────┼────────────┼────────────┼───────────────┼────────┘    │
└──────────┼────────────┼────────────┼────────────┼───────────────┼─────────────┘
           │            │            │            │               │
           └────────────┴────────────┴────────────┴───────────────┘
                                     │
                                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                        DATABASE (PostgreSQL 15)                                │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Tables:                                                                       │
│  ┌─────────────────┬──────────────────┬──────────────────┐                   │
│  │    families     │     students     │     teachers     │                   │
│  ├─────────────────┼──────────────────┼──────────────────┤                   │
│  │ - id            │ - id             │ - id             │                   │
│  │ - family_number │ - name           │ - name           │                   │
│  │ - parent_name   │ - email          │ - email          │                   │
│  │ - parent_email  │ - family_id (FK) │ - hourly_rate    │                   │
│  │                 │ - hourly_rate    │ - specialties    │                   │
│  └─────────────────┴──────────────────┴──────────────────┘                   │
│                                                                                │
│  ┌─────────────────────────────┬────────────────────────────────┐            │
│  │         sessions            │      attendance_logs           │            │
│  ├─────────────────────────────┼────────────────────────────────┤            │
│  │ - id                        │ - id                           │            │
│  │ - meeting_id                │ - session_id (FK)              │            │
│  │ - teacher_id (FK)           │ - user_email                   │            │
│  │ - start_time                │ - role                         │            │
│  │ - end_time                  │ - teacher_id (FK)              │            │
│  │ - ai_summary                │ - student_id (FK)              │            │
│  │                             │ - join_time                    │            │
│  │                             │ - exit_time                    │            │
│  │                             │ - duration_minutes             │            │
│  └─────────────────────────────┴────────────────────────────────┘            │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ REST API
                                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js 14)                                 │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                         APPLICATION LAYER                             │    │
│  ├──────────────────────────────────────────────────────────────────────┤    │
│  │                                                                        │    │
│  │  ┌────────────────────────────────────────────────────────────────┐  │    │
│  │  │                    Main Dashboard                               │  │    │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │  │    │
│  │  │  │Real-time │  │Attendance│  │Financial │  │    User      │   │  │    │
│  │  │  │Monitoring│  │   Logs   │  │   Hub    │  │ Management   │   │  │    │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │  │    │
│  │  └────────────────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                       COMPONENT LAYER                                 │    │
│  ├──────────────────────────────────────────────────────────────────────┤    │
│  │                                                                        │    │
│  │  Active Sessions View:                                                │    │
│  │  - Real-time session cards                                            │    │
│  │  - Participant status                                                 │    │
│  │  - Auto-refresh (30s)                                                 │    │
│  │                                                                        │    │
│  │  Attendance Logs View:                                                │    │
│  │  - Searchable table                                                   │    │
│  │  - Filter by email                                                    │    │
│  │  - Duration display                                                   │    │
│  │                                                                        │    │
│  │  Financial Hub View:                                                  │    │
│  │  - Month/year selector                                                │    │
│  │  - Family billing table                                               │    │
│  │  - Teacher payroll table                                              │    │
│  │  - Summary statistics                                                 │    │
│  │                                                                        │    │
│  │  User Management View:                                                │    │
│  │  - Add/Edit families                                                  │    │
│  │  - Add/Edit students                                                  │    │
│  │  - Add/Edit teachers                                                  │    │
│  │  - Tabbed interface                                                   │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                         UI COMPONENTS                                 │    │
│  ├──────────────────────────────────────────────────────────────────────┤    │
│  │                                                                        │    │
│  │  Shadcn/UI Components:                                                │    │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ │    │
│  │  │ Button │ │  Card  │ │ Table  │ │ Input  │ │ Label  │ │  Tabs  │ │    │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘ │    │
│  │                                                                        │    │
│  │  Styled with Tailwind CSS                                             │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT (Docker Compose)                            │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐            │
│  │   Service   │         │   Service   │         │   Service   │            │
│  │     db      │────────▶│     app     │────────▶│     web     │            │
│  │ PostgreSQL  │         │   FastAPI   │         │   Next.js   │            │
│  │  Port 5432  │         │  Port 8000  │         │  Port 3000  │            │
│  └─────────────┘         └─────────────┘         └─────────────┘            │
│                                                                                │
│  Volumes:                                                                      │
│  - postgres_data (persistent database storage)                                │
│                                                                                │
│  Network:                                                                      │
│  - academy_network (bridge)                                                   │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘


DATA FLOW EXAMPLE:
═══════════════════

1. Google Meet Event (User Joins)
   └─▶ Webhook: POST /api/webhook/google-meet
       └─▶ Duration Engine: Process Join Event
           └─▶ Database: Insert AttendanceLog
               └─▶ Frontend: Real-time Monitoring (auto-refresh)

2. Billing Report Generation
   └─▶ Frontend: Select month/year → Click "Generate"
       └─▶ API: GET /api/monitoring/billing/families?year=2026&month=1
           └─▶ Billing Service: Calculate family totals
               └─▶ Duration Engine: Aggregate student minutes
                   └─▶ Database: Query attendance_logs + students
                       └─▶ Frontend: Display billing table

3. User Registration
   └─▶ Frontend: Fill student form → Click "Add"
       └─▶ API: POST /api/students
           └─▶ Validation: Check email uniqueness
               └─▶ Database: Insert student record
                   └─▶ Frontend: Refresh student list


SECURITY LAYERS:
═══════════════

┌────────────────────────────────────────────┐
│ Webhook Secret Authentication              │
│ - Header-based verification                │
│ - Configured via environment variables     │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Input Validation (Pydantic)                │
│ - Type checking                            │
│ - Email validation                         │
│ - Required field enforcement               │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ Database Constraints                       │
│ - Unique constraints (email, family_number)│
│ - Foreign key constraints                  │
│ - NOT NULL constraints                     │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│ CORS Configuration                         │
│ - Restricted origins in production         │
│ - Configurable via environment             │
└────────────────────────────────────────────┘
```

---

**Legend:**
- `│` : Vertical connection
- `─` : Horizontal connection
- `▼` : Data flow direction (down)
- `▶` : Data flow direction (right)
- `┌─┐` : Container/box boundaries
- `(FK)` : Foreign Key relationship
