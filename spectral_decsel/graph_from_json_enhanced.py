

import json
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from pathlib import Path
import os


def graph_from_json(json_name, models_dir="models"):
    """
    Convert from JSON to Graph representation (your original format).
    
    Args:
        json_name: Name of JSON file
        models_dir: Directory containing models
        
    Returns:
        tuple: (G, pos) where G is NetworkX graph and pos is layout
    """
    filepath = os.path.join(models_dir, json_name)
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    elements = data["model"]
    G = nx.Graph()

    # Add nodes with their parameters
    for e in elements:
        G.add_node(e, params=set(elements[e]))

    # Add edges based on common parameters
    for (e1, e2) in combinations(elements.keys(), 2):
        common = set(elements[e1]) & set(elements[e2])
        weight = len(common)
        if weight > 0:
            G.add_edge(e1, e2, weight=weight)

    # Create layout
    pos = nx.spring_layout(G, seed=42)
    
    return G, pos


def graph_from_json_with_plot(json_name, models_dir="models", output_dir="results"):
    """
    Convert from JSON and save visualization.
    
    Args:
        json_name: Name of JSON file
        models_dir: Directory containing models
        output_dir: Directory for output plot
        
    Returns:
        tuple: (G, pos) where G is NetworkX graph and pos is layout
    """
    G, pos = graph_from_json(json_name, models_dir)
    
    # Create visualization
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color="lightblue", 
            node_size=300, font_size=8, edge_color='gray', alpha=0.6)
    
    # Add edge weights
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
    
    output_path = os.path.join(output_dir, "graf.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Graph visualization saved to: {output_path}")
    print(f"Graph info: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    return G, pos


def graph_from_decsel_structural_model(filepath):
    """
    Load graph from DecSel structural model format.
    
    Args:
        filepath: Path to DecSel structural model JSON
        
    Returns:
        tuple: (G, metadata) where G is NetworkX graph and metadata is dict
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    G = nx.Graph()
    metadata = {}
    
    # Adapt based on actual DecSel format
    # This is a template - modify according to real structure
    
    if 'components' in data:
        for comp_id, comp_data in data['components'].items():
            G.add_node(comp_id, **comp_data)
    
    if 'sensors' in data:
        metadata['sensors'] = data['sensors']
    
    if 'edges' in data or 'relations' in data:
        edges_data = data.get('edges', data.get('relations', []))
        for edge in edges_data:
            source = edge.get('source', edge.get('from'))
            target = edge.get('target', edge.get('to'))
            weight = edge.get('weight', 1)
            if source and target:
                G.add_edge(source, target, weight=weight)
    
    # If no explicit edges, create based on shared attributes
    if G.number_of_edges() == 0 and 'components' in data:
        print("No explicit edges found, creating based on shared attributes...")
        components = data['components']
        for (c1, c2) in combinations(components.keys(), 2):
            # Example: connect if they share sensors or parameters
            shared = set(components[c1].get('sensors', [])) & \
                    set(components[c2].get('sensors', []))
            if shared:
                weight = len(shared)
                G.add_edge(c1, c2, weight=weight)
    
    return G, metadata


def graph_from_adjacency_matrix(filepath):
    """
    Load graph from adjacency matrix file.
    
    Args:
        filepath: Path to adjacency matrix (CSV or JSON)
        
    Returns:
        NetworkX graph
    """
    if filepath.endswith('.json'):
        with open(filepath, 'r') as f:
            data = json.load(f)
            adj_matrix = data.get('adjacency_matrix', data)
    else:  # CSV
        import numpy as np
        adj_matrix = np.loadtxt(filepath, delimiter=',')
    
    G = nx.from_numpy_array(adj_matrix)
    return G


def save_graph_to_json(G, output_path, format_type="custom"):
    """
    Save graph to JSON in specified format.
    
    Args:
        G: NetworkX graph
        output_path: Path to save JSON
        format_type: "custom" (your format) or "decsel"
    """
    if format_type == "custom":
        # Your original format
        model = {}
        for node in G.nodes():
            params = G.nodes[node].get('params', set())
            model[node] = list(params) if isinstance(params, set) else params
        
        data = {"model": model}
    
    elif format_type == "decsel":
        # DecSel format
        data = {
            "nodes": [{"id": node, **G.nodes[node]} for node in G.nodes()],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "weight": G[u][v].get('weight', 1)
                }
                for u, v in G.edges()
            ]
        }
    
    else:
        raise ValueError(f"Unknown format type: {format_type}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Graph saved to: {output_path}")


def convert_between_formats(input_path, output_path, 
                           input_format="custom", output_format="decsel"):
    """
    Convert graph between different JSON formats.
    
    Args:
        input_path: Input file path
        output_path: Output file path
        input_format: "custom" or "decsel"
        output_format: "custom" or "decsel"
    """
    # Load graph
    if input_format == "custom":
        G, _ = graph_from_json(os.path.basename(input_path), 
                              os.path.dirname(input_path))
    elif input_format == "decsel":
        G, _ = graph_from_decsel_structural_model(input_path)
    else:
        raise ValueError(f"Unknown input format: {input_format}")
    
    # Save in new format
    save_graph_to_json(G, output_path, output_format)
    
    print(f"Converted {input_format} → {output_format}")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")


def visualize_graph(G, output_path=None, title="Graph Visualization", 
                   layout="spring", node_colors=None, figsize=(12, 8)):
    """
    Create comprehensive graph visualization.
    
    Args:
        G: NetworkX graph
        output_path: Path to save image (optional)
        title: Plot title
        layout: Layout algorithm ("spring", "circular", "kamada_kawai")
        node_colors: List of colors or color map
        figsize: Figure size tuple
    """
    plt.figure(figsize=figsize)
    
    # Choose layout
    if layout == "spring":
        pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)
    elif layout == "circular":
        pos = nx.circular_layout(G)
    elif layout == "kamada_kawai":
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G, seed=42)
    
    # Determine node colors
    if node_colors is None:
        node_colors = "lightblue"
    
    # Draw graph
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='gray', alpha=0.5, width=1.5)
    
    # Draw edge weights
    edge_labels = nx.get_edge_attributes(G, 'weight')
    if edge_labels:
        nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {output_path}")
    else:
        plt.show()
    
    plt.close()
    
    return pos


def analyze_graph_structure(G):
    """
    Print comprehensive graph analysis.
    
    Args:
        G: NetworkX graph
    """
    print("\n" + "="*60)
    print("GRAPH STRUCTURE ANALYSIS")
    print("="*60)
    
    print(f"\nBasic Statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Density: {nx.density(G):.4f}")
    
    if G.number_of_edges() > 0:
        print(f"\nConnectivity:")
        print(f"  Is connected: {nx.is_connected(G)}")
        if nx.is_connected(G):
            print(f"  Diameter: {nx.diameter(G)}")
            print(f"  Average shortest path: {nx.average_shortest_path_length(G):.2f}")
        else:
            print(f"  Number of components: {nx.number_connected_components(G)}")
        
        print(f"\nCentrality (top 5 nodes):")
        degree_cent = nx.degree_centrality(G)
        top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:5]
        for node, cent in top_degree:
            print(f"    Node {node}: {cent:.4f}")
        
        print(f"\nClustering:")
        print(f"  Average clustering coefficient: {nx.average_clustering(G):.4f}")
        
        if 'weight' in next(iter(G.edges(data=True)))[2]:
            print(f"\nWeights:")
            weights = [G[u][v]['weight'] for u, v in G.edges()]
            print(f"  Min weight: {min(weights)}")
            print(f"  Max weight: {max(weights)}")
            print(f"  Average weight: {sum(weights)/len(weights):.2f}")
    
    print("="*60 + "\n")


class GraphConverter:
    """
    Unified interface for loading and converting graphs in different formats.
    """
    
    def __init__(self):
        self.supported_formats = ['custom', 'decsel', 'adjacency']
    
    def load(self, filepath, format_type='auto'):
        """
        Load graph from file, auto-detecting format if needed.
        
        Args:
            filepath: Path to graph file
            format_type: Format type or 'auto'
            
        Returns:
            tuple: (G, metadata)
        """
        if format_type == 'auto':
            format_type = self._detect_format(filepath)
        
        print(f"Loading graph from {filepath} (format: {format_type})")
        
        if format_type == 'custom':
            G, pos = graph_from_json(os.path.basename(filepath), 
                                    os.path.dirname(filepath))
            return G, {'pos': pos}
        
        elif format_type == 'decsel':
            return graph_from_decsel_structural_model(filepath)
        
        elif format_type == 'adjacency':
            G = graph_from_adjacency_matrix(filepath)
            return G, {}
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _detect_format(self, filepath):
        """Auto-detect file format."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        if 'model' in data:
            return 'custom'
        elif 'components' in data or 'nodes' in data:
            return 'decsel'
        elif 'adjacency_matrix' in data:
            return 'adjacency'
        else:
            raise ValueError("Cannot auto-detect format")
    
    def save(self, G, filepath, format_type='custom'):
        """Save graph to file in specified format."""
        save_graph_to_json(G, filepath, format_type)
    
    def convert(self, input_path, output_path, 
                input_format='auto', output_format='decsel'):
        """Convert between formats."""
        if input_format == 'auto':
            input_format = self._detect_format(input_path)
        
        convert_between_formats(input_path, output_path, 
                              input_format, output_format)


if __name__ == "__main__":
    print("Graph Conversion Utilities")
    print("\nThis module provides functions to:")
    print("  - Load graphs from various formats")
    print("  - Convert between formats")
    print("  - Visualize graphs")
    print("  - Analyze graph structure")
    print("\nExample usage:")
    print("  from graph_from_json import GraphConverter")
    print("  converter = GraphConverter()")
    print("  G, metadata = converter.load('model.json', format_type='auto')")
