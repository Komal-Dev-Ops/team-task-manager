import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.project_member import ProjectMember
from app.models.enums import MemberRole
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.auth.dependencies import get_current_user, get_project_membership, require_project_admin

router = APIRouter()


@router.get("/{project_id}/tasks/", response_model=list[TaskOut])
async def list_tasks(
    project_id: uuid.UUID,
    membership: ProjectMember = Depends(get_project_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task)
        .where(Task.project_id == project_id)
        .options(selectinload(Task.assignee))
        .order_by(Task.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{project_id}/tasks/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    project_id: uuid.UUID,
    payload: TaskCreate,
    membership: ProjectMember = Depends(require_project_admin),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        assigned_to=payload.assigned_to,
        created_by=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    result = await db.execute(
        select(Task).where(Task.id == task.id).options(selectinload(Task.assignee))
    )
    return result.scalar_one()


@router.get("/{project_id}/tasks/{task_id}", response_model=TaskOut)
async def get_task(
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    membership: ProjectMember = Depends(get_project_membership),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.project_id == project_id)
        .options(selectinload(Task.assignee))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{project_id}/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    payload: TaskUpdate,
    membership: ProjectMember = Depends(get_project_membership),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id, Task.project_id == project_id)
        .options(selectinload(Task.assignee))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if membership.role == MemberRole.member:
        if task.assigned_to != current_user.id:
            raise HTTPException(status_code=403, detail="You can only update your own assigned tasks")
        if payload.status is not None:
            task.status = payload.status
    else:
        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    result2 = await db.execute(
        select(Task).where(Task.id == task.id).options(selectinload(Task.assignee))
    )
    return result2.scalar_one()


@router.delete("/{project_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    project_id: uuid.UUID,
    task_id: uuid.UUID,
    membership: ProjectMember = Depends(require_project_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.project_id == project_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
