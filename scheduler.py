from abc import abstractmethod
from typing import Dict, List
from data_model import TaskList, TaskId, EndTime
from critical_path_analysis import CriticalPathAnalysis

class SchedulerInterface():
    @abstractmethod
    def schedule(self, tasks: TaskList, resource_count: int) -> TaskList:
        pass

class LongestFirstScheduler(SchedulerInterface):
    def __str__(self) -> str:
        return 'Longest First Scheduler'

    def schedule(self, tasks: TaskList, resource_count: int) -> TaskList:
        dependency_graph = {task.id: task.dependencies.copy() for task in tasks.as_list()}
        task_sequence = []

        while dependency_graph:
            available_tasks = [task_id for task_id, deps in dependency_graph.items() if not deps]
            if not available_tasks:
                raise ValueError('Dependency cycle detected in task graph')

            next_task_id = max(available_tasks, key=lambda tid: tasks.as_map()[tid].duration)
            task_sequence.append(next_task_id)
            del dependency_graph[next_task_id]

            # Remove completed task from remaining dependencies
            for remaining_deps in dependency_graph.values():
                remaining_deps.discard(next_task_id)

        # Iterative schedule the task sequence to the available resources
        completion_times: Dict[TaskId, EndTime] = {}
        resource_next_available: List[EndTime] = [0] * resource_count

        for task_id in task_sequence:
            task = tasks.as_map()[task_id]
            
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
            
            # Schedule task: can only start after dependencies are completed and resource is available
            task.start_time = max(deps_completion_time, resource_available_time)
            task.resource_id = resource_id
            completion_times[task_id] = task.end_time
            resource_next_available[resource_id] = task.end_time

        return tasks
    
    def execution_sequence(self) -> List[TaskId]:
        return self.execution_sequence

class CriticalPathScheduler(SchedulerInterface):
    critical_path_analysis: CriticalPathAnalysis

    def __str__(self) -> str:
        return 'Critical Path Scheduler'

    def schedule(self, tasks: TaskList, resource_count: int) -> TaskList:
        self.critical_path_analysis = CriticalPathAnalysis(tasks)

        def min_slack_and_longest_duration(task_id: TaskId):
            return (self.critical_path_analysis.timing[task_id].slack, 
                    -tasks.as_map()[task_id].duration)

        dependency_graph = {task.id: task.dependencies.copy() for task in tasks.as_list()}
        task_sequence = []

        while dependency_graph:
            available_tasks = [task_id for task_id, deps in dependency_graph.items() if not deps]
            if not available_tasks:
                raise ValueError('Dependency cycle detected in task graph')

            next_task_id = min(available_tasks, key=min_slack_and_longest_duration)
            task_sequence.append(next_task_id)
            del dependency_graph[next_task_id]

            # Remove completed task from remaining dependencies
            for remaining_deps in dependency_graph.values():
                remaining_deps.discard(next_task_id)

        # Map task sequence to resources
        completion_times: Dict[TaskId, EndTime] = {}
        resource_next_available: List[EndTime] = [0] * resource_count
        for task_id in task_sequence:
            task = tasks.as_map()[task_id]
            deps_completion_time = max(
                (completion_times.get(dep_id, 0) for dep_id in task.dependencies),
                default=0
            )
            resource_candidate, resource_available_time = min(
                enumerate(resource_next_available), key=lambda x: x[1])
            if (resource_available_time <= deps_completion_time):
                # This means there are spare resources, so we can start the task immediately
                task.start_time = deps_completion_time
                # Use the resource with min distance to deps_completion_time to minimize fragmentation
                # Not guaranteed to be optimal.
                resource_candidates = {i: resource_next_available[i] for i in range(resource_count)
                                       if resource_next_available[i] <= deps_completion_time}
                task.resource_id = min(
                    enumerate(resource_candidates), key=lambda x: deps_completion_time - x[1])[0]
            else:
                # We have to delay until resource_next_available to start.
                task.start_time = resource_available_time
                # Use the resource with earliest available time
                task.resource_id = resource_candidate
            completion_times[task.id] = task.end_time
            resource_next_available[task.resource_id] = task.end_time

        return tasks