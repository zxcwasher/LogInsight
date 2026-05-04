
from sqlalchemy import  DateTime
from enum import Enum
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Model  # твой базовый класс


class Incident(Model):

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]


    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    analysis: Mapped[str] = mapped_column(default="")  # можно оставить пустым по умолчанию
    status: Mapped[str] = mapped_column(default="new")  # дефолтное значение, чтобы миграции прошли
    severity: Mapped[str] = mapped_column(default="low")
    pattern_key: Mapped[str] = mapped_column(nullable=False)
    service: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    userR: Mapped["User"] = relationship("User", back_populates="incidentR")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="incidentR")
class History_Status(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(ForeignKey("incident.id"))
    Old_status: Mapped[str]
    New_status: Mapped[str]
    Changed_at: Mapped[datetime]= mapped_column(
        DateTime,
        default=datetime.now
    )

class Status(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"



class IncidentHistory(Model):

    id: Mapped[int] = mapped_column(primary_key=True)

    incident_id: Mapped[int] = mapped_column(ForeignKey("incident.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    old_status: Mapped[str]
    new_status: Mapped[str] = mapped_column(default="open")

    changed_at: Mapped[datetime] = mapped_column(
            DateTime,
            default=datetime.utcnow
        )

    userR: Mapped["User"] = relationship("User", back_populates="incidentHistoryR")

