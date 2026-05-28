# -*- coding: utf-8 -*-
"""站内消息通知 API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter(prefix="/api/notifications", tags=["消息通知"])


class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    type: str
    is_read: bool
    link: str | None = None
    created_at: str

    model_config = {"from_attributes": True}


@router.get("", response_model=list[NotificationResponse])
def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的消息通知列表."""
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    q = q.order_by(Notification.created_at.desc())
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    # 转换 datetime 为字符串
    result = []
    for item in items:
        result.append(NotificationResponse(
            id=item.id,
            title=item.title,
            content=item.content,
            type=item.type,
            is_read=item.is_read,
            link=item.link,
            created_at=item.created_at.isoformat() if item.created_at else "",
        ))
    return result


@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取未读消息数量."""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()
    return {"count": count}


@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """标记单条消息为已读."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="消息不存在")
    notification.is_read = True
    db.commit()
    return {"detail": "已标记为已读"}


@router.put("/read-all")
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """标记所有消息为已读."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"detail": "已全部标记为已读"}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除单条消息."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="消息不存在")
    db.delete(notification)
    db.commit()
    return {"detail": "已删除"}


def create_notification(db: Session, user_id: int, title: str, content: str,
                       notification_type: str = "system", link: str = None):
    """创建消息通知（供其他模块调用）."""
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=notification_type,
        link=link,
    )
    db.add(notification)
    db.commit()
    return notification
