import json
from typing import Any, TypedDict

from flask import Flask, jsonify, request
from flask_cors import CORS

from tasklist3000 import crud
from tasklist3000.config import HOST, PORT, CORS_ALLOWED_ORIGINS, COLOR_VALUES, PRIORITY_VALUES, STATUS_VALUES
from tasklist3000.models import Base, SessionLocal, Task, engine

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": CORS_ALLOWED_ORIGINS}})

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


# Error handlers
@app.errorhandler(TaskNotFoundException)
def handle_task_not_found(e):
    return jsonify({"error": str(e)}), 404


@app.errorhandler(TaskNotAddedException)
def handle_task_not_added(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(TaskIdMissingException)
def handle_task_id_missing(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(TaskNotUpdatedException)
def handle_task_not_updated(e):
    return jsonify({"error": str(e)}), 400


# Define the root endpoint
@app.route("/", methods=["GET"])
def root():
    return "Hello, world!"


# Define the status endpoint
@app.route("/status", methods=["GET"])
def status_endpoint():
    return "Up and running"


@app.route("/config", methods=["GET"])
def get_config():
    return {"priority_values": PRIORITY_VALUES, "status_values": STATUS_VALUES, "color_values": COLOR_VALUES}


@app.route("/tasks", methods=["GET"])
def get_tasks():
    with SessionLocal() as db:
        # Force fallback in case query_params returns None.
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 100))
        tasks = crud.get_tasks(db, skip=skip, limit=limit)
    tasks_serialized = [serialize_task(task) for task in tasks]
    return json.dumps(tasks_serialized)


# Endpoint to create a new task
@app.route("/tasks", methods=["POST"])
def add_task():
    with SessionLocal() as db:
        task_data = request.get_json()
        insertion = crud.create_task(db, task_data)

    if insertion is None:
        raise TaskNotAddedException("Task not added")

    return {
        "description": "Task added successfully",
        "status_code": 200,
        "id": insertion.id,  # Return the new task's ID
    }


# Endpoint to get a single task
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    with SessionLocal() as db:
        task = crud.get_task(db, task_id=task_id)

    if task is None:
        raise TaskNotFoundException("Task not found")

    # Return serialized task to match Robyn's behavior
    return serialize_task(task)


# Endpoint to update an existing task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    with SessionLocal() as db:
        task_data = request.get_json()
        updated = crud.update_task(db, task_id=task_id, task=task_data)
    if not updated:
        raise TaskNotUpdatedException("Task not updated")
    return {"description": "Task updated successfully"}


# Endpoint to delete a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    with SessionLocal() as db:
        success = crud.delete_task(db, task_id=task_id)
    if not success:
        raise TaskNotFoundException("Task not found")
    return {"description": "Task deleted successfully"}


# Start the Flask app on port 8080
if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
