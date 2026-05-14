import uuid
from datetime import date
from pydantic import BaseModel
from app.models.enums import TaskStatus, TaskPriority


class TasksPerUser(BaseModel):
    user_id: uuid.UUID
    name: str
    count: int


class MyTask(BaseModel):
    id: uuid.UUID
    title: str
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    project_name: str
    project_id: uuid.UUID


class DashboardOut(BaseModel):
    total_tasks: int
    by_status: dict[str, int]
    overdue_tasks: int
    tasks_per_user: list[TasksPerUser]
    my_tasks: list[MyTask]
