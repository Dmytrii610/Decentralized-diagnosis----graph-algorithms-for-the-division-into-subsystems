import json
import os
import numpy as np
import matplotlib.pyplot as plt

json_dir = "results_test"

metric_colors = {
    "cross_weight": "tab:blue",
    "modularity": "tab:orange",
    "coverage": "tab:green",
    "performance": "tab:red"
}

output_dir = "wykresy_test"
os.makedirs(output_dir, exist_ok=True)

for file_name in os.listdir(json_dir):
    if not file_name.endswith(".json") and file_name.contains("combined"):
        continue

    json_path = os.path.join(json_dir, file_name)
    with open(json_path, "r") as f:
        data = json.load(f)

    cluster_data = {}
    for algo_name, entries in data.items():
        for entry in entries:
            metrics = entry["metrics"]
            n_clusters = metrics["clusters"]

            if n_clusters not in cluster_data:
                cluster_data[n_clusters] = {}
            if algo_name not in cluster_data[n_clusters]:
                cluster_data[n_clusters][algo_name] = {
                    "cross_weight": [],
                    "modularity": [],
                    "coverage": [],
                    "performance": []
                }

            cluster_data[n_clusters][algo_name]["cross_weight"].append(metrics["cross_weight"])
            cluster_data[n_clusters][algo_name]["modularity"].append(metrics["modularity"])
            cluster_data[n_clusters][algo_name]["coverage"].append(metrics["coverage"])
            cluster_data[n_clusters][algo_name]["performance"].append(
                metrics.get("performance", metrics.get("perfoemance", 0))
            )

    for n_clusters, algos in cluster_data.items():
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twinx()

        algo_names = list(algos.keys())
        x = np.arange(len(algo_names))
        width = 0.18

        offsets = {
            "cross_weight": -1.5 * width,
            "modularity": -0.5 * width,
            "coverage": 0.5 * width,
            "performance": 1.5 * width
        }

        for metric, color in metric_colors.items():
            means, stds = [], []
            for algo in algo_names:
                vals = algos[algo][metric]
                means.append(np.mean(vals))
                stds.append(np.std(vals))

            ax = ax1 if metric == "cross_weight" else ax2
            ax.bar(
                x + offsets[metric],
                means,
                width,
                yerr=stds,
                capsize=5,
                label=metric,
                color=color,
                alpha=0.85
            )

        ax1.set_xlabel("Algorytmy podziału")
        ax1.set_ylabel("Cross weight", color="tab:blue")
        ax2.set_ylabel("Pozostałe metryki (0–1)", color="tab:orange")
        ax1.set_title(f"{file_name} – wyniki dla {n_clusters} klastrów")

        ax1.set_xticks(x)
        ax1.set_xticklabels(algo_names)
        ax1.grid(True, linestyle="--", alpha=0.4)

        lines, labels = [], []
        for ax in [ax1, ax2]:
            L, lab = ax.get_legend_handles_labels()
            lines.extend(L)
            labels.extend(lab)
        ax1.legend(lines, labels, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=4)

        plt.tight_layout()
        plot_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_clusters_{n_clusters}.png")
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Wykres zapisano: {plot_path}")

    if "num_clusters" not in data:
        n_values = list(cluster_data.keys())
        if n_values:
            data["num_clusters"] = n_values
            with open(json_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"📝 Dodano liczbę klastrów do {file_name}: {n_values}")

print(f"\nWszystkie wykresy zapisano w folderze: {output_dir}")
