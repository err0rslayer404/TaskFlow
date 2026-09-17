from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.task_service import TaskService
from backend.models.user import User

task_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@task_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())
    
    search = request.args.get('search')
    status_filter = request.args.get('status')
    priority_arg = request.args.get('priority')
    priority_filter = int(priority_arg) if priority_arg and priority_arg.isdigit() else None
    category_filter = request.args.get('category')
    sort_by = request.args.get('sort_by')

    tasks = TaskService.get_student_tasks(
        student_id=user_id,
        search=search,
        status_filter=status_filter,
        priority_filter=priority_filter,
        category_filter=category_filter,
        sort_by=sort_by
    )

    return jsonify({
        'tasks': [task.to_dict() for task in tasks],
        'count': len(tasks)
    }), 200

@task_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    try:
        task = TaskService.create_task(student_id=user_id, data=data)
        return jsonify({
            'message': 'Task created successfully.',
            'task': task.to_dict()
        }), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to create task: {str(e)}'}), 500

@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())
    task = TaskService.get_task_by_id(task_id=task_id, student_id=user_id)
    if not task:
        return jsonify({'error': 'Task not found or access denied.'}), 404

    return jsonify({'task': task.to_dict()}), 200

@task_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    try:
        task = TaskService.update_task(task_id=task_id, student_id=user_id, data=data)
        return jsonify({
            'message': 'Task updated successfully.',
            'task': task.to_dict()
        }), 200
    except LookupError as le:
        return jsonify({'error': str(le)}), 404
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update task: {str(e)}'}), 500

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())
    try:
        TaskService.delete_task(task_id=task_id, student_id=user_id)
        return jsonify({'message': 'Task deleted successfully.'}), 200
    except LookupError as le:
        return jsonify({'error': str(le)}), 404
    except Exception as e:
        return jsonify({'error': f'Failed to delete task: {str(e)}'}), 500

@task_bp.route('/next', methods=['GET'])
@jwt_required()
def get_next_task():
    """
    Smart Scheduler Endpoint:
    Uses TaskPriorityQueue (Min-Heap using heapq) to return the most urgent task.
    """
    user_id = int(get_jwt_identity())
    next_task = TaskService.get_next_scheduled_task(student_id=user_id)

    if not next_task:
        return jsonify({
            'message': 'No pending tasks in queue.',
            'next_task': None
        }), 200

    return jsonify({
        'message': 'Next priority task retrieved via Min-Heap scheduler.',
        'next_task': next_task.to_dict()
    }), 200
