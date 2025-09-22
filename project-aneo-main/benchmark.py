import json
import os
from timeit import default_timer as timer
from types import MappingProxyType

import matplotlib.pyplot as plt

from graph import build_graph, find_critical_path
# from schedule import modified_critical_path
# from schedule_module import modified_critical_path
from schedule_memory import modified_critical_path
from plots import plot_schedule, plot_benchmark, plot_lengths


def compute_data(num_nodes: int, max_dep: int, plot = False, save = True) -> tuple[float,int,int]:
    start = timer()
    cores_types = 4
    mem_lim = 512
    processors = MappingProxyType({0: ({0,1,2},{3}),
                                   250: ({0,1,2,6,7,8,9},{3,4,5}),
                                   500: ({0,1,2,6,7},{3,4}),
                                   750: ({0,1},{3}),
                                   1000: ({0,1,2,6,7,8},{3,5})})
    len_cores = [(len(t1), len(t2)) for (t1,t2) in processors.values()]
    cores_types = max(len_cores)
    desc = f"{num_nodes}_{max_dep}_seed_42"
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

    schedule, makespan, tasks_order, ub = modified_critical_path(G, processors, mem_lim, data)
    result = {f"core_{core}": [] for core in range(sum(cores_types))}
    for task in schedule:
        result[f"core_{task.processor}"].append({"task": task.id, "start_time": task.start_time, "duration": task.duration})

    _, longest_path_length = find_critical_path(G)

    if save:
        with open(bind_file_name, "w") as outfile:
            json.dump({"order": tasks_order, "ub": ub}, outfile)

        with open(out_file_name, "w") as outfile:
            json.dump(result, outfile)

    end = timer()

    if plot:
        plot_schedule(result)

    return end - start,makespan,longest_path_length


if __name__ == "__main__":
    f_data: dict[int, tuple[float,int,int]] = {}
    for nt in range(10, 100, 10):
        mp = max(2, nt // 4)
        f_data[nt] = compute_data(nt, mp)
    print("first batch done")

    for nt in range(100, 1_000, 100):
        mp = max(2, int(nt ** 0.3))
        f_data[nt] = compute_data(nt, mp)
    print("second batch done")

    for nt in range(1_000, 10_000, 1_000):
        mp = max(2, int(nt ** 0.3))
        f_data[nt] = compute_data(nt, mp)
    print("third batch done")

    for nt in range(10_000, 100_000, 10_000):
        mp = max(2, int(nt ** 0.25))
        f_data[nt] = compute_data(nt, mp)
    print("fourth batch done")

    nt = 100_000
    mp = 19
    f_data[nt] = compute_data(nt, mp)
    print("fifth batch done")

    s_data: dict[int, tuple[float,int,int]] = {}
    for nt in range(10, 100, 10):
        mp = max(2, nt // 4)
        s_data[nt] = compute_data(nt, mp)
    print("sixth batch done")

    for nt in range(100, 1_000, 100):
        mp = max(2, int(nt ** 0.3))
        s_data[nt] = compute_data(nt, mp)
    print("seventh batch done")

    for nt in range(1_000, 10_000, 1_000):
        mp = max(2, int(nt ** 0.3))
        s_data[nt] = compute_data(nt, mp)
    print("eighth batch done")

    for nt in range(10_000, 100_000, 10_000):
        mp = max(2, int(nt ** 0.25))
        s_data[nt] = compute_data(nt, mp)
    print("ninth batch done")

    nt = 100_000
    mp = 19
    s_data[nt] = compute_data(nt, mp)
    print("tenth batch done")

    x = list(f_data.keys())
    fy = [v[0] for v in f_data.values()]
    sy = [v[0] for v in s_data.values()]

    plot_benchmark(x, fy, sy, False)

    # nt = 100_000
    # makespans = []
    # cp_lens = []
    # mps = list(range(10,20))
    # for mp in mps:
    #     _, makespan, cp_len = compute_data(nt, mp)
    #     makespans.append(makespan)
    #     cp_lens.append(cp_len)

    # plot_lengths(mps, makespans, cp_lens)

    first_logs = {
        10: 29.561549507999985,
        11: 28.583560345000024,
        12: 30.545821405999988,
        13: 31.324000620999982,
        14: 32.34262136999996,
        15: 33.205190835999986,
        16: 34.17761035299998,
        17: 35.70702751199997,
        18: 36.68249704699997,
        19: 37.740260473000035
    }

    second_logs = {
        10: 20.72716203599998,
        11: 24.09906744400007,
        12: 25.234214428,
        13: 25.667446510000048,
        14: 25.962816042000043,
        15: 26.893290242000035,
        16: 28.176110609000034,
        17: 29.070217559999946,
        18: 30.315600130999997,
        19: 31.219162770000025
    }

    x1 = list(first_logs.keys())
    y1 = list(first_logs.values())

    x2 = list(second_logs.keys())
    y2 = list(second_logs.values())

    plt.style.use("seaborn-v0_8-darkgrid")
    _, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x1, y1, marker='o', linestyle='-', color='royalblue', markersize=8, linewidth=2, label="Premier tour")
    ax.plot(x2, y2, marker='o', linestyle='-', color='darkorange', markersize=8, linewidth=2, label="Seconde tour")
    ax.grid(True, which="both", linestyle="--", linewidth=0.7, alpha=0.6)

    ax.set_xlabel("Max dépendences", fontsize=12)
    ax.set_ylabel("Temps d'exécution (s)", fontsize=12)
    ax.set_title("Scheduling performance (100k nœuds, max 17 cœurs, mémoire limite 512 Mo)", fontsize=14, fontweight='bold')
    ax.legend()

    plt.tight_layout()
    plt.savefig("figures/time_cloud.png")
    plt.show()
