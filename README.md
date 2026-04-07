# Iteracyjny System Autokorekty Kodu i Generowania Testów (napędzany przez LangGraph)

**Iteracyjny System Autokorekty Kodu i Generowania Testów (napędzany przez LangGraph)** to zaawansowany system orkiestracji agentów AI zbudowany przy użyciu **LangGraph** i **LangChain**. 
System implementuje autonomiczny cykl poprawy jakości kodu (Self-Healing Code Loop), w którym wyspecjalizowani agenci współpracują, aby wykryć, naprawić i zweryfikować błędy w kodzie Python.

## Kluczowe Funkcje

* **Audytor AI (Static Analysis)**: Przeprowadza rygorystyczną analizę logiczną, wykrywając błędy typu *edge-case*, takie jak niejawne konwersje typów (np. problem `bool` vs `int`), błędy dzielenia przez zero czy brak walidacji danych wejściowych.
* **Coder AI (Error-Driven Repair)**: Automatycznie implementuje poprawki na podstawie raportu audytora oraz dynamicznego kontekstu z logów błędów (Traceback) z poprzednich nieudanych prób uruchomienia kodu.
* **Tester AI (Dynamic QA)**: Generuje kompleksowe zestawy testów w frameworku `pytest`, dbając o wysokie pokrycie logiki biznesowej i scenariuszy brzegowych specyficznych dla aktualnej wersji kodu.
* **Runner AI (Isolated Execution)**: Wykonuje testy w izolowanym środowisku tymczasowym (`tempfile`), przechwytuje strumienie `stdout/stderr` i dostarcza surowe logi systemowe bezpośrednio do pętli decyzyjnej.
* **Self-Healing Loop (Autonomiczna Pętla)**: Graf steruje procesem iteracyjnie do momentu uzyskania statusu `SUCCESS` lub osiągnięcia limitu 3 prób, co zapewnia optymalizację kosztów API i zapobiega pętlom nieskończonym.
* **Persistent Artifacts & Reporting**: System automatycznie generuje strukturę katalogów, zapisując naprawiony kod oraz testy. Pliki testowe zawierają pełny raport audytora w formie dokumentacji `docstring`, co zapewnia pełną identyfikowalność decyzji AI.

## Architektura Systemu

System opiera się na grafie skierowanym z cyklami, co pozwala na powtarzanie fazy kodowania i testowania w przypadku wykrycia regresji lub błędów.

1. **Auditor** → Analiza wejściowego kodu źródłowego i generowanie szczegółowego raportu o błędach logicznych.
2. **Coder** → Naprawa kodu na podstawie raportu audytora (oraz logów błędów z poprzedniej iteracji, jeśli to kolejna próba).
3. **Tester** → Generowanie testów jednostkowych (`pytest`) ściśle dopasowanych do **aktualnej** (poprawionej) wersji kodu.
4. **Runner** → Złączenie kodu z testami w pliku tymczasowym, fizyczne uruchomienie testów i przechwycenie logów systemowych.
5. **Router (Conditional Edge)** → Logika decyzyjna oparta na wynikach od Runnera:
   - **Jeśli `SUCCESS`:** Kończy proces z sukcesem.
   - **Jeśli `FAIL`:** Wraca do węzła **Coder**, przekazując mu szczegóły błędów do poprawy.
   - **Guardrail (Limit prób):** Jeśli liczba iteracji osiągnie limit (domyślnie 3), proces jest bezwzględnie przerywany, aby uniknąć pętli nieskończonej i optymalizować koszty API.

## Technologie

- **Orkiestracja**: [LangGraph](https://www.langchain.com/langgraph)
- **Modele LLM**: OpenAI GPT-4o
- **Język**: Python 3.10+
- **Testowanie**: Pytest
- **Zarządzanie Stanem**: TypedDict (State Management)

### Wymagania
- Zainstalowany Python 3.10+
- Aktywny klucz API OpenAI

# Iterative Unit Test Generator & Fixer (powered by LangGraph)

**Iterative Unit Test Generator & Fixer** is an advanced AI agent orchestration system built using **LangGraph** and **LangChain**. The system implements an autonomous **Self-Healing Code Loop**, where specialized agents collaborate to detect, repair, and verify errors in Python code.

## Key Features

* **AI Auditor (Static Analysis)**: Performs rigorous logical analysis, detecting edge-case errors such as implicit type conversions (e.g., the `bool` vs `int` problem), division by zero, or missing input validation.
* **AI Coder (Error-Driven Repair)**: Automatically implements fixes based on the auditor's report and dynamic context provided by error logs (Tracebacks) from previous failed execution attempts.
* **AI Tester (Dynamic QA)**: Generates comprehensive test suites using the `pytest` framework, ensuring high business logic coverage and edge-case scenarios specific to the current version of the code.
* **AI Runner (Isolated Execution)**: Executes tests in an isolated temporary environment (`tempfile`), captures `stdout/stderr` streams, and delivers raw system logs directly to the decision-making loop.
* **Self-Healing Loop (Autonomous Loop)**: The graph manages the process iteratively until a `SUCCESS` status is reached or the 3-attempt limit is hit, ensuring API cost optimization and preventing infinite loops.
* **Persistent Artifacts & Reporting**: The system automatically generates a directory structure to save the repaired code and tests. Test files include the full auditor's report as a `docstring`, ensuring total traceability of AI-driven decisions.

## System Architecture

The system is based on a **Directed Acyclic Graph (DAG) with cycles**, allowing for repetitive coding and testing phases if regressions or errors are detected.

1.  **Auditor** → Analyzes the input source code and generates a detailed report on logical flaws.
2.  **Coder** → Repairs the code based on the auditor's report (and error logs from the previous iteration, if applicable).
3.  **Tester** → Generates unit tests (`pytest`) strictly tailored to the **current** (repaired) version of the code.
4.  **Runner** → Merges the code with the tests in a temporary file, executes the tests physically, and captures system logs.
5.  **Router (Conditional Edge)** → Decision logic based on Runner results:
    * **If `SUCCESS`:** Terminates the process successfully.
    * **If `FAIL`:** Returns to the **Coder** node, providing specific error details for further repair.
    * **Guardrail (Attempt Limit):** If the iteration count reaches the limit (default: 3), the process is forcefully terminated to avoid infinite loops and optimize API costs.

## Technologies

* **Orchestration**: [LangGraph](https://www.langchain.com/langgraph)
* **LLM Models**: OpenAI GPT-4o
* **Language**: Python 3.10+
* **Testing Framework**: Pytest
* **State Management**: TypedDict

## Requirements

* Python 3.10 or higher
* Active OpenAI API Key