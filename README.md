# Scheduler Module

> TODO: update this summary after feature changes

This module contains scripts and classes for scheduling tasks and performing critical path analysis.

## Directory Structure

- `critical_path_analysis.py`: Contains the `CriticalPathAnalysis` class for analyzing a project's critical path and slack times.
- `data_model.py`: Defines the `Task` class and related type aliases for task scheduling.
- `main.py`: Main script for scheduling tasks and demonstrating the functionality of the scheduler module.
- `README.md`: Documentation for the scheduler module.

## Algorithms

The following algorithms are implemented

### Longest Job First
### Prioritize critical path with ... matching  


B. Multiprocessor Scheduling with Dependencies
	•	Tasks must be assigned to m processors with limited capacity.
	•	Algorithm: List Scheduling with Earliest Finish Time (EFT).
	1.	Perform a topological sort to ensure dependencies are respected.
	2.	Assign each task to the processor that allows the earliest completion.

C. Resource-Constrained Project Scheduling Problem (RCPSP)
	•	Algorithm: Serial Schedule Generation.
	1.	Use priority rules (e.g., EST or MST) to order tasks.
	2.	Schedule tasks sequentially, respecting dependencies and resource constraints.
	3.	Update available resources and adjust start times dynamically.