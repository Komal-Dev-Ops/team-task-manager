import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.enums import MemberRole


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class MemberOut(BaseModel):
    user_id: uuid.UUID
    name: str
    email: str
    role: MemberRole

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    created_by: uuid.UUID
    created_at: datetime
    member_count: int = 0
    task_count: int = 0

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectOut):
    members: list[MemberOut] = []


class AddMemberRequest(BaseModel):
    user_id: uuid.UUID
    role: MemberRole = MemberRole.member
