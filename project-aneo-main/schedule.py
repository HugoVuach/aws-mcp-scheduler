import heapq
from typing import Any, Optional

import networkx as nx
from networkx.classes import DiGraph


class Task:
    def __init__(self, id: int, duration: int, start_time: int, processor: int):
        self.id = id
        self.duration = duration
        self.start_time = start_time
        self.end_time = start_time + duration
        self.processor = processor


def alap_binding(graph: DiGraph) -> dict[Any,int]:
    alap_times = {}
    topo_order = list(reversed(list(nx.lexicographical_topological_sort(graph))))

    for node in topo_order:
        duration = graph.nodes[node]["duration"]
        if graph.out_degree(node) == 0:
            alap_times[node] = -duration
        else:
            successors = list(graph.successors(node))

            if successors:
                alap_times[node] = min(alap_times[succ] - duration for succ in successors)

    return alap_times

def asap_binding(graph: DiGraph) -> dict[Any,int]:
    asap_times = {}
    topo_order = list(nx.topological_sort(graph))

    for node in topo_order:
        if graph.in_degree(node) == 0:
            asap_times[node] = 0
        else:
            predecessors = list(graph.predecessors(node))

            if predecessors:
                asap_times[node] = max(asap_times[pred] + graph.nodes[pred]["duration"] for pred in predecessors)

    return asap_times


def find_earliest_processor(processor_times: list[int]) -> int:
    return min(range(len(processor_times)), key=lambda p: processor_times[p])


# def find_same_processor(predecessors: list[int], schedule: list[Task]) -> Optional[int]:
#     for task in schedule:
#         if task.id in predecessors:
#             return task.processor
#     return None


def find_same_processor(predecessors, task_map):
    for pred in predecessors:
        if pred in task_map:
            return task_map[pred].processor
    return None


def modified_critical_path(graph: DiGraph, num_processors: int, data: Optional[dict[str,Any]]) -> tuple[list[Task],int,list[tuple[int,Any]],int]:
    tasks_order: list[tuple[int,Any]] = []
    ub: int
    if data is None:
        tasks_order = []
        latest_finish, ub = alap_binding(graph)

        # Priority is the latest finish time
        for node in graph.nodes:
            heapq.heappush(tasks_order, (latest_finish[node], node))
    else:
        tasks_order = data["order"]
        ub = data["ub"]

    saved_order = tasks_order.copy()
    schedule: list[Task] = []
    min_processor_time = 0
    assigned_tasks = set()
    processor_times = [0] * num_processors
    com_penalty = 0
    task_map = {}

    while tasks_order:
        _, node = heapq.heappop(tasks_order)
        if node in assigned_tasks:
            continue

        # Check dependency constraints
        dependencies = list(graph.predecessors(node))
        # max_dependency_end = max((task.end_time for task in schedule if task.id in dependencies), default=0)
        max_dependency_end = max((task_map[dep].end_time for dep in dependencies if dep in task_map), default=0)
        start_time = max(min_processor_time, max_dependency_end)
        preferred_processor = find_same_processor(dependencies, task_map)

        # First try to allocate the next task to the same core
        # then try to allocate an already used core
        # finally allocate a never used core if there is one
        if preferred_processor is not None and processor_times[preferred_processor] <= start_time + com_penalty:
            processor = preferred_processor
        else:
            available_processors = [p for p in range(num_processors) if processor_times[p] <= start_time]
            if available_processors:
                processor = available_processors[0]
            else:
                processor = find_earliest_processor(processor_times)

        start_time = max(start_time, processor_times[processor])
        task = Task(node, graph.nodes[node]["duration"], start_time, processor)
        schedule.append(task)
        assigned_tasks.add(node)
        processor_times[processor] = task.end_time
        min_processor_time = min(processor_times)
        task_map[node] = task

    schedule.sort(key=lambda t: t.start_time)
    makespan = max(processor_times)
    return schedule, makespan, saved_order, ub

