import asyncio
import logging
from agent_system import Supervisor, WorkerAgent, Task
import uuid
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CommandInterface:
    def __init__(self):
        self.supervisor = Supervisor()
        self.task_loop = None

    async def start(self):
        """Start the supervisor and task assignment loop"""
        self.task_loop = asyncio.create_task(self.supervisor.assign_tasks())
        logger.info("System started")

    async def stop(self):
        """Stop the system"""
        if self.task_loop:
            self.task_loop.cancel()
            logger.info("System stopped")

    def add_worker(self, worker_id: str, capabilities: List[str]):
        """Add a new worker to the system"""
        worker = WorkerAgent(worker_id, capabilities)
        self.supervisor.register_worker(worker)
        logger.info(f"Added worker {worker_id} with capabilities: {capabilities}")

    def submit_task(self, task_type: str, data: Dict, priority: int = 1):
        """Submit a new task to the system"""
        task = Task(
            id=str(uuid.uuid4()),
            type=task_type,
            data=data,
            priority=priority
        )
        self.supervisor.submit_task(task)
        logger.info(f"Submitted task {task.id} of type {task_type} with priority {priority}")

    def get_worker_status(self):
        """Get current status of all workers"""
        statuses = {}
        for worker_id, worker in self.supervisor.workers.items():
            statuses[worker_id] = {
                "status": worker.status.value,
                "current_task": worker.current_task.id if worker.current_task else None
            }
        return statuses

    def get_task_results(self):
        """Get results of completed tasks"""
        return self.supervisor.task_results

async def main():
    # Create command interface
    interface = CommandInterface()
    await interface.start()

    # Example commands
    try:
        # Add workers
        interface.add_worker("worker1", ["data_processing", "analysis"])
        interface.add_worker("worker2", ["reporting", "data_processing"])

        # Submit tasks
        interface.submit_task(
            "data_processing",
            {"input": "data.csv", "operation": "clean"},
            priority=1
        )
        interface.submit_task(
            "analysis",
            {"input": "processed_data.json", "method": "statistical"},
            priority=2
        )

        # Let the system run for a while
        await asyncio.sleep(5)

        # Check status
        print("\nWorker Statuses:")
        for worker_id, status in interface.get_worker_status().items():
            print(f"{worker_id}: {status}")

        # Check results
        print("\nTask Results:")
        for task_id, result in interface.get_task_results().items():
            print(f"{task_id}: {result}")

    finally:
        await interface.stop()

if __name__ == "__main__":
    asyncio.run(main()) 