from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from collections import defaultdict
from backend.models.task import Task
from backend.models.user import User

class ProgressService:
    @staticmethod
    def get_student_progress(student_id: int) -> Dict[str, Any]:
        """Compute comprehensive real-time progress statistics for a student."""
        tasks = Task.query.filter_by(student_id=student_id).all()
        now = datetime.now(timezone.utc)

        total_tasks = len(tasks)
        completed_tasks = 0
        pending_tasks = 0
        overdue_tasks = 0
        due_today_tasks = 0
        high_priority_tasks = 0
        medium_priority_tasks = 0
        low_priority_tasks = 0

        category_map = defaultdict(lambda: {'total': 0, 'completed': 0, 'pending': 0})
        priority_map = {
            1: {'name': 'High', 'total': 0, 'completed': 0, 'pending': 0},
            2: {'name': 'Medium', 'total': 0, 'completed': 0, 'pending': 0},
            3: {'name': 'Low', 'total': 0, 'completed': 0, 'pending': 0}
        }

        today_start = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
        today_end = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)

        for task in tasks:
            cat = task.category or 'General'
            category_map[cat]['total'] += 1
            
            prio = task.priority if task.priority in priority_map else 2
            priority_map[prio]['total'] += 1

            dl = task.deadline
            if dl.tzinfo is None:
                dl = dl.replace(tzinfo=timezone.utc)

            if task.completed:
                completed_tasks += 1
                category_map[cat]['completed'] += 1
                priority_map[prio]['completed'] += 1
            else:
                pending_tasks += 1
                category_map[cat]['pending'] += 1
                priority_map[prio]['pending'] += 1
                
                if dl < now:
                    overdue_tasks += 1
                elif today_start <= dl <= today_end:
                    due_today_tasks += 1

            if task.priority == 1:
                high_priority_tasks += 1
            elif task.priority == 2:
                medium_priority_tasks += 1
            elif task.priority == 3:
                low_priority_tasks += 1

        completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

        # Format categories list
        categories_data = [
            {
                'category': cat_name,
                'total': data['total'],
                'completed': data['completed'],
                'pending': data['pending'],
                'rate': round((data['completed'] / data['total'] * 100), 1) if data['total'] > 0 else 0.0
            }
            for cat_name, data in sorted(category_map.items(), key=lambda x: x[1]['total'], reverse=True)
        ]

        return {
            'student_id': student_id,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'due_today_tasks': due_today_tasks,
            'high_priority_tasks': high_priority_tasks,
            'medium_priority_tasks': medium_priority_tasks,
            'low_priority_tasks': low_priority_tasks,
            'completion_rate': completion_rate,
            'categories': categories_data,
            'priorities': [
                priority_map[1],
                priority_map[2],
                priority_map[3]
            ]
        }

    @staticmethod
    def get_weekly_progress(student_id: int) -> List[Dict[str, Any]]:
        """
        Compute daily completed vs created tasks over the last 7 days.
        Returns array of { day: 'Mon', date: 'YYYY-MM-DD', completed: N, created: M }
        """
        now = datetime.now(timezone.utc)
        days_data = []

        # Iterate past 7 days from (today - 6 days) to today
        for i in range(6, -1, -1):
            day_date = (now - timedelta(days=i)).date()
            day_start = datetime(day_date.year, day_date.month, day_date.day, 0, 0, 0, tzinfo=timezone.utc)
            day_end = datetime(day_date.year, day_date.month, day_date.day, 23, 59, 59, tzinfo=timezone.utc)

            # Query tasks completed on this day
            completed_count = Task.query.filter(
                Task.student_id == student_id,
                Task.completed == True,
                Task.completed_at >= day_start,
                Task.completed_at <= day_end
            ).count()

            # Query tasks created on this day
            created_count = Task.query.filter(
                Task.student_id == student_id,
                Task.created_at >= day_start,
                Task.created_at <= day_end
            ).count()

            days_data.append({
                'day': day_date.strftime('%a'),
                'date': day_date.isoformat(),
                'completed': completed_count,
                'created': created_count
            })

        return days_data
