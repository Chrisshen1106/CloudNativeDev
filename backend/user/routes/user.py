from flask import Blueprint, request, jsonify
from controllers.user import user_controller


user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/create', methods=['POST'])
def create_user():
    data = request.get_json()
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