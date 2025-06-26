import threading
import logging
import queue
from communication.protocol import create_message, TOPIC_TASK_REQUEST
from config.settings import SCHEDULER_ID, LOAD_BALANCER_ID
from tasks.task import Task
from data.processor import process_data_from_file
import time

class Scheduler(threading.Thread):
    def __init__(self, task_queue, message_bus, data_file_path):
        super().__init__(name=SCHEDULER_ID)
        self.task_queue = task_queue
        self.message_bus = message_bus
        self.data_file_path = data_file_path
        self._is_running = True
        self.daemon = True

    def run(self):
        logging.info("Scheduler is running, watching the central task queue.")
        self.load_initial_tasks()
        while self._is_running:
            try:
                task = self.task_queue.get_task(block=True)
                if task is None:
                    continue
                task_payload = {
                    "task_id": task.task_id,
                    "data": task.data,
                    "priority": task.priority,
                    "location": task.data_location
                }
                logging.info(f"Scheduler picked up task {task.task_id} from queue.")
                msg = create_message(
                    topic=TOPIC_TASK_REQUEST,
                    sender_id=SCHEDULER_ID,
                    payload={"task": task_payload}
                )
                self.message_bus.send_message(msg)
                time.sleep(0.1)
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Scheduler encountered an error: {e}", exc_info=True)
                threading.Event().wait(1)
        logging.info("Scheduler is shutting down.")

    def load_initial_tasks(self):
        logging.info(f"Performing initial task load from: {self.data_file_path}")
        try:
            task_data_list = process_data_from_file(self.data_file_path)
            if task_data_list:
                for task_data in task_data_list:
                    initial_task = Task(
                        task_id=task_data.get('task_id', None),
                        data=task_data.get('data', {}),
                        priority=task_data.get('priority', 5),
                        data_location=task_data.get('location', 'unspecified')
                    )
                    self.task_queue.add_task(initial_task)
                logging.info(f"Loaded {len(task_data_list)} initial tasks into the queue.")
        except Exception as e:
            logging.error(f"Failed to load initial tasks: {e}", exc_info=True)

    def stop(self):
        self._is_running = False
        self.task_queue.add_task(None)