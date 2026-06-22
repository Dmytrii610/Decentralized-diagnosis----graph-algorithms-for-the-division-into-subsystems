"""
Complete integration workflow demonstration.
This script shows the full process of integrating your spectral method with DecSel.
"""

import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def setup_directories():
    """Create necessary directory structure."""
    dirs = [
        "models",
        "results/spectral",
        "results/comparison",
        "results/benchmark",
        "data/processed"
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    
    print("Directory structure created")


def create_sample_models():
    """Create sample models in both your format and DecSel-like format."""
    
    # My model
    custom_model = {
        "model": {
            "Sensor1": ["temperature", "pressure", "flow"],
            "Sensor2": ["pressure", "flow", "level"],
            "Sensor3": ["flow", "level", "valve_state"],
            "Pump1": ["pressure", "flow", "power"],
            "Pump2": ["pressure", "level", "power"],
            "Valve1": ["flow", "valve_state", "position"],
            "Valve2": ["level", "valve_state", "position"],
            "Tank1": ["level", "temperature", "volume"],
            "Tank2": ["level", "pressure", "volume"]
        }
    }
    
    with open("models/water_network_custom.json", 'w') as f:
        json.dump(custom_model, f, indent=2)
    
    print("✓ Sample models created")


def workflow_step_1_load_data():
    """
    STEP 1: Load and prepare data
    """
    print("\n" + "="*80)
    print("STEP 1: LOADING DATA")
    print("="*80 + "\n")
    
    from graph_from_json_enhanced import GraphConverter
    
    converter = GraphConverter()
    
    # Load format
    G, metadata = converter.load("models/water_network_custom.json", format_type='custom')
    
    print(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Analyze structure
    from graph_from_json_enhanced import analyze_graph_structure
    analyze_graph_structure(G)
    
    return G, metadata


def workflow_step_2_run_spectral(G):
    """
    STEP 2: Run spectral clustering
    """
    print("\n" + "="*80)
    print("STEP 2: SPECTRAL CLUSTERING")
    print("="*80 + "\n")
    
    from spectral_partition_decsel import spectral_clustering_range
    
    # Test multiple k values
    k_values = [2, 3, 4, 5]
    
    results = {}
    for k in k_values:
        print(f"\n--- Testing k={k} ---")
        from spectral_partition_decsel import spectral_clustering
        
        result = spectral_clustering(
            G,
            k=k,
            network_name=f"water_network_k{k}",
            output_dir="results/spectral",
            save_plot=True,
            save_metrics=True,
            weighted=True
        )
        
        results[k] = result
        
        print(f"Modularity: {result['metrics']['modularity']:.4f}")
        print(f"Cross-weight: {result['metrics']['cross_weight']:.2f}")
    
    return results


def workflow_step_3_compare_methods(G, spectral_results):
    """
    STEP 3: Compare with other methods
    """
    print("\n" + "="*80)
    print("STEP 3: COMPARING WITH OTHER METHODS")
    print("="*80 + "\n")
    
    # Run Louvain for comparison
    import community as community_louvain
    
    louvain_partition = community_louvain.best_partition(G, weight='weight')
    louvain_communities = []
    for comm_id in set(louvain_partition.values()):
        louvain_communities.append(set([n for n in louvain_partition if louvain_partition[n] == comm_id]))
    
    louvain_modularity = nx.algorithms.community.quality.modularity(G, louvain_communities)
    
    print(f"Louvain method:")
    print(f"  Communities: {len(louvain_communities)}")
    print(f"  Modularity: {louvain_modularity:.4f}")
    
    # Compare results
    print(f"\nComparison for k=3:")
    if 3 in spectral_results:
        spectral_mod = spectral_results[3]['metrics']['modularity']
        print(f"  Spectral modularity:  {spectral_mod:.4f}")
        print(f"  Louvain modularity:   {louvain_modularity:.4f}")
        print(f"  Difference:           {abs(spectral_mod - louvain_modularity):.4f}")
    
    return {
        'louvain': {
            'partition': louvain_partition,
            'communities': louvain_communities,
            'modularity': louvain_modularity
        }
    }


def workflow_step_4_visualize_comparison(G, spectral_results, other_results):
    """
    STEP 4: Create comparison visualizations
    """
    print("\n" + "="*80)
    print("STEP 4: CREATING VISUALIZATIONS")
    print("="*80 + "\n")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    pos = nx.spring_layout(G, seed=42)
    
    for idx, k in enumerate([2, 3, 4]):
        if k not in spectral_results:
            continue
        
        ax = axes[0, idx]
        result = spectral_results[k]
        
        colors = []
        for node in G.nodes():
            cluster = result['label_dict'][node]
            colors.append(plt.cm.tab10(cluster / k))
        
        nx.draw(G, pos, ax=ax, node_color=colors, with_labels=True,
                node_size=400, font_size=7, edge_color='gray', alpha=0.6)
        
        mod = result['metrics']['modularity']
        ax.set_title(f"Spectral k={k}\nModularity: {mod:.3f}")
    
    ax = axes[1, 0]
    louvain_partition = other_results['louvain']['partition']
    colors = [plt.cm.tab10(louvain_partition[node] / len(set(louvain_partition.values()))) 
              for node in G.nodes()]
    
    nx.draw(G, pos, ax=ax, node_color=colors, with_labels=True,
            node_size=400, font_size=7, edge_color='gray', alpha=0.6)
    
    louvain_mod = other_results['louvain']['modularity']
    ax.set_title(f"Louvain\nModularity: {louvain_mod:.3f}")
    
    ax = axes[1, 1]
    methods = ['Spectral\nk=2', 'Spectral\nk=3', 'Spectral\nk=4', 'Louvain']
    modularities = [
        spectral_results[2]['metrics']['modularity'],
        spectral_results[3]['metrics']['modularity'],
        spectral_results[4]['metrics']['modularity'],
        louvain_mod
    ]
    
    bars = ax.bar(methods, modularities, color=['tab:blue', 'tab:blue', 'tab:blue', 'tab:orange'])
    ax.set_ylabel('Modularity')
    ax.set_title('Modularity Comparison')
    ax.set_ylim([0, 1])
    ax.grid(True, alpha=0.3)
    
    for bar, val in zip(bars, modularities):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}', ha='center', va='bottom')
    
    ax = axes[1, 2]
    cross_weights = [
        spectral_results[2]['metrics']['cross_weight'],
        spectral_results[3]['metrics']['cross_weight'],
        spectral_results[4]['metrics']['cross_weight']
    ]
    
    ax.bar(['k=2', 'k=3', 'k=4'], cross_weights, color='tab:red')
    ax.set_ylabel('Cross-edge Weight')
    ax.set_title('Cross-edge Weights (Spectral)')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = "results/comparison/complete_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Comparison visualization saved to: {output_path}")


def workflow_step_5_generate_report(spectral_results, other_results):
    """
    STEP 5: Generate comprehensive report
    """
    print("\n" + "="*80)
    print("STEP 5: GENERATING REPORT")
    print("="*80 + "\n")
    
    report = {
        "experiment": "Spectral Clustering - DecSel Integration",
        "date": "2026-01-27",
        "network": "Water Distribution Network (Custom Format)",
        "methods_tested": ["Spectral (k=2,3,4,5)", "Louvain"],
        "results": {
            "spectral": {},
            "louvain": other_results['louvain']['modularity']
        }
    }
    
    for k, result in spectral_results.items():
        report["results"]["spectral"][f"k_{k}"] = result['metrics']
    
    report_path = "results/comparison/integration_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Report saved to: {report_path}")
    
    print("\n" + "-"*80)
    print("SUMMARY")
    print("-"*80 + "\n")
    
    print("Spectral Clustering Results:")
    for k, result in spectral_results.items():
        metrics = result['metrics']
        print(f"  k={k}:")
        print(f"    Modularity:   {metrics['modularity']:.4f}")
        print(f"    Coverage:     {metrics['coverage']:.4f}")
        print(f"    Performance:  {metrics['performance']:.4f}")
        print(f"    Cross-weight: {metrics['cross_weight']:.2f}")
    
    print(f"\nLouvain Results:")
    print(f"  Modularity: {other_results['louvain']['modularity']:.4f}")
    
    best_k = max(spectral_results.keys(), 
                 key=lambda k: spectral_results[k]['metrics']['modularity'])
    print(f"\nBest k (by modularity): {best_k}")
    print(f"  Modularity: {spectral_results[best_k]['metrics']['modularity']:.4f}")


def create_integration_checklist():
    """
    Create a checklist for DecSel integration.
    """
    checklist = """
# INTEGRATION CHECKLIST

## Pre-integration
- [ ] Clone DecSel repository
- [ ] Install all dependencies (pip install -r requirements.txt)
- [ ] Install Gurobi and set up license (for BILP)
- [ ] Install METIS library
- [ ] Test DecSel examples (loop_GOY.py, etc.)

## File Placement
- [ ] Copy spectral_partition_decsel.py to DecSel/spectral/
- [ ] Copy spectral_interface.py to DecSel/spectral/
- [ ] Copy graph_from_json_enhanced.py to DecSel/utils/
- [ ] Create __init__.py files in new directories

## Code Integration
- [ ] Import spectral module in loop_GOY.py
- [ ] Add spectral method to decomposition comparison
- [ ] Integrate with existing metrics system
- [ ] Add spectral option to command-line arguments

## Testing
- [ ] Test with simple graphs
- [ ] Test with GOY network data
- [ ] Test with other DecSel networks
- [ ] Compare results with METIS and BILP
- [ ] Validate metrics calculations

## Documentation
- [ ] Update README with spectral method info
- [ ] Add docstrings to all functions
- [ ] Create usage examples
- [ ] Document performance comparison

## Validation
- [ ] Run full benchmark suite
- [ ] Compare with published results
- [ ] Check computational efficiency
- [ ] Verify result reproducibility

## Optional Enhancements
- [ ] Add parallel processing for multiple k values
- [ ] Implement adaptive k selection
- [ ] Add visualization improvements
- [ ] Create interactive dashboard
- [ ] Write paper/report on integration

## Final Steps
- [ ] Clean up temporary files
- [ ] Organize output directory
- [ ] Create comprehensive examples
- [ ] Submit pull request (if contributing to DecSel)
"""
    
    with open("INTEGRATION_CHECKLIST.md", 'w') as f:
        f.write(checklist)
    
    print("Integration checklist created: INTEGRATION_CHECKLIST.md")


def main():
    """
    Run complete integration workflow.
    """
    print("="*80)
    print("SPECTRAL CLUSTERING - DECSEL INTEGRATION WORKFLOW")
    print("="*80)
    
    print("\nThis script demonstrates the complete workflow for integrating")
    print("your spectral clustering method with the DecSel framework.")
    
    # Setup
    print("\n[Setup]")
    setup_directories()
    create_sample_models()
    
    try:
        # Step 1: Load data
        G, metadata = workflow_step_1_load_data()
        
        # Step 2: Run spectral clustering
        spectral_results = workflow_step_2_run_spectral(G)
        
        # Step 3: Compare with other methods
        other_results = workflow_step_3_compare_methods(G, spectral_results)
        
        # Step 4: Visualize comparisons
        workflow_step_4_visualize_comparison(G, spectral_results, other_results)
        
        # Step 5: Generate report
        workflow_step_5_generate_report(spectral_results, other_results)
        
        # Create integration checklist
        create_integration_checklist()
        
        print("\n" + "="*80)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("="*80)
        
        print("\nGenerated files:")
        print("  - models/water_network_custom.json")
        print("  - results/spectral/*.png (visualizations)")
        print("  - results/spectral/*.json (metrics)")
        print("  - results/comparison/complete_comparison.png")
        print("  - results/comparison/integration_report.json")
        print("  - INTEGRATION_CHECKLIST.md")
        
        
    except Exception as e:
        print(f"\nError during workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
