from agents.base_agent import BaseAgent
from communication.protocol import (
    TOPIC_TASK_REQUEST, TOPIC_AGENT_REGISTER, TOPIC_TASK_EXECUTE, 
    TOPIC_AGENT_STATUS_UPDATE, TOPIC_SYSTEM_COMMAND, CMD_PAUSE_WORKER, CMD_RESUME_WORKER
)
from config.settings import LOAD_BALANCER_ID
from collections import deque
import threading
import time

class LoadBalancerAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(LOAD_BALANCER_ID, message_bus)
        self.workers = {}
        self.paused_workers = set()
        self.task_backlog = deque()
        self.discovery_lock = threading.Lock()
        self.last_discovery_time = 0
        self.discovery_interval = 10
        self.worker_timeout = 60

    def register_subscriptions(self):
        self.message_bus.subscribe(TOPIC_AGENT_REGISTER, self.handle_worker_registration)
        self.message_bus.subscribe(TOPIC_TASK_REQUEST, self.handle_task_request)
        self.message_bus.subscribe(TOPIC_AGENT_STATUS_UPDATE, self.handle_agent_status_update)
        self.message_bus.subscribe(TOPIC_SYSTEM_COMMAND, self.handle_system_command)
        self.message_bus.subscribe("TOPIC_CLUSTER_RESPONSE", self.handle_cluster_response)

    def setup(self):
        self.discover_existing_workers()
        self.start_periodic_tasks()

    def start_periodic_tasks(self):
        def periodic_discovery():
            while True:
                time.sleep(self.discovery_interval)
                self.cleanup_stale_workers()
                if time.time() - self.last_discovery_time > self.discovery_interval:
                    self.discover_existing_workers()
                self.log_system_status()
        
        discovery_thread = threading.Thread(target=periodic_discovery, daemon=True)
        discovery_thread.start()

    def cleanup_stale_workers(self):
        current_time = time.time()
        stale_workers = []
        
        for worker_id, data in self.workers.items():
            if current_time - data.get("last_seen", 0) > self.worker_timeout:
                stale_workers.append(worker_id)
        
        for worker_id in stale_workers:
            self.log(f"Removing stale worker: {worker_id}")
            del self.workers[worker_id]
            self.paused_workers.discard(worker_id)

    def log_system_status(self):
        idle_workers = [w_id for w_id, data in self.workers.items() if data["status"] == "IDLE"]
        busy_workers = [w_id for w_id, data in self.workers.items() if data["status"] == "BUSY"]
        
        self.log(f"=== SYSTEM STATUS ===")
        self.log(f"Tasks in backlog: {len(self.task_backlog)}")
        self.log(f"Total workers: {len(self.workers)}")
        self.log(f"IDLE workers: {len(idle_workers)} - {idle_workers}")
        self.log(f"BUSY workers: {len(busy_workers)} - {busy_workers}")
        self.log(f"Paused workers: {len(self.paused_workers)}")

    def discover_existing_workers(self):
        with self.discovery_lock:
            self.last_discovery_time = time.time()
            
            discovery_message = {
                "command": "WORKER_DISCOVERY_REQUEST",
                "requester": self.agent_id,
                "timestamp": self.last_discovery_time
            }
            
            self.send_message(TOPIC_SYSTEM_COMMAND, payload=discovery_message, recipient_id="broadcast")
            self.request_worker_status_from_cluster()
            self.log(f"Sent worker discovery broadcast and cluster status request")

    def request_worker_status_from_cluster(self):
        cluster_request = {
            "command": "GET_ALL_WORKER_STATUS",
            "requester": self.agent_id,
            "timestamp": time.time()
        }
        
        self.send_message("TOPIC_CLUSTER_QUERY", payload=cluster_request, recipient_id="cluster_manager")

    def handle_cluster_response(self, message):
        payload = message.get("payload", {})
        command = payload.get("command")
        
        if command == "WORKER_STATUS_LIST":
            cluster_workers = payload.get("workers", [])
            current_time = time.time()
            
            for worker_info in cluster_workers:
                worker_id = worker_info.get("agent_id")
                if worker_id and worker_id.startswith("worker_"):
                    self.workers[worker_id] = {
                        "status": worker_info.get("status", "IDLE"),
                        "node_id": worker_info.get("node_id", "unknown"),
                        "last_seen": current_time
                    }
            
            self.log(f"Updated worker registry from cluster manager: {len(cluster_workers)} workers")
            self.try_dispatch_backlog()

    def handle_worker_registration(self, message):
        worker_id = message["payload"].get("agent_id") or message.get("sender_id")
        
        if worker_id and worker_id.startswith("worker_"):
            payload = message["payload"]
            status = payload.get("status", "IDLE")
            node_id = payload.get("node_id", "unknown-dynamic-node")
            current_time = time.time()

            self.workers[worker_id] = {
                "status": status, 
                "node_id": node_id,
                "last_seen": current_time
            }
            
            self.log(f"Registered worker: {worker_id} on node {node_id}. Status: {status}")

            if status == "IDLE":
                self.log(f"New IDLE worker {worker_id} available. Checking backlog.")
                self.try_dispatch_backlog()

    def handle_agent_status_update(self, message):
        payload = message.get("payload", {})
        agent_id = payload.get("agent_id")
        status = payload.get("status")
        command = payload.get("command")
        
        if command == "WORKER_DISCOVERY_RESPONSE":
            if agent_id and agent_id.startswith("worker_"):
                self.workers[agent_id] = {
                    "status": status or "IDLE",
                    "node_id": payload.get("node_id", "unknown"),
                    "last_seen": time.time()
                }
                self.log(f"Discovered worker via response: {agent_id} - {status}")
                return
        
        if agent_id and agent_id in self.workers:
            self.workers[agent_id]["status"] = status
            self.workers[agent_id]["last_seen"] = time.time()
            
            self.log(f"Worker {agent_id} status updated to {status}")
            
            if status == "IDLE":
                self.try_dispatch_backlog()

    def handle_task_request(self, message):
        task = message["payload"]["task"]
        self.task_backlog.append(task)
        
        self.log(f"Received task {task.get('task_id', 'unknown')}. Backlog size: {len(self.task_backlog)}")
        
        self.try_dispatch_backlog()
        
        if len(self.task_backlog) > 5:
            available_workers = self.get_available_workers()
            if not available_workers:
                self.log(f"No available workers found with {len(self.task_backlog)} tasks queued. Triggering discovery.")
                self.discover_existing_workers()
                self.send_scaling_pause_request()

    def send_scaling_pause_request(self):
        pause_request = {
            "command": "PAUSE_SCALING",
            "reason": "LoadBalancer discovering existing workers",
            "duration": 15,
            "requester": self.agent_id,
            "available_workers": len(self.get_available_workers()),
            "backlog_size": len(self.task_backlog)
        }
        
        self.send_message("TOPIC_CLUSTER_COMMAND", payload=pause_request, recipient_id="cluster_manager")

    def handle_system_command(self, message):
        payload = message.get("payload", {})
        command = payload.get("command")
        
        if command == "WORKER_DISCOVERY_REQUEST":
            if self.agent_id.startswith("worker_"):
                response = {
                    "command": "WORKER_DISCOVERY_RESPONSE",
                    "agent_id": self.agent_id,
                    "status": getattr(self, 'status', 'IDLE'),
                    "node_id": getattr(self, 'node_id', 'unknown'),
                    "timestamp": time.time()
                }
                self.send_message(TOPIC_AGENT_STATUS_UPDATE, payload=response)
            return
        
        target = payload.get("target_worker")
        
        if command == CMD_PAUSE_WORKER and target in self.workers:
            self.log(f"Pausing assignments to worker {target}")
            self.paused_workers.add(target)
            
        elif command == CMD_RESUME_WORKER and target in self.paused_workers:
            self.log(f"Resuming assignments to worker {target}")
            self.paused_workers.remove(target)
            
            self.log(f"Worker {target} resumed. Checking backlog.")
            self.try_dispatch_backlog()

    def get_available_workers(self):
        return [
            w_id for w_id, data in self.workers.items() 
            if data["status"] == "IDLE" and w_id not in self.paused_workers
        ]

    def validate_task(self, task):
        required_fields = ["task_id", "data", "priority", "location"]
        for field in required_fields:
            if field not in task:
                self.log(f"Error: Task missing {field}. Task data: {task}")
                return False
        return True

    def try_dispatch_backlog(self):
        with self.discovery_lock:
            if not self.task_backlog:
                return

            available_workers = self.get_available_workers()
            
            if not available_workers:
                self.log(f"No available workers for {len(self.task_backlog)} queued tasks")
                return

            dispatched_count = 0
            while self.task_backlog and available_workers:
                task_to_assign = self.task_backlog.popleft()
                
                if not self.validate_task(task_to_assign):
                    continue
                
                worker_to_assign = available_workers.pop(0)
                
                self.workers[worker_to_assign]["status"] = "BUSY"
                self.workers[worker_to_assign]["last_seen"] = time.time()
                
                task_payload = {
                    "task_id": task_to_assign["task_id"],
                    "data": task_to_assign["data"],
                    "priority": task_to_assign["priority"],
                    "location": task_to_assign["location"]
                }

                self.send_message(
                    TOPIC_TASK_EXECUTE, 
                    payload={"task": task_payload}, 
                    recipient_id=worker_to_assign
                )
                
                dispatched_count += 1
                self.log(f"Task {task_to_assign['task_id']} assigned to worker {worker_to_assign}")

            self.log(f"Dispatched {dispatched_count} tasks. Remaining backlog: {len(self.task_backlog)}")
            
            if self.task_backlog and not self.get_available_workers():
                current_time = time.time()
                if current_time - self.last_discovery_time > 5:
                    self.log("Still have tasks but no available workers. Triggering discovery.")
                    self.discover_existing_workers()