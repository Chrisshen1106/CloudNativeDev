from passlib.hash import pbkdf2_sha256

def verify_login(provided_password: str, stored_password: str) -> bool:
    is_correct = pbkdf2_sha256.verify(provided_password, stored_password)
    return is_correct