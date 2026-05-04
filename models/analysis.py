
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from database import Model


class Analysis(Model):

    id: Mapped[int] = mapped_column(primary_key=True)

    key: Mapped[str] = mapped_column(unique=True, index=True)
    pattern: Mapped[str]
    severity: Mapped[str]
    message: Mapped[str]
    category: Mapped[str]
    service: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    source: Mapped[str] = mapped_column(default="system")

    enabled: Mapped[bool] = mapped_column(default=True, index=True)
    priority: Mapped[int] = mapped_column(default=0, index=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)