from passlib.hash import pbkdf2_sha256

from utils.utils import verify_login


def test_verify_login_accepts_matching_password():
    stored_password = pbkdf2_sha256.hash("correct-password")

    assert verify_login("correct-password", stored_password) is True


def test_verify_login_rejects_non_matching_password():
    stored_password = pbkdf2_sha256.hash("correct-password")

    assert verify_login("wrong-password", stored_password) is False
