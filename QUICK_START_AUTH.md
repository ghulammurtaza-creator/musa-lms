# Quick Start Guide - Authentication & Assignments

## Getting Started in 5 Minutes

### Step 1: Run Database Migration

```bash
cd backend
alembic upgrade head
```

### Step 2: Create Admin User

```bash
cd backend
python create_users.py
```

Follow the prompts to create:
- Admin user (required)
- Sample users for testing (optional)

### Step 3: Start the Backend

```bash
cd backend
python main.py
```

Backend will run on: http://localhost:8000

### Step 4: Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:3000

### Step 5: Login

1. Go to http://localhost:3000
2. Click "Login"
3. Use your admin credentials
4. You'll be redirected to the admin dashboard

## Quick Testing Workflow

### As Admin (Full Access)

1. **Create Users**:
   - Go to http://localhost:3000/signup
   - Create a tutor account
   - Create a student account
   - (Or use sample users if created)

2. **Assign Student to Tutor**:
   - Login as admin
   - Go to "Student-Tutor Assignments"
   - Select student and tutor from dropdowns
   - Click "Assign"

3. **View System**:
   - Check active sessions
   - View attendance logs
   - Monitor financial data

### As Tutor

1. **Login**:
   - Email: tutor@example.com
   - Password: tutor123

2. **View Students**:
   - Navigate to "My Students"
   - See assigned students

3. **Create Assignment**:
   - Go to "Assignments"
   - Click "Create Assignment"
   - Fill form:
     - Title: "Week 1 Homework"
     - Description: "Complete exercises 1-10"
     - Due Date: (select a future date)
     - Points: 100
     - Select students to assign
   - Submit

4. **Schedule a Class** (Optional):
   - Go to "Schedule Class"
   - Connect Google Calendar
   - Schedule a Google Meet session

### As Student

1. **Login**:
   - Email: student1@example.com
   - Password: student123

2. **View Tutors**:
   - Navigate to "My Tutors"
   - See assigned tutors

3. **View & Submit Assignment**:
   - Go to "Assignments"
   - Click on an assignment
   - Fill in your answer or upload a file
   - Click "Submit Assignment"

4. **Check Grades**:
   - Return to assignments page
   - Graded assignments show score and feedback

### As Tutor - Grade Assignment

1. **View Submissions**:
   - Go to "Assignments"
   - Click on an assignment with submissions

2. **Grade** (Coming from assignment management):
   - Select a submission
   - Enter grade (0-100)
   - Add feedback
   - Submit

## Default Credentials (if using sample users)

- **Admin**: admin@example.com / (your chosen password)
- **Tutor**: tutor@example.com / tutor123
- **Student 1**: student1@example.com / student123
- **Student 2**: student2@example.com / student123

## API Documentation

View interactive API docs at: http://localhost:8000/api/docs

## Common Tasks

### Create a New User via API

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "full_name": "New User",
    "role": "student"
  }'
```

### Get Authentication Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -F "username=tutor@example.com" \
  -F "password=tutor123"
```

### Test Protected Endpoint

```bash
# Replace YOUR_TOKEN with actual token from login
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Cannot Login
- Check backend is running on port 8000
- Verify credentials are correct
- Clear browser localStorage
- Check browser console for errors

### Database Errors
- Ensure PostgreSQL is running
- Check database connection in `.env`
- Run migration: `alembic upgrade head`

### CORS Errors
- Verify backend CORS settings include `http://localhost:3000`
- Check frontend is running on correct port

### Assignment File Upload Not Working
- Ensure `backend/uploads/assignments/` directory exists
- Check directory permissions
- Verify file size limits

## Next Steps

1. **Customize**: Update SECRET_KEY in production
2. **Email Setup**: Configure email notifications
3. **Google OAuth**: Set up Google Calendar for tutors
4. **Billing**: Integrate with existing billing system
5. **Analytics**: Add reporting dashboards

## Support Resources

- Full Documentation: `AUTHENTICATION_ASSIGNMENTS_GUIDE.md`
- API Docs: http://localhost:8000/api/docs
- System Architecture: `ARCHITECTURE.md`
- Setup Guide: `SETUP.md`

## Security Notes

⚠️ **Important for Production**:

1. Change `SECRET_KEY` in `backend/app/core/security.py`
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Implement rate limiting
5. Regular security audits
6. Strong password policies
7. Token refresh mechanism

## Feature Summary

✅ **Completed Features**:
- User authentication (JWT-based)
- Role-based access control (admin/tutor/student)
- Student-tutor relationship management
- Assignment creation and management
- Assignment submission (text + files)
- Grading system with feedback
- Role-based dashboards
- Protected routes

🔄 **Existing Features Still Available**:
- Google Meet integration
- Automated attendance tracking
- Financial billing system
- Real-time session monitoring
- Google Calendar scheduling

---

**Ready to go!** Start with Step 1 above and you'll be up and running in minutes.
