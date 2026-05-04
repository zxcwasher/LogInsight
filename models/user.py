from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Model
from sqlalchemy import String, Boolean



class User(Model):

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(default="viewer", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    incidentR: Mapped[list["Incident"]] = relationship("Incident", back_populates="userR")

    incidentHistoryR: Mapped[list["IncidentHistory"]] = relationship(
        "IncidentHistory",
        back_populates="userR"
    )


    commentR: Mapped[list["Comment"]] = relationship("Comment", back_populates = "userR")





