import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scipy.linalg import fractional_matrix_power

import sys
import os
sys.path.append(os.path.abspath("..")) # Dostosuj ścieżkę do modułów DecSel jeśli trzeba

from wdn import network_diagnoser
from gdec import decompose, graph_creation

from spectral_partition_decsel import spectral_clustering
input_file_name = '../Data_and_Models/examples/wdn/networks/GOY_v1.inp'
input_name = 'GOY_proof_paper_4_0_23'
input_folder = '../Data_and_Models/examples/wdn/mtes_results'
output_folder = '../Data_and_Models/examples/wdn/loop_results_bilp'
output_name = 'GOY_proof_paper'

n_subsystems = 3

nd = network_diagnoser.NetworkDiagnoser(input_file_name, input_name, input_folder, output_name, output_folder, mso=True)
nd.setup_decomposition(n_subsystems)

sm = nd.sm_data['model']
data = nd.sm_data
fmsos_eqs = [['e' + str(e) for e in el] for el in nd.msos]
n_faults = len(set(nd.fault_enc.values()))

g = graph_creation.graph_from_fmsos(fmsos_eqs, sm, data, multi_connections=True)
g.graph['edge_weight_attr'] = 'weight'

if 'e24' in g.nodes:
    g.remove_node('e24')

nx.draw_kamada_kawai(g)
print(f"Uruchamianie Twojej metody spectral_clustering dla k={n_subsystems}...")

result = spectral_clustering(
    G=g,
    k=n_subsystems,
    weighted=True,
    save_plot=True,    
    save_metrics=False,
    network_name="GOY_test"
)

label_dict = result['label_dict']
metrics = result['metrics']

print("\nMetryki Twojego podziału:")
for k, v in metrics.items():
    print(f"  {k}: {v}")

nodes_list = list(g.nodes())
parts_spectral = [label_dict[n] for n in nodes_list]

from spectral_partition_decsel import calculate_sum_of_cross_weights
cuts_spectral = calculate_sum_of_cross_weights(g, label_dict)

print(f"\nObliczony Cut Size (waga przecięć): {cuts_spectral}")
