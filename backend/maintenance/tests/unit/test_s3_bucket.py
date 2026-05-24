import pytest

from utils.s3_bucket import BucketManager


class FakeS3Client:
    def generate_presigned_url(self, **kwargs):
        return {
            "client_method": kwargs["ClientMethod"],
            "params": kwargs["Params"],
            "expires": kwargs["ExpiresIn"],
            "http_method": kwargs["HttpMethod"],
        }


def test_generate_upload_url_uses_bucket_key_and_content_type(monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "maintenance-test-bucket")
    manager = BucketManager()
    manager.s3_client = FakeS3Client()

    result = manager.generate_upload_url("users/1/images/image-1.png", "image/png")

    assert result == {
        "client_method": "put_object",
        "params": {
            "Bucket": "maintenance-test-bucket",
            "Key": "users/1/images/image-1.png",
            "ContentType": "image/png",
        },
        "expires": 300,
        "http_method": "PUT",
    }


def test_generate_read_url_uses_bucket_and_key(monkeypatch):
    monkeypatch.setenv("S3_BUCKET_NAME", "maintenance-test-bucket")
    manager = BucketManager()
    manager.s3_client = FakeS3Client()

    result = manager.generate_read_url("users/1/images/image-1.png")

    assert result == {
        "client_method": "get_object",
        "params": {
            "Bucket": "maintenance-test-bucket",
            "Key": "users/1/images/image-1.png",
        },
        "expires": 300,
        "http_method": "GET",
    }


def test_load_config_requires_bucket_name(monkeypatch):
    monkeypatch.delenv("S3_BUCKET_NAME", raising=False)
    monkeypatch.delenv("BUCKET_NAME", raising=False)
    manager = BucketManager()

    with pytest.raises(ValueError, match="Missing S3 bucket config"):
        manager._load_config()
