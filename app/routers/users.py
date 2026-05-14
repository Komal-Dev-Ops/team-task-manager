from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=list[UserOut])
async def search_users(
    q: str = Query(default="", min_length=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User)
        .where(User.email.ilike(f"{q}%"))
        .where(User.id != current_user.id)
        .limit(10)
    )
    return result.scalars().all()
