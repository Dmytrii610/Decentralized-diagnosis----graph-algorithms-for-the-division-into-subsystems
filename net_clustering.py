import os
import json
import networkx as nx
import matplotlib.pyplot as plt

from Partition_algoritms.spectral_partition import spectral_clustering
from Partition_algoritms.louvain_partition import louvain_clustering
from Partition_algoritms.KL_partition import KL_clustering
from Partition_algoritms.metis_partition import metis_clustering
from JSON_Converter.graph_from_json import graph_from_json

models_dir = "models"
json_files = [f for f in os.listdir(models_dir) if f.endswith(".json")]

color_sets = {
    2: ["red", "blue"],
    3: ["red", "blue", "green"],
    4: ["red", "blue", "green", "orange"],
    5: ["red", "blue", "green", "orange", "purple"]
}

for json_file in json_files:
    network_name = json_file.replace(".json", "")
    print(f"Przetwarzanie sieci: {network_name}")

    G, pos = graph_from_json(json_file)

    for n_clusters in range(2, 6):
        print(f"Podział na {n_clusters} podgrafy")

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
            print(f"łąd Metis ({n_clusters}): {e}")

    try:
        KL_clustering(
            G,
            iterations=200,
            position=pos,
            network_name=f"{network_name}_KL"
        )
    except Exception as e:
        print(f"łąd Kernighan–Lin: {e}")

    try:
        louvain_clustering(
            G,
            position=pos,
            nodes_color=["red", "blue", "green", "salmon", "pink"],
            network_name=f"{network_name}_Louvain"
        )
    except Exception as e:
        print(f"Błąd Louvain: {e}")

print("\nZakończono przetwarzanie wszystkich sieci.")
