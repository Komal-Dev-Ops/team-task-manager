import uuid
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from app.models.enums import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=300)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority = TaskPriority.medium
    due_date: date | None = None
    assigned_to: uuid.UUID | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v: str) -> str:
        return v.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=300)
    description: str | None = Field(default=None, max_length=2000)
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: date | None = None
    assigned_to: uuid.UUID | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v: str | None) -> str | None:
        return v.strip() if v else v


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
