import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.dependencies import CurrentUser, get_current_user
from app.models import Issue, IssueStatusHistory
from app.notifications import send_notification
from app.schemas import (
    FINAL_STATUSES,
    IssueCategory,
    IssueCreate,
    IssueDetailOut,
    IssueOut,
    IssueStatus,
    IssueUpdate,
)

log = logging.getLogger(settings.SERVICE_NAME)

router = APIRouter(prefix="/issues", tags=["issues"])

STATUS_TITLES = {
    "new": "новая",
    "in_progress": "в работе",
    "resolved": "выполнена",
    "rejected": "отклонена",
}


async def _get_issue_or_404(db: AsyncSession, issue_id: int) -> Issue:
    result = await db.execute(
        select(Issue)
        .where(Issue.id == issue_id)
        .options(selectinload(Issue.history))
        .execution_options(populate_existing=True)
    )
    issue = result.scalar_one_or_none()
    if issue is None:
        raise HTTPException(404, "Issue not found")
    return issue


@router.post("", response_model=IssueDetailOut, status_code=status.HTTP_201_CREATED)
async def create_issue(
    data: IssueCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создание заявки ЖКХ"""
    issue = Issue(
        user_id=user.id,
        title=data.title,
        description=data.description,
        address=data.address,
        category=data.category.value,
        status=IssueStatus.new.value,
    )
    issue.history.append(IssueStatusHistory(old_status=None, new_status=IssueStatus.new.value, changed_by=user.id))
    db.add(issue)
    await db.commit()

    log.info("Issue %s created by user %s: category=%s '%s'", issue.id, user.id, issue.category, issue.title)
    await send_notification(user.id, "Заявка принята", f"Ваша заявка №{issue.id} «{issue.title}» зарегистрирована.")
    return await _get_issue_or_404(db, issue.id)


@router.get("", response_model=list[IssueOut])
async def list_issues(
    status: IssueStatus | None = None,
    category: IssueCategory | None = None,
    mine: bool = False,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список заявок. Фильтры: статус, категория"""
    stmt = select(Issue).order_by(Issue.created_at.desc())
    if status is not None:
        stmt = stmt.where(Issue.status == status.value)
    if category is not None:
        stmt = stmt.where(Issue.category == category.value)
    if mine:
        stmt = stmt.where(Issue.user_id == user.id)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{issue_id}", response_model=IssueDetailOut)
async def get_issue(
    issue_id: int,
    _: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Заявка вместе с историей статусов."""
    return await _get_issue_or_404(db, issue_id)


@router.put("/{issue_id}", response_model=IssueDetailOut)
async def update_issue_status(
    issue_id: int,
    data: IssueUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    #Обновление статуса заявки
    issue = await _get_issue_or_404(db, issue_id)
    old_status = issue.status
    new_status = data.status.value

    if old_status in FINAL_STATUSES:
        raise HTTPException(409, f"Issue is already closed with status '{old_status}'")
    if new_status == old_status:
        raise HTTPException(400, f"Issue already has status '{old_status}'")
    if new_status == IssueStatus.new.value:
        raise HTTPException(400, "Cannot return issue to status 'new'")

    issue.status = new_status
    issue.history.append(
        IssueStatusHistory(old_status=old_status, new_status=new_status, changed_by=user.id, comment=data.comment)
    )
    await db.commit()

    log.info("Issue %s status changed %s -> %s by user %s", issue_id, old_status, new_status, user.id)
    message = f"Статус заявки №{issue.id} «{issue.title}»: {STATUS_TITLES[new_status]}."
    if data.comment:
        message += f" Комментарий: {data.comment}"
    await send_notification(issue.user_id, "Статус заявки изменён", message)

    return await _get_issue_or_404(db, issue_id)
