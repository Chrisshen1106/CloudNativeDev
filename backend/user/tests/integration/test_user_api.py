from passlib.hash import pbkdf2_sha256

from controllers.user import user_controller
from models import DepartmentModel, UserModel
from models.database import db


def create_department(name="Engineering"):
    department = DepartmentModel(name=name)
    db.session.add(department)
    db.session.commit()
    return department


def create_user(
    *,
    name="Ada",
    email="ada@example.com",
    password="correct-password",
    department=None,
    role="user",
):
    department = department or create_department()
    user = UserModel(
        name=name,
        email=email,
        password=pbkdf2_sha256.hash(password),
        idDepartment=department.idDepartment,
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_signup_creates_user_with_hashed_password(client, app):
    create_department()

    response = client.post(
        "/api/user/signup",
        json={
            "name": "Ada",
            "email": "ada@example.com",
            "password": "correct-password",
            "idDepartment": 1,
            "role": "user",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {
        "idUser": 1,
        "name": "Ada",
        "email": "ada@example.com",
        "department": "Engineering",
        "role": "user",
    }

    with app.app_context():
        user = user_controller.getUserByEmail("ada@example.com")
        assert user is not None
        assert user.password != "correct-password"
        assert pbkdf2_sha256.verify("correct-password", user.password)


def test_login_returns_jwt_for_valid_credentials(client):
    create_user()

    response = client.post(
        "/api/user/login",
        json={"email": "ada@example.com", "password": "correct-password"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["email"] == "ada@example.com"
    assert payload["department"] == "Engineering"
    assert payload["role"] == "user"
    assert "token" in payload


def test_login_rejects_invalid_credentials(client):
    create_user()

    response = client.post(
        "/api/user/login",
        json={"email": "ada@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 404
    assert response.get_json() == {"message": "email or password is incorrect"}


def test_get_user_by_id_returns_user_without_password(client):
    create_user()

    response = client.get("/api/user/1")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload == {
        "idUser": 1,
        "name": "Ada",
        "email": "ada@example.com",
        "department": "Engineering",
        "role": "user",
    }
    assert "password" not in payload


def test_admin_can_list_users(client):
    create_user(
        name="Grace",
        email="grace@example.com",
        password="admin-password",
        role="admin",
    )
    login_response = client.post(
        "/api/user/login",
        json={"email": "grace@example.com", "password": "admin-password"},
    )
    token = login_response.get_json()["token"]

    response = client.get(
        "/api/user/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json() == [
        {"idUser": 1, "name": "Grace", "department": "Engineering"}
    ]


def test_non_admin_cannot_list_users(client):
    create_user()
    login_response = client.post(
        "/api/user/login",
        json={"email": "ada@example.com", "password": "correct-password"},
    )
    token = login_response.get_json()["token"]

    response = client.get(
        "/api/user/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.get_json() == {"message": "Unauthorized user role"}