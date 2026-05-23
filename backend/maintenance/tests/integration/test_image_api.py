from models import ImageModel
from models.database import db
from routes.upload_image import bucket_manager


def test_create_upload_url_persists_image_metadata(client, auth_headers, monkeypatch):
    monkeypatch.setattr(bucket_manager, "bucket_name", "maintenance-test-bucket")
    monkeypatch.setattr(
        bucket_manager,
        "generate_upload_url",
        lambda object_key, content_type: f"https://upload.test/{object_key}?contentType={content_type}",
    )

    response = client.post(
        "/api/maintenance/images/upload-url",
        json={"fileName": "issue.png", "contentType": "image/png"},
        headers=auth_headers(user_id=7, role="user"),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["imageId"]
    assert payload["uploadUrl"].startswith("https://upload.test/users/7/images/")

    image = ImageModel.query.filter_by(image_id=payload["imageId"]).first()
    assert image is not None
    assert image.user_id == 7
    assert image.bucket == "maintenance-test-bucket"
    assert image.fileName == "issue.png"
    assert image.contentType == "image/png"


def test_create_upload_url_rejects_unsupported_content_type(client, auth_headers):
    response = client.post(
        "/api/maintenance/images/upload-url",
        json={"fileName": "issue.txt", "contentType": "text/plain"},
        headers=auth_headers(user_id=7, role="user"),
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "unsupported image type"}


def test_image_owner_can_create_read_url(client, auth_headers, monkeypatch):
    image = ImageModel(
        image_id="image-1",
        user_id=7,
        bucket="maintenance-test-bucket",
        object_key="users/7/images/image-1.png",
        fileName="issue.png",
        contentType="image/png",
    )
    db.session.add(image)
    db.session.commit()
    monkeypatch.setattr(
        bucket_manager,
        "generate_read_url",
        lambda object_key: f"https://read.test/{object_key}",
    )

    response = client.get(
        "/api/maintenance/images/upload-url/image-1",
        headers=auth_headers(user_id=7, role="user"),
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "readUrl": "https://read.test/users/7/images/image-1.png"
    }


def test_non_owner_cannot_create_read_url(client, auth_headers):
    image = ImageModel(
        image_id="image-1",
        user_id=7,
        bucket="maintenance-test-bucket",
        object_key="users/7/images/image-1.png",
        fileName="issue.png",
        contentType="image/png",
    )
    db.session.add(image)
    db.session.commit()

    response = client.get(
        "/api/maintenance/images/upload-url/image-1",
        headers=auth_headers(user_id=8, role="user"),
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "image not found"}


def test_admin_can_create_read_url_for_any_image(client, auth_headers, monkeypatch):
    image = ImageModel(
        image_id="image-1",
        user_id=7,
        bucket="maintenance-test-bucket",
        object_key="users/7/images/image-1.png",
        fileName="issue.png",
        contentType="image/png",
    )
    db.session.add(image)
    db.session.commit()
    monkeypatch.setattr(
        bucket_manager,
        "generate_read_url",
        lambda object_key: f"https://read.test/{object_key}",
    )

    response = client.get(
        "/api/maintenance/images/upload-url/image-1",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "readUrl": "https://read.test/users/7/images/image-1.png"
    }
