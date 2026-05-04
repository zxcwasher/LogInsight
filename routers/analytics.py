from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.permissions import require_roles
from crud.analytics.service import get_analytics_summary
from models.helper import get_db
from schemas.analytics import AnalyticsSummaryResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    return await get_analytics_summary(
        db=db,
        user_id=current_user.id,
    )