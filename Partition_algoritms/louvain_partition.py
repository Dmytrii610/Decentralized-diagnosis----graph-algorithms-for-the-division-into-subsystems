import json
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from networkx.algorithms.community import kernighan_lin
import community as community_louvain
from sklearn.cluster import KMeans
from scipy.sparse.linalg import eigsh
from collections import defaultdict
import pymetis
from JSON_Converter.json_from_graph import save_metrics_to_json
import numpy as np


def ensure_label_dict(labels, nodes):
    if isinstance(labels, dict):
        label_dict = dict(labels)
        comms = defaultdict(set)
        for n, lab in label_dict.items():
            comms[lab].add(n)
        communities = list(comms.values())
        return label_dict, communities

    if isinstance(labels, (list, tuple)) and all(isinstance(b, (set, list)) for b in labels):
        communities = [set(b) for b in labels]
        label_dict = {}
        for idx, block in enumerate(communities):
            for n in block:
                label_dict[n] = idx
        return label_dict, communities

    label_dict = {}
    for n, lab in zip(nodes, labels):
        label_dict[n] = int(lab)
    comms = defaultdict(set)
    for n, lab in label_dict.items():
        comms[lab].add(n)
    communities = list(comms.values())
    return label_dict, communities


def calculate_sum_of_cross_weights(G, label_dict):
    cross_weight = 0
    for u, v in G.edges():
        if label_dict.get(u) != label_dict.get(v):
            weight = G[u][v].get('weight')
            cross_weight += weight
    return cross_weight


def print_graph_info(G, labels, nodes_order=None):
    if nodes_order is None:
        nodes_order = list(G.nodes())
    label_dict, communities = ensure_label_dict(labels, nodes_order)
    cross_weight = calculate_sum_of_cross_weights(G, label_dict)
    modularity = nx.algorithms.community.quality.modularity(G, communities)
    coverage, performance = nx.algorithms.community.partition_quality(G, communities)
    print(f"Suma wag krawędzi między różnymi klastrami: {cross_weight}")
    print(f"Wartość modularności: {modularity}")
    print(f"Coverage: {coverage}")
    print(f"Performance: {performance}")


def optimize_louvain(G, k):
    gamma_values = np.linspace(0.05, 10, 1000)
    intervals = []

    prev_gamma = None
    prev_count = None
    for gamma in gamma_values:
        part = community_louvain.best_partition(G, resolution=gamma, random_state=42)
        _, comms = ensure_label_dict(part, list(G.nodes()))
        c = len(comms)

        if c == k:
            intervals.append((gamma, gamma))

        if prev_count is not None:
            if (prev_count - k) * (c - k) < 0:
                intervals.append((prev_gamma, gamma))

        prev_gamma = gamma
        prev_count = c

    if not intervals:
        print("Nie znaleziono żadnego gamma z liczbą klastrów =", k)
        return None, None, None

    g_low, g_high = intervals[0]

    if g_low == g_high:
        g_low -= 0.1
        g_high += 0.1

    for _ in range(700):
        mid = (g_low + g_high) / 2
        part = community_louvain.best_partition(G, resolution=mid, random_state=42)
        _, comms = ensure_label_dict(part, list(G.nodes()))
        c = len(comms)

        if c == k:
            return comms, part, mid

        if c > k:
            g_high = mid
        else:
            g_low = mid

    return comms, part, mid

def louvain_clustering(G, k, position, nodes_color, network_name):
    _, part, mid = optimize_louvain(G, k)
    partition = community_louvain.best_partition(G, random_state=42, resolution=mid)
    label_dict, communities = ensure_label_dict(partition, list(G.nodes()))
    print("Początkowa liczba klastrów:", len(communities))

    cross_weight = calculate_sum_of_cross_weights(G, label_dict)
    modularity = nx.algorithms.community.quality.modularity(G, communities)
    coverage, performance = nx.algorithms.community.partition_quality(G, communities)

    metrics = {
        "cross_weight": cross_weight,
        "modularity": modularity,
        "coverage": coverage,
        "performance": performance,
        "clusters": len(communities)
    }

    save_metrics_to_json(network_name, "Louvain", metrics)

    colors = [nodes_color[label_dict[n] % len(nodes_color)] for n in G.nodes()]

    print_graph_info(G, partition, nodes_order=list(G.nodes()))

    nx.draw(G, position, node_color=colors, with_labels=True, cmap=plt.cm.Set2, node_size=500)
    plt.savefig("Louvain_clustering.png", dpi=300, bbox_inches="tight")
    plt.clf()
