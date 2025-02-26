import json
from typing import Any, Dict, List, Union

from robyn import Robyn, Request, ALLOW_CORS

from . import crud
from .models import SessionLocal, Task, Base, engine
from .config import PRIORITY_VALUES, STATUS_VALUES, COLOR_VALUES

app = Robyn(__file__)
ALLOW_CORS(app, origins=["http://localhost:5173"])

Base.metadata.create_all(bind=engine)

# Return a dictionary with id as int and title, description as str.
def serialize_task(task: Task) -> Dict[str, Union[int, str]]:
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
async def get_config(request: Request) -> Dict[str, List[Any]]:
    return {
        "priority_values": PRIORITY_VALUES,
        "status_values": STATUS_VALUES,
        "color_values": COLOR_VALUES
    }

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
async def add_task(request: Request) -> Dict[str, Union[str, int]]:
    with SessionLocal() as db:
        task_data = request.json()
        insertion = crud.create_task(db, task_data)

    if insertion is None:
        raise Exception("Task not added")

    return {
        "description": "Task added successfully",
        "status_code": 200,
        "id": insertion.id  # Return the new task's ID
    }

# Endpoint to get a single task
@app.get("/tasks/:task_id")
async def get_task(request: Request) -> Task:
    task_id_str = request.path_params.get("task_id")
    if task_id_str is None:
        raise Exception("Task id missing")
    task_id = int(task_id_str)
    with SessionLocal() as db:
        task = crud.get_task(db, task_id=task_id)

    if task is None:
        raise Exception("Task not found")

    return task

# Endpoint to update an existing task
@app.put("/tasks/:task_id")
async def update_task(request: Request) -> Dict[str, str]:
    task_id_str = request.path_params.get("task_id")
    if task_id_str is None:
        raise Exception("Task id missing")
    task_id = int(task_id_str)
    with SessionLocal() as db:
        task_data = request.json()
        updated = crud.update_task(db, task_id=task_id, task=task_data)
    if not updated:
        raise Exception("Task not updated")
    return {"description": "Task updated successfully"}

# Endpoint to delete a task
@app.delete("/tasks/:task_id")
async def delete_task(request: Request) -> Dict[str, str]:
    task_id_str = request.path_params.get("task_id")
    if task_id_str is None:
        raise Exception("Task id missing")
    task_id = int(task_id_str)
    with SessionLocal() as db:
        success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise Exception("Task not found")
    return {"description": "Task deleted successfully"}

# Start the Robyn app on port 8080
if __name__ == "__main__":
    app.start("0.0.0.0", port=8080)
