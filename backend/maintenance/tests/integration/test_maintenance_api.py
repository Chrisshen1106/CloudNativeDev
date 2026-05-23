from controllers.maintenance import maintenance_controller
from models import MaintenanceModel
from models.database import db


def create_form(applicant_id=1, id_equipment=10, status="pending", **overrides):
    form = MaintenanceModel(
        applicant_id=applicant_id,
        idEquipment=id_equipment,
        status=status,
        issue_description="Screen does not turn on",
        **overrides,
    )
    db.session.add(form)
    db.session.commit()
    return form


def test_user_can_create_form(client, auth_headers):
    response = client.post(
        "/api/maintenance/form",
        json={
            "idEquipment": 10,
            "issue_description": "Screen does not turn on",
            "attachments": "image-1",
        },
        headers=auth_headers(user_id=7, role="user"),
    )

    assert response.status_code == 201
    assert response.get_json() == {"idForm": 1, "status": "pending"}

    form = maintenance_controller.getFormById(1)
    assert form.applicant_id == 7
    assert form.idEquipment == 10


def test_user_only_lists_own_forms(client, auth_headers):
    create_form(applicant_id=1, id_equipment=10)
    create_form(applicant_id=2, id_equipment=20)

    response = client.get(
        "/api/maintenance/forms",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] == 1
    assert payload["items"][0]["applicant_id"] == 1
    assert payload["items"][0]["idEquipment"] == 10


def test_admin_lists_all_forms(client, auth_headers):
    create_form(applicant_id=1, id_equipment=10)
    create_form(applicant_id=2, id_equipment=20)

    response = client.get(
        "/api/maintenance/forms",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] == 2
    assert [item["idEquipment"] for item in payload["items"]] == [10, 20]


def test_get_form_by_id_returns_details(client, auth_headers):
    create_form(applicant_id=1, id_equipment=10)

    response = client.get(
        "/api/maintenance/form/1",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["idForm"] == 1
    assert payload["applicant_id"] == 1
    assert payload["idEquipment"] == 10
    assert payload["status"] == "pending"


def test_get_missing_form_returns_404(client, auth_headers):
    response = client.get(
        "/api/maintenance/form/999",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Form not found"}


def test_admin_can_review_form(client, auth_headers):
    create_form()

    response = client.put(
        "/api/maintenance/review/1",
        json={"status": "approved", "reviewNote": "Approved", "reviewer_id": 99},
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "idForm": 1,
        "idEquipment": 10,
        "status": "approved",
        "reviewer_id": 99,
    }


def test_non_admin_cannot_review_form(client, auth_headers):
    create_form()

    response = client.put(
        "/api/maintenance/review/1",
        json={"status": "approved", "reviewer_id": 2},
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 403
    assert response.get_json() == {"error": "Admin privileges required"}


def test_admin_can_mark_form_repairing(client, auth_headers):
    create_form(status="approved")

    response = client.put(
        "/api/maintenance/repair/1",
        json={
            "repair_description": "Replaced display",
            "repair_solution": "Installed new panel",
            "repair_cost": "1200.50",
            "repair_vendor": "Vendor A",
            "repair_person": "Technician A",
        },
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    assert response.get_json() == {"idForm": 1, "status": "repairing"}


def test_admin_can_complete_form(client, auth_headers):
    create_form(status="repairing")

    response = client.put(
        "/api/maintenance/complete/1",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "idForm": 1,
        "idEquipment": 10,
        "status": "completed",
    }


def test_user_can_edit_form_description(client, auth_headers):
    create_form()

    response = client.put(
        "/api/maintenance/edit/form/1",
        json={"issue_description": "Keyboard is broken", "attachments": "image-2"},
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 200
    assert response.get_json() == {"idForm": 1, "status": "pending"}
    form = db.session.get(MaintenanceModel, 1)
    assert form.issue_description == "Keyboard is broken"
    assert form.attachments == "image-2"


def test_delete_form_removes_record(client, auth_headers):
    create_form()

    response = client.delete(
        "/api/maintenance/form/1",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 200
    assert response.get_json() == {}
    assert db.session.get(MaintenanceModel, 1) is None
