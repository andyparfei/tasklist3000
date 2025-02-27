import os
from collections.abc import Generator

import pytest

from tasklist3000.models import Base, engine

# Use an in-memory SQLite database for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def setup_db() -> Generator[None, None, None]:
    """Set up and tear down the database for tests."""
    # Create all tables defined in your SQLAlchemy models
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Teardown: Drop all tables
    Base.metadata.drop_all(bind=engine)
