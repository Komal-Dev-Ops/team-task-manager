import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.enums import MemberRole
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetail,
    MemberOut, AddMemberRequest,
)
from app.auth.dependencies import get_current_user, get_project_membership, require_project_admin

router = APIRouter()


@router.get("/", response_model=list[ProjectOut])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .join(ProjectMember, ProjectMember.project_id == Project.id)
        .where(ProjectMember.user_id == current_user.id)
        .options(selectinload(Project.members), selectinload(Project.tasks))
    )
    projects = result.scalars().unique().all()
    return [
        ProjectOut(
            id=p.id, name=p.name, description=p.description,
            created_by=p.created_by, created_at=p.created_at,
            member_count=len(p.members), task_count=len(p.tasks),
        )
        for p in projects
    ]


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = Project(name=payload.name, description=payload.description, created_by=current_user.id)
    db.add(project)
    await db.flush()
    membership = ProjectMember(project_id=project.id, user_id=current_user.id, role=MemberRole.admin)
    db.add(membership)
    await db.commit()
    await db.refresh(project)
    return ProjectOut(
        id=project.id, name=project.name, description=project.description,
        created_by=project.created_by, created_at=project.created_at,
        member_count=1, task_count=0,
    )


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: uuid.UUID,
    membership: ProjectMember = Depends(get_project_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.members).selectinload(ProjectMember.user),
            selectinload(Project.tasks),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectDetail(
        id=project.id, name=project.name, description=project.description,
        created_by=project.created_by, created_at=project.created_at,
        member_count=len(project.members), task_count=len(project.tasks),
        members=[
            MemberOut(user_id=m.user_id, name=m.user.name, email=m.user.email, role=m.role)
            for m in project.members
        ],
    )


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    membership: ProjectMember = Depends(require_project_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    await db.commit()
    await db.refresh(project)
    return ProjectOut(
        id=project.id, name=project.name, description=project.description,
        created_by=project.created_by, created_at=project.created_at,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    membership: ProjectMember = Depends(require_project_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()


@router.get("/{project_id}/members", response_model=list[MemberOut])
async def list_members(
    project_id: uuid.UUID,
    membership: ProjectMember = Depends(get_project_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProjectMember)
        .where(ProjectMember.project_id == project_id)
        .options(selectinload(ProjectMember.user))
    )
    members = result.scalars().all()
    return [
        MemberOut(user_id=m.user_id, name=m.user.name, email=m.user.email, role=m.role)
        for m in members
    ]


@router.post("/{project_id}/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
async def add_member(
    project_id: uuid.UUID,
    payload: AddMemberRequest,
    membership: ProjectMember = Depends(require_project_admin),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(select(User).where(User.id == payload.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == payload.user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a member")
    new_member = ProjectMember(project_id=project_id, user_id=payload.user_id, role=payload.role)
    db.add(new_member)
    await db.commit()
    return MemberOut(user_id=user.id, name=user.name, email=user.email, role=payload.role)


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    membership: ProjectMember = Depends(require_project_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member.role == MemberRole.admin and member.user_id == membership.user_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself as admin")
    await db.delete(member)
    await db.commit()
