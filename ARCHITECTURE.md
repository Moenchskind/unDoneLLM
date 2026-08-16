# MönchiBot Architektur

## Übersicht

```
┌─────────────────────────────────────────────┐
│           User Interface (Ingame Chat)      │
└──────────────────────┬──────────────────────┘
                       │ HTTP / JSON (später)
                       ▼
┌─────────────────────────────────────────────┐
│         FastAPI Backend (Python)            │
├──────────────────┬──────────────────────────┤
│                  │                          │
│    LLM Provider  │     Agent Core           │
│    Abstraktion   │                          │
│                  │                          │
│   Memory Layer   │   Tool Registry          │
│                  │                          │
│   Validator      │   Planner abstraction   │
└──────────────────┴──────────────────────────┘
```

---

## KOMPONENTEN

### 1. LLM Provider (backend/llm/provider.py)

**Abstraktion für LLM-Anbieter:**
- `LLMProvider` - Interface
- `OllamaProvider` - Realisierung für Qwen3-Coder-instruct-262k
- **Error handling**: Timeout, HTTP errors (neu implementiert)
- Asynchrone API-Aufrufe via httpx

**Status: ✅ FUNCTIONAL**
- Ollama läuft (42 models verfügbar)
- Fehlerbehandlung vollständig

---

### 2. Agent Core (backend/agent/)

**Agent Loop:**

```
OBSERVE → THINK → PLAN → ACT → VERIFY
          ↓         ↓        ↓
     Memory   LLM-Planner  Tools+Validator
                                    ↓
                              Autonomy check
```

**Features:**
- `run_cycle()`: Führt EINEN Zyklus aus (NICHT Endlosloop!)
- `autonomy_level`: OBSERVE, ASSISTED, AUTONOMOUS, FULL_AUTONOMOUS
- Validator prüft jeden Tool-Aufruf
- Memory wird bei jedem cycle aktualisiert

**Status: ✅ FUNCTIONAL**
- Agent loop vollständig implementiert
- Autonomy levels durchgesetzt (neu)
- Tests: 7/7 bestanden

---

### 3. Memory Layer (backend/memory/memory.py)

**Kategorien:**
- Short-term: Aktuelle Session
- Long-term: Persistiert in JSON files
- Knowledge: Fakten über Spielmechaniken
- Goals, Tasks, Events, Observations

**Persistenz:**
- Aktuell: JSON files (`./data/memory/`)
- Zukunft: SQLite migration (dokumentiert)

**Status: ✅ FUNCTIONAL**
- CRUD operations work
- Error handling für load_from_file (neu)
- Tests bestanden

---

### 4. Tools & Validator (backend/tools/)

**Registry:**
- `Tool` Interface
- `MockObservationTool`: Test tool (KEINE echten Weltdaten!)
- Tool registry verwaltet alle tools

**Validator:**
- "Tool/Parameter Gate" ✅ NICHT vollständige Sicherheitsschicht!
- Prüft:
  - Tool existiert?
  - Parameter gültig?
- **Prüft NICHT:**
  - Spielzustand (Ressourcen, Kollisionen)
  - Benutzerrechte
  - Business logic

**Status: ✅ FUNCTIONAL**
- Registry + Validator work
- Autonomy level integration in act() (neu)

---

### 5. Planner Abstraktion (backend/agent/planner.py)

**ZWECK:**

Klare Trennung zwischen Agent Core und Planungslogik.

```
Agent
  ↓
Planner
  ↓
LLMProvider (später)
```

**AKTUELL:**
- Interface definiert (`Planner`, `MockPlanner`)
- Mock implementation in Agent.plan() (keine echte LLM integration)

**ZUKUNFT:**
- LLM Provider für generative plans
- Prompt engineering nicht hier implementieren

**Status: ✅ STRUCTURE READY, MOCK IMPLEMENTED**

---

### 6. API Endpoints (backend/api/routes.py)

**Currently implemented:**
- `GET /` - Root info
- `GET /health` - Health check  
- `POST /api/v1/think` - Agent cycle starten (ohne LLM)
- `GET /api/v1/agent/state` - Status abrufen

**Planned (später):**
- `POST /api/v1/chat` - Chat completion (LLM integration nötig)
- `GET /api/v1/tools/available` - Tools liste (work in progress)

---

## DATENFLUSS (Agent Cycle)

```
Observation (input)
       ↓
    Agent.run_cycle()
       ↓
    ┌── OBSERVE ──→ think(observation) ─────────────┐
    │                                              │
    └── THINK ───→ think() + update memory         │
                   ↓                               │
    ┌── PLAN ────→ plan(thought) ← (später LLM)   │
    │                                              │
    └── ACT ─────→ act(plan)                       │
       ├─ validate → Validator                    │
       ├─ autonomy_level check                    │
       └─ execute tool                            │
                   ↓                               │
    ┌── VERIFY ──→ verify(results)                 │
    │                                              │
    └── return results (loop ends!)               │
```

**WICHTIG:**
- `run_cycle()` führt EINEN cycle aus, dann Ende!
- Endlos loop muss später als separate scheduler funktion implementiert werden
- Jeder Aufruf needs neue observation input

---

## AUTONOMY LEVEL IMPLEMENTATION

| Level | think() | plan() | act() |
|-------|---------|--------|-------|
| OBSERVE | ✅ Observations | ✅ Plans created | ❌ Only planned, NOT executed |
| ASSISTED | ✅ + memory | ✅ + confidence | ❌ Returned for user approval |
| AUTONOMOUS | ✅ | ✅ | ✅ Validated actions EXECUTED |
| FULL_AUTONOMOUS | ✅ | ✅ | ✅ (future: goal-driven) |

**Implementation in `Agent.act()`:**

```python
if self.autonomy_level in ["AUTONOMOUS", "FULL_AUTONOMOUS"]:
    # execute tool
else:
    # plan_only, no execution
```

---

## TECHNISCHE ENTSCHEIDUNGEN

⚠️ **PODMAN ist die Zielplattform!**
- Kein Docker-compose.yml erstellen (nur Podman)
- Spätere containerisierung via `Containerfile`
- Host-Python aktuell für easy testing

| Komponente | Status | Notes |
|-----------|--------|-------|
| LLM Provider | ✅ Ollama (HTTP) | Mit error handling |
| Agent Loop | ✅ EINMALIG | `run_cycle()` |
| Memory | ✅ JSON files | Mit persistence |
| Validator | ✅ Tool/Parameter Gate | Keine Spiellogik |
| Planner | ⏳ Interface | Mock in Agent.plan() |

---

## FUNKTIONIERENDE KOMPONENTENTESTS

✅ **7 Tests bestanden:**

1. Memory add_observation
2. Memory get_active_goals  
3. Registry list_tools
4. Registry get_tool
5. Validator validate_existing_tool
6. Validator validate_unknown_tool
7. Agent complete cycle (status=success)

---

## OFFENE FRAGEN

⚠️ **SPÄTER ZU IMPLEMENTIEREN:**

1. SML/Unreal API Integration (dokumentiert in docs/)
2. Agent.plan() mit echter LLM integration
3. SQLite Memory migration (nicht jetzt!)
4. Vision integration (Qwen-VL)
5. Podman Containerisierung (später)

---

## STATUS ZUSAMMENFASSUNG

| Phase | Status | Notes |
|-------|--------|-------|
| Backend infrastructure | ✅ Complete | FastAPI, routes, config |
| LLM Provider | ✅ Working | Ollama error handling ✓ |
| Agent Core | ✅ Working | Loop + autonomy levels ✓ |
| Memory | ✅ Working | JSON persistence ✓ |
| Tools/Validator | ✅ Working | Gate logic ✓ |
| Planner | ⏳ Structure ready | Mock implementation ✓ |
| Tests | ✅ 7/7 passing | All tests green |

**NEXT STEP: LLM integration in Agent.plan() (Phase D+)**  
**NICHT: SML, Vision, Container setup (in diesem Schritt)**
