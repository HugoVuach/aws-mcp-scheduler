import random
from typing import Any

import networkx as nx
from networkx.classes import DiGraph


def build_graph(tasks: list[dict[str, Any]]) -> DiGraph:
    G = nx.DiGraph()

    for task in tasks:
        G.add_node(task["id"], duration=task["duration"], memory=task["memory"])
        for dep in task["dependencies"]:
            G.add_edge(dep, task["id"])

    return G

def generate_random_dag(num_nodes: int) -> dict[str, list[Any]]:
    edges = []
    for j in range(1, num_nodes):
        if random.choice([True, False]):
            edges.append((0, j))
    for i in range(1, num_nodes - 1):
        if random.choice([True, False]):
            edges.append((i, num_nodes - 1))
    for i in range(1, num_nodes - 1):
        for j in range(i + 1, num_nodes - 1):
            if random.choice([True, False]):
                edges.append((i, j))
    return {"nodes": list(range(num_nodes)), "edges": edges}

def assign_subsets_and_features(dag: dict[str,list[Any]]) -> DiGraph:
    """Attribue un niveau `subset` et une caractéristique aléatoire (0-10) à chaque nœud."""
    G = nx.DiGraph()
    G.add_nodes_from(dag["nodes"])
    G.add_edges_from(dag["edges"])

    # Calculer les niveaux des nœuds avec un ordre topologique
    levels = {node: 0 for node in G.nodes}
    for node in nx.topological_sort(G):
        for successor in G.successors(node):
            levels[successor] = max(levels[successor], levels[node] + 1)

    # Générer une caractéristique aléatoire pour chaque nœud ( temps d'execusion par exemple)
    features = {node: random.randint(1, 10) for node in G.nodes}

    nx.set_node_attributes(G, levels, "subset")
    nx.set_node_attributes(G, features, "duration")
    return G

def find_critical_path(dag: DiGraph) -> tuple[list[int], int]:
    topological_order = list(nx.topological_sort(dag))
    longest_path_length = {node: 0 for node in dag.nodes}
    predecessor = {node: None for node in dag.nodes}

    for node in topological_order:
        for succ in dag.successors(node):
            new_length = longest_path_length[node] + dag.nodes[node]["duration"]
            if new_length > longest_path_length[succ]:
                longest_path_length[succ] = new_length
                predecessor[succ] = node

    end_node = max(longest_path_length, key=longest_path_length.get)
    critical_path = []
    node = end_node
    while node is not None:
        critical_path.append(node)
        node = predecessor[node]

    return list(reversed(critical_path)), longest_path_length[end_node]
