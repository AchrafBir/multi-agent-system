import queue

class TaskQueue:
    def __init__(self):
        self._queue = queue.PriorityQueue()

    def add_task(self, task):
        if task is None:
            self._queue.put((999, None)) 
            return
        self._queue.put((task.priority, task))

    def get_task(self, block=True, timeout=None):
        try:
            priority, task = self._queue.get(block=block, timeout=timeout)
            return task
        except queue.Empty:
            return None

    def __len__(self):
        return self._queue.qsize()

    def qsize(self):
        return self._queue.qsize()
