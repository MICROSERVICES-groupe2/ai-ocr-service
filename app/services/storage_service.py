import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logging import logger

class StorageService:
    def __init__(self):
        logger.info("Initializing StorageService with MinIO")
        # Initialize boto3 client for MinIO
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1' # dummy region for MinIO
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
        except ClientError:
            logger.info(f"Bucket {self.bucket} does not exist. Creating it.")
            try:
                self.s3_client.create_bucket(Bucket=self.bucket)
            except Exception as e:
                logger.error(f"Failed to create bucket: {e}")

    def upload_file(self, file_bytes: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
        logger.info(f"Uploading file {object_name} to bucket {self.bucket}")
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=object_name,
                Body=file_bytes,
                ContentType=content_type
            )
            # Retourne l'URL interne
            return f"http://{settings.MINIO_ENDPOINT}/{self.bucket}/{object_name}"
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            raise e

    def generate_presigned_url(self, object_name: str, expiry: int = 3600) -> str:
        logger.info(f"Generating presigned URL for {object_name}")
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expiry
            )
            return response
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise e

    def delete_file(self, object_name: str):
        logger.info(f"Deleting file {object_name}")
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=object_name)
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            raise e

storage_service = StorageService()
