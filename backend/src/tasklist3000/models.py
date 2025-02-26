from datetime import datetime
import os

from sqlalchemy import create_engine, Integer, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, sessionmaker
from sqlalchemy.engine import Engine

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

engine: Engine = create_engine(DATABASE_URL)
SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    full_text: Mapped[str] = mapped_column(Text)
    color: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )