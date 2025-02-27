import os

BACKEND_FRAMEWORK = "robyn"

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
PORT="8080"
HOST="0.0.0.0"
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
PRIORITY_VALUES = ["Low", "Medium", "High"]
STATUS_VALUES = ["Pending", "In Progress", "Completed"]
COLOR_VALUES = ["Red", "Green", "Blue", "Yellow", "Purple"]
