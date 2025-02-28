import httpx
import pytest

from tasklist3000.config import COLOR_VALUES, PRIORITY_VALUES, STATUS_VALUES

# disable parallel testing for these tests when running test command
pytestmark = pytest.mark.serial

# Base URL for tests
BASE_URL = "http://127.0.0.1:8000"


def test_root_endpoint() -> None:
    """Test the root endpoint of the API."""
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.text == "Hello, world!"


def test_status_endpoint() -> None:
    """Test the status endpoint of the API."""
    response = httpx.get(f"{BASE_URL}/status")
    assert response.status_code == 200
    assert response.text == "Up and running"


def test_create_task() -> None:
    """Test creating a new task."""
    task = {
        "title": "Test Task",
        "description": "This is a test task",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Medium",
        "status": "Pending",
    }
    response = httpx.post(f"{BASE_URL}/tasks", json=task)
    assert response.status_code == 200
    data = response.json()
    assert data.get("description") == "Task added successfully"


def test_get_tasks() -> None:
    """Test retrieving all tasks."""
    response = httpx.get(f"{BASE_URL}/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) > 0


def test_update_task() -> None:
    """Test updating an existing task."""
    # First, create a task to update
    task = {
        "title": "Test Task",
        "description": "This is a test task",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Medium",
        "status": "Pending",
    }
    response = httpx.post(f"{BASE_URL}/tasks", json=task)
    assert response.status_code == 200
    created_task_id = response.json().get("id")

    # Now, update the created task
    update_data = {"title": "Updated Task", "description": "This is an updated task"}
    response = httpx.put(f"{BASE_URL}/tasks/{created_task_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data.get("description") == "Task updated successfully"


def test_delete_task() -> None:
    """Test deleting a task."""
    # First, create a task to delete
    task = {
        "title": "Test Task",
        "description": "This is a test task",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Medium",
        "status": "Pending",
    }
    response = httpx.post(f"{BASE_URL}/tasks", json=task)
    assert response.status_code == 200
    created_task_id = response.json().get("id")

    # Now, delete the created task
    response = httpx.delete(f"{BASE_URL}/tasks/{created_task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data.get("description") == "Task deleted successfully"


def test_get_config() -> None:
    """Test retrieving configuration values."""
    response = httpx.get(f"{BASE_URL}/config")
    assert response.status_code == 200
    config = response.json()
    assert config["priority_values"] == PRIORITY_VALUES
    assert config["status_values"] == STATUS_VALUES
    assert config["color_values"] == COLOR_VALUES
