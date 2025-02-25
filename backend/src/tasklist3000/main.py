from robyn import Robyn

app = Robyn(__file__)

@app.get("/")
async def h(request):
    return "Hello, world!"

@app.get("/status")
async def h(request):
    return "Up and running"

@app.get("/tasks")
async def h(request):
    return "Here are your tasks!"

app.start(port=8080)