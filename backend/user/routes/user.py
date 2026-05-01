from flask import Blueprint, request, jsonify
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from utils.utils import verify_login
from controllers.user import user_controller


user_bp = Blueprint('user', __name__, url_prefix='/api')

@user_bp.route('/signup', methods=['POST'])
def create_user():
    data = request.get_json()
    data['password'] = pbkdf2_sha256.hash(data['password'])
    user = user_controller.createUser(data)
    if user:
        return jsonify(user), 200
    else:
        return jsonify({"message": "Failed to create user"}), 400

@user_bp.route('/<int:id>', methods=['GET'])
def get_user_by_id(id: int):
    try:
        user = user_controller.getUserById(id)
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
        user = user_controller.getUserByEmail(validated_data['email'])
        if user and verify_login(validated_data['password'], user.password):
            response = user_controller.schema().dump(user)
            response['token'] = create_access_token(identity=str(user.idUser))
            return jsonify(response), 200
        return jsonify({"message": "email or password is incorrect"}), 404
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500
    
@user_bp.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_user_by_id():
    try:
        current_user_id = get_jwt_identity()
        if user_controller.deleteUserById(current_user_id):
            return jsonify({"message": "User deleted successfully"}), 200
        return jsonify({"message": "User not found"}), 404
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Internal server error: {str(e)}"}), 500