import os
import pytest
from datetime import datetime, timezone, timedelta
from backend.app import create_app
from backend.database.db import db
from backend.models.user import User
from backend.models.task import Task

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key-32-bytes-long-super-safe'
    JWT_SECRET_KEY = 'test-jwt-secret-key-32-bytes-long-super-safe'

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def register_user(client, name, email, password):
    return client.post('/api/auth/register', json={
        'name': name,
        'email': email,
        'password': password
    })

def login_user(client, email, password):
    return client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })

def create_admin_user(app_context, email="admin@test.com", password="AdminPass123!"):
    admin = User(name="Admin User", email=email, role="ADMIN")
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    return admin

def test_auth_flow(client):
    # Register student
    reg_res = register_user(client, "John Doe", "john@test.com", "Secret123!")
    assert reg_res.status_code == 201
    assert 'token' in reg_res.json
    assert reg_res.json['user']['role'] == 'STUDENT'

    # Login student
    login_res = login_user(client, "john@test.com", "Secret123!")
    assert login_res.status_code == 200
    token = login_res.json['token']

    # Get /me profile
    me_res = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me_res.status_code == 200
    assert me_res.json['user']['email'] == "john@test.com"

def test_task_crud_and_ownership(client):
    # Register two students
    res_a = register_user(client, "Student A", "a@test.com", "Secret123!")
    token_a = res_a.json['token']

    res_b = register_user(client, "Student B", "b@test.com", "Secret123!")
    token_b = res_b.json['token']

    # Student A creates task
    now_iso = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    create_res = client.post('/api/tasks', json={
        'title': 'Task A1',
        'description': 'Description A1',
        'priority': 1,
        'deadline': now_iso,
        'category': 'DSA'
    }, headers={'Authorization': f'Bearer {token_a}'})
    assert create_res.status_code == 201
    task_id = create_res.json['task']['id']

    # Student A can view task
    get_res = client.get(f'/api/tasks/{task_id}', headers={'Authorization': f'Bearer {token_a}'})
    assert get_res.status_code == 200
    assert get_res.json['task']['title'] == 'Task A1'

    # Student B CANNOT view or modify Student A's task (Isolation check)
    get_b_res = client.get(f'/api/tasks/{task_id}', headers={'Authorization': f'Bearer {token_b}'})
    assert get_b_res.status_code == 404

    update_b_res = client.put(f'/api/tasks/{task_id}', json={'title': 'Hacked Title'}, headers={'Authorization': f'Bearer {token_b}'})
    assert update_b_res.status_code == 404

    delete_b_res = client.delete(f'/api/tasks/{task_id}', headers={'Authorization': f'Bearer {token_b}'})
    assert delete_b_res.status_code == 404

    # Student A updates task
    update_a_res = client.put(f'/api/tasks/{task_id}', json={'completed': True}, headers={'Authorization': f'Bearer {token_a}'})
    assert update_a_res.status_code == 200
    assert update_a_res.json['task']['completed'] is True

def test_smart_scheduler_endpoint(client):
    res = register_user(client, "Scheduler Student", "sched@test.com", "Secret123!")
    token = res.json['token']
    now = datetime.now(timezone.utc)

    # Initially no pending tasks
    next_res = client.get('/api/tasks/next', headers={'Authorization': f'Bearer {token}'})
    assert next_res.status_code == 200
    assert next_res.json['next_task'] is None

    # Create low priority task due in 2 hours
    client.post('/api/tasks', json={
        'title': 'Low Urgency Task',
        'priority': 3,
        'deadline': (now + timedelta(hours=2)).isoformat(),
        'category': 'General'
    }, headers={'Authorization': f'Bearer {token}'})

    # Create high priority task due in 5 hours
    client.post('/api/tasks', json={
        'title': 'High Urgency Task',
        'priority': 1,
        'deadline': (now + timedelta(hours=5)).isoformat(),
        'category': 'Study'
    }, headers={'Authorization': f'Bearer {token}'})

    # Min-Heap Scheduler should prioritize the High priority task (priority=1)
    next_res2 = client.get('/api/tasks/next', headers={'Authorization': f'Bearer {token}'})
    assert next_res2.status_code == 200
    assert next_res2.json['next_task']['title'] == 'High Urgency Task'
    assert next_res2.json['next_task']['priority'] == 1

def test_admin_access_control(client):
    # Register student
    reg_student = register_user(client, "Regular Student", "student@test.com", "Secret123!")
    student_token = reg_student.json['token']

    # Student tries to access admin stats -> 403 Forbidden
    stat_res = client.get('/api/admin/stats', headers={'Authorization': f'Bearer {student_token}'})
    assert stat_res.status_code == 403

    # Create and login admin
    with client.application.app_context():
        create_admin_user(client.application, email="dean@test.com", password="DeanPassword123!")
    
    login_admin = login_user(client, "dean@test.com", "DeanPassword123!")
    admin_token = login_admin.json['token']

    # Admin access succeeds
    admin_stat_res = client.get('/api/admin/stats', headers={'Authorization': f'Bearer {admin_token}'})
    assert admin_stat_res.status_code == 200
    assert 'total_students' in admin_stat_res.json['stats']

    # Admin lists students
    admin_students_res = client.get('/api/admin/students', headers={'Authorization': f'Bearer {admin_token}'})
    assert admin_students_res.status_code == 200
    assert len(admin_students_res.json['students']) >= 1
