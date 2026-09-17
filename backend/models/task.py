from datetime import datetime, timezone
from backend.database.db import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.Integer, nullable=False, default=2)  # 1 = High, 2 = Medium, 3 = Low
    deadline = db.Column(db.DateTime, nullable=False, index=True)
    category = db.Column(db.String(80), nullable=True, default='General')
    completed = db.Column(db.Boolean, default=False, nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def priority_name(self) -> str:
        mapping = {1: 'High', 2: 'Medium', 3: 'Low'}
        return mapping.get(self.priority, 'Medium')

    @property
    def status_label(self) -> str:
        if self.completed:
            return 'completed'
        
        now = datetime.now(timezone.utc)
        # Ensure deadline is timezone-aware for comparison if needed
        dl = self.deadline
        if dl.tzinfo is None:
            dl = dl.replace(tzinfo=timezone.utc)
        
        if dl < now:
            return 'overdue'
        
        if dl.date() == now.date():
            return 'due_today'
            
        return 'upcoming'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'title': self.title,
            'description': self.description or '',
            'priority': self.priority,
            'priority_name': self.priority_name,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'category': self.category or 'General',
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status_label,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Task #{self.id} "{self.title}" P:{self.priority} Comp:{self.completed}>'
