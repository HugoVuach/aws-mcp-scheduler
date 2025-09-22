import json
import time
import subprocess
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import pandas as pd

from graph import build_graph
from schedule import modified_critical_path

BUCKET_NAME = "central-supelec-data-groupe2"
NUM_CORES = 4
FILES = [
    ("task_graph_10_2_seed_42", 10),
    ("task_graph_20_5_seed_42", 20),
    ("task_graph_30_7_seed_42", 30),
    ("task_graph_40_10_seed_42", 40),
    ("task_graph_50_12_seed_42", 50),
    ("task_graph_60_15_seed_42", 60),
    ("task_graph_70_17_seed_42", 70),
    ("task_graph_80_20_seed_42", 80),
    ("task_graph_90_22_seed_42", 90),
    ("task_graph_100_3_seed_42", 100),
    ("task_graph_200_4_seed_42", 200),
    ("task_graph_300_5_seed_42", 300),
    ("task_graph_400_6_seed_42", 400),
    ("task_graph_500_6_seed_42", 500),
    ("task_graph_600_6_seed_42", 600),
    ("task_graph_700_7_seed_42", 700),
    ("task_graph_800_7_seed_42", 800),
    ("task_graph_900_7_seed_42", 900),
    ("task_graph_1000_7_seed_42", 1000),
    ("task_graph_2000_9_seed_42", 2000),
    ("task_graph_3000_11_seed_42", 3000),
    ("task_graph_4000_12_seed_42", 4000)
]
results = []

print("=== Benchmark LOCAL vs CLOUD ===\n")

for file_name, nb_nodes in FILES:
    # LOCAL BENCHMARK
    in_file_path = f"input_data/{file_name}.json"
    bind_file_path = f"bindings/{file_name}.json"

    with open(in_file_path, "r") as f:
        dag = json.load(f)
    try:
        with open(bind_file_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = None

    G = build_graph(dag["tasks"])

    # Mesure du temps d'exécution local
    start = timer()
    schedule, _, tasks_order, ub = modified_critical_path(G, NUM_CORES, data)
    end = timer()
    local_time = round(end - start, 6)
    print(f"[LOCAL] {file_name} ({nb_nodes} tâches) → {local_time} sec")

    # CLOUD BENCHMARK via Lambda
    payload = {
        "file_name": file_name,
        "num_cores": NUM_CORES
    }

    cmd = [
        "aws", "lambda", "invoke",
        "--function-name", "ordonnanceur_groupe2",
        "--payload", json.dumps(payload),
        "--cli-binary-format", "raw-in-base64-out",
        "response.json"
    ]

    subprocess.run(cmd, check=True)

    # Lecture de la réponse JSON générée par Lambda
    with open("response.json", "r") as f:
        response = json.load(f)

    # Extraction du temps Cloud retourné par Lambda
    cloud_time = response.get("execution_time", 0)
    print(f"[CLOUD] {file_name} ({nb_nodes} tâches) → {cloud_time:.3f} sec")

    # Ajout au tableau de résultats
    results.append({
        "file": file_name,
        "nodes": nb_nodes,
        "cores": NUM_CORES,
        "local_time": local_time,
        "cloud_time": cloud_time
    })

# Création du DataFrame final
df = pd.DataFrame(results)
df.to_csv("benchmark_results.csv", index=False)
print("\n✅ Résultats enregistrés dans benchmark_results.csv")

# Plot du graphique de comparaison
plt.plot(df["nodes"], df["local_time"], label="Local", marker="o")
plt.plot(df["nodes"], df["cloud_time"], label="Cloud", marker="s")
plt.xlabel("Nombre de tâches (nœuds)")
plt.ylabel("Temps d'exécution (s)")
plt.title("Comparaison efficacité : Cloud vs Local")
plt.grid()
plt.legend()
plt.savefig("benchmark_plot.png")
plt.show()
