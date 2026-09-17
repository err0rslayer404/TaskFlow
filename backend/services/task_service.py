from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from backend.database.db import db
from backend.models.task import Task
from backend.dsa.priority_queue import TaskPriorityQueue

class TaskService:
    @staticmethod
    def get_student_tasks(
        student_id: int,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        priority_filter: Optional[int] = None,
        category_filter: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[Task]:
        """Fetch and filter tasks belonging to a specific student."""
        query = Task.query.filter_by(student_id=student_id)

        # Search filter (title, description, category)
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                (Task.title.ilike(search_term)) |
                (Task.description.ilike(search_term)) |
                (Task.category.ilike(search_term))
            )

        # Priority filter (1, 2, 3)
        if priority_filter is not None:
            query = query.filter_by(priority=priority_filter)

        # Category filter
        if category_filter and category_filter.lower() != 'all':
            query = query.filter(Task.category.ilike(category_filter.strip()))

        # Status filter
        now = datetime.now(timezone.utc)
        if status_filter:
            status_lower = status_filter.lower()
            if status_lower == 'completed':
                query = query.filter_by(completed=True)
            elif status_lower == 'pending':
                query = query.filter_by(completed=False)
            elif status_lower == 'overdue':
                query = query.filter(Task.completed == False, Task.deadline < now)
            elif status_lower == 'due_today':
                # Matching current date
                today_start = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=timezone.utc)
                today_end = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)
                query = query.filter(
                    Task.completed == False,
                    Task.deadline >= today_start,
                    Task.deadline <= today_end
                )
            elif status_lower == 'upcoming':
                query = query.filter(Task.completed == False, Task.deadline > now)
            elif status_lower == 'high_priority':
                query = query.filter_by(priority=1)

        # Sorting
        if sort_by == 'deadline_asc':
            query = query.order_by(Task.deadline.asc())
        elif sort_by == 'deadline_desc':
            query = query.order_by(Task.deadline.desc())
        elif sort_by == 'priority_asc':
            query = query.order_by(Task.priority.asc(), Task.deadline.asc())
        elif sort_by == 'created_desc':
            query = query.order_by(Task.created_at.desc())
        else:
            # Default sorting: active tasks first, priority ascending, deadline ascending
            query = query.order_by(Task.completed.asc(), Task.priority.asc(), Task.deadline.asc())

        return query.all()

    @staticmethod
    def create_task(student_id: int, data: Dict[str, Any]) -> Task:
        """Create a new task for the student."""
        title = data.get('title', '').strip()
        if not title:
            raise ValueError('Task title is required.')

        deadline_raw = data.get('deadline')
        if not deadline_raw:
            raise ValueError('Task deadline is required.')

        if isinstance(deadline_raw, str):
            try:
                # Handle ISO formatted strings
                # Support "YYYY-MM-DDTHH:MM" and "YYYY-MM-DDTHH:MM:SS" with/without Z
                clean_iso = deadline_raw.replace('Z', '+00:00')
                deadline = datetime.fromisoformat(clean_iso)
            except Exception:
                raise ValueError('Invalid deadline format. Use ISO format (e.g. YYYY-MM-DDTHH:MM).')
        elif isinstance(deadline_raw, datetime):
            deadline = deadline_raw
        else:
            raise ValueError('Invalid deadline data type.')

        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)

        priority = int(data.get('priority', 2))
        if priority not in (1, 2, 3):
            raise ValueError('Priority must be 1 (High), 2 (Medium), or 3 (Low).')

        description = data.get('description', '')
        category = data.get('category', 'General')

        task = Task(
            student_id=student_id,
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            category=category,
            completed=False
        )

        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def get_task_by_id(task_id: int, student_id: Optional[int] = None) -> Optional[Task]:
        """Fetch a task by ID, optionally enforcing student ownership."""
        task = db.session.get(Task, task_id)
        if not task:
            return None
        if student_id is not None and task.student_id != student_id:
            return None
        return task

    @staticmethod
    def update_task(task_id: int, student_id: int, data: Dict[str, Any]) -> Task:
        """Update an existing task owned by the student."""
        task = TaskService.get_task_by_id(task_id, student_id)
        if not task:
            raise LookupError('Task not found or access denied.')

        if 'title' in data:
            title = str(data['title']).strip()
            if not title:
                raise ValueError('Task title cannot be empty.')
            task.title = title

        if 'description' in data:
            task.description = data['description']

        if 'priority' in data:
            priority = int(data['priority'])
            if priority not in (1, 2, 3):
                raise ValueError('Priority must be 1 (High), 2 (Medium), or 3 (Low).')
            task.priority = priority

        if 'deadline' in data:
            deadline_raw = data['deadline']
            if isinstance(deadline_raw, str):
                try:
                    clean_iso = deadline_raw.replace('Z', '+00:00')
                    task.deadline = datetime.fromisoformat(clean_iso)
                except Exception:
                    raise ValueError('Invalid deadline format.')
            elif isinstance(deadline_raw, datetime):
                task.deadline = deadline_raw
            if task.deadline.tzinfo is None:
                task.deadline = task.deadline.replace(tzinfo=timezone.utc)

        if 'category' in data:
            task.category = data['category']

        if 'completed' in data:
            was_completed = task.completed
            new_completed = bool(data['completed'])
            task.completed = new_completed
            if new_completed and not was_completed:
                task.completed_at = datetime.now(timezone.utc)
            elif not new_completed:
                task.completed_at = None

        db.session.commit()
        return task

    @staticmethod
    def delete_task(task_id: int, student_id: int) -> bool:
        """Delete a task owned by the student."""
        task = TaskService.get_task_by_id(task_id, student_id)
        if not task:
            raise LookupError('Task not found or access denied.')

        db.session.delete(task)
        db.session.commit()
        return True

    @staticmethod
    def get_next_scheduled_task(student_id: int) -> Optional[Task]:
        """
        Smart Scheduler:
        1. Query incomplete tasks for the student.
        2. Insert all incomplete tasks into TaskPriorityQueue (Min-Heap using heapq).
        3. Pop/peek the highest priority task (High priority -> Earlier deadline -> Lower ID).
        """
        incomplete_tasks = Task.query.filter_by(student_id=student_id, completed=False).all()
        if not incomplete_tasks:
            return None

        # Build Min-Heap Priority Queue
        pq = TaskPriorityQueue.from_tasks(incomplete_tasks)
        
        # Pop the highest urgency task from Min-Heap
        next_task = pq.pop()
        return next_task
