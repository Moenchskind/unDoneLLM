# MönchiBot – Agent Runtime für Satisfactory

>Ein autonomer KI-Sidekick für Satisfactory, der Wahrnehmung, Gedächtnis, Ziele und Action-Planung kombiniert.

## 🏗️ Status

⚠️ **PROTOTYP PHASE** – Backend existiert mit Testing.  
**SML/Unreal Integration NICHT IMPLEMENTIERT!**

### ✅ Erledigt
- Backend Struktur vollständig
- LLM Provider (Ollama) mit Fehlerbehandlung
- Agent Cycle: OBSERVE→THINK→PLAN→ACT→VERIFY (EINMALIG)
- Memory Layer (JSON persistiert)
- Tool Registry + Validator
- Autonomy Levels: OBSERVE, ASSISTED, AUTONOMOUS, FULL_AUTONOMOUS
- Tests: 7 Tests, alle bestanden

### ⏳ In Arbeit / TODO
- SML/Unreal Mod Integration ❌ (nur Analyse dokumentiert)
- Agent LLM integration in plan() phase ❌ (Mock implementiert)
- Vision integration (Qwen-VL) ❌ (später Phase E+)

---

## 📁 Projektstruktur

```
MonchiBot/
├── ARBEITSANWEISUNG.md      # Ursprüngliche Anweisungen (german)
├── README.md                 # Dieser artikel
├── ARCHITECTURE.md           # Systemarchitektur
├── IMPLEMENTATION_REPORT.md  # Implementationsstatus
├── REVIEW_REPORT.md          # Technical review findings
└── backend/
    ├── main.py              # FastAPI server
    ├── config.py            # Konfiguration
    ├── llm/                 # LLM Provider (Ollama)
    ├── memory/              # Memory Layer (JSON→SQLite migrating later)
    ├── agent/               # Agent Core + Planner abstraction
    ├── tools/               # Registry + Validator
    ├── models/              # Pydantic schemas
    └── api/                 # REST endpoints
```

---

## ⚙️ Technologie Stack

- **Python 3.14.7**
- **FastAPI** (Web API)
- **Ollama** (LLM Provider: Qwen3-Coder-instruct-262k)
- **Pydantic v2.x** (Typisierung, validation)
- **httpx** (Async HTTP Client)

---

## 🧪 Tests

```bash
cd /home/phippel/Projekte/SF-playmod/MonchiBot
pip3 install pytest pytest-asyncio --break-system-packages -q
python3 -m pytest tests/test_basic.py -v
```

✅ **7 Tests, alle bestanden**

---

## 📖 Dokumentation

| Datei | Status |
|-------|--------|
| README.md (diese) | ✅ Aktuell |
| ARCHITECTURE.md | ✅ Systemarchitektur |
| IMPLEMENTATION_REPORT.md | ✅ Was implementiert wurde |
| REVIEW_REPORT.md | ✅ Technical review results |
| docs/SYSTEM_ARCHITECTURE.md | ✅ Komponentendiagramm |
| docs/LLM_PROVIDER.md | ✅ LLM Abstraktion |
| docs/SATISFACTORY_MODDING_ANALYSIS.md | ⚠️ Analyse (keine Implementierung) |

---

## 🤖 Autonomy Levels

| Level | Verhalten |
|-------|-----------|
| OBSERVE (default) | Beobachtungen speichern, keinerlei Aktionen ausführen |
| ASSISTED | Planung + Validierung aber keine Ausführung |
| AUTONOMOUS | Validierte Aktionen ausführen |
| FULL_AUTONOMOUS | Reserviert für spätere Ziel-Engine |

---

## 🔒 Sicherheit

- Validator = Tool/Parameter Gate (keine Spiellogik validation)
- LLM = unvertrauenswürdig, immer validieren
- Autonomy levels definieren Ausführungsrechte

---

## 🐳 Containerisierung

⚠️ **Podman ist die Zielplattform!**

Aktuell: Host-Python-Prozess  
Später: Podman container (no Docker-compose.yml!)

Container setup in separatem Schritt konfigurieren.

---

## 🚀 Erste Schritte (Host)

```bash
cd /home/phippel/Projekte/SF-playmod/MonchiBot

# Install dependencies
pip3 install fastapi uvicorn pydantic httpx typing-extensions pytest pytest-asyncio --break-system-packages -q

# Run server
python3 -m uvicorn backend.main:app --reload
```

---

## 📝 Lizenz

Privat / Forschung

---

## 🧪 TESTS

### Unit Tests (9)
- Memory, Registry, Validator, Agent structure

### LLM Integration Tests (11)  
- Pydantic Models, Planner Interface
- Ohne echte Ollama Verbindung

### E2E Integration Tests (4)
- **Mit echtem Qwen LLM über Ollama!**
- Dauer: ~17s pro Test
- Prüft kompletten Datenfluss:
  ```
  Observation → Agent.think() → Planner.run_plan()
    → OllamaProvider.chat_completions()
    → Qwen3-Coder-Next (echtes LLM!)
    → StructuredPlan.model_validate_json()
    → Autonomy Gate → Tool Execution
  ```

```bash
# Alle Tests ausführen
pytest tests/ -v

# Nur E2E Tests mit Ollama
pytest tests/test_e2e_llm.py -v
```
