import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, projects, tasks, dashboard, users

app = FastAPI(title="Team Task Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/api/v1/projects", tags=["tasks"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

app.mount("/static", StaticFiles(directory="static"), name="static")

PAGES_DIR = os.path.join("static", "pages")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return FileResponse(f"{PAGES_DIR}/login.html")


for _page in ["login", "signup", "dashboard", "projects", "project-detail", "tasks"]:
    _html = f"{PAGES_DIR}/{_page}.html"

    def _make_route(f=_html):
        async def route():
            return FileResponse(f)
        return route

    app.add_api_route(f"/{_page}", _make_route(), methods=["GET"])
