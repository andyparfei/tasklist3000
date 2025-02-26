import json
from typing import Any, TypedDict

from robyn import ALLOW_CORS, Request, Robyn

from . import crud
from .config import COLOR_VALUES, PRIORITY_VALUES, STATUS_VALUES
from .models import Base, SessionLocal, Task, engine

app = Robyn(__file__)
ALLOW_CORS(app, origins=["http://localhost:5173"])

Base.metadata.create_all(bind=engine)


class TaskNotFoundException(Exception):
    pass


class TaskNotAddedException(Exception):
    pass


class TaskIdMissingException(Exception):
    pass


class TaskNotUpdatedException(Exception):
    pass


class TaskDict(TypedDict):
    id: int
    title: str
    description: str


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


# Return a dictionary with id as int and title, description as str.
def serialize_task(task: Task) -> TaskDict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
    }


# Define the root endpoint
@app.get("/")
async def root(request: Request) -> str:
    return "Hello, world!"


# Define the status endpoint (renamed to avoid duplicate function names)
@app.get("/status")
async def status_endpoint(request: Request) -> str:
    return "Up and running"


@app.get("/config")
async def get_config(request: Request) -> ConfigDict:
    return {"priority_values": PRIORITY_VALUES, "status_values": STATUS_VALUES, "color_values": COLOR_VALUES}


@app.get("/tasks")
async def get_tasks(request: Request) -> str:
    with SessionLocal() as db:
        # Force fallback in case query_params returns None.
        skip = int(request.query_params.get("skip") or "0")
        limit = int(request.query_params.get("limit") or "100")
        tasks = crud.get_tasks(db, skip=skip, limit=limit)
    tasks_serialized = [serialize_task(task) for task in tasks]
    return json.dumps(tasks_serialized)


# Endpoint to create a new task
@app.post("/tasks")
async def add_task(request: Request) -> AddTaskResponseDict:
    with SessionLocal() as db:
        task_data = request.json()
        insertion = crud.create_task(db, task_data)

    if insertion is None:
        raise TaskNotAddedException("Task not added")

    return {
        "description": "Task added successfully",
        "status_code": 200,
        "id": insertion.id,  # Return the new task's ID
    }


# Endpoint to get a single task
@app.get("/tasks/:task_id")
async def get_task(request: Request) -> Task:
    task_id_str = request.path_params.get("task_id")
    if task_id_str is None:
        raise TaskIdMissingException("Task id missing")
    task_id = int(task_id_str)
    with SessionLocal() as db:
        task = crud.get_task(db, task_id=task_id)

    if task is None:
        raise TaskNotFoundException("Task not found")

    return task


# Endpoint to update an existing task
@app.put("/tasks/:task_id")
async def update_task(request: Request) -> UpdateTaskResponseDict:
    task_id_str = request.path_params.get("task_id")
    if task_id_str is None:
        raise TaskIdMissingException("Task id missing")
    task_id = int(task_id_str)
    with SessionLocal() as db:
        task_data = request.json()
        updated = crud.update_task(db, task_id=task_id, task=task_data)
    if not updated:
        raise TaskNotUpdatedException("Task not updated")
    return {"description": "Task updated successfully"}


# Endpoint to delete a task
@app.delete("/tasks/:task_id")
async def delete_task(request: Request) -> DeleteTaskResponseDict:
    task_id_str = request.path_params.get("task_id")
    if task_id_str is None:
        raise TaskIdMissingException("Task id missing")
    task_id = int(task_id_str)
    with SessionLocal() as db:
        success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise TaskNotFoundException("Task not found")
    return {"description": "Task deleted successfully"}


# Start the Robyn app on port 8080
if __name__ == "__main__":
    app.start("0.0.0.0", port=8080)
