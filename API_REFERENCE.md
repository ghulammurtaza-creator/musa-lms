# API Reference Guide

Complete API documentation for the Academy Management System.

**Base URL**: `http://localhost:8000/api`

**Interactive Docs**: `http://localhost:8000/api/docs`

---

## 📋 Table of Contents
- [Families API](#families-api)
- [Students API](#students-api)
- [Teachers API](#teachers-api)
- [Webhook API](#webhook-api)
- [Monitoring API](#monitoring-api)

---

## 👨‍👩‍👧‍👦 Families API

### Create Family
**POST** `/families`

Create a new family record.

**Request Body**:
```json
{
  "family_number": "FAM-001",
  "parent_name": "John Doe",
  "parent_email": "john.doe@example.com"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "family_number": "FAM-001",
  "parent_name": "John Doe",
  "parent_email": "john.doe@example.com",
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": null
}
```

---

### Get All Families
**GET** `/families`

Retrieve all families with pagination.

**Query Parameters**:
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "family_number": "FAM-001",
    "parent_name": "John Doe",
    "parent_email": "john.doe@example.com",
    "created_at": "2026-01-02T10:00:00Z",
    "updated_at": null
  }
]
```

---

### Get Family by ID
**GET** `/families/{family_id}`

Retrieve a specific family.

**Response** (200 OK):
```json
{
  "id": 1,
  "family_number": "FAM-001",
  "parent_name": "John Doe",
  "parent_email": "john.doe@example.com",
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": null
}
```

---

### Update Family
**PATCH** `/families/{family_id}`

Update family information (partial update).

**Request Body**:
```json
{
  "parent_name": "John Smith"
}
```

**Response** (200 OK): Updated family object

---

### Delete Family
**DELETE** `/families/{family_id}`

Delete a family and all associated students (cascade).

**Response** (204 No Content)

---

## 🎓 Students API

### Create Student
**POST** `/students`

Register a new student.

**Request Body**:
```json
{
  "name": "Alice Doe",
  "email": "alice.doe@example.com",
  "family_id": 1,
  "hourly_rate": 25.00
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Alice Doe",
  "email": "alice.doe@example.com",
  "family_id": 1,
  "hourly_rate": 25.00,
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": null
}
```

---

### Get All Students
**GET** `/students`

Retrieve all students with optional filtering.

**Query Parameters**:
- `family_id` (int, optional): Filter by family
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Pagination limit

**Response** (200 OK): Array of student objects

---

### Get Student by ID
**GET** `/students/{student_id}`

Retrieve a specific student.

**Response** (200 OK): Student object

---

### Update Student
**PATCH** `/students/{student_id}`

Update student information.

**Request Body**:
```json
{
  "hourly_rate": 30.00
}
```

**Response** (200 OK): Updated student object

---

### Delete Student
**DELETE** `/students/{student_id}`

Delete a student record.

**Response** (204 No Content)

---

## 👨‍🏫 Teachers API

### Create Teacher
**POST** `/teachers`

Register a new teacher.

**Request Body**:
```json
{
  "name": "Dr. Smith",
  "email": "dr.smith@academy.com",
  "hourly_rate": 50.00,
  "subject_specialties": "Math, Physics"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "Dr. Smith",
  "email": "dr.smith@academy.com",
  "hourly_rate": 50.00,
  "subject_specialties": "Math, Physics",
  "created_at": "2026-01-02T10:00:00Z",
  "updated_at": null
}
```

---

### Get All Teachers
**GET** `/teachers`

Retrieve all teachers.

**Query Parameters**:
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Pagination limit

**Response** (200 OK): Array of teacher objects

---

### Get Teacher by ID
**GET** `/teachers/{teacher_id}`

Retrieve a specific teacher.

**Response** (200 OK): Teacher object

---

### Update Teacher
**PATCH** `/teachers/{teacher_id}`

Update teacher information.

**Request Body**:
```json
{
  "hourly_rate": 55.00
}
```

**Response** (200 OK): Updated teacher object

---

### Delete Teacher
**DELETE** `/teachers/{teacher_id}`

Delete a teacher record.

**Response** (204 No Content)

---

## 🔔 Webhook API

### Google Meet Webhook
**POST** `/webhook/google-meet`

Receive Google Meet join/exit events.

**Headers**:
- `X-Webhook-Secret`: Secret for authentication

**Request Body**:
```json
{
  "meeting_id": "abc-defg-hij",
  "user_email": "alice.doe@example.com",
  "event_type": "join",
  "timestamp": "2026-01-02T10:30:00Z",
  "role": "Student"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Join event processed for alice.doe@example.com",
  "session_id": 1
}
```

**Event Types**:
- `join`: User joined the meeting
- `exit`: User left the meeting

**Roles**:
- `Teacher`: Instructor
- `Student`: Learner

---

### Generate Session Summary
**POST** `/webhook/sessions/{session_id}/generate-summary`

Generate AI summary for a session.

**Query Parameters**:
- `transcript` (string, optional): Full transcript text

**Response** (200 OK):
```json
{
  "status": "success",
  "summary": "Dr. Smith taught algebra concepts...",
  "session_id": 1
}
```

---

## 📊 Monitoring API

### Get Active Sessions
**GET** `/monitoring/active-sessions`

Retrieve all currently active sessions.

**Response** (200 OK):
```json
[
  {
    "session_id": 1,
    "meeting_id": "abc-defg-hij",
    "teacher_name": "Dr. Smith",
    "start_time": "2026-01-02T10:00:00Z",
    "participants": [
      {
        "user_email": "dr.smith@academy.com",
        "role": "Teacher",
        "join_time": "2026-01-02T10:00:00Z",
        "is_active": true
      },
      {
        "user_email": "alice.doe@example.com",
        "role": "Student",
        "join_time": "2026-01-02T10:05:00Z",
        "is_active": true
      }
    ]
  }
]
```

---

### Get Attendance Logs
**GET** `/monitoring/attendance-logs`

Query attendance history with filtering.

**Query Parameters**:
- `session_id` (int, optional): Filter by session
- `user_email` (string, optional): Filter by user
- `skip` (int, optional): Pagination offset
- `limit` (int, optional): Pagination limit

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "session_id": 1,
    "user_email": "alice.doe@example.com",
    "role": "Student",
    "teacher_id": null,
    "student_id": 1,
    "join_time": "2026-01-02T10:05:00Z",
    "exit_time": "2026-01-02T11:05:00Z",
    "duration_minutes": 60.0,
    "created_at": "2026-01-02T10:05:00Z",
    "updated_at": "2026-01-02T11:05:00Z"
  }
]
```

---

### Get Family Billing
**GET** `/monitoring/billing/families`

Generate billing reports for all families.

**Query Parameters** (required):
- `year` (int): Year for billing (e.g., 2026)
- `month` (int): Month for billing (1-12)

**Response** (200 OK):
```json
[
  {
    "family_id": 1,
    "family_number": "FAM-001",
    "parent_name": "John Doe",
    "parent_email": "john.doe@example.com",
    "students": [
      {
        "student_id": 1,
        "student_name": "Alice Doe",
        "student_email": "alice.doe@example.com",
        "total_minutes": 240.0,
        "hourly_rate": 25.00,
        "total_amount": 100.00
      }
    ],
    "total_family_amount": 100.00,
    "billing_month": "2026-01"
  }
]
```

---

### Get Single Family Billing
**GET** `/monitoring/billing/families/{family_id}`

Generate billing report for specific family.

**Query Parameters** (required):
- `year` (int): Year for billing
- `month` (int): Month for billing

**Response** (200 OK): Single family billing object

---

### Get Teacher Payroll
**GET** `/monitoring/payroll/teachers`

Generate payroll reports for all teachers.

**Query Parameters** (required):
- `year` (int): Year for payroll
- `month` (int): Month for payroll

**Response** (200 OK):
```json
[
  {
    "teacher_id": 1,
    "teacher_name": "Dr. Smith",
    "teacher_email": "dr.smith@academy.com",
    "total_minutes": 480.0,
    "hourly_rate": 50.00,
    "total_amount": 400.00,
    "billing_month": "2026-01"
  }
]
```

---

### Get Single Teacher Payroll
**GET** `/monitoring/payroll/teachers/{teacher_id}`

Generate payroll report for specific teacher.

**Query Parameters** (required):
- `year` (int): Year for payroll
- `month` (int): Month for payroll

**Response** (200 OK): Single teacher payroll object

---

## ❌ Error Responses

All endpoints follow consistent error response format:

**400 Bad Request**:
```json
{
  "detail": "Validation error message"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Invalid webhook secret"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource with id X not found"
}
```

**422 Unprocessable Entity**:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error"
}
```

---

## 🔒 Authentication

Currently, the webhook endpoint uses header-based authentication:

**Header**: `X-Webhook-Secret`
**Value**: Configured in `.env` as `GOOGLE_WEBHOOK_SECRET`

---

## 📝 Notes

1. All datetime fields are in ISO 8601 format with timezone (UTC)
2. All monetary amounts are in decimal format (e.g., 25.00)
3. All durations are in minutes
4. Cascading deletes are enabled (deleting a family deletes all students)
5. Email fields are validated and must be valid email addresses
6. Unique constraints exist on `email` fields and `family_number`

---

## 🧪 Testing Endpoints

### Using cURL

**Create a family**:
```bash
curl -X POST http://localhost:8000/api/families \
  -H "Content-Type: application/json" \
  -d '{
    "family_number": "FAM-001",
    "parent_name": "John Doe",
    "parent_email": "john@example.com"
  }'
```

**Get all families**:
```bash
curl http://localhost:8000/api/families
```

**Send webhook event**:
```bash
curl -X POST http://localhost:8000/api/webhook/google-meet \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: your-webhook-secret" \
  -d '{
    "meeting_id": "test-123",
    "user_email": "alice@example.com",
    "event_type": "join",
    "timestamp": "2026-01-02T10:00:00Z",
    "role": "Student"
  }'
```

---

## 🔗 Related Resources

- Interactive API Docs: http://localhost:8000/api/docs
- ReDoc Documentation: http://localhost:8000/api/redoc
- Health Check: http://localhost:8000/health

---

**Last Updated**: January 2, 2026
