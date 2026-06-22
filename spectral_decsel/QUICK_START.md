# Quick Start Guide - Integracja Spektralna + DecSel

## 5-Minutowy Start

### Krok 1: Pobierz Pliki (1 min)

Masz już wszystkie potrzebne pliki w pakiecie integracyjnym.

### Krok 2: Zainstaluj Zależności (2 min)

```bash
pip install networkx matplotlib scikit-learn scipy numpy python-louvain
```

### Krok 3: Przetestuj Lokalnie (2 min)

```bash
# Test podstawowy
python complete_workflow.py

# Sprawdź wyniki
ls -R results/
```

**Gotowe!** Powinieneś zobaczyć:
- Wykresy w `results/spectral/`
- Metryki w plikach JSON
- Raport porównawczy

---

## 30-Minutowa Integracja z DecSel

### Krok 1: Przygotuj DecSel (10 min)

```bash
# Sklonuj repozytorium
git clone https://github.com/asztyber/DecSel.git
cd DecSel

# Zainstaluj zależności
pip install -r requirements.txt

# (Opcjonalnie) Zainstaluj Gurobi dla BILP
# Instrukcje: https://www.gurobi.com/downloads/

# (Opcjonalnie) Zainstaluj METIS
# Instrukcje: https://github.com/KarypisLab/METIS
```

### Krok 2: Dodaj Spektralny Moduł (5 min)

```bash
# Utwórz strukturę katalogów
mkdir -p DecSel/spectral
mkdir -p DecSel/utils

# Skopiuj pliki
cp spectral_partition_decsel.py DecSel/spectral/
cp spectral_interface.py DecSel/spectral/
cp graph_from_json_enhanced.py DecSel/utils/

# Utwórz __init__.py
touch DecSel/spectral/__init__.py
touch DecSel/utils/__init__.py
```

### Krok 3: Uruchom Test (5 min)

```bash
cd DecSel

# Wygeneruj model strukturalny GOY
python structural_model_GOY.py

# To powinno stworzyć plik w data/
```

### Krok 4: Dodaj do loop_GOY.py (10 min)

Otwórz `DecSel/loop_GOY.py` i dodaj:

```python
# Na początku pliku, po innych importach:
from spectral.spectral_interface import SpectralDecomposer

# W funkcji głównej, przed lub po innych metodach dekompozycji:
def run_spectral_decomposition(G, k_values):
    """Run spectral decomposition for different k values."""
    print("\n" + "="*60)
    print("SPECTRAL DECOMPOSITION")
    print("="*60)
    
    results = {}
    for k in k_values:
        print(f"\nRunning spectral with k={k}...")
        decomposer = SpectralDecomposer(n_clusters=k, weighted=True)
        
        communities = decomposer.decompose(
            G,
            network_name=f"GOY_k{k}",
            output_dir="results/spectral",
            save_plot=True,
            save_metrics=True
        )
        
        metrics = decomposer.get_metrics()
        results[k] = metrics
        
        print(f"  Modularity: {metrics['modularity']:.4f}")
        print(f"  Cross-weight: {metrics['cross_weight']:.2f}")
    
    return results

# Następnie w main():
# Po wczytaniu grafu G
k_values = [2, 3, 4, 5]
spectral_results = run_spectral_decomposition(G, k_values)
```

Zapisz i uruchom:

```bash
python loop_GOY.py
```

---

## Szybkie Porównanie Wyników

Po uruchomieniu, sprawdź:

```bash
# Zobacz wszystkie wyniki spektralne
ls results/spectral/

# Zobacz metryki
cat results/spectral/GOY_k3_spectral_k3_metrics.json

# Zobacz wizualizacje
open results/spectral/GOY_k3_spectral_k3.png  # Mac
xdg-open results/spectral/GOY_k3_spectral_k3.png  # Linux
```

---

## Przykładowa Interpretacja Wyników

### Dobre Wyniki (dla k=3):

```json
{
  "modularity": 0.45,      // > 0.3 to dobry wynik
  "cross_weight": 12.5,     // Im niższe, tym lepiej
  "coverage": 0.82,         // > 0.8 to świetnie
  "performance": 0.89       // > 0.8 to świetnie
}
```

### Co to znaczy?

- **Modularity**: Czy klastry są dobrze odseparowane?
  - < 0.3: słabe
  - 0.3-0.5: dobre
  - > 0.5: bardzo dobre

- **Cross-weight**: Ile komunikacji między klastrami?
  - Im niższe, tym lepiej dla systemów rozproszonych

- **Coverage**: Czy krawędzie są wewnątrz klastrów?
  - > 0.8: bardzo dobre

- **Performance**: Ogólna jakość podziału
  - > 0.8: bardzo dobre

---

## Porównanie z Innymi Metodami

| Metoda    | Modularity | Cross-weight | Szybkość | Kontrola k |
|-----------|------------|--------------|----------|------------|
| Spektralna| ★★★★☆      | ★★★★☆        | ★★★☆☆    | ★★★★★      |
| METIS     | ★★★★☆      | ★★★★★        | ★★★★★    | ★★★★★      |
| BILP      | ★★★★★      | ★★★★★        | ★☆☆☆☆    | ★★★★★      |
| Louvain   | ★★★★★      | ★★★☆☆        | ★★★★☆    | ★☆☆☆☆      |

**Zalety spektralnej:**
- Solidne podstawy matematyczne
- Pełna kontrola nad k
- Dodatkowe metryki diagnostyczne
- Łatwa interpretacja

**Kiedy używać spektralnej:**
- Potrzebujesz dokładnie k klastrów
- Chcesz zrozumieć strukturę grafu
- Potrzebujesz porównywalnych wyników
- Graf nie jest zbyt duży (< 10,000 węzłów)

---

## Troubleshooting 1-Linijkowy

```bash
# Problem: ModuleNotFoundError
touch spectral/__init__.py utils/__init__.py

# Problem: "k must be smaller than n"
# Zmniejsz k lub użyj większego grafu

# Problem: Import errors
export PYTHONPATH="/path/to/DecSel:$PYTHONPATH"

# Problem: Brak wykresów
mkdir -p results/spectral && python loop_GOY.py
```

---

## Następne Kroki

1. ✅ Uruchomiłeś podstawowe testy
2. ✅ Zintegrowałeś z DecSel
3. ⬜ Przetestuj na swoich danych
4. ⬜ Porównaj z METIS/BILP
5. ⬜ Dostosuj parametry
6. ⬜ Napisz raport/publikację

---

## Potrzebujesz Pomocy?

1. **Przeczytaj**: `README.md` - kompletna dokumentacja
2. **Przeczytaj**: `INTEGRATION_GUIDE.md` - szczegółowy przewodnik
3. **Uruchom**: `run_examples.py` - 6 przykładów demonstracyjnych
4. **Sprawdź**: Sekcję Troubleshooting w README

---

## Benchmark Szybki

```bash
# Uruchom benchmark porównawczy
python -c "
from spectral_interface import SpectralBenchmark
import networkx as nx

G = nx.karate_club_graph()
for u, v in G.edges():
    G[u][v]['weight'] = 1

benchmark = SpectralBenchmark()
benchmark.run_spectral(G, k_values=[2, 3, 4], network_name='karate')
benchmark.compare_methods()
"
```

---

**Powodzenia z integracją! 🚀**

Jeśli wszystko działa, powinieneś mieć teraz kompletny system porównywania metod dekompozycji grafów.
