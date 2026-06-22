import os
import json
import numpy as np
import matplotlib.pyplot as plt

json_dir = "results_test"
output_dir = "plots_by_method_new"
os.makedirs(output_dir, exist_ok=True)

# Mapowanie: klucz wyświetlany -> klucz w JSON
metric_map = {
    "NCut":        "cross_weight",
    "modularność": "modularity",
    "pokrycie":    "coverage",
    "wydajność":   ["performance", "perfoemance"]  # obsługa literówki
}

metric_colors = {
    "NCut":        "tab:blue",
    "modularność": "tab:orange",
    "pokrycie":    "tab:green",
    "wydajność":   "tab:red"
}

cluster_counts = [2, 3, 4, 5]
data_by_method = {n: {} for n in cluster_counts}

# Wczytanie wszystkich plików JSON z katalogu (bez filtra "combined")
for file_name in os.listdir(json_dir):
    if not file_name.endswith(".json"):
        continue

    with open(os.path.join(json_dir, file_name), "r") as f:
        data = json.load(f)

    for algo_name, entries in data.items():
        if algo_name == "num_clusters":
            continue
        if not isinstance(entries, list):
            continue

        for entry in entries:
            m = entry.get("metrics", {})
            n_clusters = m.get("clusters")
            if n_clusters not in cluster_counts:
                continue

            if algo_name not in data_by_method[n_clusters]:
                data_by_method[n_clusters][algo_name] = {
                    k: [] for k in metric_colors
                }

            for display_name, json_key in metric_map.items():
                # obsługa listy możliwych kluczy (literówka w perfoemance)
                if isinstance(json_key, list):
                    value = next(
                        (m[k] for k in json_key if k in m), None
                    )
                else:
                    value = m.get(json_key)

                if value is not None:
                    data_by_method[n_clusters][algo_name][display_name]\
                        .append(value)

# Diagnostyka – wypisz co zostało wczytane
for n in cluster_counts:
    print(f"\nk={n}: {list(data_by_method[n].keys())}")
    for algo, metrics in data_by_method[n].items():
        for metric, vals in metrics.items():
            print(f"  {algo} | {metric}: {len(vals)} wartości")

# Wykresy
for n_clusters in cluster_counts:
    methods = list(data_by_method[n_clusters].keys())
    if not methods:
        print(f"Brak danych dla k={n_clusters}, pomijam.")
        continue

    x = np.arange(len(methods))
    width = 0.18
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    offsets = {
        "NCut":        -1.5 * width,
        "modularność": -0.5 * width,
        "pokrycie":     0.5 * width,
        "wydajność":    1.5 * width
    }

    for metric, color in metric_colors.items():
        means, stds = [], []
        for method in methods:
            values = data_by_method[n_clusters][method][metric]
            if values:
                means.append(np.mean(values))
                stds.append(np.std(values))
            else:
                means.append(np.nan)
                stds.append(np.nan)

        ax = ax1 if metric == "NCut" else ax2
        ax.bar(
            x + offsets[metric],
            means,
            width,
            yerr=stds,
            capsize=5,
            color=color,
            label=metric,
            alpha=0.85
        )

    ax1.set_ylabel("NCut", color=metric_colors["NCut"])
    ax2.set_ylabel("Modularność / Pokrycie / Wydajność",
                   color="tab:orange")
    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=20)

    lines, labels = [], []
    for ax in (ax1, ax2):
        L, lab = ax.get_legend_handles_labels()
        lines.extend(L)
        labels.extend(lab)
    ax1.legend(lines, labels,
               loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=4)
    ax1.grid(True, linestyle="--", alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(
        output_dir, f"new_metrics_by_method_clusters_{n_clusters}.png"
    )
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Zapisano: {save_path}")
