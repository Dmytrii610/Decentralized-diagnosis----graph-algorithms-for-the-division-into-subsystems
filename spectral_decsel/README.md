# Integracja Spektralnego Podziału Grafów z DecSel

## Przegląd

Ten pakiet zawiera wszystkie niezbędne pliki do integracji Twojej metody spektralnego podziału grafów z frameworkiem [DecSel](https://github.com/asztyber/DecSel).

DecSel to system do selekcji testów diagnostycznych dla rozproszonych systemów, który wykorzystuje dekompozycję grafów. Twoja metoda spektralna oferuje alternatywne podejście do dekompozycji z dodatkowymi metrykami jakości.

## Zawartość Pakietu

### Główne Pliki

1. **INTEGRATION_GUIDE.md** - Szczegółowy przewodnik integracji
2. **spectral_partition_decsel.py** - Ulepszona wersja Twojej metody spektralnej
3. **spectral_interface.py** - Adapter do integracji z DecSel
4. **graph_from_json_enhanced.py** - Rozszerzona obsługa różnych formatów
5. **run_examples.py** - Przykłady użycia
6. **complete_workflow.py** - Kompletny workflow demonstracyjny

### Twoje Oryginalne Pliki

- `spectral_partition.py` - Twoja oryginalna implementacja
- `graph_from_json.py` - Twoja konwersja JSON → graf
- `plot_metrics_combined.py` - Twoje wizualizacje metryk

## Szybki Start

### 1. Instalacja Zależności

```bash
pip install networkx matplotlib scikit-learn scipy numpy python-louvain
```

### 2. Testowanie Lokalnie (bez DecSel)

```bash
# Uruchom przykłady demonstracyjne
python run_examples.py

# Lub kompletny workflow
python complete_workflow.py
```

### 3. Integracja z DecSel

```bash
# Sklonuj DecSel
git clone https://github.com/asztyber/DecSel.git
cd DecSel

# Zainstaluj zależności DecSel
pip install -r requirements.txt

# Skopiuj pliki spektralne
mkdir -p spectral utils
cp ../spectral_partition_decsel.py spectral/
cp ../spectral_interface.py spectral/
cp ../graph_from_json_enhanced.py utils/

# Utwórz pliki __init__.py
touch spectral/__init__.py
touch utils/__init__.py
```

## Struktura Katalogów

### Docelowa Struktura w DecSel

```
DecSel/
├── spectral/
│   ├── __init__.py
│   ├── spectral_partition_decsel.py    # Twoja metoda
│   └── spectral_interface.py           # Adapter
├── utils/
│   ├── __init__.py
│   └── graph_from_json_enhanced.py     # Konwersje
├── data/                                # Dane sieci wodnych
├── results/                             # Wyniki eksperymentów
├── loop_GOY.py                         # Główna pętla (MODYFIKUJ)
└── decomposition_only_GOY.py           # Dekompozycja (MODYFIKUJ)
```

## Kluczowe Cechy

### Metody Spektralnej

- **Algorytm**: Spektralna dekompozycja Laplace'a + KMeans
- **Parametry**: 
  - `k` - liczba klastrów
  - `weighted` - czy używać wag krawędzi
  - `random_state` - seed dla reprodukowalności

### Metryki Jakości

Twoja metoda oblicza:

1. **Cross-weight** - suma wag krawędzi między klastrami (minimalizuj)
2. **Modularity** - modularność podziału (maksymalizuj, zakres 0-1)
3. **Coverage** - pokrycie (maksymalizuj, zakres 0-1)
4. **Performance** - wydajność (maksymalizuj, zakres 0-1)
5. **Communication cost** - liczba krawędzi między klastrami

### Porównanie z Innymi Metodami

DecSel zawiera:
- **METIS** - hierarchiczna dekompozycja
- **BILP** - optymalizacja całkowitoliczbowa (wymaga Gurobi)
- **Louvain** - detekcja społeczności

Twoja metoda oferuje:
- Solidne podstawy teoretyczne (algebra spektralna)
- Kontrolowaną liczbę partycji
- Dodatkowe metryki diagnostyczne
- Łatwą interpretację wyników

## Przykłady Użycia

### Przykład 1: Podstawowe Użycie

```python
from spectral_partition_decsel import spectral_clustering
import networkx as nx

# Wczytaj lub stwórz graf
G = nx.karate_club_graph()

# Dodaj wagi (opcjonalnie)
for u, v in G.edges():
    G[u][v]['weight'] = 1

# Uruchom spektralny podział
result = spectral_clustering(
    G, 
    k=3,
    network_name="my_network",
    output_dir="results",
    save_plot=True,
    save_metrics=True
)

# Wyniki
print(f"Communities: {result['communities']}")
print(f"Modularity: {result['metrics']['modularity']:.4f}")
```

### Przykład 2: Adapter DecSel

```python
from spectral_interface import SpectralDecomposer

# Inicjalizuj
decomposer = SpectralDecomposer(n_clusters=3, weighted=True)

# Dekompozycja
communities = decomposer.decompose(G, network_name="test")

# Metryki
metrics = decomposer.get_metrics()
print(metrics)
```

### Przykład 3: Porównanie Metod

```python
from spectral_interface import SpectralBenchmark

# Stwórz benchmark
benchmark = SpectralBenchmark(output_dir="results/benchmark")

# Uruchom dla różnych k
benchmark.run_spectral(G, k_values=[2, 3, 4, 5], network_name="my_net")

# Porównaj
benchmark.compare_methods()
benchmark.save_benchmark()
```

### Przykład 4: Twój Format JSON

```python
from graph_from_json_enhanced import graph_from_json

# Wczytaj z Twojego formatu
G, pos = graph_from_json("model.json", models_dir="models")

# Uruchom spektralny podział
result = spectral_clustering(G, k=3)
```

## Integracja z loop_GOY.py

Dodaj do `loop_GOY.py`:

```python
from spectral.spectral_interface import SpectralDecomposer

# W funkcji głównej, po innych metodach dekompozycji:

# Spectral decomposition
print("\n--- Spectral Decomposition ---")
for k in k_values:
    spectral_dec = SpectralDecomposer(n_clusters=k, weighted=True)
    communities = spectral_dec.decompose(
        structural_graph,
        network_name=f"GOY_spectral_k{k}",
        output_dir="results/spectral",
        save_plot=True,
        save_metrics=True
    )
    
    metrics = spectral_dec.get_metrics()
    print(f"k={k}: Modularity={metrics['modularity']:.4f}, "
          f"Cross-weight={metrics['cross_weight']:.2f}")
    
    # Zapisz do porównania
    all_results['spectral'][k] = metrics
```

## Format Danych

### Twój Format (Custom)

```json
{
  "model": {
    "Component1": ["param1", "param2", "param3"],
    "Component2": ["param2", "param3", "param4"],
    "Component3": ["param3", "param4", "param5"]
  }
}
```

### Format DecSel (Przykład)

```json
{
  "components": {
    "C1": {"type": "sensor", "sensors": ["S1", "S2"]},
    "C2": {"type": "pump", "sensors": ["S2", "S3"]}
  },
  "relations": [
    {"source": "C1", "target": "C2", "weight": 2}
  ]
}
```

Oba formaty są obsługiwane przez `GraphConverter`.

## Wyniki i Wizualizacje

Po uruchomieniu otrzymasz:

### Pliki JSON z Metrykami

```json
{
  "method": "Spectral",
  "cross_weight": 14.0,
  "modularity": 0.2456,
  "coverage": 0.7891,
  "performance": 0.8234,
  "clusters": 3,
  "weighted": true
}
```

### Wizualizacje PNG

- Grafy z kolorowaniem klastrów
- Wykresy porównawcze metryk
- Wizualizacje struktury grafu

### Raporty Porównawcze

- Tabele z metrykami dla różnych k
- Porównanie z METIS/BILP/Louvain
- Statystyki wydajności

## Testowanie

### Test 1: Proste Grafy

```bash
python run_examples.py
```

To uruchomi 6 przykładów demonstracyjnych.

### Test 2: Workflow Kompletny

```bash
python complete_workflow.py
```

To przeprowadzi pełny workflow integracji.

### Test 3: Z Danymi DecSel

Po integracji z DecSel:

```bash
cd DecSel
python structural_model_GOY.py  # Generuj model
python loop_GOY.py              # Uruchom z Twoją metodą
```

## Rozwiązywanie Problemów

### Problem: ModuleNotFoundError

**Rozwiązanie**: Sprawdź czy pliki `__init__.py` istnieją w katalogach `spectral/` i `utils/`.

```bash
touch spectral/__init__.py
touch utils/__init__.py
```

### Problem: "k must be smaller than number of nodes"

**Rozwiązanie**: Graf ma za mało węzłów. Zmniejsz `k` lub użyj większego grafu.

### Problem: Import errors z DecSel

**Rozwiązanie**: Upewnij się, że DecSel jest w PYTHONPATH:

```bash
export PYTHONPATH="/path/to/DecSel:$PYTHONPATH"
```

### Problem: Gurobi license error

**Rozwiązanie**: BILP wymaga Gurobi, ale Twoja metoda nie. Możesz pominąć BILP w testach.

## Wydajność

### Złożoność Czasowa

- **Spektralna dekompozycja**: O(n³) dla małych grafów, O(n·k²) dla dużych (sparse)
- **METIS**: O(n·log(n))
- **BILP**: NP-trudny (powolny dla dużych grafów)

### Rekomendacje

- Dla n < 1000: wszystkie metody działają dobrze
- Dla n > 1000: rozważ sparse eigensolver
- Dla n > 10000: METIS może być szybszy

## Dalsza Rozbudowa

### Możliwe Ulepszenia

1. **Automatyczny wybór k**
   - Metoda gap statistic
   - Silhouette analysis
   - Elbow method

2. **Równoległe przetwarzanie**
   - Parallel KMeans
   - Multi-threading dla wielu k

3. **Interaktywna wizualizacja**
   - Plotly/Dash dashboard
   - Interactive graph exploration

4. **Dodatkowe metryki**
   - Normalized Cut
   - Conductance
   - Edge expansion

## Publikacja i Cytowanie

Jeśli używasz tej integracji w badaniach:

**DecSel:**
```
Anna Sztyber-Betley, Elodie Chanthery, Louise Travé-Massuyès, 
Carlos Gustavo Pérez-Zuñiga. "Diagnosis test selection for 
distributed systems under communication and privacy constraints", 
Applied Intelligence (submitted).
```

**Spektralna dekompozycja:**
```
Von Luxburg, U. (2007). A tutorial on spectral clustering. 
Statistics and Computing, 17(4), 395-416.
```

## Wsparcie i Kontakt

### Problemy z Integracją

1. Sprawdź INTEGRATION_GUIDE.md dla szczegółów
2. Uruchom przykłady testowe
3. Sprawdź sekcję Troubleshooting

### Contributing do DecSel

Jeśli chcesz dodać swoją metodę do głównego repo DecSel:

1. Fork repozytorium
2. Dodaj swoją metodę
3. Stwórz Pull Request
4. Opisz zmiany i wyniki testów

## Licencja

- Twój kod: [Twoja licencja]
- DecSel: MIT License
- Zależności: sprawdź odpowiednie licencje

## Changelog

### v1.0 (2026-01-27)
- Początkowa integracja
- Wsparcie dla formatów custom i DecSel
- Pełny zestaw metryk
- Przykłady i dokumentacja

## Bibliografia

1. DecSel: https://github.com/asztyber/DecSel
2. Spectral Clustering Tutorial: Von Luxburg (2007)
3. NetworkX: https://networkx.org/
4. METIS: http://glaros.dtc.umn.edu/gkhome/metis/metis/overview

## Status

✅ Gotowe do użycia
✅ Przetestowane na przykładach
⏳ Oczekuje na testy z pełnymi danymi DecSel
⏳ Oczekuje na porównanie wyników z METIS/BILP
