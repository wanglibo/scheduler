from typing import Dict, Set, List, Optional, TypeAlias

# Type aliases for domain-specific concepts
TaskId: TypeAlias = int
Duration: TypeAlias = int
StartTime: TypeAlias = int
EndTime: TypeAlias = int
ResourceId: TypeAlias = int
DependencySet: TypeAlias = Set[TaskId]

class Task:
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

    def is_scheduled(self) -> bool:
        return self.start_time is not None and self.resource_id is not None

    @property
    def end_time(self) -> Optional[int]:
        if self.start_time is not None:
            return self.start_time + self.duration
        return None

def topological_sort(tasks: List[Task]) -> List[TaskId]:
    """
    Sorts tasks by dependencies, prioritizing longer duration tasks.
    Returns a list of task IDs in execution order.
    """
    dependency_graph = {task.id: task.dependencies.copy() for task in tasks}
    execution_order = []

    while dependency_graph:
        available_tasks = [task_id for task_id, deps in dependency_graph.items() if not deps]
        if not available_tasks:
            raise ValueError('Dependency cycle detected in task graph')
        
        # Select task with longest duration among available tasks. Other heuristics are possible.
        next_task_id = max(
            available_tasks,
            key=lambda task_id: next(task for task in tasks if task.id == task_id).duration
        )
        
        execution_order.append(next_task_id)
        del dependency_graph[next_task_id]
        
        # Remove completed task from remaining dependencies
        for remaining_deps in dependency_graph.values():
            remaining_deps.discard(next_task_id)
            
    return execution_order

def schedule_tasks(tasks: List[Task], resource_count: int) -> List[Task]:
    """
    Schedules tasks across available resources, respecting dependencies.
    Returns list of tasks with assigned start times and resources.
    """
    execution_sequence = topological_sort(tasks)
    task_map = {task.id: task for task in tasks}
    
    # Track completion times for dependency checking
    completion_times: Dict[TaskId, EndTime] = {}
    resource_next_available: List[EndTime] = [0] * resource_count

    for task_id in execution_sequence:
        task = task_map[task_id]
        
        # Find earliest possible start time based on dependencies
        deps_completion_time = max(
            (completion_times.get(dep_id, 0) for dep_id in task.dependencies),
            default=0
        )
        
        # Find earliest available resource
        resource_id, resource_available_time = min(
            enumerate(resource_next_available),
            key=lambda x: x[1]
        )
        
        # Schedule task
        task.start_time = max(deps_completion_time, resource_available_time)
        task.resource_id = resource_id
        completion_times[task_id] = task.end_time
        resource_next_available[resource_id] = task.end_time

    return list(task_map.values())

# Test data
SAMPLE_TASKS = [
    Task(1, 'T1', 3),
    Task(2, 'T2', 2),
    Task(3, 'T3', 4, {1, 2}),
    Task(4, 'T4', 2, {3}),
    Task(5, 'T5', 1, {3}),
]
AVAILABLE_RESOURCES = 2

def main():
    scheduled_tasks = schedule_tasks(SAMPLE_TASKS, AVAILABLE_RESOURCES)
    
    print("Task Schedule:")
    for task in scheduled_tasks:
        print(task)
    
    print("\nResource Timeline:")
    for resource_id in range(AVAILABLE_RESOURCES):
        resource_tasks = [t for t in scheduled_tasks if t.resource_id == resource_id]
        resource_tasks.sort(key=lambda t: t.start_time)
        
        print(f'\nResource {resource_id}:')
        for task in resource_tasks:
            print(f'{task.name}: [{task.start_time} -> {task.end_time}]')

if __name__ == '__main__':
    main()