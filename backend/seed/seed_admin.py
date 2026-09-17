import os
import sys
from datetime import datetime, timezone, timedelta

# Add parent directory to sys.path so we can import backend packages
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app import create_app
from backend.database.db import db
from backend.models.user import User
from backend.models.task import Task

def seed_database():
    app = create_app()
    with app.app_context():
        db.create_all()

        admin_email = os.getenv('ADMIN_EMAIL', 'admin@taskflow.edu')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'AdminPassword123!')
        admin_name = os.getenv('ADMIN_NAME', 'Dean Admin')

        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name=admin_name,
                email=admin_email,
                role='ADMIN'
            )
            admin.set_password(admin_pass)
            db.session.add(admin)
            print(f"Created Admin account: {admin_email}")
        else:
            print(f"Admin account already exists: {admin_email}")

        # Seed sample students if no students exist
        student_count = User.query.filter_by(role='STUDENT').count()
        if student_count == 0:
            print("Seeding sample students and realistic task datasets...")
            now = datetime.now(timezone.utc)

            students_data = [
                {
                    'name': 'Rahul Sharma',
                    'email': 'rahul.sharma@college.edu',
                    'password': 'StudentPassword123!',
                    'tasks': [
                        {
                            'title': 'Complete Min-Heap Priority Queue Assignment',
                            'description': 'Implement binary heap push and pop algorithms with O(log n) complexity.',
                            'priority': 1,
                            'deadline': now + timedelta(hours=4),
                            'category': 'DSA Study',
                            'completed': False
                        },
                        {
                            'title': 'Database Normalization 3NF Submission',
                            'description': 'Decompose relation schemas to BCNF and 3NF for hospital database.',
                            'priority': 1,
                            'deadline': now - timedelta(days=1), # Overdue
                            'category': 'Database',
                            'completed': False
                        },
                        {
                            'title': 'Full-Stack React Dashboard Layout',
                            'description': 'Build responsive sidebar and statistics grid.',
                            'priority': 2,
                            'deadline': now + timedelta(days=2),
                            'category': 'Web Dev',
                            'completed': True,
                            'completed_at': now - timedelta(days=1)
                        },
                        {
                            'title': 'Computer Networks Socket Programming Lab',
                            'description': 'TCP/UDP client-server packet transmission demo.',
                            'priority': 2,
                            'deadline': now + timedelta(days=3),
                            'category': 'Networks',
                            'completed': True,
                            'completed_at': now - timedelta(days=2)
                        },
                        {
                            'title': 'Prepare for Operating Systems Midterm',
                            'description': 'Review process synchronization, semaphores, and virtual memory.',
                            'priority': 1,
                            'deadline': now + timedelta(days=1),
                            'category': 'Exam Prep',
                            'completed': False
                        },
                        {
                            'title': 'Campus Hackathon Team Registration',
                            'description': 'Form 4-person team and draft problem statement pitch.',
                            'priority': 3,
                            'deadline': now + timedelta(days=6),
                            'category': 'Extracurricular',
                            'completed': True,
                            'completed_at': now - timedelta(days=3)
                        }
                    ]
                },
                {
                    'name': 'Priya Patel',
                    'email': 'priya.patel@college.edu',
                    'password': 'StudentPassword123!',
                    'tasks': [
                        {
                            'title': 'Linear Algebra Eigenvalues Problem Set',
                            'description': 'Solve exercises 4.1 to 4.8 on matrix diagonalization.',
                            'priority': 1,
                            'deadline': now + timedelta(hours=6),
                            'category': 'Mathematics',
                            'completed': False
                        },
                        {
                            'title': 'AI Search Algorithms (A* & Minimax) Notebook',
                            'description': 'Implement heuristic evaluation and tree search.',
                            'priority': 2,
                            'deadline': now + timedelta(days=4),
                            'category': 'AI/ML',
                            'completed': True,
                            'completed_at': now - timedelta(hours=12)
                        },
                        {
                            'title': 'Software Engineering UML Class Diagrams',
                            'description': 'Draw sequence and class architecture diagrams for e-commerce system.',
                            'priority': 3,
                            'deadline': now + timedelta(days=5),
                            'category': 'Software Eng',
                            'completed': True,
                            'completed_at': now - timedelta(days=1)
                        }
                    ]
                },
                {
                    'name': 'Alex Chen',
                    'email': 'alex.chen@college.edu',
                    'password': 'StudentPassword123!',
                    'tasks': [
                        {
                            'title': 'Cybersecurity Cryptography Lab: RSA Implementation',
                            'description': 'Write modular exponentiation and prime generation scripts in Python.',
                            'priority': 1,
                            'deadline': now + timedelta(days=1),
                            'category': 'Security',
                            'completed': False
                        },
                        {
                            'title': 'Cloud Computing Docker Containerization Workshop',
                            'description': 'Build multi-stage Dockerfile and push image to registry.',
                            'priority': 2,
                            'deadline': now - timedelta(days=2), # Overdue
                            'category': 'DevOps',
                            'completed': False
                        },
                        {
                            'title': 'Read Clean Code Chapter 4: Comments and Formatting',
                            'description': 'Self-study reading assignment.',
                            'priority': 3,
                            'deadline': now + timedelta(days=7),
                            'category': 'Reading',
                            'completed': False
                        }
                    ]
                }
            ]

            for s_data in students_data:
                student = User(
                    name=s_data['name'],
                    email=s_data['email'],
                    role='STUDENT'
                )
                student.set_password(s_data['password'])
                db.session.add(student)
                db.session.flush() # get student.id

                for t_data in s_data['tasks']:
                    task = Task(
                        student_id=student.id,
                        title=t_data['title'],
                        description=t_data['description'],
                        priority=t_data['priority'],
                        deadline=t_data['deadline'],
                        category=t_data['category'],
                        completed=t_data['completed'],
                        completed_at=t_data.get('completed_at')
                    )
                    db.session.add(task)
                
                print(f"Created student {student.email} with {len(s_data['tasks'])} tasks.")

        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()
