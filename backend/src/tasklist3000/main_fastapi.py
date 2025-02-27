# fastapi implementation

import json
from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict

from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tasklist3000 import crud
from tasklist3000.config import HOST, PORT, CORS_ALLOWED_ORIGINS, COLOR_VALUES, PRIORITY_VALUES, STATUS_VALUES
from tasklist3000.models import Base, SessionLocal, Task, engine

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# Pydantic models for request and response validation
class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    color: Optional[str] = None
    full_text: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskDict(TypedDict):
    id: int
    title: str
    description: str
    status: str
    priority: str
    color: str
    full_text: str


class ConfigDict(TypedDict):
    priority_values: list[Any]
    status_values: list[Any]
    color_values: list[Any]


class AddTaskResponseDict(TypedDict):
    description: str
    status_code: int
    id: int


class UpdateTaskResponseDict(TypedDict):
    description: str


class DeleteTaskResponseDict(TypedDict):
    description: str


# Return a dictionary with all task fields.
def serialize_task(task: Task) -> TaskDict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "color": task.color,
        "full_text": task.full_text,
    }


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define the root endpoint
@app.get("/")
async def root():
    return Response(content="Hello, world!", media_type="text/plain")


# Define the status endpoint
@app.get("/status")
async def status_endpoint():
    return Response(content="Up and running", media_type="text/plain")


@app.get("/config")
async def get_config() -> ConfigDict:
    return {"priority_values": PRIORITY_VALUES, "status_values": STATUS_VALUES, "color_values": COLOR_VALUES}


@app.get("/tasks")
async def get_tasks(skip: int = Query(0), limit: int = Query(100)) -> str:
    with SessionLocal() as db:
        tasks = crud.get_tasks(db, skip=skip, limit=limit)
    tasks_serialized = [serialize_task(task) for task in tasks]
    return json.dumps(tasks_serialized)


# Endpoint to create a new task
@app.post("/tasks")
async def add_task(task: Request) -> AddTaskResponseDict:
    task_data = await task.json()
    with SessionLocal() as db:
        insertion = crud.create_task(db, task_data)

    if insertion is None:
        raise HTTPException(status_code=400, detail="Task not added")

    return {
        "description": "Task added successfully",
        "status_code": 200,
        "id": insertion.id,  # Return the new task's ID
    }


# Endpoint to get a single task
@app.get("/tasks/{task_id}")
async def get_task(task_id: int) -> TaskDict:
    with SessionLocal() as db:
        task = crud.get_task(db, task_id=task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Serialize the SQLAlchemy model to a dictionary
    return serialize_task(task)


# Endpoint to update an existing task
@app.put("/tasks/{task_id}")
async def update_task(task_id: int, request: Request) -> UpdateTaskResponseDict:
    task_data = await request.json()
    with SessionLocal() as db:
        updated = crud.update_task(db, task_id=task_id, task=task_data)
    if not updated:
        raise HTTPException(status_code=400, detail="Task not updated")
    return {"description": "Task updated successfully"}


# Endpoint to delete a task
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int) -> DeleteTaskResponseDict:
    with SessionLocal() as db:
        success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"description": "Task deleted successfully"}


# Start the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
