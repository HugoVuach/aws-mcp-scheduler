import json
from typing import Any, Optional

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

def plot_lengths(x: list, makespan: list, cp_len: list):
    plt.style.use("seaborn-v0_8-darkgrid")
    _, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x, makespan, marker='o', linestyle='-', color='royalblue', markersize=8, linewidth=2, label="Makespan")
    ax.plot(x, cp_len, marker='o', linestyle='-', color='darkorange', markersize=8, linewidth=2, label="CP length")
    ax.grid(True, which="both", linestyle="--", linewidth=0.7, alpha=0.6)

    ax.set_xlabel("Max dependencies", fontsize=12)
    ax.set_ylabel("Average Makespan", fontsize=12)
    ax.set_title("Scheduling performance", fontsize=14, fontweight='bold')
    ax.legend()

    plt.tight_layout()
    plt.savefig("figures/lengths.png")
    plt.show()

def plot_benchmark(x: list[Any], fy: list[Any], sy: Optional[list[Any]] = None, log = False):
    plt.style.use("seaborn-v0_8-darkgrid")
    _, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x, fy, marker='.', linestyle='-', color='royalblue', markersize=8, linewidth=2, label="Premier tour")
    if sy is not None:
        ax.plot(x, sy, marker='.', linestyle='-', color='darkorange', markersize=8, linewidth=2, label="Seconde tour")

    ax.grid(True, which="both", linestyle="--", linewidth=0.7, alpha=0.6)

    ax.set_xlabel("#Nœuds", fontsize=12)
    ax.set_ylabel("Temps d'éxecution (s)", fontsize=12)
    ax.set_title("Scheduling performance", fontsize=14, fontweight='bold')
    ax.legend()
    name = "benchmark"
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
        name += "log"

    plt.tight_layout()
    plt.savefig(f"figures/{name}.png")
    plt.show()

def plot_schedule(schedule: dict[str, list[dict[str, Any]]]):
    num_cores = len(schedule)
    makespan = 0
    _, ax = plt.subplots(figsize=(10, 6))
    for core, tasks in schedule.items():
        for task in tasks:
            makespan = max(makespan, task["duration"]+task["start_time"])
            ax.barh(core, task["duration"], left=task["start_time"], height=0.8, label=task["task"])

    ax.set_xlabel("Time")
    ax.set_ylabel("Processors")
    # ax.set_xticks(range(0, makespan, 250))
    ax.set_yticks(range(num_cores))
    ax.set_yticklabels([f"P{i}" for i in range(num_cores)])
    ax.set_title(f"Task Scheduling Visualization\nMakespan: {makespan}")
    plt.tight_layout()
    plt.savefig(f"figures/schedule_{makespan}.png")
    plt.show()

# def plot_dag(G: DiGraph) -> None:
#     pos = nx.multipartite_layout(G, subset_key="subset")  # Utiliser les niveaux pour le layout
#     labels = {node: f"{node}\n{G.nodes[node]['duration']}" for node in G.nodes}  # Labels avec caractéristique

#     nx.draw(G, pos, with_labels=True, labels=labels, node_size=700, node_color="skyblue", arrowsize=20)
#     plt.savefig("figures/dag.png")
#     plt.show()


if __name__ == "__main__":
    desc = "1000_7_seed_42_c_4"
    file_name = "schedule.json"
    file_name = f"schedule_{desc}.json"
    with open(f"output_data/{file_name}", "r") as infile:
        schedule = json.load(infile)

    plot_schedule(schedule)
