import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    memberships: Mapped[list["ProjectMember"]] = relationship(back_populates="user")  # noqa: F821
    assigned_tasks: Mapped[list["Task"]] = relationship(  # noqa: F821
        back_populates="assignee", foreign_keys="Task.assigned_to"
    )
