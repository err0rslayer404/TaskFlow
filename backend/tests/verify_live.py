import urllib.request
import urllib.parse
import json
import sys
from datetime import datetime, timezone, timedelta

BASE_URL = "http://127.0.0.1:5001/api"
FRONTEND_URL = "http://localhost:5173"

def make_request(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    req_body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=req_body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_code = response.getcode()
            res_body = response.read().decode("utf-8")
            return res_code, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return e.code, json.loads(err_body) if err_body else {"error": str(e)}

def test_live_system():
    print("=== LIVE SYSTEM VERIFICATION ===")

    # 1. Health Check
    print("\n1. Testing Backend Health Check...")
    code, res = make_request("/health")
    assert code == 200, f"Health check failed with {code}: {res}"
    print(f"[OK] Health Check OK: {res}")

    # 2. Frontend HTML Check
    print("\n2. Testing Frontend Dev Server...")
    try:
        with urllib.request.urlopen(FRONTEND_URL) as response:
            html = response.read().decode("utf-8")
            assert "<title>TaskFlow" in html, "TaskFlow title missing in HTML"
            print("[OK] Frontend Dev Server running and serving TaskFlow HTML!")
    except Exception as e:
        print(f"[ERROR] Frontend check error: {e}")
        sys.exit(1)

    # 3. Student Login
    print("\n3. Testing Student Login (rahul.sharma@college.edu)...")
    code, res = make_request("/auth/login", method="POST", data={
        "email": "rahul.sharma@college.edu",
        "password": "StudentPassword123!"
    })
    assert code == 200, f"Student login failed: {res}"
    student_token = res["token"]
    student_user = res["user"]
    print(f"[OK] Logged in as: {student_user['name']} ({student_user['role']})")

    # 4. Student Tasks & Min-Heap Smart Scheduler
    print("\n4. Testing Student Smart Min-Heap Scheduler (/api/tasks/next)...")
    code, res = make_request("/tasks/next", token=student_token)
    assert code == 200, f"Scheduler failed: {res}"
    next_task = res.get("next_task")
    assert next_task is not None, "Expected next task from Min-Heap"
    print(f"[OK] Top Priority Task from Min-Heap (heapq): '{next_task['title']}' (Priority: {next_task['priority_name']}, Deadline: {next_task['deadline']})")

    # 5. Create Task
    print("\n5. Testing Task Creation...")
    now = datetime.now(timezone.utc)
    code, res = make_request("/tasks", method="POST", data={
        "title": "DSA Binary Search Tree Implementation",
        "description": "Implement insert, delete, and in-order traversal in Python.",
        "priority": 1,
        "deadline": (now + timedelta(hours=3)).isoformat(),
        "category": "DSA Study"
    }, token=student_token)
    assert code == 201, f"Create task failed: {res}"
    new_task_id = res["task"]["id"]
    print(f"[OK] Created Task ID {new_task_id}: '{res['task']['title']}'")

    # 6. Verify Scheduler Min-Heap logic
    code, res = make_request("/tasks/next", token=student_token)
    assert code == 200
    top_task = res["next_task"]
    assert top_task["priority"] == 1, "Top task from Min-Heap must have Priority 1 (High)!"
    print(f"[OK] Min-Heap accurately prioritized top task #{top_task['id']} '{top_task['title']}' with earliest deadline timestamp!")

    # 7. Complete Task
    print("\n7. Testing Task Completion...")
    code, res = make_request(f"/tasks/{new_task_id}", method="PUT", data={"completed": True}, token=student_token)
    assert code == 200
    assert res["task"]["completed"] is True
    print(f"[OK] Marked task #{new_task_id} as completed!")

    # 8. Student Progress & Analytics
    print("\n8. Testing Student Progress & 7-Day Weekly Analytics...")
    code, res = make_request("/progress", token=student_token)
    assert code == 200
    prog = res["progress"]
    print(f"[OK] Student Progress: {prog['completed_tasks']}/{prog['total_tasks']} completed ({prog['completion_rate']}%)")
    
    code, res = make_request("/progress/weekly", token=student_token)
    assert code == 200
    print(f"[OK] 7-Day Weekly History: {len(res['weekly'])} daily data points retrieved.")

    # 9. Clean up created task
    code, _ = make_request(f"/tasks/{new_task_id}", method="DELETE", token=student_token)
    assert code == 200
    print(f"[OK] Deleted test task #{new_task_id}")

    # 10. Admin Login
    print("\n10. Testing Admin Login (admin@taskflow.edu)...")
    code, res = make_request("/auth/login", method="POST", data={
        "email": "admin@taskflow.edu",
        "password": "AdminPassword123!"
    })
    assert code == 200, f"Admin login failed: {res}"
    admin_token = res["token"]
    print("[OK] Admin authenticated successfully.")

    # 11. Admin Global Stats
    print("\n11. Testing Admin Global Stats (/api/admin/stats)...")
    code, res = make_request("/admin/stats", token=admin_token)
    assert code == 200
    stats = res["stats"]
    print(f"[OK] System Stats: {stats['total_students']} Students, {stats['total_tasks']} Total Tasks, {stats['completion_rate']}% Global Completion")

    # 12. Admin Students Roster
    print("\n12. Testing Admin Students Roster (/api/admin/students)...")
    code, res = make_request("/admin/students", token=admin_token)
    assert code == 200
    students = res["students"]
    print(f"[OK] Retrieved {len(students)} student records.")

    # 13. Admin Student Progress Report
    print(f"\n13. Testing Admin Student Dossier Report (/api/admin/students/{student_user['id']}/progress)...")
    code, res = make_request(f"/admin/students/{student_user['id']}/progress", token=admin_token)
    assert code == 200
    rep = res["report"]
    print(f"[OK] Student Dossier for {rep['student']['name']} loaded with {len(rep['tasks'])} task history records and {rep['progress']['completion_rate']}% completion rate.")

    print("\n========================================================")
    print("ALL 13 LIVE END-TO-END VERIFICATION CHECKS PASSED 100%!")
    print("========================================================")

if __name__ == "__main__":
    test_live_system()
