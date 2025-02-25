from robyn import Robyn
import sqlite3
import json

app = Robyn(__file__)

# Initialize SQLite database
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY, title TEXT, description TEXT)''')
conn.commit()

# Define the root endpoint
@app.get("/")
async def h(request):
    return "Hello, world!"

# Define the status endpoint
@app.get("/status")
async def h(request):
    return "Up and running"

# Define the endpoint to retrieve all tasks
@app.get("/tasks")
async def get_tasks(request):
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    return json.dumps(tasks)

# Define the endpoint to create a new task
@app.post("/tasks")
async def create_task(request):
    data = await request.json()
    title = data.get('title')
    description = data.get('description')
    c.execute('INSERT INTO tasks (title, description) VALUES (?, ?)', (title, description))
    conn.commit()
    return "Task created successfully"

# Define the endpoint to update an existing task
@app.put("/tasks/{task_id}")
async def update_task(request, task_id):
    data = await request.json()
    title = data.get('title')
    description = data.get('description')
    c.execute('UPDATE tasks SET title = ?, description = ? WHERE id = ?', (title, description, task_id))
    conn.commit()
    return "Task updated successfully"

# Define the endpoint to delete a task
@app.delete("/tasks/{task_id}")
async def delete_task(request, task_id):
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    return "Task deleted successfully"

# Start the Robyn app on port 8080
app.start(port=8080)