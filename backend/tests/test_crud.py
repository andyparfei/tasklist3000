import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tasklist3000.models import Base, Task
from tasklist3000.crud import (
    get_task,
    get_tasks,
    create_task,
    update_task,
    delete_task,
)

# Create an in-memory SQLite database for testing
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Create the tables in our test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_task(db_session):
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Low",
        "status": "Pending",
        }
    new_task = create_task(db_session, task_data)
    # Check that an ID was assigned and fields are correct.
    assert new_task.id is not None
    assert new_task.title == task_data["title"]
    assert new_task.description == task_data["description"]

def test_create_task_missing_fields(db_session):
    task_data = {
        "description": "This is a test task without a title",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Low",
        "status": "Pending",
        }
    with pytest.raises(ValueError, match="Task creation failed due to missing required fields"):
        create_task(db_session, task_data)

def test_get_task(db_session):
    # First, create a task
    task_data = {
        "title": "Sample Task",
        "description": "Sample description",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Low",
        "status": "Pending",
        }
    created = create_task(db_session, task_data)
    # Retrieve the task using its ID
    fetched = get_task(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == task_data["title"]

def test_get_nonexistent_task(db_session):
    fetched = get_task(db_session, 999)
    assert fetched is None

def test_update_task(db_session):
    # Create a task to update
    task_data = {
        "title": "Old Title",
        "description": "Old description",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Low",
        "status": "Pending",
        }
    created = create_task(db_session, task_data)
    
    update_data = {
        "title": "Updated Title",
        "description": "Updated description",
        }
    updated = update_task(db_session, created.id, update_data)
    # Check that the returned task has updated fields
    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.description == "Updated description"
    # Check that the fields not provided in update_data remain unchanged
    assert updated.full_text == task_data["full_text"]
    assert updated.color == task_data["color"]
    assert updated.priority == task_data["priority"]
    assert updated.status == task_data["status"]

def test_update_nonexistent_task(db_session):
    update_data = {
        "title": "Updated Title",
        "description": "Updated description",
        }
    updated = update_task(db_session, 999, update_data)
    assert updated is None

def test_delete_task(db_session):
    # Create a task to delete
    task_data = {
        "title": "Task to Delete",
        "description": "Delete me",
        "full_text": "Sample full text",
        "color": "Red",
        "priority": "Low",
        "status": "Pending",
        }
    created = create_task(db_session, task_data)
    
    # Delete the task and verify that deletion was successful
    result = delete_task(db_session, created.id)
    assert result is True
    # Now, fetching the task should return None
    assert get_task(db_session, created.id) is None

def test_delete_nonexistent_task(db_session):
    result = delete_task(db_session, 999)
    assert result is False

def test_get_tasks(db_session):
    # Create several tasks
    tasks_data = [
        {
            "title": "Task 1",
            "description": "Description 1",
            "full_text": "Sample full text",
            "color": "Red",
            "priority": "Low",
            "status": "Pending",
         },
        {
            "title": "Task 2",
            "description": "Description 2",
            "full_text": "Sample full text",
            "color": "Red",
            "priority": "Low",
            "status": "Pending",
        },
        {
            "title": "Task 3",
            "description": "Description 3",
            "full_text": "Sample full text",
            "color": "Red",
            "priority": "Low",
            "status": "Pending",
        },
    ]
    for data in tasks_data:
        create_task(db_session, data)
    # Retrieve tasks with no skip/limit modifications
    tasks = get_tasks(db_session)
    assert len(tasks) == len(tasks_data)

def test_get_tasks_with_pagination(db_session):
    # Create several tasks
    tasks_data = [
        {
            "title": "Task 1",
            "description": "Description 1",
            "full_text": "Sample full text",
            "color": "Red",
            "priority": "Low",
            "status": "Pending",
         },
        {
            "title": "Task 2",
            "description": "Description 2",
            "full_text": "Sample full text",
            "color": "Red",
            "priority": "Low",
            "status": "Pending",
        },
        {
            "title": "Task 3",
            "description": "Description 3",
            "full_text": "Sample full text",
            "color": "Red",
            "priority": "Low",
            "status": "Pending",
        },
    ]
    for data in tasks_data:
        create_task(db_session, data)
    # Retrieve tasks with skip and limit
    tasks = get_tasks(db_session, skip=1, limit=1)
    assert len(tasks) == 1
    assert tasks[0].title == "Task 2"