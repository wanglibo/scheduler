# Scheduler Module

This module contains scripts and classes for scheduling tasks and performing critical path analysis.

## Directory Structure

- `critical_path_analysis.py`: Contains the `CriticalPathAnalysis` class for analyzing a project's critical path and slack times.
- `data_model.py`: Defines the `Task` class and related type aliases for task scheduling.
- `scheduler.py`: Defines a few scheduling algorithms.
- `main.py`: Main script for scheduling tasks and demonstrating the functionality of the scheduler module.
- `README.md`: Documentation for the scheduler module.

## Algorithm

`scheduler.py` implements list scheduling: first we print out a task list using certain prioritization heuristics and we attempt to iteratively match resources to the task list in order.

There are two possible scheduling algorithms implemented:
1. **Longest Task First**: Longest available tasks are matched to resources with earliest availability.
2. **Critical Path First** Scheduling**: Critical path / minimum slack tasks are prioritized; tasks are matched to resources that finish the latest to reduce possible fragmentations (not necessarily minimize).