import threading
import time
import logging
from communication.protocol import create_message, TOPIC_AGENT_HEARTBEAT, TOPIC_SYSTEM_LOG
from config.settings import AGENT_HEARTBEAT_INTERVAL

class BaseAgent(threading.Thread):
    def __init__(self, agent_id, message_bus):
        super().__init__(name=agent_id)
        self.agent_id = agent_id
        self.message_bus = message_bus
        self._is_running = True
        self.daemon = True

    def register_subscriptions(self):
        pass

    def setup(self):
        pass

    def run(self):
        self.log(f"Agent started.")
        self.setup()
        last_heartbeat_time = time.time()
        
        while self._is_running:
            self.on_message_loop()
            current_time = time.time()
            if current_time - last_heartbeat_time >= AGENT_HEARTBEAT_INTERVAL:
                self.send_heartbeat()
                last_heartbeat_time = current_time
            time.sleep(0.1)
        
        self.log("Agent shutting down.")

    def on_message_loop(self):
        pass

    def send_message(self, topic, payload=None, recipient_id=None):
        msg = create_message(topic, self.agent_id, payload, recipient_id)
        self.message_bus.send_message(msg)

    def send_heartbeat(self):
        self.send_message(TOPIC_AGENT_HEARTBEAT)

    def log(self, message, level=logging.INFO):
        log_message = f"[{self.agent_id}] {message}"
        logging.log(level, log_message)
        self.send_message(TOPIC_SYSTEM_LOG, payload={"log": log_message})

    def stop(self):
        self._is_running = False