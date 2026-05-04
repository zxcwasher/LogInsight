from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database import Model


class Event(Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incident.id"),
        index=True
    )


    pattern_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("analysis.id"),
        index=True,
        nullable=True
    )

    user_id: Mapped[int] = mapped_column(index=True)

    category: Mapped[str] = mapped_column(index=True)
    pattern_key: Mapped[str] = mapped_column(index=True)


    timestamp: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        index=True
    )

    service: Mapped[Optional[str]]
    raw_message: Mapped[str]

    severity: Mapped[str] = mapped_column(index=True)
    message: Mapped[str]

    host: Mapped[Optional[str]]


    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    source: Mapped[str]