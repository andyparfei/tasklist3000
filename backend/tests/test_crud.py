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
    task_data = {"title": "Test Task", "description": "This is a test task"}
    new_task = create_task(db_session, task_data)
    # Check that an ID was assigned and fields are correct.
    assert new_task.id is not None
    assert new_task.title == task_data["title"]
    assert new_task.description == task_data["description"]

def test_get_task(db_session):
    # First, create a task
    task_data = {"title": "Sample Task", "description": "Sample description"}
    created = create_task(db_session, task_data)
    # Retrieve the task using its ID
    fetched = get_task(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == task_data["title"]

def test_update_task(db_session):
    # Create a task to update
    task_data = {"title": "Old Title", "description": "Old description"}
    created = create_task(db_session, task_data)
    
    update_data = {"title": "Updated Title", "description": "Updated description"}
    updated = update_task(db_session, created.id, update_data)
    # Check that the returned task has updated fields
    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.description == "Updated description"

def test_delete_task(db_session):
    # Create a task to delete
    task_data = {"title": "Task to Delete", "description": "Delete me"}
    created = create_task(db_session, task_data)
    
    # Delete the task and verify that deletion was successful
    result = delete_task(db_session, created.id)
    assert result is True
    # Now, fetching the task should return None
    assert get_task(db_session, created.id) is None

def test_get_tasks(db_session):
    # Create several tasks
    tasks_data = [
        {"title": "Task 1", "description": "Description 1"},
        {"title": "Task 2", "description": "Description 2"},
        {"title": "Task 3", "description": "Description 3"},
    ]
    for data in tasks_data:
        create_task(db_session, data)
    # Retrieve tasks with no skip/limit modifications
    tasks = get_tasks(db_session)
    assert len(tasks) == len(tasks_data)