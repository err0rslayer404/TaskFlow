# LIVE URL
https://task-flow-8fj4.vercel.app/


# TaskFlow - Smart Student Task Scheduler & Academic Management System
> Production-grade, full-stack Academic Productivity & Student Management Platform powered by Python Flask, SQLite, custom Min-Heap Priority Queue DSA (`heapq`), and modern SaaS React UI with Recharts
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

