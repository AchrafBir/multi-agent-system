import time
import random
import threading
from agents.base_agent import BaseAgent
from communication.protocol import (
    TOPIC_TASK_EXECUTE, TOPIC_TASK_COMPLETED, TOPIC_AGENT_REGISTER, 
    TOPIC_AGENT_STATUS_UPDATE, TOPIC_RESOURCE_UPDATE, TOPIC_SYSTEM_COMMAND, CMD_SHUTDOWN_WORKER
)
from data.processor import preprocess_data
from tasks.task import TaskStatus

class WorkerAgent(BaseAgent):
    def __init__(self, agent_id, message_bus, node_id: str):
        super().__init__(agent_id, message_bus)
        self.node_id = node_id
        self.status = "IDLE"
        self.current_task = None
        self.current_task_id = None
        self.last_heartbeat = time.time()
        self.tasks_completed = 0
        
        self.start_heartbeat()

    def register_subscriptions(self):
        self.message_bus.subscribe(TOPIC_TASK_EXECUTE, self.handle_task_execute)
        self.message_bus.subscribe(TOPIC_SYSTEM_COMMAND, self.handle_system_command)
        
    def setup(self):
        register_payload = {
            "agent_id": self.agent_id,
            "status": self.status, 
            "node_id": self.node_id
        }
        self.send_message(TOPIC_AGENT_REGISTER, payload=register_payload)
        
        self.update_status(self.status)
        
        self.report_resources(is_busy=False)

    def start_heartbeat(self):
        def heartbeat_loop():
            while self._is_running:
                try:
                    time.sleep(30)
                    if self._is_running:
                        self.send_heartbeat()
                except Exception as e:
                    self.log(f"Heartbeat error: {e}", level='error')
        
        heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        heartbeat_thread.start()

    def send_heartbeat(self):
        self.last_heartbeat = time.time()

        cpu_usage = random.uniform(2, 98)
        memory_usage = random.uniform(10, 80)

        heartbeat_payload = {
            "agent_id": self.agent_id,
            "status": self.status,
            "node_id": self.node_id,
            "current_task_id": self.current_task_id,
            "heartbeat": True,
            "timestamp": self.last_heartbeat,
            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_usage, 2)
        }

        self.send_message(TOPIC_AGENT_STATUS_UPDATE, payload=heartbeat_payload)
        self.report_resources(is_busy=(self.status == "BUSY"))

    def handle_task_execute(self, message):
        if not self._is_running:
            return

        if self.status == "BUSY":
            self.log(f"Worker {self.agent_id} is already BUSY, cannot accept new task")
            return

        task_data = message["payload"]["task"]
        task_id = task_data.get('task_id', 'unknown')
        
        self.current_task = task_data
        self.current_task_id = task_id
        
        self.log(f"Received task {task_id} for execution")
        
        self.update_status("BUSY", task_id=task_id)
        self.report_resources(is_busy=True)

        task_thread = threading.Thread(
            target=self._execute_task_in_background,
            args=(self.current_task,),
            daemon=True
        )
        task_thread.start()

    def _execute_task_in_background(self, task):
        task_id = task.get('task_id', 'unknown')
        self.log(f"Starting execution of task {task_id} in background thread")
        
        try:
            data_complexity = len(str(task.get('data', '')))
            base_time = 2.0
            complexity_factor = min(data_complexity / 100.0, 6.0)
            processing_time = base_time + complexity_factor + random.uniform(0, 2)
            
            self.log(f"Task {task_id} estimated processing time: {processing_time:.2f} seconds")
            
            start_time = time.time()
            while time.time() - start_time < processing_time:
                if not self._is_running:
                    self.log(f"Worker shutting down, aborting task {task_id}")
                    return
                    
                time.sleep(min(1.0, processing_time - (time.time() - start_time)))
                
                if time.time() - start_time > 1.0:
                    progress = min(100, int(((time.time() - start_time) / processing_time) * 100))
                    self.log(f"Task {task_id} progress: {progress}%")

            self.log(f"Successfully completed task {task_id}")
            self.tasks_completed += 1
            self._finish_task(task_id, "completed")
            
        except Exception as e:
            self.log(f"Error executing task {task_id}: {e}", level='error')
            self._finish_task(task_id, "failed")

    def _finish_task(self, task_id, result_status):
        try:
            self.current_task = None
            self.current_task_id = None
            
            if result_status == "completed":
                self.status = "IDLE"
            else:
                self.status = "FAILED"
                threading.Timer(5.0, lambda: setattr(self, 'status', 'IDLE')).start()
            
            status_update_payload = {
                "agent_id": self.agent_id,
                "status": self.status,
                "node_id": self.node_id,
                "task_completed": task_id,
                "tasks_completed": self.tasks_completed,
                "timestamp": time.time()
            }
            self.send_message(TOPIC_AGENT_STATUS_UPDATE, payload=status_update_payload)
            
            completed_payload = {
                "task_id": task_id,
                "worker_id": self.agent_id,
                "node_id": self.node_id,
                "status": result_status,
                "completion_time": time.time()
            }
            self.send_message(TOPIC_TASK_COMPLETED, payload=completed_payload)
            
            self.report_resources(is_busy=False)
            
            self.log(f"Task {task_id} finished with status: {result_status}. Worker now {self.status}")
            
        except Exception as e:
            self.log(f"Error finishing task {task_id}: {e}", level='error')

    def handle_system_command(self, message):
        payload = message.get("payload", {})
        command = payload.get("command")
        
        if command == "WORKER_DISCOVERY_REQUEST":
            self.log(f"Responding to worker discovery request from {payload.get('requester', 'unknown')}")
            self.respond_to_discovery()
            return
        
        if message.get("recipient_id") == self.agent_id or message.get("recipient_id") == "broadcast":
            if command == CMD_SHUTDOWN_WORKER:
                self.log("Received shutdown command. Will terminate after current task.")
                self.graceful_shutdown()
            elif command == "PAUSE_WORKER":
                self.log("Received pause command - stopping task acceptance")
                self.status = "PAUSED"
                self.update_status("PAUSED")
            elif command == "RESUME_WORKER":
                self.log("Received resume command - resuming task acceptance")
                if self.status == "PAUSED":
                    self.status = "IDLE"
                    self.update_status("IDLE")

    def respond_to_discovery(self):
        discovery_response = {
            "command": "WORKER_DISCOVERY_RESPONSE",
            "agent_id": self.agent_id,
            "status": self.status,
            "node_id": self.node_id,
            "current_task_id": self.current_task_id,
            "last_heartbeat": self.last_heartbeat,
            "timestamp": time.time()
        }
        self.send_message(TOPIC_AGENT_STATUS_UPDATE, payload=discovery_response)
        self.log(f"Sent discovery response - Status: {self.status}")

    def graceful_shutdown(self):
        if self.current_task:
            self.log(f"Waiting for current task {self.current_task_id} to complete before shutdown")
        else:
            self.log("No active task, shutting down immediately")
        
        final_status = {
            "agent_id": self.agent_id,
            "status": "SHUTTING_DOWN",
            "node_id": self.node_id,
            "timestamp": time.time()
        }
        self.send_message(TOPIC_AGENT_STATUS_UPDATE, payload=final_status)
        self.stop()

    def update_status(self, status, task_id=None):
        self.status = status
        
        cpu_usage = random.uniform(2, 98)
        memory_usage = random.uniform(10, 80)

        payload = {
            "agent_id": self.agent_id,
            "status": self.status,
            "node_id": self.node_id,
            "timestamp": time.time(),
            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_usage, 2),
            "tasks_completed": self.tasks_completed
        }
        
        if task_id:
            payload["task_id"] = task_id
            payload["current_task_id"] = task_id

        self.send_message(TOPIC_AGENT_STATUS_UPDATE, payload=payload)
        self.log(f"Status updated to {status}" + (f" for task {task_id}" if task_id else ""))

    def report_resources(self, is_busy):
        try:
            if is_busy:
                cpu = random.uniform(60, 98)
                mem = random.uniform(40, 80)
            else:
                cpu = random.uniform(2, 15)
                mem = random.uniform(10, 25)
                
            payload = {
                "agent_id": self.agent_id,
                "node_id": self.node_id,
                "cpu": round(cpu, 2),
                "memory": round(mem, 2),
                "status": self.status,
                "timestamp": time.time()
            }
            self.send_message(TOPIC_RESOURCE_UPDATE, payload=payload)
            
        except Exception as e:
            self.log(f"Error reporting resources: {e}", level='error')

    def get_worker_info(self):
        return {
            "agent_id": self.agent_id,
            "node_id": self.node_id,
            "status": self.status,
            "current_task_id": self.current_task_id,
            "last_heartbeat": self.last_heartbeat
        }