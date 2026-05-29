from flask import Blueprint, request, jsonify
from controllers.department import department_controller

dept_bp = Blueprint('department', __name__, url_prefix='/api/user/department')

@dept_bp.route('/create', methods=['POST'])
def create_department():
    data = request.get_json()
    department = department_controller.create_department(data)
    if department:
        return jsonify(department), 200
    else:
        return jsonify({"message": "Failed to create department"}), 400

@dept_bp.route('/<int:id>', methods=['GET'])
def get_department_by_id(id: int):
    department = department_controller.get_department_by_id(id)
    if department:
        return jsonify(department), 200
    return jsonify({"message": "Department not found"}), 404