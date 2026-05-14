import uuid
from datetime import datetime, date
from pydantic import BaseModel
from app.models.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None
    assigned_to: uuid.UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    assigned_to: uuid.UUID | None = None


class AssigneeOut(BaseModel):
    id: uuid.UUID
    name: str

    model_config = {"from_attributes": True}


class TaskOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    due_date: date | None
    assigned_to: uuid.UUID | None
    assignee: AssigneeOut | None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
