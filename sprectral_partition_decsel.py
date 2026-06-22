import networkx as nx
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from scipy.sparse.linalg import eigsh
from collections import defaultdict
import numpy as np

# Funkcja pomocnicza z Twojego kodu (bez zmian)
def ensure_label_dict(labels, nodes):
    label_dict = {}
    for n, lab in zip(nodes, labels):
        label_dict[n] = int(lab)
    comms = defaultdict(set)
    for n, lab in label_dict.items():
        comms[lab].add(n)
    communities = list(comms.values())
    return label_dict, communities

def spectral_clustering_for_decsel(G, k, weight='weight'):
    """
    Wersja algorytmu spektralnego przystosowana do DecSel.
    Zwraca słownik partycji: {node_id: cluster_id}
    """
    nodes_order = list(G.nodes())
    
    # 1. Obliczenie Laplacianu (z uwzględnieniem wag z DecSel!)
    # W DecSel wagi krawędzi oznaczają liczbę wspólnych zmiennych lub wymuszenia CaP.
    # Upewnij się, że graf wejściowy ma atrybut wagi (domyślnie 'weight').
    try:
        L = nx.laplacian_matrix(G, nodelist=nodes_order, weight=weight)
        L = L.asfptype()
    except Exception as e:
        print(f"Błąd tworzenia macierzy Laplace'a: {e}")
        # Fallback dla małych grafów lub błędów
        return {n: 0 for n in nodes_order}

    n = L.shape[0]
    
    # Zabezpieczenie dla k
    if k >= n:
        k = max(2, n - 1)
    
    # 2. Wektory własne (Twoja logika z eigsh SM)
    # k wektorów dla k klastrów (lub k-1 dla bisekcji, ale sklearn KMeans lubi k wymiarów)
    try:
        vals, vecs = eigsh(L, k=k, which='SM')
    except Exception as e:
        # Fallback jeśli eigsh zawiedzie (np. graf niespójny)
        print(f"Eigsh failed, using dense fallback: {e}")
        vals, vecs = np.linalg.eigh(L.todense())
        vecs = vecs[:, :k]

    # 3. K-Means
    # Używamy wektorów jako cech
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels_array = kmeans.fit_predict(vecs)

    # 4. Przygotowanie wyniku dla DecSel
    label_dict, _ = ensure_label_dict(labels_array, nodes_order)
    
    return label_dict
