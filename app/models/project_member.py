import uuid
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, Enum, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.enums import MemberRole


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (UniqueConstraint("project_id", "user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, name="memberrole"), nullable=False, default=MemberRole.member
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship(back_populates="members")  # noqa: F821
    user: Mapped["User"] = relationship(back_populates="memberships")
