import asyncio
import logging
from agent_system import Supervisor, WorkerAgent, Task
import uuid
from datetime import datetime

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_system():
    # Create supervisor
    supervisor = Supervisor()
    logger.info("Supervisor created")

    # Create and register workers with different capabilities
    workers = [
        WorkerAgent("data_processor", ["data_processing", "analysis"]),
        WorkerAgent("reporter", ["reporting", "data_processing"]),
        WorkerAgent("analyzer", ["analysis", "data_processing"])
    ]
    
    for worker in workers:
        supervisor.register_worker(worker)
    logger.info(f"Registered {len(workers)} workers")

    # Start task assignment loop
    task_loop = asyncio.create_task(supervisor.assign_tasks())
    logger.info("Task assignment loop started")

    # Create test tasks with different types and priorities
    tasks = [
        Task(
            id=str(uuid.uuid4()),
            type="data_processing",
            data={"input": "dataset1.csv", "operation": "clean"},
            priority=1
        ),
        Task(
            id=str(uuid.uuid4()),
            type="analysis",
            data={"input": "processed_data.json", "method": "statistical"},
            priority=2
        ),
        Task(
            id=str(uuid.uuid4()),
            type="reporting",
            data={"input": "analysis_results.json", "format": "pdf"},
            priority=3
        ),
        Task(
            id=str(uuid.uuid4()),
            type="data_processing",
            data={"input": "dataset2.csv", "operation": "transform"},
            priority=1
        )
    ]

    # Submit tasks
    for task in tasks:
        supervisor.submit_task(task)
        logger.info(f"Submitted task {task.id} of type {task.type} with priority {task.priority}")

    # Let the system run for a while
    logger.info("System running for 10 seconds...")
    await asyncio.sleep(10)

    # Print results
    logger.info("\nTask Results:")
    for task_id, result in supervisor.task_results.items():
        logger.info(f"Task {task_id}: {result}")

    # Print worker statuses
    logger.info("\nWorker Statuses:")
    for worker_id, worker in supervisor.workers.items():
        logger.info(f"Worker {worker_id}: {worker.status.value}")

    # Cancel the task loop
    task_loop.cancel()
    logger.info("Test completed")

if __name__ == "__main__":
    logger.info("Starting multi-agent system test")
    asyncio.run(test_system()) 