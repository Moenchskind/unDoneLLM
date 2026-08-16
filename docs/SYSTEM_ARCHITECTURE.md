# Systemarchitektur – MönchiBot

## 1. Übersicht

MönchiBot ist ein Agent-Runtime-System für Satisfactory mit folgender Schichtenarchitektur:

```
┌─────────────────────────────────────────────┐
│           User Interface (Ingame Chat)      │
└──────────────────────┬──────────────────────┘
                       │ HTTP / JSON
                       ▼
┌─────────────────────────────────────────────┐
│         FastAPI Backend (Python)            │
├──────────────────┬──────────────────────────┤
│                  │                          │
│    LLM Provider  │     Agent Core           │
│    Abstraction   │                          │
│                  │                          │
│   Memory Layer   │   Tool Registry          │
│                  │                          │
│   validator      │   Vision Adapter         │
└──────────────────┴──────────────────────────┘

```

## 2. Komponentenübersicht

### 2.1 LLM Provider (Frontend → Backend)

- **Provider-Abstraktion**: Unabhängige Implementierung für Ollama, OpenAI, etc.
- **Erster Provider**: Qwen3-Coder-instruct-262k via Ollama
- **Anforderung**: Saubere Trennung zwischen Agent und LLM-Anbindung

### 2.2 Agent Core

**Agent Loop (OBSERVE → THINK → PLAN → ACT → VERIFY)**:

1. **Observation**: Weltzustand empfangen
2. **Memory Access**: Relevantes Gedächtnis laden
3. **Planning**: Zielorientierte Aktion erzeugen
4. **Action Validation**: Sicherheitsprüfung vor Ausführung
5. **Execution**: Tool-Aufruf ausführen
6. **Verification**: Ergebnis prüfen → Feedback an Memory

### 2.3 Memory Layer

**Kategorien**:
- short-term memory (aktuelle Sitzung)
- long-term memory (persistiert)
- knowledge (Fakten über Spielmechaniken)
- observations (Erkundungen, Erfahrungen)
- goals (Ziele + Status)
- tasks (Teilaufgaben)
- events (geschichtete Ereignisse)

**Strategie**:  
- JSON-basiertes Storage initially
- Später Migration auf SQLite möglich
- Kein vollständiges Memory in chaque Prompt (Kontext-Windows)

### 2.4 Tool Registry

**Prinzipien**:
- Jedes Tool hat spezifische Parameter & Rückgabetypen
- Tools sind sauber getrennt von Spielmechaniken
- Validator kann vor Ausführung prüfen

**Beispieltools (konzeptionell)**:
```json
[
  {
    "name": "observe_world",
    "description": "Aktuellen Weltzustand abfragen",
    "parameters": [],
    "returns": "ObservationSchema"
  },
  {
    "name": "build",
    "description": "Gebäude errichten",
    "parameters": ["building_type", "position", "rotation"],
    "returns": "BuildResult"
  }
]
```

### 2.5 Validator

**Prüfungen**:
- Tool existiert in Registry?
- Parameter syntaktisch korrekt? (Pydantic Validation)
- Parameter semantisch gültig? (z.B. Position innerhalb Spielwelt?)
- Ressourcen vorhanden?
- Kollisionen möglich?

**Design**:  
- LLM VORSCHLÄGE prüfen, aber nicht entscheiden
- Autorität außerhalb des LLM

### 2.6 Vision Adapter (später)

**Zukünftig**:
- Screenshot / Viewport Erfassung möglich
- Qwen-VL modell bar
- Strukturierte Daten VORrangig gegenüber Vision

## 3. Technische Stack

### Backend
- Framework: **FastAPI**
- LLM Anbindung: **ollama-python** (oder HTTP direkt)
- Typisierung: **Pydantic v2.x**
- Serialization: **JSON**

### Speicherung
- short-term: In-Memory
- long-term: JSON Files → SQLite Migration später

## 4. Erweiterbarkeit

### Provider-Austausch
```
LLMInterface → OllamaProvider / OpenAIProvider / ...
```

### Memory Storage
```
MemoryBackend (interface) → JSONStorage / SQLiteStorage / ...
```

### Tools
```python
class Tool(ABC):
    @abstractmethod
    def execute(self, **kwargs): ...
```

## 5. Sicherheitsprinzipien

- LLM = nicht vertrauenswürdig
- Validator vor jeder Aktion
- Konservative Default-Einstellungen (Aktionen blockieren bis批准)
- Benutzerbestätigung bei destruktiven Aktionen (build demolish)

## 6. aktueller Status

- ✅ Backend-Struktur existiert (leere Dateien)
- ✅ Ollama läuft mit Qwen3-Coder-instruct-262k
- ❌ Noch keine Implementierung der Komponenten
- ⏳ Satisfactory Modding (SML/Unreal) noch nicht implementiert

---

## PHASE D+3 STATUS (aktuell)

### LLM Integration Echt ✅

Der Code verwendet aktuell **echte Ollama Integration**:

```
OllamaProvider → localhost:11434/api/chat
  ↓
Qwen3-Coder-instruct-262k:latest (51GB Modell)
  ↓
Structured JSON Response
  ↓
Pydantic Validation
```

### Test Coverage

| Type | Tests | Dauer |
|------|-------|--------|
| Unit | 9 | ~0.07s |
| LLM Schema | 11 | ~0.14s |
| **E2E (echter Ollama)** | 4 | ~38s! |

### WICHTIG: 
- Die `test_e2e_llm.py` Tests verwenden **ECHTES** Qwen Modell!
- Das ist keine Simulation - echte HTTP Aufrufe an localhost:11434
- Dauer liegt bei ~17s pro E2E Test aufgrund LLM Processing!

### NOCH NICHT IMPLEMENTIERT:
- SML/Satisfactory Mod (Analyse dokumentiert)
- Unreal Build API  
- Vision processing
