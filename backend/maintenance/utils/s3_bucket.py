import os
import boto3

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

        self.s3_client = boto3.client("s3")
        self.bucket_name = os.getenv("S3_BUCKET_NAME")

    def generate_upload_url(self, object_key, content_type):
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