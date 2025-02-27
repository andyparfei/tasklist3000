import os
import socket
import threading
import time
from collections.abc import Generator
from contextlib import closing

import pytest
import requests

from tasklist3000.main import app
from tasklist3000.models import Base, engine
from common_test_utils import (
    test_create_task,
    test_delete_task,
    test_get_config,
    test_get_tasks,
    test_root_endpoint,
    test_status_endpoint,
    test_update_task,
)

# disable parallel testing for these tests when running test command
pytestmark = pytest.mark.serial

# Use an in-memory SQLite database for testing
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


def find_free_port():
    """Find a free port on localhost."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class RobynServerThread(threading.Thread):
    """Thread for running a Robyn server with proper shutdown capability."""
    
    def __init__(self, app, host, port):
        threading.Thread.__init__(self)
        self.app = app
        self.host = host
        self.port = port
        self.daemon = True
        self.server_started = threading.Event()
        
    def run(self):
        """Run the Robyn server."""
        # Add a shutdown route to the Robyn app
        @self.app.get("/shutdown")
        async def shutdown_route(request):
            # This doesn't actually shut down the server, but we'll use it as a signal
            self.server_started.set()
            return "Shutting down server"
        
        # Signal that the server is ready to start
        self.server_started.set()
        
        # Run the Robyn app
        self.app.start(host=self.host, port=self.port)
    
    def shutdown(self):
        """Attempt to shut down the Robyn server."""
        # Robyn doesn't have a clean shutdown mechanism
        # We'll try to make a request to our shutdown route
        try:
            requests.get(f"http://{self.host}:{self.port}/shutdown")
        except:
            pass
        
        # Since Robyn doesn't have a clean shutdown, we'll rely on the daemon thread
        # to be terminated when the test process exits


@pytest.fixture(scope="module", autouse=True)
def setup_server_and_db() -> Generator[None, None, None]:
    """Set up the database and start the Robyn server for testing."""
    # Create all tables defined in your SQLAlchemy models
    Base.metadata.create_all(bind=engine)
    
    # Find a free port
    port = find_free_port()
    
    # Start the server in a separate thread
    server_thread = RobynServerThread(app, "127.0.0.1", port)
    server_thread.start()
    
    # Wait for the server to be ready to start
    server_thread.server_started.wait(timeout=5)
    
    # Update the BASE_URL in the common test utils
    import common_test_utils as utils
    utils.BASE_URL = f"http://127.0.0.1:{port}"
    
    # Give the server a moment to start
    time.sleep(1)

    yield

    # Attempt to shut down the server
    server_thread.shutdown()
    
    # Wait for the server to shut down
    time.sleep(1)
    
    # Teardown: Drop all tables
    Base.metadata.drop_all(bind=engine)
