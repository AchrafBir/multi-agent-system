# Multi-Agent System (MAS)

A task-processing system that coordinates worker agents and provides a desktop (Tkinter) dashboard for real-time monitoring of queue progress, agent health, and performance metrics.

## Key features

- Desktop real-time dashboard (Tkinter): live metrics, agent status, and logs
- Dynamic agent management: spawn/stop workers based on workload (auto-scaling if enabled)
- Task queue: generate, enqueue, distribute, and process tasks
- Resource monitoring: CPU/memory sampling and throughput/latency tracking
- Modular codebase: clear separation of agents, communication, tasks, and metrics
- Optional multi-node operation: run agents on different machines if your communication layer is configured for remote connectivity

## Quickstart

```bash
git clone https://github.com/AchrafBir/multi-agent-system.git
cd multi-agent-system

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python generate_tasks.py
python main.py
```

Expected: a Tkinter window opens showing live queue, agents, metrics, and logs while tasks are being processed.

## Architecture

High-level components:

- Controller (`main.py`)
  - owns the queue lifecycle
  - starts and supervises worker agents
  - aggregates metrics and logs for the dashboard

- Agents (`agents/`)
  - worker processes/threads that pull tasks from the queue
  - report status and metrics

- Communication (`communication/`)
  - message passing between controller and agents
  - can be local-only or remote-capable depending on implementation

- Task system (`tasks/`)
  - task definitions and queue persistence (for example JSON-backed queue)

- Metrics (`utils/metrics.py`)
  - throughput, latency, and resource sampling

- Dashboard (`dashboard/dashboard.py`)
  - Tkinter UI displaying queue, agents, metrics, and logs

Data flow:

Task generator -> Task queue -> Agents -> Metrics/Logs -> Dashboard

## Deployment modes

- Single-node (default)
  - controller and agents run on the same machine

- Multi-node (optional)
  - controller runs on one machine
  - agents run on other machines and connect to the controller through `communication/`
  - requires configuring controller host/port (or equivalent) in `config/`


## Project structure

```text
agents/               Agent implementations (workers, lifecycle, status)
communication/        Inter-agent/controller communication layer
config/               Configuration files (constants, JSON/YAML, etc.)
dashboard/            Tkinter dashboard UI (dashboard.py)
data/                 Persistence/caching utilities (if used)
tasks/                Task definitions and queue storage (e.g., tasks.json)
utils/                Helpers and metrics collection
generate_tasks.py     Task generation utility
main.py               Entry point (controller + dashboard)
requirements.txt      Dependencies
LICENSE               License file
```

## Repository hygiene
```gitignore
.venv/
myenv/
__pycache__/
*.pyc
*.log
logs/
tasks/tasks.json
*.sqlite
.DS_Store
```
## Requirements

- Python 3.10+
- OS: Linux/Windows (tested on: add your OS here)

Note (Linux): Tkinter may require an additional package from your distro (for example `python3-tk`).

## Installation

```bash
git clone https://github.com/AchrafBir/multi-agent-system.git
cd multi-agent-system

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Usage

### 1) Generate tasks

```bash
python generate_tasks.py
```

This creates or refreshes the task queue used by agents.

### 2) Start the system

```bash
python main.py
```

This starts the controller, launches agents, and opens the Tkinter dashboard.

### 3) Monitor via dashboard

Typical dashboard panels:

- Task queue: queued/completed/failed counts
- Performance: throughput and processing latency
- Agent resources: CPU/memory utilization
- Agent status: active/idle/busy/error
- Logs: real-time activity and task lifecycle events

## Configuration

Configuration is stored in `config/`. Document the actual keys used by your code.

Common settings to expose:

- Agent scaling
  - `AGENT_MIN`
  - `AGENT_MAX`
  - `SCALE_UP_THRESHOLD`
  - `SCALE_DOWN_THRESHOLD`

- Queue
  - `TASK_QUEUE_PATH`

- Dashboard
  - `DASHBOARD_REFRESH_MS`

- Logging
  - `LOG_LEVEL`
  - `LOG_PATH`

## Metrics

Metrics typically tracked:

- Throughput: tasks completed per unit time
- Latency: average/median processing time per task
- Resource utilization: CPU and memory per agent (sampled)
- Errors: task failures, retries, agent restarts

## Benchmarking

Recommended procedure:

```bash
python generate_tasks.py
python main.py
```

Report (once measured):

- Hardware: CPU / RAM / OS
- Number of agents
- Task count and task type
- Throughput and latency summary

## Troubleshooting

- Dashboard does not open
  - Verify Tkinter is installed (Linux may require `python3-tk`)
  - Check logs for UI initialization errors

- Queue not progressing
  - Ensure tasks were generated successfully
  - Validate queue file format (JSON errors are common)
  - Inspect dashboard logs for task parsing/processing errors

- High CPU usage
  - Reduce max agent count
  - Increase dashboard refresh interval
  - Reduce task complexity

- Dependency issues
  - Recreate venv and reinstall requirements:
    - delete `.venv/`, recreate, then `pip install -r requirements.txt`

## Roadmap

- Durable queue backend (Redis or database)
- True multi-node support with authentication and secure transport
- Retry policy and dead-letter queue
- CI: lint + tests + packaging

## Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/name`
3. Commit changes
4. Add/update tests
5. Open a pull request

## License

MIT License. See `LICENSE`.
