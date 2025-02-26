import os

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")
PRIORITY_VALUES = ["Low", "Medium", "High"]
STATUS_VALUES = ["Pending", "In Progress", "Completed"]
COLOR_VALUES = ["Red", "Green", "Blue", "Yellow", "Purple"]
