from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class Task:
    id: str
    type: str
    data: Dict[str, Any]
    priority: int = 1
    status: str = "pending"

class Agent(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.current_task: Optional[Task] = None

    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        pass

    async def execute_task(self, task: Task) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        self.current_task = task
        try:
            result = await self.process_task(task)
            self.status = AgentStatus.IDLE
            return result
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_id} failed to process task {task.id}: {str(e)}")
            raise

class WorkerAgent(Agent):
    def __init__(self, agent_id: str, capabilities: List[str]):
        super().__init__(agent_id)
        self.capabilities = capabilities

    async def process_task(self, task: Task) -> Dict[str, Any]:
        logger.info(f"Worker {self.agent_id} processing task {task.id}")
        # Simulate task processing
        await asyncio.sleep(1)
        return {"result": f"Task {task.id} completed by {self.agent_id}"}

class Supervisor:
    def __init__(self):
        self.workers: Dict[str, WorkerAgent] = {}
        self.task_queue: List[Task] = []
        self.task_results: Dict[str, Dict[str, Any]] = {}

    def register_worker(self, worker: WorkerAgent):
        self.workers[worker.agent_id] = worker
        logger.info(f"Worker {worker.agent_id} registered with capabilities: {worker.capabilities}")

    def submit_task(self, task: Task):
        self.task_queue.append(task)
        logger.info(f"Task {task.id} submitted to queue")

    async def assign_tasks(self):
        while True:
            if not self.task_queue:
                await asyncio.sleep(1)
                continue

            task = self.task_queue.pop(0)
            available_workers = [w for w in self.workers.values() if w.status == AgentStatus.IDLE]
            
            if not available_workers:
                self.task_queue.append(task)  # Put back in queue if no workers available
                await asyncio.sleep(1)
                continue

            # Simple round-robin assignment
            worker = available_workers[0]
            try:
                result = await worker.execute_task(task)
                self.task_results[task.id] = result
                logger.info(f"Task {task.id} completed with result: {result}")
            except Exception as e:
                logger.error(f"Failed to process task {task.id}: {str(e)}")

async def main():
    # Create supervisor
    supervisor = Supervisor()

    # Create and register workers
    worker1 = WorkerAgent("worker1", ["data_processing", "analysis"])
    worker2 = WorkerAgent("worker2", ["data_processing", "reporting"])
    supervisor.register_worker(worker1)
    supervisor.register_worker(worker2)

    # Start task assignment loop
    task_loop = asyncio.create_task(supervisor.assign_tasks())

    # Submit some example tasks
    tasks = [
        Task("task1", "data_processing", {"input": "data1"}),
        Task("task2", "analysis", {"input": "data2"}),
        Task("task3", "reporting", {"input": "data3"})
    ]

    for task in tasks:
        supervisor.submit_task(task)

    # Let the system run for a while
    await asyncio.sleep(5)
    task_loop.cancel()

if __name__ == "__main__":
    asyncio.run(main()) 