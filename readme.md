# Multi-Agent System (MAS)

A distributed computing system that manages and monitors worker agents across multiple nodes for parallel task processing.

## 🚀 Features

- **Real-time Dashboard**: Desktop GUI (Tkinter) with live metrics and monitoring
- **Dynamic Agent Management**: Automatic worker scaling and load balancing
- **Task Queue System**: Efficient task distribution and processing
- **Resource Monitoring**: CPU, memory, and performance tracking
- **Node Distribution**: Support for multiple compute nodes
- **Auto-scaling**: Dynamic worker creation based on workload

## 📊 Dashboard Overview

The system provides a comprehensive dashboard showing:

- **Task Queue Status**: Current queued and completed tasks
- **Performance Metrics**: Average processing times and throughput
- **Agent Resources**: CPU and memory utilization across all agents
- **Node Distribution**: Worker distribution across compute nodes
- **Real-time Logs**: System activity and task processing logs

## 🏗️ Project Structure

```
mas/
├── .venv/                 # Python virtual environment
├── agents/               # Agent-related modules
├── communication/        # Inter-agent communication
├── config/              # Configuration files
├── dashboard/           # Web dashboard components
│   ├── __pycache__/
│   └── dashboard.py     # Main dashboard application
├── data/                # Data storage and caching
│   ├── __pycache__/
│   ├── storage.py       # Data persistence layer
│   ├── __init__.py
│   └── processor.py     # Data processing utilities
├── myenv/               # Additional environment files
├── tasks/               # Task management
│   └── tasks.json       # Task definitions and queue
├── utils/               # Utility functions
│   ├── __pycache__/
│   ├── helpers.py       # Helper functions
│   └── metrics.py       # Performance metrics collection
├── generate_tasks.py    # Task generation utility
├── main.py             # Main application entry point
└── system.log          # System logs
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mas
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚦 Usage

### Starting the System

1. **Generate tasks first**
   ```bash
   python generate_tasks.py
   ```
   This creates the initial task queue that the agents will process.

2. **Launch the main application**
   ```bash
   python main.py
   ```
   This starts the multi-agent system and opens a Tkinter-based dashboard window.

3. **Monitor the system**
   - The dashboard will automatically open as a desktop application (Tkinter GUI)
   - Monitor real-time system performance and agent status through the interface
   - No web browser required - everything runs in the desktop application

### Task Management

- **Generate tasks**: Use `generate_tasks.py` to create new tasks
- **Monitor progress**: View task completion in the dashboard
- **Resource allocation**: Agents automatically scale based on queue size

### Configuration

Edit configuration files in the `config/` directory to customize:
- Agent behavior and resource limits
- Task processing parameters
- Dashboard refresh intervals
- Logging levels

## 📈 Performance Metrics

The system tracks several key performance indicators:

- **Throughput**: Tasks completed per minute (currently ~100 tasks/min)
- **Response Time**: Average task processing time (currently ~0.2s)
- **Resource Utilization**: CPU (~52%) and Memory (~46%) usage
- **Agent Efficiency**: Most productive agents and task distribution

## 🔧 Key Components

### Agents
- **Worker Agents**: Process individual tasks from the queue
- **Dynamic Scaling**: Agents created/destroyed based on workload
- **Status Monitoring**: Real-time tracking of agent health and performance

### Dashboard
- **Desktop Application**: Tkinter-based GUI for system monitoring
- **Real-time Updates**: Live metrics and status updates
- **Agent Management**: View and control individual agents
- **System Logs**: Comprehensive logging with filtering capabilities

### Task Processing
- **Queue Management**: FIFO task processing with priority support
- **Load Balancing**: Intelligent task distribution across agents
- **Fault Tolerance**: Automatic retry and error handling

## 🔍 Monitoring

### Dashboard Sections

1. **Task Queue**: Shows pending and completed task counts
2. **Performance**: Displays processing times and throughput
3. **Agent Resources**: CPU/memory usage across all agents
4. **Node Distribution**: Geographic/logical distribution of workers
5. **System Logs**: Real-time activity monitoring

### Log Analysis
- View system logs in real-time through the dashboard
- Filter logs by component, severity, or time range
- Monitor task processing and agent lifecycle events

## 🚨 Troubleshooting

### Common Issues

1. **High CPU Usage**: Adjust agent count or task complexity
2. **Memory Leaks**: Monitor long-running agents and restart if needed
3. **Task Backlog**: Scale up agents or optimize task processing
4. **Connection Issues**: Check network connectivity between nodes

### Performance Optimization

- Monitor resource usage patterns in the dashboard
- Adjust worker count based on queue depth
- Optimize task processing algorithms
- Use caching for frequently accessed data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

[Add your license information here]

## 📞 Support

For issues and questions:
- Check the system logs in the dashboard
- Review the troubleshooting section
- Open an issue in the repository

---

**Last Updated**: Generated from system dashboard showing 10,413 completed tasks with optimal performance metrics.
