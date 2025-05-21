# Multi-Agent System with Supervisor

This is a Python-based multi-agent system that implements a supervisor-worker architecture. The system allows for distributed task processing with a central supervisor coordinating the work.

## Features

- Supervisor agent for task coordination and worker management
- Worker agents with specific capabilities
- Asynchronous task processing
- Task queue system
- Error handling and logging
- Status tracking for agents

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The system can be run directly using:

```bash
python agent_system.py
```

### Creating Custom Workers

To create a custom worker agent, extend the `WorkerAgent` class:

```python
class CustomWorker(WorkerAgent):
    def __init__(self, agent_id: str, capabilities: List[str]):
        super().__init__(agent_id, capabilities)
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        # Implement your custom task processing logic here
        pass
```

### Submitting Tasks

Tasks can be submitted to the supervisor:

```python
task = Task(
    id="unique_task_id",
    type="task_type",
    data={"input": "your_data"},
    priority=1
)
supervisor.submit_task(task)
```

## Architecture

- `Agent`: Abstract base class for all agents
- `WorkerAgent`: Base class for worker agents
- `Supervisor`: Manages workers and task distribution
- `Task`: Data structure for representing tasks

## License

MIT License 