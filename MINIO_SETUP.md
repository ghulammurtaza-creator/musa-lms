# MinIO Setup for Assignment Document Storage

## Overview
MinIO has been integrated into the Academy Management System to provide object storage for assignment submissions. This replaces the local file system storage with a scalable, S3-compatible solution.

## Services Added

### 1. MinIO Container
- **Image**: `minio/minio:latest`
- **Container Name**: `academy_minio`
- **Ports**:
  - `9000`: MinIO API
  - `9001`: MinIO Console (Web UI)
- **Credentials**:
  - Root User: `minioadmin`
  - Root Password: `minioadmin123`
- **Bucket**: `academy-assignments`

### 2. Access MinIO Console
Visit: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin123`

## Features Implemented

### File Upload
- Students can now upload assignment files
- Files are stored in MinIO with automatic organization by assignment and student
- Path structure: `assignments/{assignment_id}/student_{student_id}/{unique_filename}`
- Supports all file types with proper content type detection

### File Download
Two methods available:

#### 1. Direct Download
```
GET /api/assignments/submissions/{submission_id}/download
```
- Downloads file directly through the API
- Requires authentication
- Returns file as attachment

#### 2. Presigned URL
```
GET /api/assignments/submissions/{submission_id}/file-url
```
- Returns a temporary download URL (valid for 1 hour)
- Useful for frontend direct downloads
- More efficient for large files

### Authorization
- **Students**: Can only download their own submissions
- **Tutors**: Can download submissions for assignments they created
- **Admins**: Can download all submissions

## API Endpoints

### Submit Assignment with File
```http
POST /api/assignments/{assignment_id}/submit
Content-Type: multipart/form-data

Parameters:
- submission_text (optional): Text submission
- file (optional): File upload
```

### Download Submission File
```http
GET /api/assignments/submissions/{submission_id}/download
Authorization: Bearer {token}

Response: Binary file with attachment headers
```

### Get Presigned Download URL
```http
GET /api/assignments/submissions/{submission_id}/file-url
Authorization: Bearer {token}

Response:
{
  "url": "http://minio:9000/academy-assignments/...",
  "expires_in": 3600,
  "filename": "document.pdf"
}
```

## Configuration

### Environment Variables (docker-compose.yml)
```yaml
MINIO_ENDPOINT: minio:9000
MINIO_ACCESS_KEY: minioadmin
MINIO_SECRET_KEY: minioadmin123
MINIO_BUCKET_NAME: academy-assignments
MINIO_SECURE: "false"  # Set to "true" for HTTPS
```

### Backend Configuration (config.py)
The MinIO settings are automatically loaded from environment variables:
- `minio_endpoint`: MinIO server address
- `minio_access_key`: Access key for authentication
- `minio_secret_key`: Secret key for authentication
- `minio_bucket_name`: Bucket name for storage
- `minio_secure`: Whether to use SSL/TLS

## MinIO Service (minio_service.py)

### Methods Available

#### `upload_file(file_data, file_name, content_type, folder)`
Uploads a file to MinIO
- Returns: Object name (path) in MinIO

#### `download_file(object_name)`
Downloads a file from MinIO
- Returns: File content as bytes

#### `delete_file(object_name)`
Deletes a file from MinIO
- Returns: Boolean success status

#### `get_presigned_url(object_name, expires)`
Generates a temporary download URL
- Default expiration: 1 hour
- Returns: Presigned URL string

#### `file_exists(object_name)`
Checks if a file exists
- Returns: Boolean

## Data Migration

### Old File System to MinIO
If you have existing files in the old `uploads/assignments` directory, you can migrate them:

```python
# Migration script (run in backend container)
import os
from app.services.minio_service import get_minio_service

minio = get_minio_service()
old_dir = "uploads/assignments"

for filename in os.listdir(old_dir):
    filepath = os.path.join(old_dir, filename)
    with open(filepath, 'rb') as f:
        file_data = f.read()
        object_name = minio.upload_file(
            file_data=file_data,
            file_name=filename,
            folder="assignments/migrated"
        )
        print(f"Migrated {filename} -> {object_name}")
```

## Tutor Portal Features

Tutors can now:
1. View all submissions for their assignments
2. Download submitted files
3. See submission status (pending/submitted/graded)
4. Grade submissions
5. Provide feedback

### Accessing Submissions
```
GET /api/assignments/{assignment_id}/submissions
```

Returns all submissions with:
- Student details
- Submission text
- File path (if file attached)
- Status and grade
- Submission and grading timestamps

## Security Features

- File access is strictly controlled by user role
- All file operations require authentication
- Presigned URLs expire after 1 hour
- Files are organized by assignment and student to prevent conflicts
- Unique filenames prevent overwrites

## Monitoring

### Check MinIO Health
```bash
curl http://localhost:9000/minio/health/live
```

### View MinIO Logs
```bash
docker logs academy_minio
```

### View Backend Logs
```bash
docker logs academy_backend | grep -i minio
```

## Troubleshooting

### Issue: Cannot connect to MinIO
**Solution**: Ensure MinIO container is running
```bash
docker ps | grep minio
```

### Issue: Bucket not found
**Solution**: The bucket is auto-created on first use, but you can manually create it:
1. Visit http://localhost:9001
2. Login with credentials
3. Create bucket named `academy-assignments`

### Issue: File upload fails
**Solution**: Check MinIO container logs
```bash
docker logs academy_minio --tail 50
```

### Issue: Presigned URLs not accessible
**Solution**: Ensure you're using the URL within 1 hour of generation

## Production Considerations

### For Production Deployment:

1. **Change Credentials**:
   ```yaml
   MINIO_ACCESS_KEY: <strong-access-key>
   MINIO_SECRET_KEY: <strong-secret-key>
   ```

2. **Enable SSL/TLS**:
   ```yaml
   MINIO_SECURE: "true"
   ```

3. **Use Persistent Storage**:
   The `minio_data` volume ensures files persist across container restarts

4. **Set Retention Policies**:
   Configure lifecycle policies in MinIO console for automatic cleanup

5. **Enable Versioning**:
   Enable bucket versioning to keep file history

6. **Monitor Storage Usage**:
   Set up alerts for storage capacity

## Next Steps

1. Test file upload from student portal
2. Test file download from tutor portal
3. Verify file permissions and security
4. Set up backup strategy for MinIO data
5. Configure production credentials

## Support

For issues or questions:
- Check logs: `docker logs academy_backend`
- Check MinIO console: http://localhost:9001
- Review API documentation: http://localhost:8000/api/docs
