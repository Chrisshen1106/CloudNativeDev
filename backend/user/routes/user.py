import datetime
from flask import Blueprint, request, jsonify
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from utils.utils import verify_login
from controllers.user import user_controller


user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()
    data['password'] = pbkdf2_sha256.hash(data['password'])
    user = user_controller.create_user(data)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"message": "Failed to create user"}), 400

@user_bp.route('/<int:id>', methods=['GET'])
def get_user_by_id(id: int):
    try:
        user = user_controller.get_user_by_id(id)
        if user:
            return jsonify(user), 200
        return jsonify({"message": "User not found"}), 404
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    
@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        validated_data = user_controller.schema(only=['email', 'password']).load(data)
        user = user_controller.get_user_by_email(validated_data['email'])
        if user and verify_login(validated_data['password'], user.password):
            response = user_controller.schema().dump(user)
            response['token'] = create_access_token(identity=str(user.idUser), additional_claims={"role": user.role}, expires_delta=datetime.timedelta(days=1))
            return jsonify(response), 200
        return jsonify({"message": "email or password is incorrect"}), 404
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500
    
# 取得所有使用者
@user_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        role = get_jwt().get("role", "")
        if role != "admin":
            return jsonify({"message": "Unauthorized user role"}), 403
        users = user_controller.get_all_users()
        response = user_controller.schema(many=True, only=['idUser', 'name', 'department']).dump(users)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500

# 測試在 eks 上能不能正常連線到 S3
@user_bp.route('/users_test_s3', methods=['GET'])
# @jwt_required()  # 1. 先註解掉驗證
def get_all_users_test_s3():
    try:
        users = user_controller.get_all_users()
        response = user_controller.schema(many=True, only=['idUser', 'name', 'department']).dump(users)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500