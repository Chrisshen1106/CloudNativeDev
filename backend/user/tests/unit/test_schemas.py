import pytest
from marshmallow import ValidationError

from models import DepartmentSchema, UserSchema


def test_department_schema_loads_required_name():
    payload = {"name": "Engineering"}

    assert DepartmentSchema().load(payload) == payload


def test_user_schema_loads_valid_user_payload():
    payload = {
        "name": "Ada",
        "email": "ada@example.com",
        "password": "plain-password",
        "idDepartment": 1,
        "role": "admin",
    }

    assert UserSchema().load(payload) == payload


def test_user_schema_rejects_invalid_role():
    payload = {
        "name": "Ada",
        "email": "ada@example.com",
        "password": "plain-password",
        "idDepartment": 1,
        "role": "owner",
    }

    with pytest.raises(ValidationError) as exc_info:
        UserSchema().load(payload)

    assert "role" in exc_info.value.messages


def test_user_schema_rejects_invalid_email():
    payload = {
        "name": "Ada",
        "email": "not-an-email",
        "password": "plain-password",
        "idDepartment": 1,
        "role": "user",
    }

    with pytest.raises(ValidationError) as exc_info:
        UserSchema().load(payload)

    assert "email" in exc_info.value.messages
