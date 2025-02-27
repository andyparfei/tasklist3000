import os

BACKEND_FRAMEWORK = "robyn" # "fastapi" or "flask" or "robyn"

# For Docker, use a path in /data which will be mounted as a volume
DB_PATH = os.getenv("DATABASE_URL", "sqlite:////data/tasks.db")
PORT="8080"
HOST="0.0.0.0" # Listen on all interfaces
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
PRIORITY_VALUES = ["Low", "Medium", "High"]
STATUS_VALUES = ["Pending", "In Progress", "Completed"]
COLOR_VALUES = ["Red", "Green", "Blue", "Yellow", "Purple"]
