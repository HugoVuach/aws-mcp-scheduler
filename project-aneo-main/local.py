import json
import os
from timeit import default_timer as timer
from types import MappingProxyType

from graph import build_graph
# from schedule import modified_critical_path
# from schedule_module import modified_critical_path
from schedule_memory import modified_critical_path
from plots import plot_schedule


if __name__ == "__main__":
    start = timer()
    cores_types = 4
    mem_lim = 512
    processors = MappingProxyType({0: ({0,1,2},{3}),
                                   250: ({0,1,2,6,7,8,9},{3,4,5}),
                                   500: ({0,1,2,6,7},{3,4}),
                                   750: ({0,1},{3}),
                                   1000: ({0,1,2,6,7,8},{3,5})})
    processors = MappingProxyType({0: ({0,1,2},{3}),
                                   250: ({0,1,2,6,7,8,9,10,11,12},{3,4,5,13,14,15}),
                                   500: ({0,1,2,6,7,8,9},{3,4,15}),
                                   750: ({0,1,7,8,9},{3,14,15}),
                                   1000: ({0,1,2,6,7,8,9,10,11,12,17},{3,4,5,13,14,15,16})})
    len_cores = [(len(t1), len(t2)) for (t1,t2) in processors.values()]
    cores_types = max(len_cores)
    desc = "1000_7_seed_42"
    desc = "100000_17_seed_42"
    file_name = f"task_graph_{desc}"
    in_file_name = f"input_data/{file_name}.json"
    bind_file_name = f"bindings/{file_name}.json"
    out_file_name = f"output_data/schedule_{desc}_c_{cores_types}.json"
    # in_file_name = "input_data/graph.json"
    # bind_file_name = "bindings/graph.json"
    # out_file_name = "output_data/schedule.json"

    start = timer()
    with open(in_file_name, "r") as infile:
        graph = json.load(infile)

    data = None
    if os.path.exists(bind_file_name):
        with open(bind_file_name, "r") as infile:
            data = json.load(infile)
            tasks_order = data["order"]
            ub = data["ub"]

    G = build_graph(graph["tasks"])

    # schedule, makespan = modified_critical_path(G, num_cores, bind_file)
    schedule, makespan, tasks_order, ub = modified_critical_path(G, processors, mem_lim, data)

    with open(bind_file_name, "w") as outfile:
        json.dump({"order": tasks_order, "ub": ub}, outfile)

    result = {f"core_{core}": [] for core in range(sum(cores_types))}
    # for id, task in schedule.items():
    #     result[f"core_{task[2]}"].append({"task": id, "start_time": task[0]})

    for task in schedule:
        result[f"core_{task.processor}"].append({"task": task.id, "start_time": task.start_time, "duration": task.duration})

    with open(out_file_name, "w") as outfile:
        json.dump(result, outfile)

    end = timer()
    print(f"Required time: {end-start}s")

    print(G.number_of_edges())

    # plot_schedule(result)
