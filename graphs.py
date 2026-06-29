import os
import networkx as nx
import matplotlib.pyplot as plt

from JSON_Converter.graph_from_json import graph_from_json

# ── Konfiguracja ─────────────────────────────────────────────────────────────
MODELS_DIR = "models"
OUTPUT_DIR = "network_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

NODE_COLOR = "#4C9BE8"   # kolor wszystkich węzłów


def get_edge_widths(G: nx.Graph) -> list:
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    if not weights:
        return []
    max_w = max(weights)
    return [0.5 + 2.5 * (w / max_w) for w in weights]


# ── Wizualizacja ──────────────────────────────────────────────────────────────

def draw_network(G: nx.Graph, pos: dict, title: str, save_path: str) -> None:
    n = G.number_of_nodes()
    fig_size = max(8, min(22, n * 0.35))
    fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.82))

    widths = get_edge_widths(G)
    node_sz = max(150, 500 - n * 3)

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        width=widths,
        alpha=0.55,
        edge_color="#555555",
    )
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color=NODE_COLOR,
        node_size=node_sz,
        linewidths=0.6,
        edgecolors="#333333",
    )

    if n <= 60:
        nx.draw_networkx_labels(
            G, pos, ax=ax,
            font_size=7,
            font_color="#111111",
        )

    if n <= 30:
        edge_labels = {
            (u, v): G[u][v]["weight"]
            for u, v in G.edges()
            if G[u][v]["weight"] > 1
        }
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=edge_labels,
            ax=ax, font_size=6, alpha=0.7,
        )

    stats = (f"węzły: {G.number_of_nodes()}  |  "
             f"krawędzie: {G.number_of_edges()}  |  "
             f"śr. stopień: {2*G.number_of_edges()/G.number_of_nodes():.1f}")
    ax.set_title(f"{title}\n{stats}", fontsize=11, fontweight="bold", pad=12)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"  Zapisano: {save_path}")


def print_stats(name: str, G: nx.Graph) -> None:
    n = G.number_of_nodes()
    m = G.number_of_edges()
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    print(f"\n{'─'*48}")
    print(f"  Sieć              : {name}")
    print(f"  Węzły (równania)  : {n}")
    print(f"  Krawędzie         : {m}")
    print(f"  Gęstość           : {nx.density(G):.4f}")
    print(f"  Śr. stopień       : {2*m/n:.2f}")
    if weights:
        print(f"  Śr. waga krawędzi : {sum(weights)/len(weights):.2f}")
        print(f"  Maks. waga        : {max(weights)}")
    print(f"  Spójny            : {nx.is_connected(G)}")


# ── Główna pętla ──────────────────────────────────────────────────────────────

def main():
    json_files = sorted(f for f in os.listdir(MODELS_DIR) if f.endswith(".json"))

    if not json_files:
        print(f"Brak plików JSON w katalogu '{MODELS_DIR}'.")
        return

    print(f"Znaleziono {len(json_files)} sieci: {json_files}")

    for file_name in json_files:
        network_name = file_name.replace(".json", "")
        print(f"\nPrzetwarzanie: {network_name}")

        # użycie istniejącego konwertera – zwraca (G, pos)
        G, pos = graph_from_json(file_name)

        print_stats(network_name, G)

        save_path = os.path.join(OUTPUT_DIR, f"{network_name}_graph.png")
        draw_network(G, pos, title=network_name, save_path=save_path)

    print(f"\nGotowe. Wykresy zapisano w '{OUTPUT_DIR}'.")


if __name__ == "__main__":
    main()
