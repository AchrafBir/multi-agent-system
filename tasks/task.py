from dataclasses import dataclass, field
from enum import Enum, auto
from utils.helpers import generate_unique_id
import time

class TaskStatus(Enum):
    PENDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass(order=False)
class Task:
    data: dict
    priority: int = 10
    data_location: str | None = None
    task_id: str = field(default_factory=lambda: generate_unique_id("task_"))
    status: TaskStatus = TaskStatus.PENDING
    result: any = None
    creation_time: float = field(default_factory=time.time)

    def __lt__(self, other):
        if self.priority == other.priority:
            return self.creation_time < other.creation_time
        return self.priority < other.priority
