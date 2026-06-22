import networkx as nx
import numpy as np
# Import Twojego zmodyfikowanego algorytmu
from sprectral_partition_decsel import spectral_clustering_for_decsel

class DecSelSpectral:
    def __init__(self, system_model, n_subsystems, cap_constraints=None):
        """
        system_model: Obiekt zawierający wszystkie MSO (Testy) i zmienne.
        n_subsystems: Liczba podsystemów (k).
        cap_constraints: Lista par równań, które muszą być razem (Communication & Privacy).
        """
        self.all_fmsos = system_model['fmsos'] # Lista wszystkich dostępnych MSO
        self.equations = system_model['equations'] # Lista wszystkich równań
        self.n_subsystems = n_subsystems
        self.cap_constraints = cap_constraints if cap_constraints else []
        
        # Parametr alpha z równania (2) w artykule: Cost = I + alpha * |S|
        self.alpha = 1.0 / (len(self.all_fmsos) + 1)
    def build_graph(self, selected_fmsos):
        """
        Krok 3 z Algorytmu 1: Budowa grafu zależności między równaniami.
        """
        G = nx.Graph()
        
        # POPRAWKA: Dodajemy tylko identyfikatory równań jako węzły
        # self.equations to lista słowników, więc wyciągamy 'id'
        equation_ids = [eq['id'] for eq in self.equations]
        G.add_nodes_from(equation_ids)
        
        # Dodaj krawędzie na podstawie wybranych testów (FMSO)
        for fmso in selected_fmsos:
            eqs = fmso['equations']
            # eqs to lista słowników równań wewnątrz danego FMSO
            for i in range(len(eqs)):
                for j in range(i + 1, len(eqs)):
                    # Wyciągamy ID równań
                    e1_id = eqs[i]['id']
                    e2_id = eqs[j]['id']
                    
                    # Oblicz liczbę wspólnych zmiennych
                    # Używamy zbiorów (sets) do obliczenia części wspólnej
                    vars1 = set(eqs[i]['vars'])
                    vars2 = set(eqs[j]['vars'])
                    shared_vars = len(vars1 & vars2)
                    
                    if shared_vars > 0:
                        if G.has_edge(e1_id, e2_id):
                            G[e1_id][e2_id]['weight'] += shared_vars
                        else:
                            G.add_edge(e1_id, e2_id, weight=shared_vars)

        # Obsługa ograniczeń CaP (Communication and Privacy)
        # Zakładamy, że cap_constraints to lista krotek (id1, id2)
        if G.edges():
            max_weight = max([d['weight'] for u, v, d in G.edges(data=True)])
        else:
            max_weight = 1
            
        cap_weight = max_weight * len(self.equations) * 10
        
        for e1_id, e2_id in self.cap_constraints:
            if G.has_node(e1_id) and G.has_node(e2_id):
                if G.has_edge(e1_id, e2_id):
                    G[e1_id][e2_id]['weight'] += cap_weight
                else:
                    G.add_edge(e1_id, e2_id, weight=cap_weight)
                
        return G

    def select_tests_bilp(self, decomposition):
        """
        Krok 5 z Algorytmu 1: Selekcja testów (BILP).
        Minimalizujemy liczbę przecięć (cuts) przy zachowaniu diagnozowalności.
        Tutaj musisz użyć solvera (np. Gurobi, CPLEX lub scipy.optimize.milp).
        
        Ponieważ nie mam Twojego silnika BILP, to jest PLACEHOLDER.
        W prawdziwym DecSel tutaj następuje optymalizacja.
        """
        # TODO: Tu podłączasz logikę z pliku selection.py z repozytorium DecSel
        # lub własną implementację BILP wg równań (4)-(7) z artykułu.
        
        print("--- Symulacja kroku selekcji (wymaga solvera BILP) ---")
        # Zwracamy losowy podzbiór dla demonstracji przepływu
        import random
        return random.sample(self.all_fmsos, k=min(len(self.all_fmsos), 20))

    def calculate_interconnections(self, selection, decomposition):
        """Oblicza I_S^D (koszt interkoneksji) zgodnie z równaniem (1)."""
        cost = 0
        for fmso in selection:
            # Sprawdź zmienne współdzielone między podsystemami dla tego testu
            # To jest uproszczona logika
            pass 
        return cost

    def run(self):
        """Główna pętla DecSel (Algorytm 1 z artykułu)"""
        
        # 1. Inicjalizacja: S_0 = Wszystkie FMSO
        current_selection = self.all_fmsos
        k = 0
        
        prev_cost = float('inf')
        
        while True:
            print(f"\n=== Iteracja k={k} ===")
            
            # 2. Budowa grafu G_k na podstawie S_k
            print("Budowanie grafu zależności...")
            G_k = self.build_graph(current_selection)
            
            # 3. DEKOMPOZYCJA (Tutaj wchodzi Twój algorytm Spektralny!)
            # Zamiast METIS używamy Twojego spectral_clustering
            print(f"Uruchamianie Spectral Clustering dla k={self.n_subsystems}...")
            decomposition = spectral_clustering_for_decsel(
                G_k, 
                k=self.n_subsystems, 
                weight='weight' # Ważne: używamy wag zdefiniowanych w build_graph
            )
            
            # Wypisz statystyki podziału
            clusters = set(decomposition.values())
            print(f"Znaleziono podział na {len(clusters)} klastrów.")
            
            # 4. SELEKCJA (Wybór najlepszych MSO dla tego podziału)
            print("Optymalizacja selekcji testów (BILP)...")
            new_selection = self.select_tests_bilp(decomposition)
            
            # 5. Sprawdzenie warunku stopu
            # Wg artykułu: stop gdy koszt interkoneksji się nie zmienia
            # Tutaj uproszczone porównanie długości zbiorów dla demonstracji
            if len(new_selection) == len(current_selection) and k > 0:
                print("Algorytm zbiegł (brak zmian w selekcji).")
                break
                
            current_selection = new_selection
            k += 1
            if k > 10: # Bezpiecznik
                print("Osiągnięto limit iteracji.")
                break
                
        return decomposition, current_selection

# --- Przykładowe użycie (Symulacja danych) ---
if __name__ == "__main__":
    # Symulacja danych wejściowych
    fake_equations = [{'id': i, 'vars': [i, (i+1)%20]} for i in range(20)]
    fake_fmsos = [{'equations': [fake_equations[i], fake_equations[(i+1)%20]]} for i in range(20)]
    
    system_data = {
        'equations': fake_equations,
        'fmsos': fake_fmsos
    }
    
    # Ograniczenia CaP
    cap = [(0, 1), (5, 6)] 
    
    # Inicjalizacja algorytmu
    decsel = DecSelSpectral(system_data, n_subsystems=3, cap_constraints=cap)
    
    # POPRAWIONA LINIA (usunięto zbędną spację przed final_part)
    final_part, final_tests = decsel.run()
    
    print("\nOstateczny podział:", final_part)
    print(f"Wybrano {len(final_tests)} testów.")
