from typing import List, Dict 
from data_model import Task, TaskList, TaskId, EndTime
from heuristics import SchedulingHeuristicFactory, SchedulingHeuristicInterface, SchedulingHeuristicType
from critical_path_analysis import CriticalPathAnalysis

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
        Task('T1', 3),
        Task('T2', 2),
        Task('T3', 4, {'T1', 'T2'}),
        Task('T4', 2, {'T3'}),
        Task('T5', 1, {'T3'}),
    ])
    SAMPLE_10 = TaskList([
        Task("T1", 3, set()),              # Task T1: No dependencies
        Task("T2", 2, {"T1"}),             # Task T2: Depends on Task T1
        Task("T3", 4, {"T1"}),             # Task T3: Depends on Task T1
        Task("T4", 1, {"T2", "T3"}),       # Task T4: Depends on Task T2 and Task T3
        Task("T5", 5, {"T4"}),             # Task T5: Depends on Task T4
        Task("T6", 2, {"T1"}),             # Task T6: Depends on Task T1
        Task("T7", 3, {"T6"}),             # Task T7: Depends on Task T6
        Task("T8", 4, {"T5", "T7"}),       # Task T8: Depends on Task T5 and Task T7
        Task("T9", 6, {"T2", "T8"}),       # Task T9: Depends on Task T2 and Task T8
        Task("T10", 2, {"T3", "T9"}),      # Task T10: Depends on Task T3 and Task T9
    ])
    SAMPLE_20 = TaskList([
        Task("T1", 5, set()),                           # T1: No dependencies
        Task("T2", 3, set()),                           # T2: No dependencies
        Task("T3", 4, {"T1"}),                          # T3: Depends on T1
        Task("T4", 2, {"T1", "T2"}),                    # T4: Depends on T1 and T2
        Task("T5", 6, {"T3", "T4"}),                    # T5: Depends on T3 and T4
        Task("T6", 3, {"T2"}),                          # T6: Depends on T2
        Task("T7", 2, {"T5"}),                          # T7: Depends on T5
        Task("T8", 7, {"T6"}),                          # T8: Depends on T6
        Task("T9", 5, {"T4", "T6"}),                    # T9: Depends on T4 and T6
        Task("T10", 4, {"T8"}),                         # T10: Depends on T8
        Task("T11", 2, {"T7", "T9"}),                   # T11: Depends on T7 and T9
        Task("T12", 8, {"T10", "T11"}),                 # T12: Depends on T10 and T11
        Task("T13", 1, {"T3", "T5"}),                   # T13: Depends on T3 and T5
        Task("T14", 6, {"T8", "T13"}),                  # T14: Depends on T8 and T13
        Task("T15", 3, {"T9"}),                         # T15: Depends on T9
        Task("T16", 7, {"T12", "T14"}),                 # T16: Depends on T12 and T14
        Task("T17", 4, {"T15"}),                        # T17: Depends on T15
        Task("T18", 5, {"T16", "T17"}),                 # T18: Depends on T16 and T17
        Task("T19", 2, {"T18"}),                        # T19: Depends on T18
        Task("T20", 3, {"T19"}),                        # T20: Depends on T19        
    ])

    def test(tasks: TaskList, available_resources: int, heuristic_type: SchedulingHeuristicType) -> None:
        analysis = CriticalPathAnalysis(tasks)
        scheduler = Scheduler(heuristic_type)
        scheduled_tasks = scheduler.schedule_tasks(tasks, available_resources).as_list()
        
        print("=========================================")
        print("Heuristic:", heuristic_type)
        print("Critical Path Analysis:", analysis)
        print("\nTask Schedule:")
        for task in scheduled_tasks:
            print(task)

        print("\nExecution sequence:", scheduler.debug_trace.task_sequence)
        
        print("\nResource Timeline:")
        for resource_id in range(available_resources):
            resource_tasks = [t for t in scheduled_tasks if t.resource_id == resource_id]
            resource_tasks.sort(key=lambda t: t.start_time)
            
            print(f'\nResource {resource_id}:')
            for task in resource_tasks:
                print(f'{task.id}: [{task.start_time} -> {task.end_time})')

    test(SAMPLE_TASKS, 2, SchedulingHeuristicType.NEXT_LONGEST)
    test(SAMPLE_TASKS, 2, SchedulingHeuristicType.MIN_SLACK)
    test(SAMPLE_10, 3, SchedulingHeuristicType.NEXT_LONGEST)
    test(SAMPLE_10, 3, SchedulingHeuristicType.MIN_SLACK)
    test(SAMPLE_20, 3, SchedulingHeuristicType.NEXT_LONGEST)
    test(SAMPLE_20, 3, SchedulingHeuristicType.MIN_SLACK)
    test(SAMPLE_20, 5, SchedulingHeuristicType.NEXT_LONGEST)
    test(SAMPLE_20, 5, SchedulingHeuristicType.MIN_SLACK)

if __name__ == '__main__':
    main()