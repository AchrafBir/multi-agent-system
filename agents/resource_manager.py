import time
from agents.base_agent import BaseAgent
from communication.protocol import (
    TOPIC_RESOURCE_UPDATE, TOPIC_SYSTEM_COMMAND, CMD_PAUSE_WORKER,
    CMD_RESUME_WORKER, CMD_SCALE_OUT, CMD_SCALE_IN
)
from config.settings import (
    RESOURCE_MANAGER_ID, RESOURCE_MANAGER_CHECK_INTERVAL, HIGH_CPU_THRESHOLD,
    LOW_CPU_THRESHOLD, SCALE_OUT_QUEUE_THRESHOLD, WORKER_COOLDOWN_PERIOD,
    SCALE_IN_LOAD_THRESHOLD, NUM_WORKERS
)

class ResourceManagerAgent(BaseAgent):
    def __init__(self, message_bus, task_queue):
        super().__init__(RESOURCE_MANAGER_ID, message_bus)
        self.task_queue = task_queue
        self.resources = {}
        self.last_check_time = time.time()

    def register_subscriptions(self):
        self.message_bus.subscribe(TOPIC_RESOURCE_UPDATE, self.handle_resource_update)
    
    def setup(self):
        pass

    def handle_resource_update(self, message):
        agent_id = message["payload"]["agent_id"]
        if agent_id not in self.resources:
            self.resources[agent_id] = {"status": "active", "resume_time": 0}
        
        self.resources[agent_id].update({
            "cpu": message["payload"]["cpu"],
            "memory": message["payload"]["memory"]
        })
        self.log(f"Resource update for {agent_id}: CPU={message['payload']['cpu']}%, Memory={message['payload']['memory']}%")

    def on_message_loop(self):
        current_time = time.time()
        if current_time - self.last_check_time > RESOURCE_MANAGER_CHECK_INTERVAL:
            self.evaluate_system_state()
            self.last_check_time = current_time

    def evaluate_system_state(self):
        self.log("Evaluating system resource state...")
        self.check_for_overloaded_workers()
        self.check_for_system_wide_load()

    def check_for_overloaded_workers(self):
        for agent_id, data in list(self.resources.items()):
            cpu = data.get("cpu", 0)
            current_status = data.get("status", "active")
            
            if cpu > HIGH_CPU_THRESHOLD and current_status == "active":
                self.log(f"ACTION: PAUSE {agent_id} due to high CPU usage.")
                self.send_command(CMD_PAUSE_WORKER, {"target_worker": agent_id})
                self.resources[agent_id]["status"] = "paused"
                self.resources[agent_id]["pause_time"] = time.time() 

            elif cpu < LOW_CPU_THRESHOLD and current_status == "paused":
                pause_time = data.get("pause_time", 0)
                if time.time() - pause_time > WORKER_COOLDOWN_PERIOD:
                    self.log(f"ACTION: RESUME {agent_id} due to low CPU and cooldown completion.")
                    self.send_command(CMD_RESUME_WORKER, {"target_worker": agent_id})
                    self.resources[agent_id]["status"] = "active"
                else:
                    self.log(f"INFO: {agent_id} CPU is normal, but still in cooldown. Waiting.")

    def check_for_system_wide_load(self):
        q_size = self.task_queue.qsize()

        if q_size > SCALE_OUT_QUEUE_THRESHOLD:
            self.log(f"High system load detected (queue size: {q_size}). Requesting scale out.")
            self.send_command(CMD_SCALE_OUT)
            return

        num_workers = len(self.resources)
        if num_workers > NUM_WORKERS:
            idle_workers = [
                agent_id for agent_id, data in self.resources.items()
                if data.get("cpu", 100) < LOW_CPU_THRESHOLD and data.get("status") == "active"
            ]
            idle_ratio = len(idle_workers) / num_workers
            if idle_ratio >= SCALE_IN_LOAD_THRESHOLD and q_size == 0:
                worker_to_remove = idle_workers[0]
                self.log(f"ACTION: SCALE IN. System load is low. Requesting shutdown of {worker_to_remove}.")
                self.send_command(CMD_SCALE_IN, {"target_worker": worker_to_remove})
                del self.resources[worker_to_remove]

    def send_command(self, command, payload_extra={}):
        payload = {"command": command}
        payload.update(payload_extra)
        self.send_message(TOPIC_SYSTEM_COMMAND, payload=payload)