from models import db, Department, User, Equipment


def create_user(n=1):
    dept = Department(name=f"Dept-{n}")
    db.session.add(dept)
    db.session.flush()
    user = User(
        name=f"User {n}",
        email=f"user{n}@test.com",
        password="hashed",
        idDepartment=dept.idDepartment,
        role="user",
    )
    db.session.add(user)
    db.session.commit()
    return user


def create_equipment(user_id, name="Test Laptop", status="in_use"):
    e = Equipment(idUser=user_id, name=name, status=status, version=0)
    db.session.add(e)
    db.session.commit()
    return e


# --- Create ---

def test_admin_can_create_asset(client, auth_headers):
    user = create_user(1)

    response = client.post(
        "/api/asset/assets",
        json={"name": "New Laptop", "idUser": user.idUser},
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 201
    assert "id" in response.get_json()


def test_non_admin_cannot_create_asset(client, auth_headers):
    response = client.post(
        "/api/asset/assets",
        json={"name": "New Laptop", "idUser": 1},
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 403
    assert response.get_json() == {"message": "僅管理員可新增資產"}


def test_create_asset_without_body_returns_400(client, auth_headers):
    response = client.post(
        "/api/asset/assets",
        json={},
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "未提供資料"}


# --- List ---

def test_user_sees_only_own_assets(client, auth_headers):
    user1 = create_user(1)
    user2 = create_user(2)
    create_equipment(user1.idUser, name="Laptop A")
    create_equipment(user2.idUser, name="Laptop B")

    response = client.get(
        "/api/asset/user",
        headers=auth_headers(user_id=user1.idUser, role="user"),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["total"] == 1
    assert payload["items"][0]["idUser"] == user1.idUser


def test_admin_sees_all_assets(client, auth_headers):
    user1 = create_user(1)
    user2 = create_user(2)
    create_equipment(user1.idUser, name="Laptop A")
    create_equipment(user2.idUser, name="Laptop B")

    response = client.get(
        "/api/asset/user",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    assert response.get_json()["total"] == 2


# --- Get by ID ---

def test_get_asset_returns_full_details(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser, name="My Laptop")

    response = client.get(
        f"/api/asset/assets/{equipment.idEquipment}",
        headers=auth_headers(user_id=user.idUser, role="user"),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["name"] == "My Laptop"
    assert payload["status"] == "in_use"
    assert payload["maintenanceHistory"] == []


def test_get_missing_asset_returns_404(client, auth_headers):
    response = client.get(
        "/api/asset/assets/999",
        headers=auth_headers(user_id=1, role="user"),
    )

    assert response.status_code == 404


# --- Update (including optimistic locking) ---

def test_update_success(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)

    response = client.put(
        f"/api/asset/assets/{equipment.idEquipment}",
        json={"name": "Updated Laptop", "version": 0},
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    assert response.get_json() == {"success": True}


def test_version_increments_after_update(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)
    asset_id = equipment.idEquipment
    token_headers = auth_headers(user_id=99, role="admin")

    client.put(
        f"/api/asset/assets/{asset_id}",
        json={"name": "v1", "version": 0},
        headers=token_headers,
    )

    response = client.put(
        f"/api/asset/assets/{asset_id}",
        json={"name": "v2", "version": 1},
        headers=token_headers,
    )

    assert response.status_code == 200


def test_conflict_returns_409_with_asset(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)

    response = client.put(
        f"/api/asset/assets/{equipment.idEquipment}",
        json={"name": "Stale Update", "version": 99},
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 409
    body = response.get_json()
    assert body["success"] is False
    assert body["content"]["version"] == 0


def test_conflict_asset_contains_latest_data(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)
    asset_id = equipment.idEquipment
    token_headers = auth_headers(user_id=99, role="admin")

    client.put(
        f"/api/asset/assets/{asset_id}",
        json={"name": "Someone Else", "version": 0},
        headers=token_headers,
    )

    response = client.put(
        f"/api/asset/assets/{asset_id}",
        json={"name": "My Change", "version": 0},
        headers=token_headers,
    )

    assert response.status_code == 409
    asset = response.get_json()["content"]
    assert asset["name"] == "Someone Else"
    assert asset["version"] == 1


def test_missing_version_returns_400(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)

    response = client.put(
        f"/api/asset/assets/{equipment.idEquipment}",
        json={"name": "No Version"},
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 400


def test_stale_update_does_not_overwrite(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)
    asset_id = equipment.idEquipment
    token_headers = auth_headers(user_id=99, role="admin")

    client.put(
        f"/api/asset/assets/{asset_id}",
        json={"name": "Correct Update", "version": 0},
        headers=token_headers,
    )
    client.put(
        f"/api/asset/assets/{asset_id}",
        json={"name": "Overwrite Attempt", "version": 0},
        headers=token_headers,
    )

    eq = db.session.get(Equipment, asset_id)
    assert eq.name == "Correct Update"


def test_non_admin_cannot_update_asset(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)

    response = client.put(
        f"/api/asset/assets/{equipment.idEquipment}",
        json={"name": "Hack", "version": 0},
        headers=auth_headers(user_id=user.idUser, role="user"),
    )

    assert response.status_code == 403
    assert response.get_json() == {"message": "僅管理員可編輯資產"}


# --- Delete ---

def test_admin_can_delete_asset(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser)
    asset_id = equipment.idEquipment

    response = client.delete(
        f"/api/asset/assets/{asset_id}",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    assert response.get_json() == {"success": True}
    assert db.session.get(Equipment, asset_id) is None


# --- Status ---

def test_admin_can_set_status_repairing(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser, status="in_use")

    response = client.put(
        f"/api/asset/status/repairing/{equipment.idEquipment}",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    eq = db.session.get(Equipment, equipment.idEquipment)
    assert eq.status == "repairing"


def test_admin_can_set_status_in_use(client, auth_headers):
    user = create_user(1)
    equipment = create_equipment(user.idUser, status="repairing")

    response = client.put(
        f"/api/asset/status/in_use/{equipment.idEquipment}",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 200
    eq = db.session.get(Equipment, equipment.idEquipment)
    assert eq.status == "in_use"


def test_set_status_on_missing_asset_returns_404(client, auth_headers):
    response = client.put(
        "/api/asset/status/repairing/999",
        headers=auth_headers(user_id=99, role="admin"),
    )

    assert response.status_code == 404
