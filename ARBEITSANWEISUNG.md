# MönchiBot – Arbeitsanweisung für den Coding-Agenten

## 1. Projekt

Du arbeitest am Projekt **MönchiBot**.

MönchiBot soll langfristig ein autonomer KI-Sidekick für **Satisfactory** werden.

Die grundlegende Idee:

> MönchiBot besitzt ein LLM als „Gehirn“, erhält Wahrnehmungen aus der Spielwelt, besitzt ein Gedächtnis, verfolgt Ziele, plant Aktionen und kann über eine kontrollierte Tool-Schnittstelle mit Satisfactory interagieren.

Das Projekt soll nicht als einfacher Chatbot gebaut werden.

Es soll langfristig eine **Agent Runtime** werden.

---

# 2. Grundarchitektur

Die langfristige Architektur ist:

```text
                    ┌──────────────────────┐
                    │      MönchiBot       │
                    │    Agent Runtime     │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
     Perception             Memory               Goals
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                           Planner
                               │
                               ▼
                         Tool Registry
                               │
                               ▼
                        Action Validator
                               │
                               ▼
                     Satisfactory Adapter
                               │
                               ▼
                         Game World
                               │
                               └──────→ Observation
```

Die Architektur muss modular bleiben.

Das Backend darf nicht fest auf ein bestimmtes LLM, Ollama oder eine bestimmte Satisfactory-Mod-Implementierung verdrahtet werden.

---

# 3. LLM

Das erste geplante Modell ist:

**Qwen3-Coder-Next**

Das Modell wird zunächst lokal über **Ollama** angesprochen.

Die Anwendung soll jedoch nicht davon ausgehen, dass Ollama der einzige mögliche Provider ist.

Erstelle deshalb eine geeignete Abstraktion, beispielsweise:

```text
LLM Interface
    ↓
Ollama Provider
    ↓
Qwen3-Coder-Next
```

Ein späterer Providerwechsel soll möglich sein, ohne Agent, Memory oder Tool-System neu schreiben zu müssen.

---

# 4. Vision

MönchiBot soll langfristig sehen können.

Die Vision ist **nicht zwingend Bestandteil des ersten funktionsfähigen Prototyps**, muss aber architektonisch berücksichtigt werden.

Geplant ist:

```text
Satisfactory
    │
    ├── strukturierte Welt-Daten
    │
    └── Screenshots / Kamerabilder
              ↓
           Vision Model
              ↓
          Perception
```

Für Vision kann später beispielsweise ein Qwen-VL-Modell verwendet werden.

Wichtig:

Das Vision-Modell und das Planungs-/Coding-Modell müssen nicht dasselbe Modell sein.

Das Backend soll diese Möglichkeit berücksichtigen.

Vision darf außerdem nicht für Informationen verwendet werden, die der Satisfactory-Mod bereits zuverlässig strukturiert liefern kann.

Beispiel:

* Position → strukturierte Daten
* Inventar → strukturierte Daten
* Stromproduktion → strukturierte Daten
* „Wie sieht die Fabrik aus?“ → Vision

---

# 5. Perception

MönchiBot benötigt eine einheitliche Wahrnehmungsschicht.

Diese soll später beispielsweise folgende Informationen aufnehmen können:

* Spielerposition
* Spielerrotation
* Spielerzustand
* Inventar
* Gesundheit
* Ausrüstung
* aktuelle Welt
* Gebäude
* Gebäudepositionen
* Gebäuderotationen
* Förderbänder
* Ressourcen
* Produktionsraten
* Stromproduktion
* Stromverbrauch
* freigeschaltete Technologien
* MAM-Forschung
* verfügbare Rezepte
* nahe Objekte
* relevante Ereignisse
* Screenshots / Vision-Daten

Die genaue Satisfactory-Implementierung wird später festgelegt.

Für den Backend-Prototyp dürfen dafür zunächst Mock-/Testdaten verwendet werden.

---

# 6. Memory

MönchiBot soll ein Gedächtnis besitzen.

Für einen ersten Prototyp ist eine einfache lokale Speicherung akzeptabel.

Langfristig soll Memory logisch mindestens folgende Kategorien unterstützen:

```text
short-term memory
long-term memory
knowledge
observations
goals
tasks
events
```

Vermeide eine Architektur, bei der die komplette Memory bei jeder Anfrage vollständig in den System-Prompt eingefügt werden muss.

Memory soll später selektiv abgerufen werden können.

Eine spätere Migration von JSON zu SQLite oder einer anderen lokalen Datenbank muss möglich bleiben.

---

# 7. Goals

MönchiBot soll zwischen folgenden Ebenen unterscheiden können:

```text
Personality
    ↓
Long-term Goals
    ↓
Mid-term Goals
    ↓
Tasks
    ↓
Actions
```

Beispiel:

```text
Ziel:
Automatisiere Eisenproduktion.

Teilziel:
Erhöhe Eisenplattenproduktion.

Task:
Baue vier Constructor.

Action:
Baue Constructor an Position X/Y/Z.
```

Das Zielsystem darf nicht mit dem LLM fest verdrahtet werden.

---

# 8. Agent Loop

Die langfristige Agentenschleife lautet:

```text
OBSERVE
   ↓
THINK
   ↓
PLAN
   ↓
ACT
   ↓
VERIFY
   ↓
OBSERVE
```

Insbesondere **VERIFY** ist verpflichtend.

Nach einer Aktion muss das System feststellen können:

```text
success
failure
partial success
unknown
```

Beispiel:

```text
LLM:
build(Constructor, position)

Game:
BUILD_COLLISION

Agent:
Plan ändern
```

Ein fehlgeschlagener Befehl darf nicht einfach als erfolgreich betrachtet werden.

---

# 9. Tools / Actions

LLMs dürfen nicht direkt Unreal Engine oder interne Spielobjekte manipulieren.

Stattdessen gibt es eine kontrollierte Tool-Schicht.

Beispielhafte Tools:

```text
observe_world
observe_inventory
observe_power
find_build_location
build
demolish
rotate
connect
move
interact
craft
research
```

Diese Liste ist zunächst nur konzeptionell.

Implementiere keine Satisfactory-spezifischen Tools, deren tatsächliche technische Grundlage nicht bekannt ist.

---

# 10. Action Validation

Vor der Ausführung einer Aktion soll eine Validierungsschicht stehen:

```text
LLM
 ↓
Tool Request
 ↓
Validator
 ↓
Satisfactory Adapter
 ↓
Game
```

Der Validator soll perspektivisch beispielsweise prüfen können:

* existiert das Tool?
* sind die Parameter korrekt?
* ist das Gebäude bekannt?
* ist die Position gültig?
* sind Ressourcen vorhanden?
* ist die Aktion erlaubt?
* liegt eine Kollision vor?
* benötigt die Aktion Benutzerbestätigung?

Das LLM darf niemals direkt ungeprüfte Engine-Aufrufe erzeugen.

---

# 11. Benutzerinteraktion

Die bevorzugte Benutzeroberfläche ist zunächst der vorhandene **Satisfactory-Ingame-Chat**.

Ein separates Chatfenster ist nur erforderlich, wenn die Modding-Möglichkeiten des Ingame-Chats dies technisch nicht sinnvoll erlauben.

Beispiele:

```text
Spieler:
MönchiBot, bau mir vier Schmelzöfen für Eisen.

MönchiBot:
Ich plane die Eisenproduktion.
```

MönchiBot soll langfristig auch selbstständig Nachrichten senden können.

---

# 12. Autonomie

Das System soll langfristig verschiedene Autonomiegrade unterstützen.

Geplant sind:

```text
OBSERVE
ASSISTED
AUTONOMOUS
FULL_AUTONOMOUS
```

Beispiel:

```text
OBSERVE:
Nur wahrnehmen und berichten.

ASSISTED:
Planen und Aktionen vorschlagen.

AUTONOMOUS:
Erlaubte Aktionen selbstständig durchführen.

FULL_AUTONOMOUS:
Ziele verfolgen und eigene Aufgaben erzeugen.
```

Die Sicherheits- und Berechtigungslogik soll unabhängig vom LLM funktionieren.

---

# 13. Satisfactory-Mod

Der Satisfactory-Teil soll über einen Adapter an das Backend angebunden werden.

Geplante Kommunikation:

```text
Satisfactory Mod
       │
       │ HTTP / JSON
       ▼
MönchiBot Backend
       │
       ▼
Agent
```

Das Backend darf nicht voraussetzen, dass die Mod bereits existiert.

Der aktuelle Auftrag besteht deshalb NICHT darin, eine vollständige Satisfactory-Mod zu erfinden.

Zuerst soll untersucht und dokumentiert werden:

* aktuelle Satisfactory-Modding-Möglichkeiten
* SML
* relevante Unreal-Engine-Schnittstellen
* HTTP-Kommunikation aus der Mod
* Threading-Anforderungen
* mögliche Einschränkungen
* Möglichkeiten zur Weltabfrage
* Möglichkeiten zur Gebäudeplatzierung
* Möglichkeiten zur Screenshot-/Viewport-Erfassung
* relevante Versionen und Kompatibilitätsfragen

Wenn etwas nicht sicher bekannt ist:

**Nicht halluzinieren. Dokumentieren und als offene Frage markieren.**

---

# 14. Entwicklungsprinzip

Arbeite inkrementell.

Nicht versuchen, das komplette Projekt auf einmal zu implementieren.

Priorität:

```text
1. Architektur
2. Backend-Grundgerüst
3. Datenmodelle
4. LLM-Abstraktion
5. Agent Loop
6. Memory
7. Tool-System
8. Tests
9. Satisfactory-Adapter
10. Vision
11. echte Mod-Integration
12. Autonomie
```

Diese Reihenfolge darf geändert werden, wenn technische Erkenntnisse dies begründen.

Änderungen müssen jedoch dokumentiert werden.

---

# 15. Aktueller Auftrag

## Phase A – Analyse

Untersuche zunächst das vorhandene Repository und die vorhandene Entwicklungsumgebung.

Prüfe insbesondere:

* Betriebssystem
* Python-Version
* vorhandene Python-Umgebung
* Ollama
* vorhandene Modelle
* vorhandene Node/C++-Werkzeuge
* Git
* vorhandene Projektstruktur
* vorhandene Satisfactory-Modding-Projekte

Keine unnötigen globalen Änderungen durchführen.

---

## Phase B – Architektur

Erstelle bzw. vervollständige:

```text
README.md
ARCHITECTURE.md
docs/API.md
docs/MEMORY.md
docs/TOOLS.md
docs/VISION.md
```

Dokumentiere die tatsächliche Architektur.

Keine erfundenen APIs als Fakten darstellen.

---

## Phase C – Minimaler Backend-Prototyp

Erstelle einen minimalen, lokal laufenden Python-Backend-Prototyp.

Bevorzugt:

**FastAPI**

Der Server soll zunächst mindestens eine saubere API-Struktur besitzen.

Die konkrete Endpoint-Struktur darfst du sinnvoll verbessern.

Die ursprüngliche Idee enthält:

```text
/think
/remember
```

Diese Endpunkte dürfen verwendet werden, wenn sie architektonisch sinnvoll sind.

---

## Phase D – Agent

Implementiere einen minimalen Agenten, der:

1. eine Observation erhält,
2. Memory berücksichtigen kann,
3. einen Plan bzw. eine Aktion erzeugen kann,
4. die Aktion validiert,
5. ein strukturiertes Ergebnis zurückgibt.

Noch keine echte Unreal-Ausführung.

---

## Phase E – Tests

Erstelle Tests für:

* API
* Memory
* Agent
* Goals
* Tool Registry
* Validator
* Fehlerbehandlung

Der Prototyp muss ohne Satisfactory startbar und testbar sein.

Mocks sind ausdrücklich erlaubt.

---

# 16. Keine unnötigen Abhängigkeiten

Bevor neue Bibliotheken hinzugefügt werden:

1. Prüfen, ob die Funktion mit der Standardbibliothek möglich ist.
2. Prüfen, ob bereits eine vorhandene Abhängigkeit verwendet werden kann.
3. Nur dann neue Abhängigkeit hinzufügen.

Jede neue wichtige Abhängigkeit soll begründet werden.

---

# 17. Kein Overengineering

Das Projekt ist experimentell.

Nicht vorsorglich:

* Kubernetes
* Microservice-Landschaft
* Redis
* Kafka
* PostgreSQL
* Cloud-Dienste
* unnötige Container
* komplexe Message Broker

einführen.

MönchiBot läuft zunächst lokal auf einem einzelnen Rechner.

Die Architektur soll erweiterbar sein, aber der Prototyp soll klein bleiben.

---

# 18. Codequalität

Bevorzugt:

* klare Typisierung
* kleine Module
* verständliche Namen
* Pydantic-Modelle für API-Daten
* strukturierte Fehlerbehandlung
* Logging
* Tests
* keine unnötigen globalen Zustände

Keine riesigen monolithischen Dateien.

---

# 19. Sicherheitsregel für autonome Aktionen

Das LLM ist ein nicht vertrauenswürdiger Entscheider.

Es darf Vorschläge erzeugen.

Es darf nicht die Sicherheitsgrenzen selbst definieren.

Die tatsächliche Autorisierung einer Aktion muss außerhalb des LLM liegen.

Insbesondere destruktive Aktionen sollen später separat kontrollierbar sein.

Beispiele:

```text
build       → möglicherweise automatisch
move        → möglicherweise automatisch
connect     → möglicherweise automatisch
demolish    → möglicherweise Bestätigung
large-scale demolition → Bestätigung
```

Diese Regeln sollen konfigurierbar sein.

---

# 20. Arbeitsweise des Coding-Agenten

Arbeite selbstständig, aber nicht blind.

Wenn eine technische Entscheidung unklar ist:

1. untersuche vorhandenen Code,
2. untersuche lokale Dokumentation,
3. prüfe verfügbare Quellen,
4. dokumentiere die Unsicherheit,
5. wähle die kleinste sinnvolle Lösung.

Nicht einfach APIs, Klassen oder SML-Funktionen erfinden.

Wenn externe Recherche nicht möglich ist, markiere die Stelle ausdrücklich als:

```text
UNKNOWN / NEEDS VERIFICATION
```

---

# 21. Abschlussbericht

Nach Abschluss der aktuellen Arbeitsrunde soll ein Bericht erstellt werden:

```text
IMPLEMENTED
----------------
Was wurde tatsächlich implementiert?

CHANGED
----------------
Welche Dateien wurden geändert?

DECISIONS
----------------
Welche Architekturentscheidungen wurden getroffen?

ASSUMPTIONS
----------------
Welche Annahmen wurden gemacht?

UNKNOWN / NEEDS VERIFICATION
----------------
Welche Punkte sind noch unsicher?

TESTS
----------------
Welche Tests wurden ausgeführt?

NOT IMPLEMENTED
----------------
Was wurde bewusst noch nicht implementiert?

NEXT STEP
----------------
Was ist der sinnvollste nächste Entwicklungsschritt?
```

---

# 22. Wichtigste Regel

**Baue nicht das, was du glaubst, dass MönchiBot irgendwann brauchen könnte.**

Baue zuerst eine kleine, getestete Grundlage, auf der MönchiBot wachsen kann.

Das Ziel ist nicht möglichst viel Code.

Das Ziel ist eine belastbare Agentenarchitektur.

MönchiBot soll später selbstständig Satisfactory spielen können.

Heute soll er zunächst lernen, wie man dafür technisch sauber gebaut wird.
