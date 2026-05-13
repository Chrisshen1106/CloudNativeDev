from app import create_app
from flask_jwt_extended import create_access_token

app = create_app()
with app.app_context():
    # 生成 Admin Token (idUser=12)
    admin_token = create_access_token(identity='12', additional_claims={'role': 'admin'})
    print("--- Admin Token (User ID: 12) ---")
    print(admin_token)
    print()

    # 生成 User Token (idUser=11)
    user_token = create_access_token(identity='5', additional_claims={'role': 'user'})
    print("--- User Token (User ID: 5) ---")
    print(user_token)