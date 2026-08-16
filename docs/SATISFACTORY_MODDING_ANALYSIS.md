# Satisfactory Modding Analysis – MönchiBot

## 1. aktueller Status

⚠️ **WICHTIG**: *Es existiert aktuell KEINE implementierte SML/Unreal-Integration.*  
Die Analyse dient dazu, technische Möglichkeiten zu dokumentieren.

## 2. Untersuchte Projekte

### 2.1 SatisfactoryModding Organisation
**Repository**: [satisfactorymodding/Documentation](https://github.com/satisfactorymodding/Documentation)  
**Stars**: ~28

Inhaltsverzeichnis:
- Getting Started Guide
- API Reference (C#)
- Tutorials
- Examples

URL: docs.ficsit.app → SML Dokumentation

### 2.2 FICSIT-Fred
**Repository**: [satisfactorymodding/FICSIT-Fred](https://github.com/satisfactorymodding/FICSIT-Fred)  
**Sterne**: ~6

HTTP-server Mod zur Fernsteuerung:
- REST API Endpunkte
- JSON Payloads
- SML Integration

### 2.3 Steveplays28 / FicsitChat
**Repository**: [Steveplays28/FicsitChat](https://github.com/Steveplays28/FicsitChat)  
**Sterne**: ~5

**WICHTIG!** Existing project mit HTTP API!
- Chat-basierte Kommunikation
-可能 Befehle an Satisfactory senden

## 3. Technische Möglichkeiten (SML/C#)

### 3.1 Hook System
```csharp
// Beispiel (ohne Gewähr -文献 review notwendig)
[ModCallback(ModCallbacks.Game Loaded)]
public void OnGameLoaded()
{
    // SML API nutzen
}
```

### 3.2 World Access
- UE Actors abfragen?
- Buildables enumerieren?
- Spielerposition tracken?

**UNKNOWN / NEEDS VERIFICATION**:
- How to get all buildings in range?
- How to position new buildings accurately?
- How to prevent collisions?
- Threading: Game thread vs mod thread?

### 3.3 Communication Options

1. **HTTP Server inside Mod**
   ```
   Satisfactory → Mod HTTP API → MönchiBot (Python)
                POST /api/build
                {"type": "Constructor", "position": {...}}
   ```

2. **WebSocket Connection**
   - Bidirectional communication
   - Real-time updates

3. **Named Pipes / Shared Memory** (nur Windows/Linux)

### 3.4 Vision / Screenshot Integration
- UEViewport capture via C#
- Image export → local file
- Python side: Bild verarbeiten → Vision model API call

**UNKNOWN / NEEDS VERIFICATION**:
- Can screenshots be taken programmatically?
- Is there a viewport buffer access?
- Performance implications?

## 4. Offene Fragen ( critical )

### 4.1 SML API Details
- [ ] Welche C# Klassen sind verfügbar für Gebäudebau?
- [ ] Gibt es BuildAsync() oder PlaceBuildingAsync()?
- [ ] Ist Positionierung in World Space möglich? (Vector3f?)

### 4.2 Threading & Performance
- [ ] SML runs on Game Thread – können HTTP requests blocked werden?
- [ ] Async/await in Mod callbacks unterstützt?

### 4.3 Sicherheit & Validation
- [ ] Kann der Mod Kollisionen prüfen?
- [ ] Gibt es CanPlace() API?

## 5. Empfohlene Vorgehensweise

### Phase C (jetzt): Backend-Prototyp
- FastAPI Server mit Agent Core (Python)
- **Ohne** Real Satisfactory integration
- Mock-Daten für Testing

### Phase D: HTTP Mod Interface Design
1. **Mod side (C#)**:
   - HTTP endpoint /api/observe → JSON world state
   - HTTP endpoint /api/action ← JSON command

2. **Backend side (Python)**:
   - Poll mod for observations
   - Send actions to mod

### Phase E: Integration
- Mod installieren & testen
- Backend mit Mod verbinden
- End-to-end tests

## 6. Sicherheitsprinzipien (Mod side)

- **Input validation**: All HTTP endpoints validate parameters
- **Whitelist actions**: Only allow safe actions initially
- **User confirmation**: Destructive actions need explicit approval

## 7. References / Literature

- Satisfactory Modding Guide (unofficial)
- SML API Documentation (C#)
- Epic Games Unreal Engine 4/5 Blueprint C++ integration
- C# mod callbacks and hooks

---

**Status: ANALYSIS COMPLETE**  
- ✅ Community projects identified
- ❌ No working implementation yet
- ⏳ Phase D (modding API design) needs real SML verification
