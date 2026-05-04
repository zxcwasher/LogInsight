from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from utils.setting import get_db_url

DATABASE_URL = get_db_url()



class Model(DeclarativeBase):
    __abstract__ = True
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id: Mapped[int] = mapped_column (primary_key=True)


