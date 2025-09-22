import networkx as nx
import matplotlib.pyplot as plt
import random
import json
import argparse

def generate_task_graph(num_tasks, max_dependencies=None, random_seed=None):
    """ Génère un graphe de tâches avec des dépendances aléatoires """

    # Initialiser la graine aléatoire si fournie
    if random_seed is None:
        random_seed = random.randint(0, 99999)  # Générer une graine aléatoire
    random.seed(random_seed)

    G = nx.DiGraph()  # Graphe orienté
    tasks = [f"task{i}" for i in range(1, num_tasks + 1)]  # Création des tâches
    G.add_nodes_from(tasks)  # Ajout des tâches comme nœuds

    task_data = {}  # Dictionnaire pour stocker les infos des tâches

    # Déterminer max_dependencies aléatoirement si non fourni
    if max_dependencies is None:
        max_dependencies = random.randint(1, num_tasks - 1)  # Plus de flexibilité

    for task in tasks:
        # Génération aléatoire des attributs
        duration = random.randint(5, 30)  # Durée entre 5 et 30 unités
        memory = random.choice([256, 512, 1024, 2048])  # Mémoire en Mo

        # Déterminer les dépendances
        if task != "task1":  # La première tâche n'a pas de dépendances
            num_deps = random.randint(1, min(max_dependencies, len(tasks) - 1))  
            possible_parents = [t for t in tasks if t < task]  # Seulement les tâches précédentes
            selected_parents = random.sample(possible_parents, min(len(possible_parents), num_deps))  # Choix aléatoire
        else:
            selected_parents = []

        # Ajouter les infos au dictionnaire
        task_data[task] = {
            "id": task,
            "duration": duration,
            "memory": memory,
            "dependencies": selected_parents
        }

        # Ajouter les dépendances dans le graphe
        for dep in selected_parents:
            G.add_edge(dep, task)

    return G, task_data, random_seed, max_dependencies

def save_graph_to_json(task_data, num_tasks, max_dependencies, random_seed):
    """ Sauvegarde le graphe sous format JSON """
    graph_json = {
        "graph_id": f"task_graph_ntask_{num_tasks}_max_dep_{max_dependencies}_seed_{random_seed}",
        "random_seed": random_seed,
        "max_dependencies": max_dependencies,
        "tasks": list(task_data.values())  # Convertir le dictionnaire en liste
    }

    filename = f"input_data/task_graph_{num_tasks}_{max_dependencies}_seed_{random_seed}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(graph_json, f, indent=4)  # Enregistrement avec indentation

    print(f"\n✅ Graphe sauvegardé sous {filename}")
    print(f"🔹 Pour reproduire ce graphe, utilisez la seed : {random_seed}")
    print(f"🔹 Nombre maximal de dépendances utilisé : {max_dependencies}")

def main():
    """ Fonction principale du script """
    parser = argparse.ArgumentParser(description="Génère un graphe de tâches avec dépendances aléatoires et l'enregistre en JSON.")

    # Argument obligatoire : nombre de tâches
    parser.add_argument("--num_tasks", type=int, required=True, help="Nombre de tâches à générer.")

    # Argument optionnel : seed aléatoire
    parser.add_argument("--seed", type=int, required=False, help="Graine aléatoire pour reproduire le graphe (optionnel).")

    # Argument optionnel : nombre maximal de dépendances
    parser.add_argument("--max_dependencies", type=int, required=False, help="Nombre maximal de dépendances par tâche (optionnel, aléatoire si absent).")

    args = parser.parse_args()

    # Générer le graphe avec ou sans seed et max_dependencies
    G, task_data, random_seed, max_dependencies = generate_task_graph(
        num_tasks=args.num_tasks, 
        max_dependencies=args.max_dependencies, 
        random_seed=args.seed
    )

    assert nx.is_directed_acyclic_graph(G), "Le graphe généré contient un cycle !"

    # Sauvegarde en JSON
    save_graph_to_json(task_data, args.num_tasks, max_dependencies, random_seed)

    # Dessiner le graphe
    # plt.figure(figsize=(8, 6))
    # pos = nx.shell_layout(G)  # Disposition en couches
    # nx.draw(G, pos, with_labels=True, node_color="lightblue", edge_color="black",
    #         node_size=2000, font_size=12, font_weight="bold", arrows=True)

    # Affichage du graphe
    # plt.title(f"Graphe des dépendances des tâches (seed={random_seed}, max_dep={max_dependencies})")
    # plt.show()

def loop_main():
    for nt in range(10, 100, 10):
        mp = max(2, nt // 4)
        G, task_data, _, _ = generate_task_graph(
                num_tasks=nt,
                max_dependencies=mp,
                random_seed=42
        )

        assert nx.is_directed_acyclic_graph(G), "Le graphe généré contient un cycle !"

        # Sauvegarde en JSON
        save_graph_to_json(task_data, nt, mp, 42)

    for nt in range(100, 1_000, 100):
        mp = max(2, int(nt ** 0.3))
        G, task_data, _, _ = generate_task_graph(
                num_tasks=nt,
                max_dependencies=mp,
                random_seed=42
        )

        assert nx.is_directed_acyclic_graph(G), "Le graphe généré contient un cycle !"

        # Sauvegarde en JSON
        save_graph_to_json(task_data, nt, mp, 42)

    for nt in range(1_000, 10_000, 1_000):
        mp = max(2, int(nt ** 0.3))
        G, task_data, _, _ = generate_task_graph(
                num_tasks=nt,
                max_dependencies=mp,
                random_seed=42
        )

        assert nx.is_directed_acyclic_graph(G), "Le graphe généré contient un cycle !"

        # Sauvegarde en JSON
        save_graph_to_json(task_data, nt, mp, 42)

    for nt in range(10_000, 100_000, 10_000):
        mp = max(2, int(nt ** 0.25))
        G, task_data, _, _ = generate_task_graph(
                num_tasks=nt,
                max_dependencies=mp,
                random_seed=42
        )

        assert nx.is_directed_acyclic_graph(G), "Le graphe généré contient un cycle !"

        # Sauvegarde en JSON
        save_graph_to_json(task_data, nt, mp, 42)

    for nt in range(100_000, 1_000_000, 100_000):
        mp = max(2, int(nt ** 0.25))
        G, task_data, _, _ = generate_task_graph(
                num_tasks=nt,
                max_dependencies=mp,
                random_seed=42
        )

        assert nx.is_directed_acyclic_graph(G), "Le graphe généré contient un cycle !"

        # Sauvegarde en JSON
        save_graph_to_json(task_data, nt, mp, 42)

if __name__ == "__main__":
    loop_main()
