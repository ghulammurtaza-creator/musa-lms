"""MinIO service for file storage"""
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from typing import Optional
import uuid
from datetime import timedelta
from app.core.config import get_settings

settings = get_settings()


class MinIOService:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl
        )
        self.bucket_name = settings.minio_bucket_name
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created MinIO bucket: {self.bucket_name}")
            else:
                print(f"MinIO bucket exists: {self.bucket_name}")
        except S3Error as e:
            print(f"Error checking/creating bucket: {e}")
    
    def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
        folder: str = "assignments"
    ) -> str:
        """
        Upload a file to MinIO
        
        Args:
            file_data: File content as bytes
            file_name: Original file name
            content_type: MIME type of the file
            folder: Folder/prefix in the bucket
        
        Returns:
            Object name (path) in MinIO
        """
        try:
            # Generate unique file name
            file_extension = file_name.split('.')[-1] if '.' in file_name else ''
            unique_name = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())
            object_name = f"{folder}/{unique_name}"
            
            # Upload file
            self.client.put_object(
                self.bucket_name,
                object_name,
                BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            
            return object_name
        except S3Error as e:
            print(f"Error uploading file to MinIO: {e}")
            raise
    
    def download_file(self, object_name: str) -> bytes:
        """
        Download a file from MinIO
        
        Args:
            object_name: Object name (path) in MinIO
        
        Returns:
            File content as bytes
        """
        try:
            response = self.client.get_object(self.bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error downloading file from MinIO: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO
        
        Args:
            object_name: Object name (path) in MinIO
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            print(f"Error deleting file from MinIO: {e}")
            return False
    
    def get_presigned_url(
        self,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> str:
        """
        Get a presigned URL for downloading a file
        
        Args:
            object_name: Object name (path) in MinIO
            expires: URL expiration time
        
        Returns:
            Presigned URL
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            raise
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in MinIO
        
        Args:
            object_name: Object name (path) in MinIO
        
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False


# Global MinIO service instance
minio_service: Optional[MinIOService] = None


def get_minio_service() -> MinIOService:
    """Get or create MinIO service instance"""
    global minio_service
    if minio_service is None:
        minio_service = MinIOService()
    return minio_service
