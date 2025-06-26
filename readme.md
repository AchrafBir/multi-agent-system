# Multi-Agent System (MAS) for Load Balancing in Big Data Environments

This project is a **Multi-Agent System (MAS)** designed specifically for **load balancing** and task management in **big data environments**. The system is capable of generating, scheduling, and processing tasks across a distributed network of agents, ensuring optimal load distribution and resource utilization. The system supports real-time monitoring through a graphical dashboard, providing detailed insights into task progress, agent health, and overall system performance.

## Key Features

- **Load Balancing**: The system uses an intelligent load balancing mechanism to ensure that tasks are evenly distributed among worker agents based on their available resources. This ensures no agent is overwhelmed, making it ideal for **large-scale, big data processing** environments.
  
- **Big Data Ready**: Designed to efficiently manage and process large amounts of data. It can scale to handle thousands of tasks concurrently, with the ability to distribute and process data across multiple worker nodes in real-time.
  
- **Task Generation and Queueing**: Automatically generates tasks with random data, priorities, and locations, and stores them in a priority queue. The queue is managed dynamically, processing tasks based on their priority and system resource availability.

- **Multi-Agent Architecture**: Includes various agents responsible for different functions in the system:
  - **Worker Agents**: Process the tasks assigned by the load balancer.
  - **Load Balancer Agent**: Distributes tasks across available worker agents based on current load and resource usage.
  - **Resource Manager Agent**: Manages the allocation of resources across agents to ensure efficient task processing.
  - **Cluster Manager Agent**: Coordinates and oversees the overall functioning of the agent network.
  - **Monitor Agent**: Monitors the health and status of agents and the system.
  
- **Real-Time Dashboard**: A graphical user interface (GUI) that displays system statistics, agent performance, and task progress in real-time. It allows users to visualize the task queue, agent status, resource utilization, and completed tasks.

- **Comprehensive Logging**: All actions in the system, including task generation, agent status updates, and load balancing actions, are logged for debugging, monitoring, and analysis.

## Requirements

- Python 3.x
- `tkinter` for GUI
- `logging` for logging system events
- `threading` for multi-threaded task processing
- Additional dependencies (listed in `requirements.txt`)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/multi-agent-system.git
    cd multi-agent-system
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

You can configure the system by editing the `config/settings.py` file. Important configuration parameters include:

- `NUM_TASKS_TO_GENERATE`: Number of tasks to generate in the system.
- `TASK_GENERATION_INTERVAL`: Interval between the generation of tasks.
- `INITIAL_NODES`: List of initial nodes for worker agents.
- `NUM_WORKERS`: Number of worker agents to create.
- `LOAD_BALANCER_STRATEGY`: Configurable strategies for load balancing (e.g., based on CPU, memory, or custom metrics).

## Usage

To run the system, you need to generate tasks first, and then start the system:

### Step 1: Generate Tasks

Before running the main system, you must generate the tasks that will be processed. To do this, run the `generate_tasks.py` script:
```bash
python generate_tasks.py
