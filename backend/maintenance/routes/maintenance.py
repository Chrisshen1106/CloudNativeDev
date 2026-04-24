from flask import Blueprint, request, jsonify
from controllers.maintenance import maintenance_controller

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/create', methods=['POST'])
def create_maintenance():
    try:
        data = request.get_json()
        result = maintenance_controller.createMaintenance(data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@maintenance_bp.route('/<int:id>', methods=['GET'])
def get_maintenance_by_id(id):
    try:
        result = maintenance_controller.getMaintenanceById(id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
@maintenance_bp.route('/user/<int:user_id>', methods=['GET'])
def get_all_maintenance_by_user_id(user_id):
    try:
        result = maintenance_controller.getAllMaintenanceByUserId(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404