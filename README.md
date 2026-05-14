# Team Task Manager

A full-stack collaborative task management web application built with FastAPI, PostgreSQL, and Vanilla JavaScript.

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI
- **Database**: PostgreSQL + SQLAlchemy (async) + Alembic
- **Auth**: JWT (python-jose + passlib/bcrypt)
- **Frontend**: HTML + CSS + Vanilla JS + Bootstrap 5
- **Deployment**: Railway

## Features

- User signup & login with JWT authentication
- Create projects (creator becomes Admin automatically)
- Admin can add/remove members, create/delete tasks
- Members can view assigned projects and update their task status
- Dashboard with total tasks, tasks by status, overdue tasks, tasks per user
- Role-based access control (Admin vs Member)

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL running locally

### Steps

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd team-task-manager
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a local PostgreSQL database**
   ```bash
   createdb taskmanager
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/taskmanager
   SECRET_KEY=your_secret_key_here   # generate: openssl rand -hex 32
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Open the app**
   - App: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Deployment on Railway

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create a Railway project**
   - Go to [railway.app](https://railway.app) and create a new project
   - Connect your GitHub repository

3. **Add PostgreSQL addon**
   - In Railway dashboard, click **+ New** → **Database** → **PostgreSQL**
   - Railway will automatically set the `DATABASE_URL` environment variable

4. **Set environment variables** in Railway dashboard under **Variables**:
   ```
   SECRET_KEY=<generate with: openssl rand -hex 32>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=480
   ```

5. **Deploy**
   - Railway will automatically detect Python via Nixpacks
   - The `Procfile` runs migrations then starts the server:
     ```
     alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```

6. **Access your live app**
   - Railway provides a public URL under **Settings** → **Domains**

## Project Structure

```
team-task-manager/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment variable settings
│   ├── database.py          # Async SQLAlchemy setup
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API route handlers
│   └── auth/                # JWT and dependency utilities
├── static/
│   ├── css/app.css
│   ├── js/api.js            # Shared fetch wrapper
│   └── pages/               # HTML frontend pages
├── migrations/              # Alembic migration files
├── requirements.txt
├── Procfile
├── railway.toml
└── .env.example
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/auth/signup | Create account |
| POST | /api/v1/auth/login | Login |
| GET | /api/v1/auth/me | Current user |
| GET | /api/v1/projects/ | List my projects |
| POST | /api/v1/projects/ | Create project |
| GET | /api/v1/projects/{id} | Project detail |
| POST | /api/v1/projects/{id}/members | Add member (admin) |
| DELETE | /api/v1/projects/{id}/members/{uid} | Remove member (admin) |
| GET | /api/v1/projects/{id}/tasks/ | List tasks |
| POST | /api/v1/projects/{id}/tasks/ | Create task (admin) |
| PATCH | /api/v1/projects/{id}/tasks/{tid} | Update task |
| DELETE | /api/v1/projects/{id}/tasks/{tid} | Delete task (admin) |
| GET | /api/v1/dashboard/ | Dashboard stats |
| GET | /api/v1/users/?q= | Search users by email |
