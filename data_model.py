from dataclasses import dataclass
from typing import Dict, Set, List, Optional, TypeAlias

# Type aliases for domain-specific concepts
TaskId: TypeAlias = int
Duration: TypeAlias = int
StartTime: TypeAlias = int
EndTime: TypeAlias = int
ResourceId: TypeAlias = int
DependencySet: TypeAlias = Set[TaskId]

class Task:
    """Represents a task in a project."""
    id: TaskId
    name: str
    duration: Duration
    dependencies: DependencySet
    start_time: Optional[StartTime]
    resource_id: Optional[ResourceId]

    def __init__(self, id: TaskId, name: str, duration: Duration, 
                 dependencies: Optional[DependencySet] = None) -> None:
        self.id = id
        self.name = name
        self.duration = duration
        self.dependencies = dependencies or set()
        self.start_time = None
        self.resource_id = None

    def __str__(self) -> str:
        task_info = f'Task {self.id}({self.name}) duration={self.duration}'
        if self.dependencies:
            task_info += f' dependencies={self.dependencies}'
        if self.is_scheduled():
            return f'{task_info} start={self.start_time} end={self.end_time} resource={self.resource_id}'
        return task_info
    
    def __repr__(self) -> str:
        return f'Task {self.id}'

    def is_scheduled(self) -> bool:
        return self.start_time is not None and self.resource_id is not None

    @property
    def end_time(self) -> Optional[int]:
        if self.start_time is not None:
            return self.start_time + self.duration
        return None

@dataclass
class TaskList:
    """Represents a list of tasks in a project."""
    tasks: List[Task]
    task_map: Dict[TaskId, Task]

    def __init__(self, tasks: List[Task]) -> None:
        self.tasks = tasks
        self.task_map = {task.id: task for task in tasks}

    def as_list(self) -> List[Task]:
        return self.tasks

    def as_map(self) -> Dict[TaskId, Task]:
        return self.task_map
    
    def copy(self) -> 'TaskList':
        return TaskList(self.tasks.copy())