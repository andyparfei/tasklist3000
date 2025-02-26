import pytest
import sqlite3
import json
import httpx
import os
import threading
import time

os.environ["DATABASE_URL"] = "sqlite:///./tasks_test.db"

from tasklist3000.main import app
from tasklist3000.models import Base, engine

# Setup and teardown for the SQLite database and server
@pytest.fixture(scope="module", autouse=True)
def setup_server_and_db():
    # Create all tables defined in your SQLAlchemy models
    Base.metadata.create_all(bind=engine)
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=app.start, kwargs={"host": "127.0.0.1", "port": 8000})
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    
    yield

# Base URL for tests
BASE_URL = "http://127.0.0.1:8000"

def test_root_endpoint():
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.text == "Hello, world!"

def test_status_endpoint():
    response = httpx.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    assert response.text == "Up and running"

def test_create_task():
    task = {"title": "Test Task", "description": "This is a test task"}
    response = httpx.post(f"{BASE_URL}/tasks", json=task)
    assert response.status_code == 200
    data = response.json()
    assert data.get("description") == "Task added successfully"

def test_get_tasks():
    response = httpx.get(f"{BASE_URL}/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) > 0

def test_update_task():
    task = {"title": "Updated Task", "description": "This is an updated task"}
    response = httpx.put(f"{BASE_URL}/tasks/1", json=task)
    assert response.status_code == 200
    data = response.json()
    assert data.get("description") == "Task updated successfully"

def test_delete_task():
    response = httpx.delete(f"{BASE_URL}/tasks/1")
    assert response.status_code == 200
    data = response.json()
    assert data.get("description") == "Task deleted successfully"