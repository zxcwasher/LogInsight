from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.permissions import require_roles
from crud.comment import (
    create_comment,
    get_comment_by_incident,
    update_comment,
    delete_comment,
)
from models.helper import get_db
from schemas.comment import SComment

router = APIRouter(prefix="/comment", tags=["comment"])


@router.post("/incident/{incident_id}/comment")
async def add_comments(
    incident_id: int,
    comment: SComment,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer")),
):
    return await create_comment(
        db=db,
        comment_text=comment.comment,
        user_id=current_user.id,
        incident_id=incident_id,
    )


@router.get("/incident/{incident_id}/comment")
async def get_comment_by_incident_route(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    return await get_comment_by_incident(db, incident_id)


@router.put("/{comment_id}")
async def update_comment_route(
    comment_id: int,
    comment: SComment,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer")),
):
    updated_comment = await update_comment(
        db=db,
        comment_id=comment_id,
        comment_text=comment.comment,
    )

    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    return updated_comment


@router.delete("/{comment_id}")
async def delete_comment_route(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer")),
):
    deleted = await delete_comment(db, comment_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")

    return {"status": "deleted"}