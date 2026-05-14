import uuid
from datetime import datetime, date, timezone
from sqlalchemy import String, Text, ForeignKey, DateTime, Date, Enum, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import TaskPriority, TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, name="taskpriority"), nullable=False, default=TaskPriority.medium
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="taskstatus"), nullable=False, default=TaskStatus.todo
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project: Mapped["Project"] = relationship(back_populates="tasks")  # noqa: F821
    assignee: Mapped["User"] = relationship(  # noqa: F821
        back_populates="assigned_tasks", foreign_keys=[assigned_to]
    )
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])  # noqa: F821
