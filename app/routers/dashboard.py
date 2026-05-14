from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.enums import TaskStatus
from app.schemas.dashboard import DashboardOut, TasksPerUser, MyTask
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=DashboardOut)
async def dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Project IDs the user belongs to
    proj_result = await db.execute(
        select(ProjectMember.project_id).where(ProjectMember.user_id == current_user.id)
    )
    project_ids = [r[0] for r in proj_result.all()]

    if not project_ids:
        return DashboardOut(
            total_tasks=0,
            by_status={s.value: 0 for s in TaskStatus},
            overdue_tasks=0,
            tasks_per_user=[],
            my_tasks=[],
        )

    # Total tasks
    total_result = await db.execute(
        select(func.count(Task.id)).where(Task.project_id.in_(project_ids))
    )
    total_tasks = total_result.scalar() or 0

    # By status
    status_result = await db.execute(
        select(Task.status, func.count(Task.id))
        .where(Task.project_id.in_(project_ids))
        .group_by(Task.status)
    )
    by_status = {s.value: 0 for s in TaskStatus}
    for row in status_result.all():
        by_status[row[0].value] = row[1]

    # Overdue
    overdue_result = await db.execute(
        select(func.count(Task.id)).where(
            and_(
                Task.project_id.in_(project_ids),
                Task.due_date < date.today(),
                Task.status != TaskStatus.done,
            )
        )
    )
    overdue_tasks = overdue_result.scalar() or 0

    # Tasks per user
    per_user_result = await db.execute(
        select(User.id, User.name, func.count(Task.id).label("count"))
        .join(Task, Task.assigned_to == User.id)
        .where(Task.project_id.in_(project_ids))
        .group_by(User.id, User.name)
        .order_by(func.count(Task.id).desc())
    )
    tasks_per_user = [
        TasksPerUser(user_id=r[0], name=r[1], count=r[2])
        for r in per_user_result.all()
    ]

    # My tasks
    my_tasks_result = await db.execute(
        select(Task, Project.name.label("project_name"))
        .join(Project, Project.id == Task.project_id)
        .where(
            Task.assigned_to == current_user.id,
            Task.status != TaskStatus.done,
        )
        .order_by(Task.due_date.asc().nullslast())
    )
    my_tasks = [
        MyTask(
            id=row.Task.id,
            title=row.Task.title,
            status=row.Task.status,
            priority=row.Task.priority,
            due_date=row.Task.due_date,
            project_name=row.project_name,
            project_id=row.Task.project_id,
        )
        for row in my_tasks_result.all()
    ]

    return DashboardOut(
        total_tasks=total_tasks,
        by_status=by_status,
        overdue_tasks=overdue_tasks,
        tasks_per_user=tasks_per_user,
        my_tasks=my_tasks,
    )
