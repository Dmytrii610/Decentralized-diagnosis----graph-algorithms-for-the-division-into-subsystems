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

# Convert from JSON to Graph representation
def graph_from_json(json_name):
    with open(f"models/{json_name}", "r", encoding="utf-8") as f:
        data = json.load(f)
    elements = data["model"]
    G = nx.Graph()

    for e in elements:
        G.add_node(e, params=set(elements[e]))

    for (e1, e2) in combinations(elements.keys(), 2):
        common = set(elements[e1]) & set(elements[e2])
        weight = len(common)
        if weight > 0:
            G.add_edge(e1, e2, weight=weight)

    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=300, font_size=8)
    plt.savefig("graf.png", dpi=300, bbox_inches="tight")
    plt.clf()
    return G,pos
