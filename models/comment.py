
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Model


class Comment(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    comment: Mapped[Optional[str]] = mapped_column(nullable=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incident.id"))

    userR: Mapped["User"] = relationship("User", back_populates="commentR")
    incidentR: Mapped["Incident"] = relationship("Incident", back_populates="comments")

