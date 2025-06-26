import sys
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import time
import threading
import logging
import random
import tkinter as tk

from config import settings, logging_config
from tasks.task import Task
from tasks.task_queue import TaskQueue
from tasks.scheduler import Scheduler
from communication.message_bus import MessageBus
from dashboard.dashboard import Dashboard

from agents.worker_agent import WorkerAgent
from agents.load_balancer import LoadBalancerAgent
from agents.monitor_agent import MonitorAgent
from agents.resource_manager import ResourceManagerAgent
from agents.cluster_manager import ClusterManagerAgent

def task_generator(task_queue):
    thread = threading.current_thread()
    node_choices = settings.INITIAL_NODES + ["unspecified"]
    while getattr(thread, "is_running", True):
        new_task = Task(
            data={"payload": f"data_{random.randint(1000, 9999)}"},
            priority=random.choice([1, 5, 10]),
            data_location=random.choice(node_choices)
        )
        task_queue.add_task(new_task)
        logging.info(f"Generated new task: {new_task.task_id} (Prio: {new_task.priority}, Loc: {new_task.data_location})")
        time.sleep(settings.TASK_GENERATION_INTERVAL)

def main():
    logging_config.setup_logging()
    logging.info("Starting Enhanced Multi-Agent System...")

    message_bus = MessageBus()
    task_queue = TaskQueue()
    
    agents = []
    agents_lock = threading.Lock()

    logging.info("Phase 1: Creating all agents...")
    for i in range(settings.NUM_WORKERS):
        worker_id = f"worker_initial_{i}"
        node_id = settings.INITIAL_NODES[i % len(settings.INITIAL_NODES)]
        agents.append(WorkerAgent(worker_id, message_bus, node_id))

    agents.append(LoadBalancerAgent(message_bus))
    agents.append(MonitorAgent(message_bus))
    agents.append(ResourceManagerAgent(message_bus, task_queue))
    agents.append(ClusterManagerAgent(message_bus, agents, agents_lock))
    data_file_path = "data/tasks.json"
    scheduler = Scheduler(task_queue, message_bus, "data/tasks.json")
    
    logging.info("Phase 2: Registering all agent subscriptions...")
    for agent in agents:
        agent.register_subscriptions()
    
    root = tk.Tk()
    app = Dashboard(root, message_bus, task_queue)

    logging.info("Phase 3: Starting all threads...")
    message_bus.start()
    scheduler.start()
    for agent in agents:
        agent.start()

    generator_thread = threading.Thread(target=task_generator, args=(task_queue,), name="TaskGenerator", daemon=True)
    generator_thread.is_running = True
    generator_thread.start()
    
    def on_closing():
        logging.info("Shutdown sequence initiated...")
        generator_thread.is_running = False
        scheduler.stop()
        
        with agents_lock:
            for agent in agents:
                agent.stop()
        
        generator_thread.join(2)
        scheduler.join(2)
        for agent in agents:
            agent.join(2)
        message_bus.stop()
        message_bus.join(2)
        
        logging.info("System has been shut down.")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
