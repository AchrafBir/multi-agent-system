import time

class PerformanceTracker:
    def __init__(self):
        self.start_time = time.time()
        self.tasks_completed = 0

    def task_completed(self):
        self.tasks_completed += 1

    def get_throughput(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time == 0:
            return 0
        return self.tasks_completed / elapsed_time