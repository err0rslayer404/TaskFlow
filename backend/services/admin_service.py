from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.database.db import db
from backend.models.user import User
from backend.models.task import Task
from backend.services.progress_service import ProgressService

class AdminService:
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        """Compute aggregate system-wide statistics across all students and tasks."""
        students = User.query.filter_by(role='STUDENT').all()
        total_students = len(students)

        tasks = Task.query.all()
        total_tasks = len(tasks)
        now = datetime.now(timezone.utc)

        completed_tasks = 0
        pending_tasks = 0
        overdue_tasks = 0
        high_priority = 0
        medium_priority = 0
        low_priority = 0

        active_student_ids = set()

        for task in tasks:
            active_student_ids.add(task.student_id)
            if task.priority == 1:
                high_priority += 1
            elif task.priority == 2:
                medium_priority += 1
            elif task.priority == 3:
                low_priority += 1

            if task.completed:
                completed_tasks += 1
            else:
                pending_tasks += 1
                dl = task.deadline
                if dl.tzinfo is None:
                    dl = dl.replace(tzinfo=timezone.utc)
                if dl < now:
                    overdue_tasks += 1

        active_students = len(active_student_ids)
        completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

        # Recent task activity (latest 10 tasks)
        recent_tasks = Task.query.order_by(Task.updated_at.desc()).limit(10).all()
        recent_activity = []
        for t in recent_tasks:
            student = db.session.get(User, t.student_id)
            recent_activity.append({
                'task_id': t.id,
                'task_title': t.title,
                'student_name': student.name if student else 'Unknown',
                'student_email': student.email if student else '',
                'completed': t.completed,
                'priority_name': t.priority_name,
                'updated_at': t.updated_at.isoformat() if t.updated_at else None
            })

        return {
            'total_students': total_students,
            'active_students': active_students,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': completion_rate,
            'task_distribution': {
                'completed': completed_tasks,
                'pending': pending_tasks - overdue_tasks if (pending_tasks - overdue_tasks) >= 0 else 0,
                'overdue': overdue_tasks
            },
            'priority_distribution': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            },
            'recent_activity': recent_activity
        }

    @staticmethod
    def get_students_summary(search: Optional[str] = None, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch list of all students with individual task metrics and progress."""
        query = User.query.filter_by(role='STUDENT')
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (User.name.ilike(search_term)) |
                (User.email.ilike(search_term))
            )

        students = query.order_by(User.created_at.desc()).all()
        now = datetime.now(timezone.utc)
        results = []

        for student in students:
            tasks = Task.query.filter_by(student_id=student.id).all()
            total = len(tasks)
            completed = sum(1 for t in tasks if t.completed)
            pending = total - completed
            overdue = sum(1 for t in tasks if not t.completed and (t.deadline.replace(tzinfo=timezone.utc) if t.deadline.tzinfo is None else t.deadline) < now)
            high_priority = sum(1 for t in tasks if t.priority == 1)
            rate = round((completed / total * 100), 1) if total > 0 else 0.0

            results.append({
                'id': student.id,
                'name': student.name,
                'email': student.email,
                'joined_date': student.created_at.strftime('%b %d, %Y') if student.created_at else 'N/A',
                'total_tasks': total,
                'completed_tasks': completed,
                'pending_tasks': pending,
                'overdue_tasks': overdue,
                'high_priority_tasks': high_priority,
                'completion_rate': rate
            })

        # Apply admin filter types
        if filter_type == 'high_progress':
            results = [s for s in results if s['completion_rate'] >= 75.0]
        elif filter_type == 'low_progress':
            results = [s for s in results if s['completion_rate'] < 50.0]
        elif filter_type == 'overdue':
            results = [s for s in results if s['overdue_tasks'] > 0]
        elif filter_type == 'most_active':
            results = sorted(results, key=lambda s: s['total_tasks'], reverse=True)

        return results

    @staticmethod
    def get_student_report(student_id: int) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive student progress report for admin view."""
        student = User.query.filter_by(id=student_id, role='STUDENT').first()
        if not student:
            return None

        progress = ProgressService.get_student_progress(student_id)
        weekly = ProgressService.get_weekly_progress(student_id)
        tasks = Task.query.filter_by(student_id=student_id).order_by(Task.deadline.asc()).all()

        return {
            'student': student.to_dict(),
            'progress': progress,
            'weekly_performance': weekly,
            'tasks': [t.to_dict() for t in tasks]
        }
