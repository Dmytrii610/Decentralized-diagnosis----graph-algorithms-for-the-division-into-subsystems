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


def spectral_clustering(G, k, nodes_color, position, nodes_order=None,network_name=None):
    if nodes_order is None:
        nodes_order = list(G.nodes())
    L = nx.laplacian_matrix(G, nodelist=nodes_order)
    n = L.shape[0]
    if k >= n:
        raise ValueError("k must be smaller than number of nodes")
    _, vecs = eigsh(L, k=k, which='SM')  # vecs shape: (n, k)
    nodes_features = vecs[:, :k]
    kmeans = KMeans(n_clusters=k, random_state=69)
    labels_array = kmeans.fit_predict(nodes_features)
    label_dict, communities = ensure_label_dict(labels_array, nodes_order)

    num_clusters = len(communities)

    cross_weight = calculate_sum_of_cross_weights(G, label_dict)
    modularity = nx.algorithms.community.quality.modularity(G, communities)
    coverage, performance = nx.algorithms.community.partition_quality(G, communities)
    metrics = {
        "cross_weight": cross_weight,
        "modularity": modularity,
        "coverage": coverage,
        "performance": performance,
	"clusters": num_clusters
    }
    save_metrics_to_json(network_name,"Spectral", metrics)
    color_list = [nodes_color[label_dict[n] % len(nodes_color)] for n in nodes_order]
    print_graph_info(G, labels_array, nodes_order=nodes_order)
    nx.draw(G, position, node_color=color_list, with_labels=True, node_size=500)
    plt.savefig("spectral_clustering.png", dpi=300, bbox_inches="tight")
    plt.clf()
