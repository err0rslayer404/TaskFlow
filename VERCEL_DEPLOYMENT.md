# Vercel Deployment Guide

## 1. GitHub
Push this entire project as ONE repository:

    taskschedular/
    ├── frontend/
    ├── backend/
    ├── .gitignore
    └── README.md

Do not commit `.env`, databases, `node_modules`, `dist`, or `__pycache__`.

## 2. Backend on Vercel
Create a Vercel project from the same GitHub repository.
Set Root Directory to `backend`.

Environment variables:
- DATABASE_URL = your PostgreSQL connection string
- JWT_SECRET_KEY = a long random secret
- SECRET_KEY = a long random secret
- FRONTEND_URL = your deployed frontend URL

If the backend uses SQLAlchemy with SQLite in the current code, change the production database URL to PostgreSQL before using it with real accounts/data.

## 3. Frontend on Vercel
Create a second Vercel project from the same GitHub repository.
Set Root Directory to `frontend`.

Build command:
    npm run build

Output directory:
    dist

Environment variable:
    VITE_API_URL=https://YOUR-BACKEND-PROJECT.vercel.app/api

Redeploy after setting the variable.

## 4. Local development
Frontend:
    cd frontend
    npm install
    npm run dev

Backend:
    cd backend
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python app.py

## 5. Database
Use PostgreSQL for Vercel production. SQLite is suitable for local development/testing, but serverless deployments should use an external persistent database.
