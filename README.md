#LIVE URL
https://task-flow-8fj4.vercel.app/


# TaskFlow - Smart Student Task Scheduler & Academic Management System
> Production-grade, full-stack Academic Productivity & Student Management Platform powered by Python Flask, SQLite, custom Min-Heap Priority Queue DSA (`heapq`), and modern SaaS React UI with Recharts.

---

## 1. Project Overview

**TaskFlow** is a comprehensive academic productivity and student management application designed for universities and colleges. Unlike standard To-Do applications, TaskFlow integrates algorithmic scheduling via a **Min-Heap Priority Queue**, robust role-based access control (`STUDENT` vs `ADMIN`), real-time completion analytics, deadline tracking, and student progress reports.

---

## 2. Key Features

### Student Workspace
- **Dual-Mode Dashboard**: Real-time overview of tasks, completion percentage, overdue alerts, and urgent deadlines.
- **Smart Min-Heap Task Scheduler**: Computes and reveals the student's next most urgent assignment using Python's `heapq` Priority Queue in $O(\log n)$ time.
- **Complete Task Manager**: Create, edit, delete, complete, and reopen assignments with search, sorting, and multi-criteria filters.
- **Deadline Status Badges**: Automatically detects `Overdue`, `Due Today`, `Upcoming`, and `Completed` items.
- **Dedicated Progress Analytics**: 7-day productivity history with interactive Recharts bar charts, category progress bars, and priority breakdowns.

### Admin Administration Portal
- **Global Overview**: System-wide statistics including total students, active students, aggregate completion rates, and overdue tasks.
- **Visual Analytics**: Interactive Recharts Pie and Bar charts for global task distribution and priority spreads.
- **Recent Student Activity**: Live audit stream of student task modifications and completions.
- **Student Roster & Filters**: Directory of all students with individual task metrics, progress bars, and filters (`High Progress`, `Low Progress`, `Overdue Tasks`, `Most Active`).
- **Student Dossier & Progress Reports**: Comprehensive individual student audits with complete assignment histories and browser print capability (`window.print()`).

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18 + Vite | Dynamic, component-driven user interface |
| **Styling** | Custom Vanilla CSS (SaaS Theme) | Clean typography, responsive grid, priority borders, zero Tailwind |
| **Charts** | Recharts | Interactive weekly productivity trends & distribution charts |
| **Icons** | Lucide React | Modern feather-style iconography |
| **Networking** | Axios + Interceptors | REST API communication with Bearer JWT injection |
| **Backend** | Python 3 + Flask | Modular REST API service |
| **Database & ORM** | SQLite + SQLAlchemy | Relational persistence with foreign keys and cascade deletion |
| **Authentication** | Flask-JWT-Extended + Werkzeug | JWT authorization and salted SHA256 password hashing |
| **DSA Engine** | `heapq` (Python standard library) | Min-Heap Priority Queue for optimal academic scheduling |

---

## 4. Application Architecture

```
                    React Frontend (Vite + Recharts)
                                  │
                                  │ REST API (JSON / Bearer JWT)
                                  ▼
                            Flask Backend
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
  Authentication API          Task API                Admin API
   (JWT & Password Hash)    (CRUD & Ownership)     (Analytics & Reports)
                                  │                        │
                                  ▼                        ▼
                       Min-Heap Priority Queue       SQLAlchemy ORM
                       (heapq algorithm)                   │
                                  │                        ▼
                                  └─────────────────► SQLite Database
```

---

## 5. DSA Implementation: Priority Queue / Min Heap

The core scheduling engine is implemented in `backend/dsa/priority_queue.py` using Python's `heapq` binary min-heap.

### Heap Key Design
Each pending assignment is pushed to the min-heap as a tuple:
```python
heapq.heappush(self._heap, (task.priority, task.deadline_timestamp, task.id, task))
```

### Order of Precedence
1. **Priority Value**: `1` (High), `2` (Medium), `3` (Low). Lower integer = higher urgency.
2. **Deadline Timestamp**: For identical priorities, the task with the earlier unix timestamp has higher urgency.
3. **Task ID**: Deterministic tie-breaker for tasks with identical priority and deadline.

### Time & Space Complexity

| Operation | Time Complexity | Space Complexity | Description |
|---|---|---|---|
| **Push** (`push`) | $O(\log n)$ | $O(1)$ | Inserts task and maintains binary min-heap invariant |
| **Pop** (`pop`) | $O(\log n)$ | $O(1)$ | Extracts highest-urgency task from root |
| **Peek** (`peek`) | $O(1)$ | $O(1)$ | Inspects root element without removal |
| **Build Heap** (`from_tasks`) | $O(n)$ | $O(n)$ | Constructs heap from list of pending student tasks |

---

## 6. Database Schema

```
Users (users)
├── id (INTEGER, PK)
├── name (VARCHAR)
├── email (VARCHAR, UNIQUE, INDEXED)
├── password_hash (VARCHAR)
├── role (VARCHAR: 'ADMIN' | 'STUDENT')
└── created_at (DATETIME)
       │ 1
       │
       ▼ *
Tasks (tasks)
├── id (INTEGER, PK)
├── student_id (INTEGER, FK -> users.id, INDEXED)
├── title (VARCHAR)
├── description (TEXT)
├── priority (INTEGER: 1=High, 2=Medium, 3=Low)
├── deadline (DATETIME, INDEXED)
├── category (VARCHAR)
├── completed (BOOLEAN, INDEXED)
├── completed_at (DATETIME, NULLABLE)
├── created_at (DATETIME)
└── updated_at (DATETIME)
```

---

## 7. REST API Endpoints

### Authentication
- `POST /api/auth/register` - Create new student account
- `POST /api/auth/login` - Authenticate and return JWT access token
- `GET  /api/auth/me` - Retrieve current user session profile

### Student Tasks & Smart Scheduler
- `GET    /api/tasks` - List & filter student tasks (`search`, `status`, `priority`, `category`, `sort_by`)
- `POST   /api/tasks` - Create a new assignment
- `GET    /api/tasks/<id>` - Retrieve specific task (enforces ownership)
- `PUT    /api/tasks/<id>` - Update task details or toggle completion
- `DELETE /api/tasks/<id>` - Delete task
- `GET    /api/tasks/next` - **Smart Scheduler**: returns highest-priority pending task via Min-Heap

### Student Progress
- `GET /api/progress` - Student completion rates, priority distribution, and category counts
- `GET /api/progress/weekly` - 7-day daily activity trend

### Administration (Role: `ADMIN`)
- `GET /api/admin/stats` - Global KPIs, aggregate distributions, and recent activity
- `GET /api/admin/students` - Student directory with individual progress indicators
- `GET /api/admin/students/<id>` - Student profile
- `GET /api/admin/students/<id>/tasks` - Student task history
- `GET /api/admin/students/<id>/progress` - Complete student dossier with charts data

---

## 8. Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Seed admin and sample student datasets
python seed/seed_admin.py

# Run the backend server (starts on http://127.0.0.1:5001)
python app.py
```

### 2. Frontend Setup
```bash
# In a separate terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite dev server (starts on http://localhost:5173)
npm run dev
```

---

## 9. Development Seed Accounts

For local development and testing, run `python backend/seed/seed_admin.py`.

| Role | Email | Password | Description |
|---|---|---|---|
| **Admin** | `admin@taskflow.edu` | `AdminPassword123!` | System Administrator Portal |
| **Student** | `rahul.sharma@college.edu` | `StudentPassword123!` | Enrolled Student with sample tasks |
| **Student** | `priya.patel@college.edu` | `StudentPassword123!` | Enrolled Student with sample tasks |
| **Student** | `alex.chen@college.edu` | `StudentPassword123!` | Enrolled Student with sample tasks |

*Students can also register new accounts directly from the login page.*

---

## 10. Running Test Suite

```bash
# Run DSA unit tests and API integration tests
python -m pytest backend/tests

# Run live end-to-end verification
python backend/tests/verify_live.py
```
