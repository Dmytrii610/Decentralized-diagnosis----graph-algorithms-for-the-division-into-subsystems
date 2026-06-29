import os
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

def KL_clustering(G, iterations, position,network_name):
    partition = kernighan_lin.kernighan_lin_bisection(G, max_iter=iterations, weight='weight')
    label_dict, communities = ensure_label_dict(partition, list(G.nodes()))
    colors = ['red' if label_dict[n] == 0 else 'blue' for n in G.nodes()]
    cross_weight = calculate_sum_of_cross_weights(G,label_dict)
    n_cuts = nx.cut_size(G, partition[0], partition[1], weight='weight')
    modularity = nx.algorithms.community.quality.modularity(G, communities)
    coverage, performance = nx.algorithms.community.partition_quality(G, communities)
    num_clusters = len(communities)
    metrics = {
	"cross_weight": cross_weight,
	"modularity": modularity,
	"coverage": coverage,
	"perfoemance": performance,
	"clusters": num_clusters
    }
    save_metrics_to_json(network_name, "KernighanLin", metrics)
    print(f"Liczba przecięć: {n_cuts}")
    print(f"Wartość modularności: {modularity}")
    print(f"Coverage: {coverage}")
    print(f"Performance: {performance}")
    output_dir = os.path.join("results_png", network_name)
    nx.draw(G, position, node_color=colors, with_labels=False, node_size=100)
    plt.savefig(output_dir, dpi=300, bbox_inches="tight")
    plt.clf()
