"""
Spectral Clustering for Graph Decomposition
Enhanced version compatible with DecSel framework
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
from sklearn.cluster import KMeans
from scipy.sparse.linalg import eigsh
from collections import defaultdict
import os


def ensure_label_dict(labels, nodes):
    """
    Convert various label formats to (label_dict, communities) tuple.
    
    Args:
        labels: Labels in various formats (dict, list of sets, array)
        nodes: List of nodes in order
        
    Returns:
        tuple: (label_dict, communities) where
            - label_dict: node -> cluster_id mapping
            - communities: list of sets, each set contains nodes in a cluster
    """
    # Case 1: dict: node -> label
    if isinstance(labels, dict):
        label_dict = dict(labels)
        comms = defaultdict(set)
        for n, lab in label_dict.items():
            comms[lab].add(n)
        communities = list(comms.values())
        return label_dict, communities

    # Case 2: list/tuple of sets (communities)
    if isinstance(labels, (list, tuple)) and all(isinstance(b, (set, list)) for b in labels):
        communities = [set(b) for b in labels]
        label_dict = {}
        for idx, block in enumerate(communities):
            for n in block:
                label_dict[n] = idx
        return label_dict, communities

    # Case 3: array of labels
    label_dict = {}
    for n, lab in zip(nodes, labels):
        label_dict[n] = int(lab)
    comms = defaultdict(set)
    for n, lab in label_dict.items():
        comms[lab].add(n)
    communities = list(comms.values())
    return label_dict, communities


def calculate_sum_of_cross_weights(G, label_dict):
    """
    Calculate sum of edge weights crossing cluster boundaries.
    
    Args:
        G: NetworkX graph
        label_dict: node -> cluster_id mapping
        
    Returns:
        float: Sum of weights of edges between different clusters
    """
    cross_weight = 0
    for u, v in G.edges():
        if label_dict.get(u) != label_dict.get(v):
            weight = G[u][v].get('weight', 1)  # Default weight = 1
            cross_weight += weight
    return cross_weight


def calculate_communication_cost(G, label_dict):
    """
    Calculate communication cost (alternative metric for cross-cluster edges).
    Useful for distributed systems where minimizing inter-partition communication is crucial.
    
    Args:
        G: NetworkX graph
        label_dict: node -> cluster_id mapping
        
    Returns:
        int: Number of edges crossing cluster boundaries
    """
    comm_cost = 0
    for u, v in G.edges():
        if label_dict.get(u) != label_dict.get(v):
            comm_cost += 1
    return comm_cost


def print_graph_info(G, labels, nodes_order=None):
    """
    Print comprehensive partition quality metrics.
    
    Args:
        G: NetworkX graph
        labels: Partition labels in any supported format
        nodes_order: Optional node ordering
    """
    if nodes_order is None:
        nodes_order = list(G.nodes())
    
    label_dict, communities = ensure_label_dict(labels, nodes_order)
    
    # Calculate metrics
    cross_weight = calculate_sum_of_cross_weights(G, label_dict)
    comm_cost = calculate_communication_cost(G, label_dict)
    modularity = nx.algorithms.community.quality.modularity(G, communities)
    coverage, performance = nx.algorithms.community.partition_quality(G, communities)
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Graph Partition Quality Metrics")
    print(f"{'='*60}")
    print(f"Number of clusters: {len(communities)}")
    print(f"Cross-edge weight sum: {cross_weight:.4f}")
    print(f"Communication cost (edge count): {comm_cost}")
    print(f"Modularity: {modularity:.4f}")
    print(f"Coverage: {coverage:.4f}")
    print(f"Performance: {performance:.4f}")
    print(f"{'='*60}\n")


def spectral_clustering(G, k, nodes_color=None, position=None, nodes_order=None,
                       network_name=None, output_dir="results/spectral",
                       save_plot=True, save_metrics=True, weighted=True):
    """
    Perform spectral clustering on a graph using the Laplacian matrix.
    
    Args:
        G: NetworkX graph
        k: Number of clusters
        nodes_color: List of colors for visualization (optional)
        position: Node positions for plotting (optional)
        nodes_order: Specific node ordering (optional)
        network_name: Name for saving results (optional)
        output_dir: Directory for saving results
        save_plot: Whether to save visualization
        save_metrics: Whether to save metrics to JSON
        weighted: Whether to use weighted Laplacian (default: True)
        
    Returns:
        dict: Contains 'label_dict', 'communities', and 'metrics'
    """
    # Setup
    if nodes_order is None:
        nodes_order = list(G.nodes())
    
    if nodes_color is None:
        nodes_color = plt.cm.tab10(np.linspace(0, 1, 10))
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Compute Laplacian matrix
    if weighted:
        L = nx.laplacian_matrix(G, nodelist=nodes_order, weight='weight')
        L = L.astype(np.float64)
    else:
        L = nx.laplacian_matrix(G, nodelist=nodes_order, weight=None)
    
    n = L.shape[0]
    if k >= n:
        raise ValueError(f"k ({k}) must be smaller than number of nodes ({n})")
    
    # Compute eigenvectors
    print(f"Computing {k} smallest eigenvectors...")
    _, vecs = eigsh(L, k=k, which='SM')  # vecs shape: (n, k)
    nodes_features = vecs[:, :k]
    
    # KMeans clustering
    print(f"Performing KMeans clustering with k={k}...")
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_array = kmeans.fit_predict(nodes_features)
    
    # Convert to standard format
    label_dict, communities = ensure_label_dict(labels_array, nodes_order)
    num_clusters = len(communities)
    
    # Calculate metrics
    cross_weight = calculate_sum_of_cross_weights(G, label_dict)
    comm_cost = calculate_communication_cost(G, label_dict)
    modularity = nx.algorithms.community.quality.modularity(G, communities)
    coverage, performance = nx.algorithms.community.partition_quality(G, communities)
    
    metrics = {
        "method": "Spectral",
        "cross_weight": float(cross_weight),
        "communication_cost": int(comm_cost),
        "modularity": float(modularity),
        "coverage": float(coverage),
        "performance": float(performance),
        "clusters": num_clusters,
        "weighted": weighted
    }
    
    # Print information
    print_graph_info(G, labels_array, nodes_order=nodes_order)
    
    # Save metrics to JSON
    if save_metrics and network_name:
        metrics_file = os.path.join(output_dir, f"{network_name}_spectral_k{k}_metrics.json")
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"Metrics saved to: {metrics_file}")
    
    # Visualization
    if save_plot:
        color_list = [nodes_color[label_dict[n] % len(nodes_color)] for n in nodes_order]
        
        if position is None:
            position = nx.spring_layout(G, seed=42)
        
        plt.figure(figsize=(12, 8))
        nx.draw(G, position, node_color=color_list, with_labels=True, 
                node_size=500, font_size=8, edge_color='gray', alpha=0.6)
        
        title = f"Spectral Clustering (k={k})"
        if network_name:
            title = f"{network_name}: {title}"
        plt.title(title)
        
        # Add metrics as text
        metrics_text = f"Modularity: {modularity:.3f}\nCross-weight: {cross_weight:.2f}"
        plt.text(0.02, 0.98, metrics_text, transform=plt.gca().transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plot_file = os.path.join(output_dir, f"{network_name}_spectral_k{k}.png" if network_name 
                                else f"spectral_clustering_k{k}.png")
        plt.savefig(plot_file, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"Plot saved to: {plot_file}")
    
    return {
        'label_dict': label_dict,
        'communities': communities,
        'metrics': metrics
    }


def spectral_clustering_range(G, k_values, **kwargs):
    """
    Perform spectral clustering for multiple k values.
    
    Args:
        G: NetworkX graph
        k_values: List of k values to try
        **kwargs: Additional arguments passed to spectral_clustering
        
    Returns:
        dict: Results for each k value
    """
    results = {}
    
    for k in k_values:
        print(f"\n{'='*60}")
        print(f"Running spectral clustering with k={k}")
        print(f"{'='*60}")
        
        try:
            result = spectral_clustering(G, k, **kwargs)
            results[k] = result
        except Exception as e:
            print(f"Error for k={k}: {str(e)}")
            results[k] = None
    
    return results


# DecSel-specific integration functions

def load_decsel_graph(filepath):
    """
    Load a graph from DecSel format.
    This is a placeholder - adapt based on actual DecSel format.
    
    Args:
        filepath: Path to DecSel graph file
        
    Returns:
        NetworkX graph
    """
    # TODO: Implement based on actual DecSel format
    # This is a placeholder that assumes JSON format
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    G = nx.Graph()
    # Add implementation based on DecSel structure
    
    return G


def compare_with_metis(G, k, spectral_result):
    """
    Compare spectral clustering results with METIS.
    
    Args:
        G: NetworkX graph
        k: Number of partitions
        spectral_result: Result from spectral_clustering
        
    Returns:
        dict: Comparison metrics
    """
    # This would integrate with DecSel's METIS implementation
    # Placeholder for now
    pass


if __name__ == "__main__":
    # Example usage
    print("Spectral Clustering Module for DecSel")
    print("Import this module to use spectral clustering functionality")
    
    # Example with simple graph
    G = nx.karate_club_graph()
    result = spectral_clustering(G, k=2, network_name="karate_club", 
                                save_plot=True, save_metrics=True)
    
    print("\nExample completed successfully!")
