from flask import Blueprint, request, jsonify
from backend.middleware.auth import admin_required
from backend.services.admin_service import AdminService
from backend.services.progress_service import ProgressService
from backend.models.task import Task
from backend.models.user import User

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
@admin_required()
def get_stats():
    """Retrieve system-wide aggregated statistics."""
    stats = AdminService.get_system_stats()
    return jsonify({'stats': stats}), 200

@admin_bp.route('/students', methods=['GET'])
@admin_required()
def get_students():
    """Retrieve list of all students with individual task metrics and filters."""
    search = request.args.get('search')
    filter_type = request.args.get('filter')  # all, high_progress, low_progress, overdue, most_active

    students = AdminService.get_students_summary(search=search, filter_type=filter_type)
    return jsonify({
        'students': students,
        'count': len(students)
    }), 200

@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@admin_required()
def get_student(student_id):
    """Retrieve a single student's profile information."""
    student = User.query.filter_by(id=student_id, role='STUDENT').first()
    if not student:
        return jsonify({'error': 'Student not found.'}), 404

    return jsonify({'student': student.to_dict()}), 200

@admin_bp.route('/students/<int:student_id>/tasks', methods=['GET'])
@admin_required()
def get_student_tasks(student_id):
    """Retrieve all tasks for a specific student."""
    student = User.query.filter_by(id=student_id, role='STUDENT').first()
    if not student:
        return jsonify({'error': 'Student not found.'}), 404

    tasks = Task.query.filter_by(student_id=student_id).order_by(Task.deadline.asc()).all()
    return jsonify({
        'student': student.to_dict(),
        'tasks': [t.to_dict() for t in tasks],
        'count': len(tasks)
    }), 200

@admin_bp.route('/students/<int:student_id>/progress', methods=['GET'])
@admin_required()
def get_student_progress_report(student_id):
    """Retrieve full progress report with charts data for an individual student."""
    report = AdminService.get_student_report(student_id=student_id)
    if not report:
        return jsonify({'error': 'Student not found.'}), 404

    return jsonify({'report': report}), 200
