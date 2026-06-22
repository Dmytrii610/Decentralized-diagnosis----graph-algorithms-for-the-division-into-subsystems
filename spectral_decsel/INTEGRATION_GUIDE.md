# Plan Integracji: Spektralny Podział Grafów z DecSel

## Przegląd
Ten dokument opisuje integrację Twojego kodu spektralnego podziału grafów z repozytorium DecSel (https://github.com/asztyber/DecSel).

## Struktura Repozytorium DecSel

```
DecSel/
├── spectral/          # Kod spektralnego podziału
├── data/              # Dane wejściowe (sieci wodne)
├── bilp/              # Solver BILP
├── gdec/              # Dekompozycja grafów
├── wdn/               # Water Distribution Networks
├── structural_model_GOY.py  # Generowanie modelu strukturalnego
├── loop_GOY.py              # Główna pętla algorytmu
└── decomposition_only_GOY.py # Tylko dekompozycja
```

## Twoje Pliki

1. **spectral_partition.py** - Implementacja spektralnego podziału z KMeans
2. **graph_from_json.py** - Konwersja JSON → NetworkX
3. **plot_metrics_combined.py** - Wizualizacja metryk

## Plan Integracji

### Krok 1: Umieść Swoje Pliki w Strukturze DecSel

```
DecSel/
├── spectral/
│   ├── spectral_partition.py      # Twój plik (zmodyfikowany)
│   ├── __init__.py                # Nowy plik
│   └── spectral_interface.py     # Nowy - adapter do DecSel
├── utils/                         # Nowy folder
│   ├── __init__.py
│   ├── graph_from_json.py        # Twój plik (dostosowany)
│   └── plot_metrics_combined.py  # Twój plik (dostosowany)
```

### Krok 2: Modyfikacje Kodu

#### A. Dostosowanie `spectral_partition.py`

**Zmiany:**
- Dodaj parametr `weighted` do obsługi grafów ważonych (DecSel używa wag)
- Uniezależnij od struktury `models/` (używaj ścieżek relatywnych)
- Dodaj wsparcie dla formatu danych DecSel
- Zachowaj kompatybilność z Twoim formatem JSON

#### B. Dostosowanie `graph_from_json.py`

**Zmiany:**
- Dodaj funkcję do wczytywania danych z formatu DecSel
- Zachowaj funkcję `graph_from_json` dla Twojego formatu
- Ujednolicenie obsługi wag krawędzi

#### C. Integracja z `loop_GOY.py`

**Dodaj:**
- Import Twojego modułu spektralnego
- Wywołanie spektralnej dekompozycji w głównej pętli
- Porównanie z innymi metodami (METIS, itp.)

### Krok 3: Ujednolicenie Formatu Danych

DecSel prawdopodobnie używa:
- Modeli strukturalnych sieci wodnych (GOY - Goyeneche)
- Formatu opisującego czujniki, komponenty i relacje

Twój format JSON:
```json
{
  "model": {
    "element1": ["param1", "param2"],
    "element2": ["param2", "param3"]
  }
}
```

**Rozwiązanie:** Stwórz konwerter między formatami lub adapter wspólny.

### Krok 4: Metryki i Porównanie

Dodaj Twoje metryki do systemu DecSel:
- `cross_weight` - suma wag między klastrami
- `modularity` - modularność
- `coverage` - pokrycie
- `performance` - wydajność

Porównaj z:
- METIS (używany w DecSel)
- BILP
- Inne metody z DecSel

## Szczegółowe Instrukcje Implementacji

### 1. Instalacja DecSel

```bash
git clone https://github.com/asztyber/DecSel.git
cd DecSel
pip install -r requirements.txt
```

**Uwaga:** Potrzebna licencja Gurobi dla BILP.

### 2. Struktura Katalogów

```bash
mkdir -p DecSel/utils
mkdir -p DecSel/results/spectral
```

### 3. Skopiuj i Dostosuj Pliki

Zobacz załączone zmodyfikowane wersje plików w tym pakiecie.

### 4. Uruchom Testy

```bash
# Najpierw wygeneruj model strukturalny
python structural_model_GOY.py

# Uruchom Twoją metodę spektralną
python run_spectral_decomposition.py

# Porównaj z innymi metodami
python loop_GOY_with_spectral.py
```

## Kluczowe Punkty Integracji

### 1. Format Grafu

DecSel używa grafów reprezentujących:
- Węzły = komponenty/czujniki sieci wodnej
- Krawędzie = powiązania diagnostyczne/fizyczne
- Wagi = siła powiązania

### 2. Cel Dekompozycji

DecSel dekompozuje dla:
- Rozproszonych systemów diagnostycznych
- Minimalizacji komunikacji między podsystemami
- Zachowania prywatności

Twoje metryki są idealne!

### 3. Integracja z Pętlą Główną

W `loop_GOY.py` dodaj:

```python
from spectral.spectral_interface import SpectralDecomposer

# W głównej pętli
spectral_dec = SpectralDecomposer(n_clusters=k)
partitions = spectral_dec.decompose(graph)
```

## Testowanie

### Test 1: Prosty Graf

```python
# Użyj małego grafu z Twojego formatu
test_file = "models/test_network.json"
```

### Test 2: Sieć GOY

```python
# Użyj pełnej sieci GOY z DecSel
test_file = "data/GOY_structural_model.json"
```

### Test 3: Porównanie Metod

```python
# Porównaj spektralną, METIS, BILP
compare_methods(graph, k_values=[2, 3, 4, 5])
```

## Metryki Sukcesu

✓ Spektralna metoda działa na danych DecSel
✓ Metryki są porównywalne z innymi metodami
✓ Kod jest zintegrowany z główną pętlą
✓ Wykresy porównawcze generują się poprawnie
✓ Dokumentacja jest aktualna

## Potencjalne Problemy

1. **Format Danych**
   - Rozwiązanie: Adapter/konwerter między formatami

2. **Zależności**
   - DecSel: Gurobi, METIS
   - Twoje: NetworkX, sklearn, scipy
   - Rozwiązanie: Dodaj do requirements.txt

3. **Różne Systemy Metryk**
   - Rozwiązanie: Ujednolicony interfejs metryk

4. **Wizualizacje**
   - Rozwiązanie: Wspólny format wykresów

## Następne Kroki

1. Sklonuj repozytorium DecSel
2. Zainstaluj zależności
3. Skopiuj zmodyfikowane pliki (załączone)
4. Uruchom testy
5. Porównaj wyniki
6. Zaktualizuj dokumentację
7. (Opcjonalnie) Stwórz Pull Request do DecSel

## Przydatne Linki

- Repozytorium: https://github.com/asztyber/DecSel
- Benchmark sieci: https://github.com/asztyber/wdn-sa-benchmark
- Paper: [hal-03773713](https://hal.science/hal-03773713/)

## Kontakt z Autorami

Jeśli chcesz wnieść swój wkład do DecSel, możesz:
- Otworzyć Issue na GitHubie
- Stworzyć Pull Request
- Skontaktować się z autorami przez GitHub
