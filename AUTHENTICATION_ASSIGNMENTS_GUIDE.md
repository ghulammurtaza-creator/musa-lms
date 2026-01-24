# Authentication & Assignment Management System - Implementation Guide

## Overview

The Musa LMS has been successfully enhanced with a comprehensive authentication system, role-based access control, student-tutor relationship management, and an assignments module. This document provides a complete guide to the new features.

## New Features

### 1. Authentication System
- **User Registration & Login**: Secure signup and login with JWT token-based authentication
- **Three User Roles**:
  - **Admin**: Full system access
  - **Tutor**: Can schedule classes, create assignments, manage students
  - **Student**: Can view tutors, submit assignments, attend classes

### 2. Student-Tutor Relationship Management
- Admins can assign students to tutors
- Many-to-many relationship support (students can have multiple tutors, tutors can have multiple students)
- Students can view their assigned tutors
- Tutors can view their assigned students

### 3. Assignment Management System
- **For Tutors**:
  - Create assignments with title, description, due date, and points
  - Assign assignments to specific students
  - Grade submitted assignments with feedback
  - View all assignment submissions
  
- **For Students**:
  - View assigned assignments
  - Submit assignments with text and/or file uploads
  - View grades and feedback
  - Track assignment status (pending, submitted, graded)

## Database Schema

### New Tables

#### `auth_users`
- `id`: Primary key
- `email`: Unique user email
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name
- `role`: Enum (admin, tutor, student)
- `is_active`: Boolean
- `created_at`, `updated_at`: Timestamps

#### `student_tutor` (Association Table)
- `student_id`: Foreign key to auth_users
- `tutor_id`: Foreign key to auth_users
- `assigned_at`: Timestamp

#### `assignments`
- `id`: Primary key
- `tutor_id`: Foreign key to auth_users
- `title`: Assignment title
- `description`: Assignment description
- `due_date`: Due date timestamp
- `total_points`: Maximum points
- `created_at`, `updated_at`: Timestamps

#### `assignment_submissions`
- `id`: Primary key
- `assignment_id`: Foreign key to assignments
- `student_id`: Foreign key to auth_users
- `submission_text`: Text submission
- `file_path`: Path to uploaded file
- `status`: Enum (pending, submitted, graded)
- `grade`: Score received
- `feedback`: Tutor feedback
- `submitted_at`, `graded_at`: Timestamps

## Backend API Endpoints

### Authentication (`/api/auth`)
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/users` - List all users (admin only)
- `GET /api/auth/tutors` - List all tutors
- `GET /api/auth/students` - List all students (tutor/admin)
- `DELETE /api/auth/users/{user_id}` - Delete user (admin only)

### Relationships (`/api/relationships`)
- `POST /api/relationships/assign` - Assign student to tutor (admin only)
- `DELETE /api/relationships/unassign` - Unassign student from tutor (admin only)
- `GET /api/relationships/student/{student_id}/tutors` - Get tutors for student
- `GET /api/relationships/tutor/{tutor_id}/students` - Get students for tutor
- `GET /api/relationships/my-tutors` - Get tutors for current student
- `GET /api/relationships/my-students` - Get students for current tutor

### Assignments (`/api/assignments`)
- `POST /api/assignments` - Create assignment (tutor/admin)
- `GET /api/assignments` - List assignments (filtered by role)
- `GET /api/assignments/{id}` - Get assignment details
- `PUT /api/assignments/{id}` - Update assignment (tutor/admin)
- `DELETE /api/assignments/{id}` - Delete assignment (tutor/admin)
- `GET /api/assignments/{id}/submissions` - List submissions for assignment
- `POST /api/assignments/{id}/submit` - Submit assignment (student)
- `PUT /api/assignments/submissions/{id}/grade` - Grade submission (tutor/admin)
- `GET /api/assignments/my-submissions` - Get current student's submissions

## Frontend Structure

### Pages

#### Public Pages
- `/` - Landing page with role descriptions
- `/login` - Login page
- `/signup` - Registration page

#### Admin Pages
- `/dashboard` - Admin dashboard with system overview
- `/dashboard/relationships` - Student-tutor assignment management
- `/dashboard/users` - User management
- `/dashboard/sessions` - Active sessions monitoring
- `/dashboard/logs` - Attendance logs
- `/dashboard/financial` - Financial hub

#### Tutor Pages
- `/tutor/dashboard` - Tutor dashboard
- `/tutor/students` - View assigned students
- `/tutor/assignments` - Create and manage assignments
- `/tutor/schedule` - Schedule Google Meet classes

#### Student Pages
- `/student/dashboard` - Student dashboard
- `/student/tutors` - View assigned tutors
- `/student/assignments` - View and submit assignments

### Components

#### Authentication
- `AuthContext.tsx` - Authentication context provider
- `Login page` - Login form
- `Signup page` - Registration form

#### Assignment Management
- `TutorAssignmentsView.tsx` - Tutor assignment management
- `StudentAssignmentsView.tsx` - Student assignment view and submission
- `MyStudentsView.tsx` - View tutor's students
- `MyTutorsView.tsx` - View student's tutors

#### Relationship Management
- `StudentTutorManagement.tsx` - Admin interface for managing assignments

#### Layout
- `DashboardLayout.tsx` - Protected layout with role-based navigation

## Setup Instructions

### 1. Database Migration

Run the Alembic migration to create new tables:

```bash
cd backend
alembic upgrade head
```

### 2. Create Admin User

You'll need to create an admin user manually or via a script. Here's a Python script:

```python
from app.core.database import SessionLocal
from app.models.models import AuthUser, AuthUserRole
from app.core.security import get_password_hash

db = SessionLocal()

admin = AuthUser(
    email="admin@example.com",
    hashed_password=get_password_hash("admin123"),
    full_name="System Administrator",
    role=AuthUserRole.ADMIN,
    is_active=True
)

db.add(admin)
db.commit()
print("Admin user created successfully!")
```

### 3. Start Backend

```bash
cd backend
python main.py
```

### 4. Start Frontend

```bash
cd frontend
npm install  # if needed
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

## Usage Workflows

### Admin Workflow

1. **Login** as admin
2. **Create Users**: 
   - Use signup page or create via API
3. **Assign Students to Tutors**:
   - Navigate to `/dashboard/relationships`
   - Select student and tutor
   - Click "Assign Student to Tutor"
4. **Monitor System**:
   - View active sessions
   - Check attendance logs
   - Review financial data

### Tutor Workflow

1. **Login** as tutor
2. **Connect Google Calendar**:
   - Go to schedule page
   - Connect Google account (existing feature)
3. **View Students**:
   - Navigate to "My Students"
   - See all assigned students
4. **Create Assignment**:
   - Go to "Assignments"
   - Click "Create Assignment"
   - Fill in details and select students
   - Submit
5. **Grade Submissions**:
   - View assignment submissions
   - Add grade and feedback
   - Submit grading

### Student Workflow

1. **Login** as student
2. **View Tutors**:
   - Navigate to "My Tutors"
   - See all assigned tutors
3. **View Assignments**:
   - Go to "Assignments"
   - See all assigned work
4. **Submit Assignment**:
   - Click on an assignment
   - Add text answer or upload file
   - Click "Submit Assignment"
5. **View Grades**:
   - Graded assignments show score and feedback

## Security Features

1. **Password Hashing**: Using bcrypt with passlib
2. **JWT Tokens**: Secure token-based authentication
3. **Role-Based Access Control**: Enforced at API level
4. **Token Expiration**: 7-day token expiration
5. **Protected Routes**: Frontend routes protected with authentication

## File Upload

Assignment submissions support file uploads:
- Files stored in `backend/uploads/assignments/`
- Unique filenames with timestamps
- Format: `{student_id}_{assignment_id}_{timestamp}_{filename}`

## Environment Variables

Add to your backend `.env` file:

```env
# Authentication
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# File Upload
UPLOAD_DIR=uploads/assignments
```

## Testing

### 1. Test User Creation

```bash
# Signup via API
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User",
    "role": "student"
  }'
```

### 2. Test Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -F "username=test@example.com" \
  -F "password=test123"
```

### 3. Test Protected Endpoint

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Next Steps & Enhancements

Potential future improvements:

1. **Email Notifications**: 
   - Assignment due date reminders
   - Grade notifications
   
2. **Assignment Types**:
   - Multiple choice questions
   - Quizzes with auto-grading
   
3. **File Management**:
   - File download for tutors
   - Multiple file uploads
   
4. **Analytics Dashboard**:
   - Student progress tracking
   - Assignment completion rates
   
5. **Chat System**:
   - Real-time messaging between students and tutors

## Troubleshooting

### Common Issues

1. **Migration Errors**:
   - Ensure database is running
   - Check Alembic version history
   - Run `alembic downgrade base` then `alembic upgrade head`

2. **Authentication Errors**:
   - Verify JWT secret key is set
   - Check token expiration
   - Clear localStorage in browser

3. **File Upload Issues**:
   - Ensure `uploads/assignments/` directory exists
   - Check write permissions
   - Verify Content-Type in requests

4. **CORS Errors**:
   - Verify frontend URL in backend CORS settings
   - Check browser console for specific errors

## Support

For issues or questions:
- Check API documentation at `/api/docs`
- Review error logs in backend console
- Check browser console for frontend errors

## Conclusion

The Musa LMS now has a complete authentication system with role-based access control, student-tutor relationship management, and a full-featured assignment system. All features are production-ready and follow security best practices.
