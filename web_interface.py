from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import asyncio
import os
from agent_system import Supervisor, WorkerAgent, Task

app = FastAPI(title="Multi-Agent System API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the supervisor
supervisor = Supervisor()

# Create and register workers
worker1 = WorkerAgent("worker1", ["data_processing", "analysis"])
worker2 = WorkerAgent("worker2", ["data_processing", "reporting"])
supervisor.register_worker(worker1)
supervisor.register_worker(worker2)

# Start the task assignment loop in the background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(supervisor.assign_tasks())

class TaskRequest(BaseModel):
    type: str
    data: Dict[str, Any]
    priority: int = 1

@app.get("/")
async def read_root():
    return FileResponse('templates/index.html')

@app.get("/workers")
async def get_workers():
    return {
        "workers": [
            {
                "id": worker.agent_id,
                "status": worker.status.value,
                "capabilities": worker.capabilities
            }
            for worker in supervisor.workers.values()
        ]
    }

@app.get("/tasks")
async def get_tasks():
    return {
        "pending_tasks": [
            {
                "id": task.id,
                "type": task.type,
                "priority": task.priority,
                "status": task.status
            }
            for task in supervisor.task_queue
        ]
    }

@app.post("/submit")
async def submit_task(task_request: TaskRequest):
    import uuid
    task_id = str(uuid.uuid4())
    task = Task(
        id=task_id,
        type=task_request.type,
        data=task_request.data,
        priority=task_request.priority
    )
    supervisor.submit_task(task)
    return {"message": f"Task {task_id} submitted successfully"}

@app.get("/results")
async def get_results():
    return {"results": supervisor.task_results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 