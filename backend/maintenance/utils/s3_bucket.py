import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

class BucketManager:
    def __init__(self):
        self.ALLOWED_CONTENT_TYPES = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "image/webp": "webp",
            "image/gif": "gif",
        }
        self.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        self.UPLOAD_EXPIRES = 300
        self.READ_EXPIRES = 300

        self.s3_client = None
        self.bucket_name = None

    def _load_config(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME") or os.getenv("BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError("Missing S3 bucket config. Please set BUCKET_NAME or S3_BUCKET_NAME in backend/.env")

        if self.s3_client is None:
            region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
            kwargs = {"region_name": region} if region else {}
            self.s3_client = boto3.client("s3", **kwargs)

    def generate_upload_url(self, object_key, content_type):
        self._load_config()
        upload_url = self.s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=self.UPLOAD_EXPIRES,
            HttpMethod="PUT",
        )
        return upload_url
    
    def generate_read_url(self, object_key):
        self._load_config()
        read_url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_key,
            },
            ExpiresIn=self.READ_EXPIRES,
            HttpMethod="GET",
        )
        return read_url
    
bucket_manager = BucketManager()
