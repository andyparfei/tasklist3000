"""
Entry point for the tasklist3000 package.
This allows the package to be run directly with 'python -m tasklist3000'.
"""
from tasklist3000.config import BACKEND_FRAMEWORK

 # Start the Robyn app on port 8080
if __name__ == "__main__" and BACKEND_FRAMEWORK == "robyn":
    from tasklist3000.main import app
    app.start("0.0.0.0", port=8080)

# Start the FastAPI app on port 8080
if __name__ == "__main__" and BACKEND_FRAMEWORK == "fastapi":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

# Start the Flask app on port 8080
if __name__ == "__main__" and BACKEND_FRAMEWORK == "flask":
    app.run(host="0.0.0.0", port=8080)
