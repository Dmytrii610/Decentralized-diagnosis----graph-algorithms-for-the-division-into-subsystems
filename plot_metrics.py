import os
import json
import re
import numpy as np
import matplotlib.pyplot as plt

RESULTS_DIR = "Results/metrics"
METRICS = ["modularity", "coverage", "performance", "cross_weight"]

def load_results(results_dir):
    # data[network_name][n_clusters][algorithm][metric] = [wartości]
    data = {}

    for file in os.listdir(results_dir):
        if not file.endswith(".json"):
            continue

        filepath = os.path.join(results_dir, file)

        # example: BIN_7_0_26_Spectral_5_results.json. Wzór w Regular Expressions
        match = re.match(r"^(.*?)_([A-Za-z]+)_([0-9]+)_results\.json$", file)
        if not match:
            match = re.match(r"^(.*)_([0-9]+)_results\.json$", file)

        if match:
            if len(match.groups()) == 3:
                network_name, _, n_clusters = match.groups()
            else:
                network_name, n_clusters = match.groups()
            n_clusters = int(n_clusters)
        else:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)

        for algo_name, entries in content.items():
            for entry in entries:
                metrics = entry.get("metrics", {})

                if network_name not in data:
                    data[network_name] = {}
                if n_clusters not in data[network_name]:
                    data[network_name][n_clusters] = {}
                if algo_name not in data[network_name][n_clusters]:
                    data[network_name][n_clusters][algo_name] = {m: [] for m in METRICS}

                for metric, value in metrics.items():
                    if metric in METRICS:
                        data[network_name][n_clusters][algo_name][metric].append(value)

    return data


def plot_metrics(data):
    os.makedirs("plots", exist_ok=True)

    for network_name, clusters_data in data.items():
        for metric in METRICS:
            for n_clusters, algos in sorted(clusters_data.items()):
                labels, means, stds = [], [], []

                for algo, values in algos.items():
                    vals = values.get(metric, [])
                    if vals:
                        labels.append(algo)
                        means.append(np.mean(vals))
                        stds.append(np.std(vals))

                if not labels:
                    continue

                plt.figure(figsize=(8, 6))
                plt.bar(labels, means, yerr=stds, capsize=6)
                plt.title(f"{network_name} — {metric.capitalize()} (liczba społeczności: {n_clusters})")
                plt.ylabel(metric.capitalize())
                plt.xlabel("Algorytm")
                plt.grid(axis="y", linestyle="--", alpha=0.6)
                plt.tight_layout()

                filename = f"plots/{network_name}_{metric}_clusters_{n_clusters}.png"
                plt.savefig(filename)
                plt.close()
                print(f"Zapisano wykres: {filename}")


if __name__ == "__main__":
    data = load_results(RESULTS_DIR)
    plot_metrics(data)
