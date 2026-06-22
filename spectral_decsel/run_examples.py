"""
Example script demonstrating integration of spectral clustering with DecSel.
This script shows how to use your spectral method alongside DecSel's existing methods.
"""

import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

# Add DecSel paths (adjust based on actual structure)
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from spectral_partition_decsel import spectral_clustering, spectral_clustering_range
from spectral_interface import SpectralDecomposer, SpectralBenchmark


def example_1_simple_graph():
    """
    Example 1: Run spectral clustering on a simple test graph.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Simple Test Graph")
    print("="*80 + "\n")
    
    G = nx.Graph()
    
    G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0), (0, 2), (1, 3)])
    
    G.add_edges_from([(4, 5), (5, 6), (6, 7), (7, 4), (4, 6), (5, 7)])
    
    G.add_edges_from([(8, 9), (9, 10), (10, 11), (11, 8), (8, 10), (9, 11)])
    
    G.add_edges_from([(3, 4), (7, 8)])
    
    for u, v in G.edges():
        if (u in [0,1,2,3] and v in [0,1,2,3]) or \
           (u in [4,5,6,7] and v in [4,5,6,7]) or \
           (u in [8,9,10,11] and v in [8,9,10,11]):
            G[u][v]['weight'] = 5  # Strong intra-community
        else:
            G[u][v]['weight'] = 1  # Weak inter-community
    
    result = spectral_clustering(
        G, 
        k=3,
        network_name="test_simple",
        output_dir="results/examples",
        save_plot=True,
        save_metrics=True
    )
    
    print("\nCommunities found:")
    for i, community in enumerate(result['communities']):
        print(f"  Community {i}: {sorted(list(community))}")
    
    print("\nMetrics:")
    for key, value in result['metrics'].items():
        print(f"  {key}: {value}")


def example_2_karate_club():
    """
    Example 2: Classic Karate Club graph with different k values.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Karate Club Graph (Multiple k values)")
    print("="*80 + "\n")
    
    G = nx.karate_club_graph()
    
    for u, v in G.edges():
        G[u][v]['weight'] = 1 + min(G.degree(u), G.degree(v)) / 10
    
    k_values = [2, 3, 4]
    results = spectral_clustering_range(
        G,
        k_values=k_values,
        network_name="karate_club",
        output_dir="results/examples",
        save_plot=True,
        save_metrics=True
    )
    
    print("\nComparison of different k values:")
    print(f"{'k':<5} {'Modularity':<12} {'Cross-weight':<15} {'Coverage':<12}")
    print("-"*50)
    
    for k, result in results.items():
        if result:
            metrics = result['metrics']
            print(f"{k:<5} {metrics['modularity']:<12.4f} "
                  f"{metrics['cross_weight']:<15.2f} {metrics['coverage']:<12.4f}")


def example_3_decsel_adapter():
    """
    Example 3: Using the SpectralDecomposer adapter class.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: SpectralDecomposer Adapter")
    print("="*80 + "\n")
    
    # Create test graph
    G = nx.barbell_graph(5, 2)
    for u, v in G.edges():
        G[u][v]['weight'] = 1
    
    # Use adapter
    decomposer = SpectralDecomposer(n_clusters=2, weighted=True)
    
    communities = decomposer.decompose(
        G,
        network_name="barbell",
        output_dir="results/examples",
        save_plot=True,
        save_metrics=True
    )
    
    print(f"Found {len(communities)} communities")
    
    partition = decomposer.get_partition_dict()
    metrics = decomposer.get_metrics()
    
    print("\nPartition:")
    for node, cluster in sorted(partition.items()):
        print(f"  Node {node} -> Cluster {cluster}")
    
    print("\nMetrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")


def example_4_benchmark():
    """
    Example 4: Benchmark spectral clustering with different parameters.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Benchmarking Spectral Clustering")
    print("="*80 + "\n")
    
    G = nx.Graph()
    
    communities_ground_truth = []
    node_id = 0
    for comm_idx in range(4):
        community = []
        for i in range(6):
            community.append(node_id)
            node_id += 1
        communities_ground_truth.append(community)
        
        for i in range(len(community)):
            for j in range(i+1, len(community)):
                if i != j:
                    G.add_edge(community[i], community[j], weight=5)
    
    G.add_edge(5, 6, weight=1)
    G.add_edge(11, 12, weight=1)
    G.add_edge(17, 18, weight=1)
    
    benchmark = SpectralBenchmark(output_dir="results/benchmark")
    benchmark.run_spectral(G, k_values=[2, 3, 4, 5], network_name="synthetic")
    
    benchmark.save_benchmark("spectral_benchmark.json")
    benchmark.compare_methods()


def example_5_with_your_json_format():
    """
    Example 5: Using your original JSON format from graph_from_json.py
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Your JSON Format Integration")
    print("="*80 + "\n")
    
    model_data = {
        "model": {
            "ComponentA": ["param1", "param2", "param3"],
            "ComponentB": ["param2", "param3", "param4"],
            "ComponentC": ["param3", "param4", "param5"],
            "ComponentD": ["param4", "param5", "param6"],
            "ComponentE": ["param1", "param5", "param6"],
        }
    }
    
    os.makedirs("models", exist_ok=True)
    with open("models/example_model.json", 'w') as f:
        json.dump(model_data, f, indent=2)
    
    from itertools import combinations
    
    elements = model_data["model"]
    G = nx.Graph()
    
    for e in elements:
        G.add_node(e, params=set(elements[e]))
    
    for (e1, e2) in combinations(elements.keys(), 2):
        common = set(elements[e1]) & set(elements[e2])
        weight = len(common)
        if weight > 0:
            G.add_edge(e1, e2, weight=weight)
    
    print(f"Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    result = spectral_clustering(
        G,
        k=2,
        network_name="example_model",
        output_dir="results/examples",
        save_plot=True,
        save_metrics=True
    )
    
    print("\nCommunities:")
    for i, community in enumerate(result['communities']):
        print(f"  Cluster {i}: {sorted(list(community))}")


def example_6_full_pipeline():
    """
    Example 6: Complete pipeline as it would work with DecSel.
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Full DecSel Integration Pipeline")
    print("="*80 + "\n")
    
    
    print("Step 1: Creating graph...")
    G = nx.erdos_renyi_graph(30, 0.2, seed=42)
    for u, v in G.edges():
        G[u][v]['weight'] = 1
    
    print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    print("\nStep 2: Running spectral decomposition...")
    spectral_decomposer = SpectralDecomposer(n_clusters=3)
    spectral_communities = spectral_decomposer.decompose(
        G,
        network_name="full_pipeline",
        output_dir="results/examples",
        save_plot=True,
        save_metrics=True
    )
    spectral_metrics = spectral_decomposer.get_metrics()
    
    print(f"  Found {len(spectral_communities)} communities")
    print(f"  Modularity: {spectral_metrics['modularity']:.4f}")
    
    print("\nStep 3: Comparison with other methods...")
    print("  (In real DecSel: compare with METIS, BILP, Louvain, etc.)")
    
    print("\nStep 4: Saving results...")
    results_dir = "results/examples"
    os.makedirs(results_dir, exist_ok=True)
    
    output = {
        "method": "spectral",
        "n_clusters": 3,
        "metrics": spectral_metrics,
        "communities": [sorted(list(c)) for c in spectral_communities]
    }
    
    with open(f"{results_dir}/full_pipeline_results.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print("  Results saved to results/examples/full_pipeline_results.json")
    
    print("\n✓ Pipeline completed successfully!")


def main():
    """
    Run all examples.
    """
    print("="*80)
    print("SPECTRAL CLUSTERING - DECSEL INTEGRATION EXAMPLES")
    print("="*80)
    
    examples = [
        ("Simple Graph", example_1_simple_graph),
        ("Karate Club (Multiple k)", example_2_karate_club),
        ("Adapter Class", example_3_decsel_adapter),
        ("Benchmarking", example_4_benchmark),
        ("Your JSON Format", example_5_with_your_json_format),
        ("Full Pipeline", example_6_full_pipeline),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all examples...\n")
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n Error in {name}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)
    print("\nResults saved in:")
    print("  - results/examples/     (plots and metrics)")
    print("  - results/benchmark/    (benchmark results)")
    print("  - models/               (example models)")


if __name__ == "__main__":
    main()
