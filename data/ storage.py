import threading

class ResultStorage:
    def __init__(self):
        self._results = {}
        self._lock = threading.Lock()

    def save_result(self, task_id, result):
        with self._lock:
            self._results[task_id] = result

    def get_result(self, task_id):
        with self._lock:
            return self._results.get(task_id)

    def get_all_results(self):
        with self._lock:
            return self._results.copy()