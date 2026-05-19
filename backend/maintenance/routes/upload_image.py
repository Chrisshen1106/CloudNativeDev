from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from botocore.exceptions import ClientError
import uuid
from controllers.image import image_controller
from utils.s3_bucket import bucket_manager


uploadImg_bp = Blueprint('uploadImg', __name__, url_prefix='/api/images')

@uploadImg_bp.route("/upload-url", methods=["POST"])
@jwt_required()
def create_upload_url():
    """
    取得 S3 presigned PUT URL。
    """
    user_id = get_jwt_identity()

    data = image_controller.schema(only=["fileName", "contentType"]).load(request.get_json())    
    fileName = data.get("fileName")
    contentType = data.get("contentType")

    if not fileName:
        return jsonify({"error": "fileName is required"}), 400

    if contentType not in bucket_manager.ALLOWED_CONTENT_TYPES:
        return jsonify({"error": "unsupported image type"}), 400
    
    image_id = str(uuid.uuid4())
    ext = bucket_manager.ALLOWED_CONTENT_TYPES[contentType]
    object_key = f"users/{user_id}/images/{image_id}.{ext}"
    
    new_image = {
        "image_id": image_id,
        "user_id": user_id,
        "bucket": bucket_manager.bucket_name,
        "object_key": object_key,
        "fileName": fileName,
        "contentType": contentType,
    }
    new_image = image_controller.schema().load(new_image)
    image_controller.createImage(new_image)
    
    try:
        upload_url = bucket_manager.generate_upload_url(object_key, contentType)
    except ClientError as e:
        return jsonify({"error": "failed to create upload url"}), 500

    return jsonify({
        "imageId": image_id,
        "uploadUrl": upload_url,
    }), 200


@uploadImg_bp.route("/upload-url/<string:image_id>", methods=["GET"])
@jwt_required()
def create_read_url(image_id: str):
    """
    取得 S3 presigned GET URL
    """
    user_id = get_jwt_identity()

    if not image_id:
        return jsonify({"error": "imageId is required"}), 400

    image = image_controller.getImageByImageId(image_id)
    if not image or image.user_id != user_id:
        return jsonify({"error": "image not found"}), 404

    try:
        read_url = bucket_manager.generate_read_url(image.object_key)
    except ClientError as e:
        return jsonify({"error": "failed to create read url"}), 500

    return jsonify({
        "readUrl": read_url,
    }), 200