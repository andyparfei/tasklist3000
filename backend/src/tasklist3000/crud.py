from typing import Optional

from robyn import Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> list[Task]:
    return db.query(Task).offset(skip).limit(limit).all()


def create_task(db: Session, task: dict[str, Task]) -> Task:
    # Create a copy of the task data and remove the id field to let the database auto-assign it
    task_data = {k: v for k, v in task.items() if k != 'id'}
    db_task = Task(**task_data)
    db.add(db_task)
    try:
        db.commit()
        db.refresh(db_task)
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Task creation failed due to missing required fields") from e
    return db_task


def update_task(db: Session, task_id: int, task: dict[str, Request]) -> Optional[Task]:
    db_task = get_task(db, task_id)
    if db_task is None:
        return None
    for key, value in task.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if db_task is None:
        return False
    db.delete(db_task)
    db.commit()
    return True
