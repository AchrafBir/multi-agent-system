import time
from agents.base_agent import BaseAgent
from communication.protocol import TOPIC_AGENT_HEARTBEAT
from config.settings import MONITOR_AGENT_ID, MONITOR_CHECK_INTERVAL, AGENT_HEARTBEAT_INTERVAL

class MonitorAgent(BaseAgent):
    def __init__(self, message_bus):
        super().__init__(MONITOR_AGENT_ID, message_bus)
        self.agent_heartbeats = {}
        self.last_check_time = time.time()

    def register_subscriptions(self):
        self.message_bus.subscribe(TOPIC_AGENT_HEARTBEAT, self.handle_heartbeat)

    def setup(self):
        pass

    def handle_heartbeat(self, message):
        agent_id = message["sender_id"]
        self.agent_heartbeats[agent_id] = time.time()
        self.log(f"Received heartbeat from {agent_id}")

    def on_message_loop(self):
        current_time = time.time()
        if current_time - self.last_check_time > MONITOR_CHECK_INTERVAL:
            self.check_agent_health()
            self.last_check_time = current_time

    def check_agent_health(self):
        self.log("Performing agent health check...")
        current_time = time.time()
        unhealthy_threshold = AGENT_HEARTBEAT_INTERVAL * 2.5
        
        for agent_id, last_beat in list(self.agent_heartbeats.items()):
            if current_time - last_beat > unhealthy_threshold:
                self.log(f"Agent {agent_id} is UNHEALTHY! No heartbeat received recently.")