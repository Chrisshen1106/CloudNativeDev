def test_create_department_and_fetch_by_id(client):
    create_response = client.post(
        "/api/user/department/create",
        json={"name": "Engineering"},
    )

    assert create_response.status_code == 200
    created_department = create_response.get_json()
    assert created_department["name"] == "Engineering"
    assert created_department["idDepartment"] == 1

    get_response = client.get("/api/user/department/1")

    assert get_response.status_code == 200
    assert get_response.get_json() == created_department


def test_fetch_missing_department_returns_404(client):
    response = client.get("/api/user/department/999")

    assert response.status_code == 404
    assert response.get_json() == {"message": "Department not found"}
