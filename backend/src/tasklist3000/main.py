from robyn import Robyn, Request
import sqlite3
import json
import os
from typing import Dict
from . import crud
from .models import SessionLocal, Task

app = Robyn(__file__)

def serialize_task(task: Task) -> Dict[str, Request]:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
    }

# Define the root endpoint
@app.get("/")
async def h(request: Request) -> str:
    return "Hello, world!"

# Define the status endpoint
@app.get("/status")
async def h(request: Request) -> str:
    return "Up and running"

# Define the endpoint to retrieve all tasks
@app.get("/tasks")
async def get_tasks(request: Request) -> str:
    with SessionLocal() as db:
        skip = request.query_params.get("skip", "0")
        limit = request.query_params.get("limit", "100")
        tasks = crud.get_tasks(db, skip=skip, limit=limit)
    tasks = [serialize_task(task) for task in tasks]
    return json.dumps(tasks)

# Define the endpoint to create a new task
@app.post("/tasks")
async def add_task(request: Request) -> Dict[str, Request]:
    with SessionLocal() as db:
        task = request.json()
        insertion = crud.create_task(db, task)

    if insertion is None:
        raise Exception("Task not added")

    return {
        "description": "Task added successfully",
        "status_code": 200,
        "id": insertion.id  # Return the new task's ID
    }

# Define the endpoint to get a single task
@app.get("/tasks/:task_id")
async def get_task(request: Request) -> Task:
    task_id = int(request.path_params.get("task_id"))
    with SessionLocal() as db:
        task = crud.get_task(db, task_id=task_id)

    if task is None:
        raise Exception("task not found")

    return task

# Define the endpoint to update an existing task
@app.put("/tasks/:task_id")
async def update_task(request: Request) -> Dict[str, str]:
    task_id = int(request.path_params.get("task_id"))
    with SessionLocal() as db:
        task_data = request.json()
        updated = crud.update_task(db, task_id=task_id, task=task_data)
    if not updated:
        raise Exception("Task not updated")
    return {"description": "Task updated successfully"}

# Define the endpoint to delete a task
@app.delete("/tasks/:task_id")
async def delete_task(request: Request) -> Dict[str, str]:
    task_id = int(request.path_params.get("task_id"))
    with SessionLocal() as db:
        success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise Exception("task not found")
    return {"description": "Task deleted successfully"}

# Start the Robyn app on port 8080
if __name__ == "__main__":
    app.start(port=8080)