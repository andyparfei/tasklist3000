from datetime import datetime
from sqlalchemy import create_engine, Integer, String, Text, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine
from .config import DB_PATH, COLOR_VALUES, PRIORITY_VALUES, STATUS_VALUES

DATABASE_URL: str = DB_PATH
engine: Engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Instead of using declarative_base(), subclass DeclarativeBase.
class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    full_text: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(Enum(*COLOR_VALUES, name="color_enum"))
    priority: Mapped[str] = mapped_column(Enum(*PRIORITY_VALUES, name="priority_enum"))
    status: Mapped[str] = mapped_column(Enum(*STATUS_VALUES, name="status_enum"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
