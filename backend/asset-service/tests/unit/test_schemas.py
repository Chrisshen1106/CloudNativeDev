import pytest
from marshmallow import ValidationError

from schemas import EquipmentSchema


def test_equipment_schema_loads_valid_payload():
    payload = {"idUser": 1, "name": "Laptop", "status": "in_use"}

    result = EquipmentSchema().load(payload)

    assert result["idUser"] == 1
    assert result["name"] == "Laptop"
    assert result["status"] == "in_use"


def test_equipment_schema_requires_id_user():
    with pytest.raises(ValidationError) as exc_info:
        EquipmentSchema().load({"name": "Laptop"})

    assert "idUser" in exc_info.value.messages


def test_equipment_schema_requires_name():
    with pytest.raises(ValidationError) as exc_info:
        EquipmentSchema().load({"idUser": 1})

    assert "name" in exc_info.value.messages


def test_equipment_schema_rejects_invalid_status():
    with pytest.raises(ValidationError) as exc_info:
        EquipmentSchema().load({"idUser": 1, "name": "Laptop", "status": "broken"})

    assert "status" in exc_info.value.messages


def test_equipment_schema_rejects_long_name():
    with pytest.raises(ValidationError) as exc_info:
        EquipmentSchema().load({"idUser": 1, "name": "x" * 101})

    assert "name" in exc_info.value.messages
