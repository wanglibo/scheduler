from enum import Enum
from typing import List
from data_model import Task, TaskList, TaskId
from critical_path_analysis import CriticalPathAnalysis
from abc import ABC, abstractmethod

class SchedulingHeuristicType(Enum):
    MIN_SLACK = 'min_slack'
    NEXT_LONGEST = 'next_longest'

class SchedulingHeuristicInterface:
    @abstractmethod
    def next_task(self, tasks: List[TaskId]) -> TaskId:
        """
        Returns the next task to be scheduled according to the given strategy. 
        Assuming the list of tasks are not empty.
        """
        pass

class SchedulingHeuristicFactory:
    tasks: TaskList
    def __init__(self, tasks: TaskList) -> None:
        self.tasks = tasks

    def create(self, heuristic_type: SchedulingHeuristicType) -> SchedulingHeuristicInterface:
        if heuristic_type == SchedulingHeuristicType.MIN_SLACK:
            critical_path_analysis = CriticalPathAnalysis(self.tasks)
            return PrioritizeMinSlack(critical_path_analysis)
        elif heuristic_type == SchedulingHeuristicType.NEXT_LONGEST:
            return PrioritizeNextLongest(self.tasks)
        raise ValueError(f'Unknown heuristic: {heuristic_type}')

class PrioritizeMinSlack(SchedulingHeuristicInterface):
    """
    Prioritizes tasks based on the critical path of the project by 
    picking the task with the least slack time.
    """
    def __init__(self, critical_path_analysis : CriticalPathAnalysis) -> None:
        self.critical_path_analysis = critical_path_analysis

    def next_task(self, task_ids: List[TaskId]) -> TaskId:
        task_timings = {tid : self.critical_path_analysis.timing[tid] for tid in task_ids}
        return min(task_timings, key=lambda tid: task_timings[tid].slack)

class PrioritizeNextLongest(SchedulingHeuristicInterface):
    """
    Prioritizes next available task with the longest duration.
    """
    def __init__(self, tasks : TaskList) -> None:
        self.task_map = tasks.as_map()

    def next_task(self, task_ids: List[TaskId]) -> TaskId:
        return max(task_ids, key=lambda tid: self.task_map[tid].duration)

if __name__ == '__main__':
    SAMPLE_TASKS = TaskList([
        Task('T1', 3),
        Task('T2', 2),
        Task('T3', 4, {'T1', 'T2'}),
        Task('T4', 2, {'T3'}),
        Task('T5', 1, {'T3'}),
    ])

    factory = SchedulingHeuristicFactory(SAMPLE_TASKS)
    min_slack = factory.create(SchedulingHeuristicType.MIN_SLACK)
    next_task_id = min_slack.next_task(['T1', 'T2'])
    print(next_task_id == 'T1')

    next_longest = factory.create(SchedulingHeuristicType.NEXT_LONGEST)
    next_task_id = next_longest.next_task(['T2', 'T3'])
    print(next_task_id == 'T3')
