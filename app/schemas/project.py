import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import MemberRole


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v: str | None) -> str | None:
        return v.strip() if v else v


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


class UpdateMemberRoleRequest(BaseModel):
    role: MemberRole
