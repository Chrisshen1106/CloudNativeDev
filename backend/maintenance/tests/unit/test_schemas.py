import pytest
from marshmallow import ValidationError

from models import ImageSchema, MaintenanceSchema


def test_maintenance_schema_loads_create_payload():
    payload = {
        "applicant_id": 1,
        "idEquipment": 10,
        "issue_description": "Screen does not turn on",
        "attachments": "image-1",
        "status": "pending",
    }

    assert MaintenanceSchema().load(payload) == payload


def test_maintenance_schema_rejects_invalid_status():
    payload = {
        "applicant_id": 1,
        "idEquipment": 10,
        "status": "unknown",
    }

    with pytest.raises(ValidationError) as exc_info:
        MaintenanceSchema().load(payload)

    assert "status" in exc_info.value.messages


def test_maintenance_schema_rejects_long_issue_description():
    payload = {
        "applicant_id": 1,
        "idEquipment": 10,
        "issue_description": "x" * 256,
    }

    with pytest.raises(ValidationError) as exc_info:
        MaintenanceSchema().load(payload)

    assert "issue_description" in exc_info.value.messages


def test_image_schema_loads_valid_payload():
    payload = {
        "image_id": "image-1",
        "user_id": 1,
        "bucket": "bucket",
        "object_key": "users/1/images/image-1.png",
        "fileName": "issue.png",
        "contentType": "image/png",
    }

    assert ImageSchema().load(payload) == payload


def test_image_schema_rejects_missing_required_fields():
    with pytest.raises(ValidationError) as exc_info:
        ImageSchema().load({"fileName": "issue.png"})

    assert "image_id" in exc_info.value.messages
    assert "user_id" in exc_info.value.messages
    assert "contentType" in exc_info.value.messages
