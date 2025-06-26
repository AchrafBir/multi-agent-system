import threading
from agents.base_agent import BaseAgent
from agents.worker_agent import WorkerAgent
from communication.protocol import (
    TOPIC_SYSTEM_COMMAND, CMD_SCALE_OUT, CMD_SCALE_IN, CMD_SHUTDOWN_WORKER
)
from config.settings import CLUSTER_MANAGER_ID
from utils.helpers import generate_unique_id

class ClusterManagerAgent(BaseAgent):
    def __init__(self, message_bus, initial_agents_list: list, agents_lock: threading.Lock):
        super().__init__(CLUSTER_MANAGER_ID, message_bus)
        self.agents = initial_agents_list
        self.agents_lock = agents_lock

    def register_subscriptions(self):
        self.message_bus.subscribe(TOPIC_SYSTEM_COMMAND, self.handle_system_command)

    def setup(self):
        pass

    def handle_system_command(self, message):
        command = message["payload"].get("command")
        if command == CMD_SCALE_OUT:
            self.scale_out()
        elif command == CMD_SCALE_IN:
            self.scale_in(message["payload"].get("target_worker"))

    def scale_out(self):
        self.log("Scale-out command received. Provisioning new worker agent.")
        new_worker_id = generate_unique_id("worker_dynamic_")
        new_node_id = f"dynamic-node-{generate_unique_id()}"
        new_worker = WorkerAgent(new_worker_id, self.message_bus, new_node_id)
        new_worker.register_subscriptions()
        
        with self.agents_lock:
            self.agents.append(new_worker)
        
        new_worker.start()
        self.log(f"New worker {new_worker_id} on node {new_node_id} started and is now processing tasks.")

    def scale_in(self, worker_id_to_remove):
        if not worker_id_to_remove:
            return
        
        self.log(f"Scale-in command received for worker {worker_id_to_remove}.")
        self.send_message(
            TOPIC_SYSTEM_COMMAND,
            payload={"command": CMD_SHUTDOWN_WORKER},
            recipient_id=worker_id_to_remove
        )
        
        with self.agents_lock:
            agent_to_remove = next((agent for agent in self.agents if agent.agent_id == worker_id_to_remove), None)
            if agent_to_remove:
                self.agents.remove(agent_to_remove)
                self.log(f"Removed worker {worker_id_to_remove} from system list.")