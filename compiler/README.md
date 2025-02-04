# Kompilator prostego języka imperatywnego

## Autor

Kinga Majcher 272354

## Struktura projektu

- `lexer.py` – Analizator leksykalny. Odpowiada za podział kodu źródłowego na tokeny, takie jak identyfikatory, operatory czy liczby.
- `parser.py` – Analizator składniowy. Tworzy drzewo składniowe na podstawie tokenów wygenerowanych przez lexer, sprawdzając poprawność gramatyczną programu.
- `symbol_table.py` – Tabela symboli. Przechowuje informacje o zmiennych, procedurach, ich adresach w pamięci oraz typach danych.
- `code_generator.py` – Generator kodu. Odpowiada za tłumaczenie drzewa składniowego na kod wynikowy w języku asemblera.
- `compiler.py` – Główny plik kompilatora. Koordynuje działanie wszystkich modułów, łącząc lexer, parser, tabelę symboli i generator kodu w jeden proces kompilacji. Dla podanego pliku wejściowego generuje gotowy kod maszynowy maszyny wirtualnej.

## Instalacja i uruchomienie

### Wymagania

- Python 3.10 (`sudo apt install python3.10`)
- Biblioteka `sly` do analizy składniowej (`pip install sly`)

### Kompilacja

W celu wywołania programu należy w terminalu wprowadzić komendę:

```sh
python3 compiler.py <plik_wejsciowy> <plik_wyjsciowy>
```

gdzie:
- `<plik_wejsciowy>` – ścieżka do pliku zawierającego kod źródłowy w języku imperatywnym
- `<plik_wyjsciowy>` – ścieżka do pliku, w którym zostanie zapisany wynikowy dla maszyny wirtualnej

## Uwagi

- Każdą redeklarację zmiennej traktuję jako błąd, a więc deklaracja zmiennej `j`, która jest potem iteratorem  w pliku `example6.imp` jest błędna. Aby program działał poprawnie należy usunąć ją z deklaracji.
- W pliku `example8.imp` podana jest błędna nazwa tablicy - `tab`. Aby program działał należy zmienić ją na poprawną nazwę, czyli `t`.
