import json
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from networkx.algorithms.community import kernighan_lin
import community as community_louvain
from sklearn.cluster import KMeans
from scipy.sparse.linalg import eigsh
from collections import defaultdict
import os
from datetime import datetime
import pymetis
# Convert from Graph to JSON representation
def save_metrics_to_json(graph_name, algorithm_name, metrics, output_dir="results_test"):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{graph_name}_results.json")

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            all_results = json.load(f)
    else:
        all_results = {}

    # Aktualizacja lub dodanie nowego wyniku
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "algorithm": algorithm_name,
        "metrics": metrics
    }

    if algorithm_name not in all_results:
        all_results[algorithm_name] = []
    all_results[algorithm_name].append(entry)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    print(f"Wyniki zapisano do: {file_path}")
