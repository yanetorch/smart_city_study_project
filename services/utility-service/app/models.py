from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Issue(Base):
    #Заявка ЖКХ от жителя

    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(30), index=True)  # water / heating / electricity / ...
    status: Mapped[str] = mapped_column(String(20), default="new", index=True)  # new / in_progress / resolved / rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    history: Mapped[list["IssueStatusHistory"]] = relationship(
        back_populates="issue",
        order_by="IssueStatusHistory.changed_at",
        cascade="all, delete-orphan",
    )


class IssueStatusHistory(Base):
    #История смены статусов заявки — кто, когда и с каким комментарием

    __tablename__ = "issue_status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id", ondelete="CASCADE"), index=True)
    old_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_status: Mapped[str] = mapped_column(String(20))
    changed_by: Mapped[int] = mapped_column(Integer)  # user_id
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    issue: Mapped[Issue] = relationship(back_populates="history")
