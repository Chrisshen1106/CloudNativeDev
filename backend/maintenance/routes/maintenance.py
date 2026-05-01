from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from controllers.maintenance import maintenance_controller

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/api')

@maintenance_bp.route('/forms', methods=['GET'])
def get_all_forms():
    try:
        result = maintenance_controller.getAllForms()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 送出維修申請
@maintenance_bp.route('/form', methods=['POST'])
@jwt_required()
def create_form():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        valided_data = maintenance_controller.schema(only=['idEquipment', 'issue_description']).load(data)
        form = maintenance_controller.createForm({**valided_data, 'applicant_id': current_user})
        response = maintenance_controller.schema(only=['idForm', 'status']).dump(form)
        return jsonify(response), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 取得維修申請單詳情
@maintenance_bp.route('/form/<int:id>', methods=['GET'])
@jwt_required()
def get_form_by_id(id: int):
    try:
        form = maintenance_controller.getFormById(id)
        if form:
            response = maintenance_controller.schema().dump(form)
            return jsonify(response), 200
        return jsonify({'error': 'Form not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@maintenance_bp.route('/user/<int:user_id>', methods=['GET'])
def get_all_maintenance_by_user_id(user_id):
    try:
        result = maintenance_controller.getAllMaintenanceByUserId(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# 審核維修申請
@maintenance_bp.route('/form_manager/<int:form_id>/review' , methods=['PUT'])
@jwt_required()
def review_form(form_id: int):
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        data = request.get_json()
        valided_data = maintenance_controller.schema(only=['status']).load(data)
        updated_form = maintenance_controller.updateFormStatusById(form_id, valided_data['status'])
        response = maintenance_controller.schema(only=['idForm', 'status']).dump(updated_form)
        return jsonify(response), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500