from typing import List, Dict 
from data_model import Task, TaskList, TaskId, EndTime
from heuristics import SchedulingHeuristicFactory, SchedulingHeuristicInterface, SchedulingHeuristicType

class DebugTrace:
    task_sequence: List[TaskId]

    def add_task_sequence(self, task_sequence: List[TaskId]) -> None:
        self.task_sequence = task_sequence

class Scheduler:
    heuristic_type: SchedulingHeuristicType
    debug_trace: DebugTrace

    def __init__(self, heuristic_type: SchedulingHeuristicType) -> None:
        self.heuristic_type = heuristic_type
        self.debug_trace = DebugTrace()

    def sequence_tasks(self, tasks: TaskList,
                       heuristic: SchedulingHeuristicInterface) -> List[TaskId]:
        """
        Returns a sequence of task IDs that can be executed in order without violating 
        dependency constraints. 
        """
        dependency_graph = {task.id: task.dependencies.copy() for task in tasks.as_list()}
        task_sequence = []

        while dependency_graph:
            available_tasks = [task_id for task_id, deps in dependency_graph.items() if not deps]
            if not available_tasks:
                raise ValueError('Dependency cycle detected in task graph')

            next_task_id = heuristic.next_task(available_tasks)
            task_sequence.append(next_task_id)
            del dependency_graph[next_task_id]

            # Remove completed task from remaining dependencies
            for remaining_deps in dependency_graph.values():
                remaining_deps.discard(next_task_id)

        return task_sequence


    def schedule_tasks(self, tasks: TaskList, resource_count: int) -> TaskList:
        """
        Schedules tasks across available resources, respecting dependencies.
        Returns list of tasks with assigned start times and resources.
        """
        task_sequence = self.sequence_tasks(
            tasks, SchedulingHeuristicFactory(tasks).create(self.heuristic_type))
        self.debug_trace.add_task_sequence(task_sequence)

        # Iterative schedule the execution sequence to the available resources
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

def main():
    SAMPLE_TASKS = TaskList([
        Task(1, 'T1', 3),
        Task(2, 'T2', 2),
        Task(3, 'T3', 4, {1, 2}),
        Task(4, 'T4', 2, {3}),
        Task(5, 'T5', 1, {3}),
    ])
    AVAILABLE_RESOURCES = 2    

    def test(tasks: TaskList, available_resources: int, heuristic_type: SchedulingHeuristicType) -> None:
        scheduler = Scheduler(heuristic_type)
        scheduled_tasks = scheduler.schedule_tasks(tasks, available_resources).as_list()
        
        print("=========================================")
        print("Heuristic:", heuristic_type)
        print("\nTask Schedule:")
        for task in scheduled_tasks:
            print(task)

        print("\nExecution sequence:", scheduler.debug_trace.task_sequence)
        
        print("\nResource Timeline:")
        for resource_id in range(AVAILABLE_RESOURCES):
            resource_tasks = [t for t in scheduled_tasks if t.resource_id == resource_id]
            resource_tasks.sort(key=lambda t: t.start_time)
            
            print(f'\nResource {resource_id}:')
            for task in resource_tasks:
                print(f'{task.name}: [{task.start_time} -> {task.end_time}]')

    test(SAMPLE_TASKS, AVAILABLE_RESOURCES, SchedulingHeuristicType.NEXT_LONGEST)
    test(SAMPLE_TASKS, AVAILABLE_RESOURCES, SchedulingHeuristicType.MIN_SLACK)

if __name__ == '__main__':
    main()