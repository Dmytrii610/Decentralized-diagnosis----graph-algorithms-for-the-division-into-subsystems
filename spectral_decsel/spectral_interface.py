"""
Spectral Decomposition Interface for DecSel Framework
This module provides an interface between spectral clustering and DecSel's decomposition system.
"""

import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os


class SpectralDecomposer:
    """
    Adapter class for integrating spectral clustering with DecSel framework.
    """
    
    def __init__(self, n_clusters: int, weighted: bool = True, random_state: int = 42):
        """
        Initialize the spectral decomposer.
        
        Args:
            n_clusters: Number of clusters/partitions
            weighted: Whether to use edge weights
            random_state: Random seed for reproducibility
        """
        self.n_clusters = n_clusters
        self.weighted = weighted
        self.random_state = random_state
        self.last_result = None
    
    def decompose(self, G: nx.Graph, **kwargs) -> List[set]:
        """
        Decompose graph into partitions using spectral clustering.
        
        Args:
            G: NetworkX graph to decompose
            **kwargs: Additional arguments
            
        Returns:
            List of sets, each containing nodes in a partition
        """
        from spectral_partition_decsel import spectral_clustering
        
        result = spectral_clustering(
            G, 
            self.n_clusters,
            weighted=self.weighted,
            save_plot=kwargs.get('save_plot', False),
            save_metrics=kwargs.get('save_metrics', False),
            network_name=kwargs.get('network_name', None),
            output_dir=kwargs.get('output_dir', 'results/spectral')
        )
        
        self.last_result = result
        return result['communities']
    
    def get_partition_dict(self) -> Dict[int, int]:
        """
        Get node to partition mapping from last decomposition.
        
        Returns:
            Dict mapping node_id to partition_id
        """
        if self.last_result is None:
            raise ValueError("No decomposition has been performed yet")
        return self.last_result['label_dict']
    
    def get_metrics(self) -> Dict:
        """
        Get metrics from last decomposition.
        
        Returns:
            Dict containing quality metrics
        """
        if self.last_result is None:
            raise ValueError("No decomposition has been performed yet")
        return self.last_result['metrics']


def convert_decsel_to_networkx(decsel_model: Dict) -> nx.Graph:
    """
    Convert DecSel structural model to NetworkX graph.
    
    Args:
        decsel_model: DecSel model dictionary
        
    Returns:
        NetworkX graph
    """
    G = nx.Graph()
    
    # This is a template - adapt based on actual DecSel format
    # Example assumes model has 'components' and 'relations' keys
    
    if 'components' in decsel_model:
        for comp_id, comp_data in decsel_model['components'].items():
            G.add_node(comp_id, **comp_data)
    
    if 'relations' in decsel_model:
        for rel in decsel_model['relations']:
            source = rel.get('source')
            target = rel.get('target')
            weight = rel.get('weight', 1)
            if source and target:
                G.add_edge(source, target, weight=weight)
    
    return G


def convert_networkx_to_decsel(G: nx.Graph, partition: Dict[int, int]) -> Dict:
    """
    Convert NetworkX graph and partition back to DecSel format.
    
    Args:
        G: NetworkX graph
        partition: Node to cluster mapping
        
    Returns:
        Dict in DecSel format with partition information
    """
    result = {
        'nodes': [],
        'partitions': {}
    }
    
    # Group nodes by partition
    from collections import defaultdict
    partition_groups = defaultdict(list)
    for node, cluster_id in partition.items():
        partition_groups[cluster_id].append(node)
    
    # Format for DecSel
    for cluster_id, nodes in partition_groups.items():
        result['partitions'][f'partition_{cluster_id}'] = {
            'nodes': list(nodes),
            'size': len(nodes)
        }
    
    # Add node list
    result['nodes'] = [{'id': node, 'partition': partition[node]} 
                       for node in G.nodes()]
    
    return result


def run_spectral_on_decsel_model(model_path: str, n_clusters: int, 
                                  output_dir: str = "results/spectral") -> Dict:
    """
    Complete workflow: load DecSel model, run spectral clustering, save results.
    
    Args:
        model_path: Path to DecSel model file
        n_clusters: Number of clusters
        output_dir: Directory for results
        
    Returns:
        Dict with results and metrics
    """
    # Load model
    with open(model_path, 'r') as f:
        decsel_model = json.load(f)
    
    # Convert to NetworkX
    G = convert_decsel_to_networkx(decsel_model)
    
    # Run spectral decomposition
    decomposer = SpectralDecomposer(n_clusters)
    network_name = os.path.splitext(os.path.basename(model_path))[0]
    
    communities = decomposer.decompose(
        G,
        save_plot=True,
        save_metrics=True,
        network_name=network_name,
        output_dir=output_dir
    )
    
    # Get partition and metrics
    partition = decomposer.get_partition_dict()
    metrics = decomposer.get_metrics()
    
    # Convert back to DecSel format
    decsel_result = convert_networkx_to_decsel(G, partition)
    
    # Save complete result
    result_path = os.path.join(output_dir, f"{network_name}_spectral_result.json")
    with open(result_path, 'w') as f:
        json.dump({
            'model': network_name,
            'method': 'spectral',
            'n_clusters': n_clusters,
            'partition': decsel_result,
            'metrics': metrics
        }, f, indent=2)
    
    print(f"\nResults saved to: {result_path}")
    
    return {
        'communities': communities,
        'partition': partition,
        'metrics': metrics,
        'decsel_format': decsel_result
    }


class SpectralBenchmark:
    """
    Benchmark spectral clustering against other methods in DecSel.
    """
    
    def __init__(self, output_dir: str = "results/benchmark"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.results = []
    
    def add_result(self, method_name: str, metrics: Dict):
        """Add benchmark result."""
        self.results.append({
            'method': method_name,
            **metrics
        })
    
    def run_spectral(self, G: nx.Graph, k_values: List[int], network_name: str):
        """
        Run spectral clustering with different k values.
        
        Args:
            G: NetworkX graph
            k_values: List of cluster counts to try
            network_name: Name of the network
        """
        from spectral_partition_decsel import spectral_clustering
        
        for k in k_values:
            print(f"\nRunning spectral with k={k}...")
            try:
                result = spectral_clustering(
                    G, k,
                    network_name=f"{network_name}_k{k}",
                    output_dir=self.output_dir,
                    save_plot=True,
                    save_metrics=True
                )
                self.add_result(f"Spectral_k{k}", result['metrics'])
            except Exception as e:
                print(f"Error with k={k}: {str(e)}")
    
    def save_benchmark(self, filename: str = "benchmark_results.json"):
        """Save all benchmark results."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Benchmark results saved to: {filepath}")
    
    def compare_methods(self):
        """Generate comparison report."""
        if not self.results:
            print("No results to compare")
            return
        
        print("\n" + "="*80)
        print("BENCHMARK COMPARISON")
        print("="*80)
        
        # Headers
        print(f"{'Method':<20} {'Modularity':<12} {'Cross-weight':<15} {'Coverage':<12} {'Performance':<12}")
        print("-"*80)
        
        # Results
        for result in self.results:
            method = result['method']
            mod = result.get('modularity', 0)
            cw = result.get('cross_weight', 0)
            cov = result.get('coverage', 0)
            perf = result.get('performance', 0)
            
            print(f"{method:<20} {mod:<12.4f} {cw:<15.2f} {cov:<12.4f} {perf:<12.4f}")
        
        print("="*80 + "\n")


def create_comparison_plot(spectral_results: Dict, other_results: Dict, 
                          output_path: str = "results/comparison.png"):
    """
    Create comparison plot between spectral and other methods.
    
    Args:
        spectral_results: Results from spectral clustering
        other_results: Results from other methods (METIS, BILP, etc.)
        output_path: Where to save the plot
    """
    import matplotlib.pyplot as plt
    
    methods = list(other_results.keys()) + ['Spectral']
    metrics_names = ['modularity', 'cross_weight', 'coverage', 'performance']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for idx, metric in enumerate(metrics_names):
        ax = axes[idx]
        values = []
        
        for method in methods:
            if method == 'Spectral':
                val = spectral_results['metrics'].get(metric, 0)
            else:
                val = other_results[method].get(metric, 0)
            values.append(val)
        
        ax.bar(methods, values, color=['tab:blue' if m != 'Spectral' else 'tab:orange' 
                                        for m in methods])
        ax.set_title(metric.capitalize())
        ax.set_ylabel('Value')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Comparison plot saved to: {output_path}")


if __name__ == "__main__":
    print("Spectral Interface for DecSel Framework")
    print("\nExample usage:")
    print("  from spectral_interface import SpectralDecomposer")
    print("  decomposer = SpectralDecomposer(n_clusters=3)")
    print("  partitions = decomposer.decompose(graph)")
