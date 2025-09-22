import json
import random
import os
from types import MappingProxyType
from timeit import default_timer as timer


from graph import build_graph
from schedule_memory import modified_critical_path
from plots import plot_schedule

BUCKET_NAME = "central-supelec-data-groupe2"


def generate_fixed_mapping(n=10, num_changes=10, time_range=(0, 40000), num_processors=20):
    """
    Génère un mapping où les n premiers processeurs sont de type 1 et les autres de type 2,
    puis fait varier leur nombre tout en conservant leur type initial.
    """
    assert 0 <= n <= num_processors, "n doit être compris entre 0 et le nombre total de processeurs"

    # Définition initiale des types
    initial_type1 = list(range(n))  # Les n premiers processeurs sont de type 1
    initial_type2 = list(range(n, num_processors))  # Les autres sont de type 2

    # Génération des instants de changement
    times = sorted(random.sample(range(time_range[0] + 1, time_range[1]), num_changes - 1))
    times.insert(0, 0)  # Ajouter t=0 au début

    mapping = {}

    for t in times:
        # Variation du nombre de processeurs actifs dans chaque type
        num_active_type1 = random.randint(1, len(initial_type1))  # Nombre actif de type 1
        num_active_type2 = random.randint(1, len(initial_type2))  # Nombre actif de type 2

        processors_type1 = set(random.sample(initial_type1, num_active_type1))
        processors_type2 = set(random.sample(initial_type2, num_active_type2))

        mapping[t] = (processors_type1, processors_type2)

    return MappingProxyType(mapping)


name = "task_graph_100000_19_seed_42"
memory_limits = [256, 512, 1024]
mapping_list = [
    # 256
    {0: ({3}, {17, 11, 13}), 2728: ({1, 2, 4, 5, 6, 7}, {18, 10, 19}), 6465: ({0, 1, 2, 4, 5, 6, 7, 8, 9}, {17}), 9438: ({0, 1, 3, 4, 5, 7, 9}, {16, 11, 12, 15}), 15619: ({0, 1, 2, 3, 4, 5, 7, 8, 9}, {10, 19, 14}), 17695: ({8}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 22455: ({0, 2, 3, 4, 5, 6, 7, 8, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 25471: ({0, 1, 2, 3, 5, 6, 7, 9}, {10, 13, 14, 15}), 28348: ({0, 4, 6, 7}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 39163: ({8, 1, 2}, {18})},
    {0: ({0, 4, 6, 8, 9}, {10, 11, 12, 13, 14, 16, 17, 18, 19}), 193: ({0, 1, 2, 4, 5, 6, 8, 9}, {10, 18, 13}), 6745: ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {10, 11, 14, 17, 18, 19}), 15252: ({0, 1, 2, 5, 6, 7, 8, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 15266: ({0, 7}, {11, 13, 17, 18, 19}), 20397: ({1, 2, 3, 4, 6}, {11, 17, 19, 15}), 21422: ({0, 1, 2, 3, 5, 6, 7, 8, 9}, {11, 12, 13, 14, 15, 18, 19}), 26047: ({5}, {12}), 33210: ({0, 4, 6, 7, 8, 9}, {10, 12}), 34058: ({8, 9, 2}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19})},
    {0: ({1, 2, 4, 6, 7, 8, 9}, {10, 13}), 1886: ({0, 2, 3, 4, 6, 8, 9}, {16}), 8190: ({1, 2, 4, 5, 7, 8, 9}, {10, 11, 13, 14, 15, 17, 19}), 11634: ({4, 5, 6, 8, 9}, {16, 18, 19, 14}), 15747: ({3}, {12, 14, 17, 18, 19}), 20315: ({1, 6}, {17}), 24796: ({0, 1, 3, 4, 7, 8}, {17, 11, 13}), 31656: ({0, 1, 4, 5, 6, 7, 8, 9}, {10, 11, 13, 14, 15, 16}), 35915: ({3, 4, 5, 6, 8}, {12, 14, 16, 18, 19}), 39144: ({0, 1, 2, 3, 4, 6, 7, 8, 9}, {17, 11})},

    # 512
    {0: ({0, 2, 3, 5, 8}, {14}), 1033: ({1, 2, 5, 7, 8, 9}, {11, 12, 15, 16, 19}), 5923: ({0, 1, 2, 4, 6, 7}, {16}), 17930: ({0, 1, 3, 4, 5, 6, 7, 8, 9}, {19}), 18806: ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {10, 12}), 23778: ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {19}), 26180: ({0, 2, 3, 4, 5, 6}, {10, 11, 13, 14, 17}), 29917: ({0, 2, 3, 5, 6, 7, 9}, {17, 19, 15}), 30688: ({0, 1, 3, 4, 5, 6, 7, 9}, {19, 11, 13}), 32563: ({2, 3, 4, 5, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19})},
    {0: ({3, 4, 6, 7, 8, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 1230: ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {11, 12, 14, 16, 18}), 2848: ({8, 9, 2, 6}, {16, 17, 10}), 3630: ({9, 6, 7}, {17, 14}), 4186: ({0, 2}, {10, 12, 13, 14, 15, 16, 18}), 6036: ({0, 1, 2, 4, 5, 6, 9}, {10, 11, 13, 14, 15, 16, 17, 18, 19}), 6633: ({0, 1, 6, 8, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 9445: ({0, 3, 4, 5, 6, 7}, {10, 11, 12, 14, 15, 16, 17, 18, 19}), 28207: ({0, 1, 2, 3, 4, 5, 6, 7, 8}, {11, 12, 13, 14, 15, 16, 17, 18, 19}), 36564: ({6}, {11, 14, 17, 18, 19})},
    {0: ({0, 2, 4}, {10, 11, 12, 14, 17}), 5032: ({0, 2, 3, 6, 9}, {10, 11, 12, 13, 14, 15, 16, 18, 19}), 10256: ({0, 1, 2, 3, 4, 5, 8, 9}, {18}), 18174: ({1, 6, 7}, {10, 11, 12, 14, 15, 16, 17, 19}), 23668: ({0, 2, 4, 6, 7, 8, 9}, {11, 12, 14, 15, 16, 17, 18}), 24966: ({2, 5}, {10, 11, 12, 13, 14, 16}), 25665: ({0, 1, 3, 4, 5, 6, 7, 8, 9}, {10, 12, 13, 14, 15, 17, 18, 19}), 27839: ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {18}), 33233: ({0, 1, 2, 4, 5, 6, 8, 9}, {10, 14, 15, 16, 17, 18, 19}), 35908: ({1, 3, 5, 6}, {10, 11, 12, 13, 14, 15, 16, 17, 18})},

    # 1024
    {0: ({9, 4, 6, 7}, {10, 11, 13, 14, 15, 16, 17, 18, 19}), 3505: ({0, 2, 3, 4, 5, 6, 7, 8, 9}, {10, 12, 13, 14, 16, 17, 18}), 8535: ({3, 4, 5, 6, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 10314: ({8, 9, 4}, {17}), 11193: ({0}, {10, 11, 12, 13, 14, 15, 17, 18, 19}), 12375: ({0, 1, 2, 3, 4, 5, 8, 9}, {10, 11, 12, 15, 17, 18}), 20571: ({0, 1, 2, 4, 5, 7, 8}, {10, 12, 13, 14, 15, 16, 17, 18, 19}), 21341: ({1, 2, 3, 4, 6, 7}, {17, 13, 14, 15}), 25415: ({0, 1, 2, 4, 5, 6, 7, 8, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 26733: ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {17, 10, 11, 15})},
    {0: ({0, 3, 4, 6}, {16, 19, 14}), 10138: ({3, 4, 5, 8, 9}, {10, 18}), 12834: ({1, 2, 4, 5}, {16}), 13793: ({0, 2, 3, 5, 6, 7}, {10, 12, 13, 14, 15, 16, 17, 19}), 16122: ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9}, {11, 12, 13, 14, 17, 18}), 22283: ({1, 2, 3, 5, 7, 8, 9}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 25947: ({3, 6}, {16, 19, 15}), 26080: ({8, 9, 4, 6}, {15}), 33463: ({8}, {10, 11, 12, 13, 15, 16, 18, 19}), 37373: ({5, 7}, {18})},
    {0: ({2, 3, 4, 6, 7, 8, 9}, {17}), 2349: ({5}, {10, 12, 15, 16, 17, 18}), 7117: ({2, 5}, {10, 12, 14}), 10092: ({4, 5, 6}, {16, 18, 14}), 11480: ({0, 1, 2, 6, 8}, {13, 14, 16, 17, 18, 19}), 18921: ({0, 3, 4, 5, 6, 7, 8, 9}, {16}), 20059: ({0, 2, 3, 4, 5, 6, 7, 8}, {10, 11, 13, 16, 19}), 25815: ({1}, {16, 18, 10, 12}), 26096: ({1, 6}, {10, 11, 12, 13, 14, 15, 16, 17, 18, 19}), 32489: ({0, 1, 2, 3, 4, 5, 6, 7, 8}, {19})},
]

for i in range(3):
    for j, mem_lim in enumerate(memory_limits):
        print(f"Mapping: {i}, Limit: {mem_lim}")
        with open(f"output_data/{name}_m{i}_l{mem_lim}.json", "r") as infile:
            schedule = json.load(infile)

        num_cores = len(schedule)
        makespan = 0
        for core, tasks in schedule.items():
            for task in tasks:
                makespan = max(makespan, task["duration"]+task["start_time"])
        print(f"makespan: {makespan}")

        # plot_schedule(schedule)

# for i in range(3):
#     for j, mem_lim in enumerate(memory_limits):
#         print(f"Mapping: {i}, Limit: {mem_lim}")
#         map = MappingProxyType(mapping_list[i+j])
#         len_cores = [(len(t1), len(t2)) for (t1,t2) in map.values()]
#         num_cores = max(len_cores)
#         in_file_name = f"input_data/{name}.json"
#         bind_file_name = f"bindings/{name}.json"
#         out_file_name = f"output_data/{name}_m{i}_l{mem_lim}.json"

#         with open(in_file_name, "r") as infile:
#             graph = json.load(infile)

#         data = None
#         if os.path.exists(bind_file_name):
#             with open(bind_file_name, "r") as infile:
#                 data = json.load(infile)
#                 tasks_order = data["order"]
#                 ub = data["ub"]

#         G = build_graph(graph["tasks"])

#         schedule, _, tasks_order, ub = modified_critical_path(G, map, mem_lim, data)
#         result = {f"core_{core}": [] for core in range(20)}
#         for task in schedule:
#             result[f"core_{task.processor}"].append({"task": task.id, "start_time": task.start_time, "duration": task.duration})

#         with open(bind_file_name, "w") as outfile:
#             json.dump({"order": tasks_order, "ub": ub}, outfile)

#         with open(out_file_name, "w") as outfile:
#             json.dump(result, outfile)
