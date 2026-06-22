import os
import json
import datetime
import networkx as nx
import matplotlib.pyplot as plt

from Partition_algoritms.spectral_partition import spectral_clustering
from Partition_algoritms.louvain_partition import louvain_clustering
from Partition_algoritms.KL_partition import KL_clustering
from Partition_algoritms.metis_partition import metis_clustering
from JSON_Converter.graph_from_json import graph_from_json

MODELS_DIR = "models"
RESULTS_DIR = "results_test"
os.makedirs(RESULTS_DIR, exist_ok=True)

json_files = [f for f in os.listdir(MODELS_DIR) if f.endswith(".json")]

color_sets = {
    2: ["red", "blue"],
    3: ["red", "blue", "green"],
    4: ["red", "blue", "green", "orange"],
    5: ["red", "blue", "green", "orange", "purple"]
}


def combine_results(network_name):
    pattern_prefix = network_name.split(".")[0]
    all_results = {}

    for file in os.listdir(RESULTS_DIR):
        if not file.startswith(pattern_prefix) or not file.endswith("_results.json"):
            continue

        filepath = os.path.join(RESULTS_DIR, file)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            for algo, entries in content.items():
                if algo not in all_results:
                    all_results[algo] = []
                all_results[algo].extend(entries)

        except Exception as e:
            print(f"Błąd przy łączeniu {file}: {e}")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for algo, entries in all_results.items():
        for entry in entries:
            if "timestamp" not in entry:
                entry["timestamp"] = timestamp

    output_path = os.path.join(RESULTS_DIR, f"{pattern_prefix}_combined_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
    print(f"Scalony plik zapisano: {output_path}")


for json_file in json_files:
    network_name = json_file.replace(".json", "")
    print(f"\n=== Przetwarzanie sieci: {network_name} ===")

    G, pos = graph_from_json(json_file)

    for n_clusters in range(2, 6):
        print(f"\n Podział na {n_clusters} podgrafy")

        try:
            spectral_clustering(
                G,
                n_clusters,
                color_sets[n_clusters],
                pos,
                network_name=f"{network_name}_Spectral_{n_clusters}"
            )
        except Exception as e:
            print(f"Błąd Spectral ({n_clusters}): {e}")

        try:
            metis_clustering(
                G,
                n_clusters=n_clusters,
                nodes_color=color_sets[n_clusters],
                position=pos,
                network_name=f"{network_name}_Metis_{n_clusters}"
            )
        except Exception as e:
            print(f"Błąd Metis ({n_clusters}): {e}")

        try:
            louvain_clustering(
                G,
                n_clusters,
                position=pos,
                nodes_color=["red", "blue", "green", "salmon", "pink"],
                network_name=f"{network_name}_Louvain_{n_clusters}"
            )
        except Exception as e:
            print(f"Błąd Louvain ({n_clusters}): {e}")

    try:
        KL_clustering(
            G,
            iterations=200,
            position=pos,
            network_name=f"{network_name}_KL"
        )
    except Exception as e:
        print(f"Błąd Kernighan–Lin: {e}")

    combine_results(network_name)
