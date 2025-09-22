import heapq
from types import MappingProxyType
from typing import Any, Optional, NewType

import networkx as nx
from networkx.classes import DiGraph


class Task:
    def __init__(self, id: int, duration: int, start_time: int, processor: int):
        self.id = id
        self.duration = duration
        self.start_time = start_time
        self.end_time = start_time + duration
        self.processor = processor

TasksOrder = NewType("TasksOrder", list[tuple[int,Any]])


def alap_binding(graph: DiGraph) -> tuple[dict[int,int],int]:
    alap_times = {}
    topo_order = list(reversed(list(nx.lexicographical_topological_sort(graph))))
    ub = 0

    for node in topo_order:
        duration = graph.nodes[node]["duration"]
        ub += duration
        if graph.out_degree(node) == 0:
            alap_times[node] = -duration
        else:
            successors = list(graph.successors(node))

            if successors:
                alap_times[node] = min(alap_times[succ] - duration for succ in successors)

    return alap_times, ub


def asap_binding(graph: DiGraph) -> dict[int,int]:
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


def find_earliest_processor(num_processors: int, processor_times: dict[int,int]) -> int:
    return min(range(num_processors), key=lambda p: processor_times[p])


def find_same_processor(predecessors: list[Any], task_map: dict[Any,Task]):
    for pred in predecessors:
        if pred in task_map:
            return task_map[pred].processor
    return None


def modified_critical_path(graph: DiGraph, processors: MappingProxyType[int,int], data: Optional[dict[str,Any]]) -> tuple[list[Task],int,TasksOrder,int]:
    ub: int
    order: list
    if data is None:
        order = []
        latest_finish, ub = alap_binding(graph)

        # Priority is the latest finish time
        for node in graph.nodes:
            heapq.heappush(order, (latest_finish[node], node))
    else:
        order = data["order"]
        ub = data["ub"]

    tasks_order = TasksOrder(order)
    saved_order = TasksOrder(order.copy())
    schedule: list[Task] = []
    min_processor_time = 0
    thresholds = sorted(processors.keys())
    ti = 0
    num_processors = processors[thresholds[ti]]
    processor_times: dict[int,int] = {p: 0 for p in range(num_processors)}
    com_penalty = 1
    task_map: dict[Any,Task] = {}

    failed_processor = 0
    failure_time = 1500

    while tasks_order:
        _, node = heapq.heappop(tasks_order)

        if ti < len(thresholds) - 1:
            next_t = thresholds[ti+1]
            if min_processor_time >= next_t:
                ti += 1
                num_processors = processors[thresholds[ti]]
                old_num_processors = processors[thresholds[ti-1]]

                if old_num_processors > num_processors:
                    for p in range(num_processors, old_num_processors):
                        processor_times[p] = ub
                elif old_num_processors < num_processors:
                    for p in range(old_num_processors, num_processors):
                        processor_times[p] = min_processor_time

        # Check dependency constraints
        dependencies = list(graph.predecessors(node))
        max_dependency_end = max((task_map[dep].end_time for dep in dependencies), default=0)
        start_time = max_dependency_end
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
                processor = find_earliest_processor(num_processors, processor_times)

        start_time = max(start_time, processor_times[processor])
        if start_time >= failure_time and processor == failed_processor:
            available_processors = [p for p in range(num_processors) if p != failed_processor and processor_times[p] <= start_time]
            if available_processors:
                processor = available_processors[0]
            else:
                available_processors = [p for p in range(len(processor_times)) if p != failed_processor]
                processor = min(available_processors, key=lambda p: processor_times[p])

        if preferred_processor is not None and processor != preferred_processor:
            start_time += com_penalty  # Communication cost

        start_time = max(start_time, processor_times[processor])
        task = Task(node, graph.nodes[node]["duration"], start_time, processor)
        schedule.append(task)
        processor_times[processor] = task.end_time
        min_processor_time = min(processor_times[p] for p in range(num_processors))
        task_map[node] = task

    schedule.sort(key=lambda t: t.start_time)
    makespan = max(processor_times)
    return schedule, makespan, saved_order, ub
