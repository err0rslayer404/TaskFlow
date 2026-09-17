from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.progress_service import ProgressService

progress_bp = Blueprint('progress', __name__, url_prefix='/api/progress')

@progress_bp.route('', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = int(get_jwt_identity())
    progress_data = ProgressService.get_student_progress(student_id=user_id)
    return jsonify({'progress': progress_data}), 200

@progress_bp.route('/weekly', methods=['GET'])
@jwt_required()
def get_weekly_progress():
    user_id = int(get_jwt_identity())
    weekly_data = ProgressService.get_weekly_progress(student_id=user_id)
    return jsonify({'weekly': weekly_data}), 200
