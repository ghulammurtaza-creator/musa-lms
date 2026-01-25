# Migration Guide: Adding Authentication to Existing System

This guide explains how the new authentication system integrates with your existing Musa LMS features.

## Overview of Changes

### What's New
- User authentication system with JWT tokens
- Role-based access control (admin, tutor, student)
- Student-tutor relationship management
- Assignment creation and submission system
- Protected routes and dashboards

### What Stays the Same
- Google Meet integration
- Automated attendance tracking
- Session monitoring
- Financial billing system
- Google Calendar scheduling
- All existing database tables (families, teachers, students, sessions, etc.)

## Database Changes

### New Tables Added
1. `auth_users` - Authentication users with roles
2. `student_tutor` - Many-to-many relationship table
3. `assignments` - Assignment information
4. `assignment_submissions` - Student submissions

### Existing Tables (Unchanged)
- `families`
- `students`
- `teachers`
- `sessions`
- `attendance_logs`
- `scheduled_classes`

## Coexistence Strategy

The new authentication system runs **alongside** the existing system:

### Option 1: Keep Both Systems
- Existing `teachers` and `students` tables remain for attendance/billing
- New `auth_users` table handles authentication and assignments
- No conflicts - they serve different purposes

### Option 2: Migrate to Unified System (Future Enhancement)
To fully integrate, you could:
1. Link `auth_users` to existing `teachers`/`students` tables
2. Add foreign keys: `teacher_id` and `student_id` to `auth_users`
3. Migrate existing users to `auth_users` table

## Step-by-Step Migration

### Phase 1: Setup (Completed)
✅ Database schema created
✅ Backend routes implemented
✅ Frontend pages and components created
✅ Migration files generated

### Phase 2: User Creation

1. **Run Database Migration**:
```bash
cd backend
alembic upgrade head
```

2. **Create Admin User**:
```bash
python create_users.py
```

3. **Onboard Existing Teachers**:
   - Have teachers sign up with their email
   - Admin assigns students to tutors
   - OR: Create a script to migrate existing teachers

4. **Onboard Students**:
   - Students sign up with their email
   - Admin assigns them to tutors
   - OR: Bulk import from existing student table

### Phase 3: Link Systems (Optional)

If you want to link authentication users to existing records:

```python
# Example: Link auth_users to existing teachers
from app.models.models import AuthUser, Teacher

def link_auth_to_teacher(auth_user_id, teacher_id):
    """Add this field to AuthUser model first"""
    # Add to AuthUser model: teacher_id = Column(Integer, ForeignKey('teachers.id'))
    auth_user = db.query(AuthUser).get(auth_user_id)
    auth_user.teacher_id = teacher_id
    db.commit()
```

### Phase 4: Data Migration Script (Optional)

Create a script to migrate existing users:

```python
# backend/migrate_existing_users.py
from app.core.database import SessionLocal
from app.models.models import AuthUser, AuthUserRole, Teacher, Student
from app.core.security import get_password_hash

db = SessionLocal()

# Migrate teachers to tutors
teachers = db.query(Teacher).all()
for teacher in teachers:
    # Check if already exists
    existing = db.query(AuthUser).filter(AuthUser.email == teacher.email).first()
    if existing:
        continue
    
    auth_user = AuthUser(
        email=teacher.email,
        hashed_password=get_password_hash("changeme123"),  # Default password
        full_name=teacher.name,
        role=AuthUserRole.TUTOR,
        is_active=True
    )
    db.add(auth_user)

# Migrate students
students = db.query(Student).all()
for student in students:
    existing = db.query(AuthUser).filter(AuthUser.email == student.email).first()
    if existing:
        continue
    
    auth_user = AuthUser(
        email=student.email,
        hashed_password=get_password_hash("changeme123"),  # Default password
        full_name=student.name,
        role=AuthUserRole.STUDENT,
        is_active=True
    )
    db.add(auth_user)

db.commit()
print("Migration complete! Users should change their passwords.")
```

## Integration Points

### 1. Google Calendar Integration (Tutors)

The existing Google Calendar OAuth flow still works:
- Tutors sign up/login with new auth system
- Navigate to schedule page
- Connect Google account (existing flow)
- Schedule classes as before

**To link**: Store Google credentials per tutor in `auth_users` instead of `teachers` table.

### 2. Attendance Tracking

Current system tracks by email. To integrate:

**Option A: Keep Separate**
- Existing attendance system continues using `teachers`/`students` tables
- No changes needed

**Option B: Link Systems**
```python
# When recording attendance, look up auth_user
attendance_log = AttendanceLog(
    session_id=session_id,
    user_email=email,
    # Add these relationships:
    student_id=student_id,  # From students table
    # Also store auth_user_id for new system
)
```

### 3. Billing System

Current billing uses `students` and `families` tables. To integrate:

**Option A: Keep Separate** (Recommended Initially)
- Continue using existing billing system
- Auth system handles login/assignments only

**Option B: Unified System**
- Add `family_id` to `auth_users` table
- Update billing queries to use `auth_users`

## Backwards Compatibility

### API Endpoints
All existing endpoints remain functional:
- `/api/teachers/*`
- `/api/students/*`
- `/api/families/*`
- `/api/sessions/*`
- `/api/webhook/*`
- `/api/monitoring/*`

### Frontend Pages
Old pages still accessible at root URL (`/`):
- Keep for admin/power users who need full system access
- New auth flow uses `/dashboard/*`, `/tutor/*`, `/student/*`

## Recommended Approach

### Short Term (Now)
1. ✅ Use both systems in parallel
2. ✅ New users use auth system for login/assignments
3. ✅ Existing attendance/billing continues as-is
4. ✅ Admin dashboard shows both auth users and legacy users

### Medium Term (Next Sprint)
1. Migrate existing teachers → tutors (auth_users)
2. Migrate existing students → student auth_users
3. Link auth_users to existing teacher/student records
4. Update attendance tracking to use auth_users

### Long Term (Future)
1. Consolidate tables
2. Deprecate separate teacher/student tables
3. Use auth_users as single source of truth
4. Maintain backwards compatibility in API

## Testing Strategy

### 1. Test New System
- Create new auth users
- Test assignment flow
- Verify role-based access

### 2. Test Existing System
- Schedule classes (existing flow)
- Track attendance (existing flow)
- Generate billing reports (existing flow)

### 3. Test Integration
- Create auth_user for existing teacher
- Verify Google Calendar still works
- Check attendance records include both systems

## Rollback Plan

If issues arise:

1. **Disable New Routes**:
```python
# In main.py, comment out:
# app.include_router(auth.router)
# app.include_router(assignments.router)
# app.include_router(relationships.router)
```

2. **Keep Database**:
- Don't drop new tables
- Existing functionality unaffected

3. **Revert Frontend**:
```bash
git revert <commit-hash>
```

## Security Considerations

### Authentication
- JWT tokens expire after 7 days
- Passwords hashed with bcrypt
- Role-based access enforced at API level

### Existing System
- No auth required for webhook endpoints
- Consider adding API keys for meeting webhooks
- Protect admin endpoints with new auth

### Recommendations
1. Add authentication to existing endpoints
2. Implement API rate limiting
3. Use environment variables for secrets
4. Enable HTTPS in production

## Support for Multiple Roles

The new system supports:
- **Admin**: Can access everything (both old and new)
- **Tutor**: Can access scheduling + assignments
- **Student**: Can access assignments only

To give tutors access to existing features:
```typescript
// In DashboardLayout.tsx
const getNavItems = () => {
  if (user?.role === 'tutor') {
    return [
      // New features
      { href: '/tutor/assignments', label: 'Assignments' },
      // Existing features
      { href: '/tutor/schedule', label: 'Schedule' },
      { href: '/tutor/attendance', label: 'Attendance' },
    ];
  }
};
```

## Conclusion

The authentication system is designed to:
- ✅ Work alongside existing features
- ✅ Not disrupt current operations
- ✅ Allow gradual migration
- ✅ Provide clear separation of concerns

You can start using the new system immediately while keeping all existing functionality intact!

## Next Steps

1. Run migrations: `alembic upgrade head`
2. Create admin user: `python create_users.py`
3. Test new auth flow
4. Gradually onboard users
5. Plan full integration (optional)

For questions or issues, refer to:
- `AUTHENTICATION_ASSIGNMENTS_GUIDE.md` - Full feature documentation
- `QUICK_START_AUTH.md` - Quick start guide
- `/api/docs` - API documentation
