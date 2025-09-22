import heapq
from types import MappingProxyType
from typing import Any, Optional, TypeAlias

import networkx as nx
from networkx.classes import DiGraph


class Task:
    def __init__(self, id: int, duration: int, start_time: int, processor: int):
        self.id = id
        self.duration = duration
        self.start_time = start_time
        self.end_time = start_time + duration
        self.processor = processor


# TasksOrder = NewType("TasksOrder", list[tuple[int,Any]])
TasksOrder: TypeAlias = list[tuple[int, Any]]
ProcessorsTypes: TypeAlias = tuple[set[int],set[int]]
ProcessorsAvailability: TypeAlias = MappingProxyType[int, ProcessorsTypes]
ScheduleBinding: TypeAlias = tuple[dict[int,int],int]


def alap_binding(graph: DiGraph) -> ScheduleBinding:
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


def find_earliest_processor(processors_types: ProcessorsTypes, processor_times: dict[int,int],
                            task_memory: int, mem_lim: int, start_time: int, banned_processor: Optional[int] = None) -> int:
    type1_processors, type2_processors = processors_types

    if task_memory > mem_lim:
        available_processors = type2_processors
    else:
        available_processors = type1_processors | type2_processors

    if banned_processor is not None:
        available_processors = [p for p in available_processors if p != banned_processor]

    used_processors = [p for p in available_processors if processor_times[p] <= start_time]
    if used_processors:
        return used_processors[0]

    return min(available_processors, key=lambda p: processor_times[p])


def find_same_processor(predecessors: list[Any], task_map: dict[Any,Task]) -> Optional[int]:
    for pred in predecessors:
        if pred in task_map:
            return task_map[pred].processor
    return None


def modified_critical_path(graph: DiGraph, processors: ProcessorsAvailability, mem_lim: int,
                           data: Optional[dict[str,Any]] = None) -> tuple[list[Task],int,TasksOrder,int]:
    ub: int
    order: TasksOrder
    if data is None:
        order = []
        latest_finish, ub = alap_binding(graph)

        # Priority is the latest finish time
        for node in graph.nodes:
            heapq.heappush(order, (latest_finish[node], node))
    else:
        order = data["order"]
        ub = data["ub"]

    tasks_order = order
    saved_order = order.copy()
    schedule: list[Task] = []
    min_processor_time = 0
    thresholds = sorted(processors.keys())
    ti = 0
    processors_types = processors[thresholds[ti]]
    all_processors = processors_types[0] | processors_types[1]
    processor_times: dict[int,int] = {p: 0 for p in all_processors}
    com_penalty = 1
    task_map: dict[Any,Task] = {}

    # failed_processor = 0
    # failure_time = 1500

    while tasks_order:
        _, node = heapq.heappop(tasks_order)

        # update availability of processors
        if ti < len(thresholds) - 1:
            next_t = thresholds[ti+1]
            if min_processor_time >= next_t:
                ti += 1
                processors_types = processors[thresholds[ti]]
                all_processors = processors_types[0] | processors_types[1]
                old_processors_types = processors[thresholds[ti-1]]

                processor_times.update({p: ub for p in old_processors_types[0] - processors_types[0]})
                processor_times.update({p: ub for p in old_processors_types[1] - processors_types[1]})
                processor_times.update({p: min_processor_time for p in processors_types[0] - old_processors_types[0]})
                processor_times.update({p: min_processor_time for p in processors_types[1] - old_processors_types[1]})

        # Check dependency constraints
        dependencies = list(graph.predecessors(node))
        max_dependency_end = max((task_map[dep].end_time for dep in dependencies), default=0)
        start_time = max_dependency_end
        preferred_processor = find_same_processor(dependencies, task_map)

        # First try to allocate the next task to the same core
        # then try to allocate an already used core
        # finally allocate a never used core if there is one
        task_mem = graph.nodes[node]["memory"]
        if preferred_processor is not None and (processor_times[preferred_processor] <= start_time + com_penalty and task_mem > mem_lim and preferred_processor in processors_types[0]):
            processor = preferred_processor
        else:
            processor = find_earliest_processor(processors_types, processor_times, task_mem, mem_lim, start_time)

        # start_time = max(start_time, processor_times[processor])
        # if start_time >= failure_time and processor == failed_processor:
        #     processor = find_earliest_processor(processors_types, processor_times, task_mem, mem_lim, start_time, failed_processor)

        if preferred_processor is not None and processor != preferred_processor:
            start_time += com_penalty  # Communication cost

        start_time = max(start_time, processor_times[processor])
        task = Task(node, graph.nodes[node]["duration"], start_time, processor)
        schedule.append(task)
        processor_times[processor] = task.end_time
        min_processor_time = min(processor_times[p] for p in all_processors)
        task_map[node] = task

    schedule.sort(key=lambda t: t.start_time)
    makespan = max(processor_times[p] for p in processor_times if processor_times[p] < ub)
    return schedule, makespan, saved_order, ub
