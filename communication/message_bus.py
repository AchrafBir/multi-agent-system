import queue
import threading
import logging
from collections import defaultdict
from config.settings import MESSAGE_BUS_PULL_TIMEOUT

class MessageBus(threading.Thread):
    def __init__(self):
        super().__init__(name="MessageBus")
        self.message_queue = queue.Queue()
        self.subscribers = defaultdict(list)
        self.lock = threading.Lock()
        self._is_running = True
        self.daemon = True

    def subscribe(self, topic, callback):
        with self.lock:
            self.subscribers[topic].append(callback)
        logging.info(f"New subscription to topic '{topic}'")

    def send_message(self, message):
        self.message_queue.put(message)

    def run(self):
        logging.info("Message Bus is running.")
        while self._is_running:
            try:
                message = self.message_queue.get(timeout=MESSAGE_BUS_PULL_TIMEOUT)
                topic = message.get("topic")
                recipient = message.get("recipient_id")
                
                with self.lock:
                    subscribers = self.subscribers.get(topic, [])
                
                for callback in subscribers:
                    try:
                        if recipient:
                            if hasattr(callback.__self__, 'agent_id') and callback.__self__.agent_id == recipient:
                                callback(message)
                        else:
                            callback(message)
                    except Exception as e:
                        logging.error(f"Error processing message in callback for topic {topic}: {e}")
            except queue.Empty:
                continue
        logging.info("Message Bus is shutting down.")

    def stop(self):
        self._is_running = False