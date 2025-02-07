from dataclasses import dataclass
from typing import List, Dict
from data_model import Task, TaskList, TaskId, StartTime, EndTime

@dataclass
class TaskTiming:
    """
    Stores timing analysis results for a single task.
    
    Attributes:
        earliest_start: Earliest possible start time for the task
        earliest_finish: Earliest possible finish time for the task
        latest_start: Latest allowed start time without delaying project
        latest_finish: Latest allowed finish time without delaying project
    """
    earliest_start: StartTime
    earliest_finish: EndTime
    latest_start: StartTime
    latest_finish: EndTime

    @property
    def slack(self) -> int:
        """Calculate total slack (float) time for this task."""
        return self.latest_start - self.earliest_start
    
    def __str__(self) -> str:
        return f'ES={self.earliest_start} EF={self.earliest_finish} LS={self.latest_start} LF={self.latest_finish} Slack={self.slack}'


class CriticalPathAnalysis:
    """
    Analyzes a project's critical path and slack times.
    """
    # Input tasks
    task_list: List[Task]
    task_map: Dict[TaskId, Task]
    # Min finish time for the project assuming unlimited resource
    min_finish_time: EndTime = None
    # Topological sorted task IDs
    topological_sorted_tasks : List[TaskId] 
    # Timing analysis results for each task
    timing : Dict[TaskId, TaskTiming]

    def __str__(self) -> str:
        lines = []
        lines.append(f'Min finish time: {self.min_finish_time}')
        for task, timing in self.timing.items():
            lines.append(f'Task {task}: {timing}')
        return '\n'.join(lines)

    def __init__(self, tasks: TaskList) -> None:
        self.task_list = tasks.as_list()
        self.task_map = tasks.as_map()
        self.timing = {task.id: TaskTiming(0, 0, 0, 0) for task in self.task_list}
        self.forward_backward_passes()

    @staticmethod
    def topological_sort(incoming_edge_graph: Dict[TaskId, List[TaskId]]) -> List[TaskId]:
        """
        Sorts tasks by dependencies, modelled as a graph with a list of incoming edges.
        """
        # Deep copy the graph to avoid modifying the input
        graph = {task_id: set(deps) for task_id, deps in incoming_edge_graph.items()}
        sorted = []
        while graph:
            # TODO: cache this result to avoid recomputing
            available_tasks = [task_id for task_id, deps in graph.items() if not deps]
            if not available_tasks:
                raise ValueError('Dependency cycle detected in task graph')
            
            next_task_id = next(iter(available_tasks))            
            sorted.append(next_task_id)
            del graph[next_task_id]
            
            for remaining_deps in graph.values():
                remaining_deps.discard(next_task_id)
                
        return sorted

    def forward_backward_passes(self):
        # Forward pass to compute earliest start and end times
        dependency_graph = {task.id: task.dependencies.copy() for task in self.task_list}
        sorted_task_ids = self.topological_sort(dependency_graph)
        for task_id in sorted_task_ids:
            earliest_start = max(
                # Find the latest finish time of dependencies
                (self.timing[dep_id].earliest_finish for dep_id in dependency_graph[task_id]),
                default=0
            )
            earliest_finish = earliest_start + self.task_map[task_id].duration
            self.timing[task_id].earliest_start = earliest_start
            self.timing[task_id].earliest_finish = earliest_finish

        # Find the minimum finish time for the project
        self.min_finish_time = max(t.earliest_finish for t in self.timing.values())

        # Backward pass to compute latest start and end times
        reversed_dependency_graph = {task.id: set() for task in self.task_list}
        for task in self.task_list:
            for parent in task.dependencies:
                reversed_dependency_graph[parent].add(task.id)
        sorted_task_ids = self.topological_sort(reversed_dependency_graph)
        for task_id in sorted_task_ids:
            latest_finish = min(
                # Find the earliest start time of dependents
                (self.timing[dep_id].latest_start for dep_id in reversed_dependency_graph[task_id]),
                default=self.min_finish_time
            )
            latest_start = latest_finish - self.task_map[task_id].duration
            self.timing[task_id].latest_start = latest_start
            self.timing[task_id].latest_finish = latest_finish

if __name__ == '__main__':
    SAMPLE_TASKS = TaskList([
        Task('T1', 3),
        Task('T2', 2),
        Task('T3', 4, {'T1', 'T2'}),
        Task('T4', 2, {'T3'}),
        Task('T5', 1, {'T3'}),
    ])
    analysis = CriticalPathAnalysis(SAMPLE_TASKS)
    print(analysis)
