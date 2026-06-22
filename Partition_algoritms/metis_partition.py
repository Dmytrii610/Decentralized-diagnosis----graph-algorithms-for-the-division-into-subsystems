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
def ensure_label_dict(labels, nodes):
    # dict: node->label
    if isinstance(labels, dict):
        label_dict = dict(labels)
        comms = defaultdict(set)
        for n, lab in label_dict.items():
            comms[lab].add(n)
        communities = list(comms.values())
        return label_dict, communities

    # lista/tuple
    if isinstance(labels, (list, tuple)) and all(isinstance(b, (set, list)) for b in labels):
        communities = [set(b) for b in labels]
        label_dict = {}
        for idx, block in enumerate(communities):
            for n in block:
                label_dict[n] = idx
        return label_dict, communities

    # array etykiet
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

def metis_clustering(G, position, n_clusters=2, nodes_color=None,network_name=None):
    node_mapping = {node: idx for idx, node in enumerate(G.nodes())}
    adjacency = [[node_mapping[nbr] for nbr in G.neighbors(node)] for node in G.nodes()]

    _, membership = pymetis.part_graph(n_clusters, adjacency=adjacency)
    label_dict = {node: membership[idx] for node, idx in node_mapping.items()}
    label_dict, communities = ensure_label_dict([label_dict[n] for n in G.nodes()], list(G.nodes()))
    cross_weight = calculate_sum_of_cross_weights(G, label_dict)
    modularity = nx.algorithms.community.quality.modularity(G, communities)
    coverage, performance = nx.algorithms.community.partition_quality(G, communities)
    num_clusters = len(communities)
    metrics = {
	"cross_weight": cross_weight,
	"modularity": modularity,
	"coverage": coverage,
	"performance": performance,
	"clusters": num_clusters
    }
    save_metrics_to_json(network_name,"metis", metrics)
    print(f"Początkowa liczba klastrów: {len(communities)}")
    print_graph_info(G, label_dict, nodes_order=list(G.nodes()))
    if nodes_color is None:
        colors = [label_dict[n] for n in G.nodes()]
        nx.draw(G, position, node_color=colors, with_labels=True, cmap=plt.cm.tab10, node_size=500)
    else:
        colors = [nodes_color[label_dict[n] % len(nodes_color)] for n in G.nodes()]
        nx.draw(G, position, node_color=colors, with_labels=True, node_size=500)
    plt.savefig("Metis_clustering.png", dpi=300, bbox_inches="tight")
    plt.clf()
