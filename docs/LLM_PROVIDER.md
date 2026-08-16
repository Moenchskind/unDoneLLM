# LLM Provider Architecture – MönchiBot

## 1. Ziel

Sauber getrennte Abstraktion zwischen Agent-Logik und LLM-Anbindung.

```
Agent Core
    ↓ (requests)
LLM Interface
    ↓ (implementation)
Provider Layer
    ↓ (HTTP / WebSocket / API Calls)
LLM Service (Ollama, OpenAI, etc.)
```

## 2. Anforderungen

### Minimalanforderung (Phase C)
- ✅ Ollama als erster Provider
- ✅ Qwen3-Coder-instruct-262k Modell ansprechen
- ✅ Saubere JSON-Payloads senden / empfangen
- ✅ Streaming responses optional

### Erweiterbarkeit (Phase später)
- OpenAI API kompatibel
- Andere Open-Source Models via API oder Local
- LLM-Switch ohne Agent-Code Änderung

## 3. Design

### 3.1 Core Interface (Python)

```python
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

class Message(TypedDict):
    role: str  # "system", "user", "assistant"
    content: str

class LLMResponse(TypedDict):
    content: str
    token_usage: Optional[Dict[str, int]]
    model: str

class LLMProvider(ABC):
    @abstractmethod
    async def chat_completions(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        pass
```

### 3.2 Ollama Provider (konkrete Implementierung)

**API-Endpoint**: `POST /api/chat`  
**Payload**:
```json
{
  "model": "qwen3-coder-instruct-262k:latest",
  "messages": [
    {"role": "user", "content": "..."}
  ],
  "stream": false
}
```

**Response**:
```json
{
  "model": "qwen3-coder-instruct-262k:latest",
  "message": {
    "role": "assistant",
    "content": "..."
  },
  "done": true,
  "total_duration": 1234567890,
  "load_duration": 12345678,
  "prompt_eval_count": 100,
  "eval_count": 20,
  "eval_duration": 123456789
}
```

**Implementierung**:
```python
import httpx

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3-coder-instruct-262k:latest"):
        self.base_url = base_url
        self.model = model

    async def chat_completions(self, ...) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": stream
                }
            )
            data = response.json()
            return {
                "content": data["message"]["content"],
                "token_usage": {
                    "prompt": data.get("prompt_eval_count", 0),
                    "completion": data.get("eval_count", 0)
                },
                "model": data["model"]
            }
```

## 4. Konfiguration

**config.py**:
```python
class LLMConfig(BaseSettings):
    provider: str = "ollama"  # "openai", custom provider...
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3-coder-instruct-262k:latest"
```

## 5. Fehlerbehandlung

- Ollama nicht erreichbar? → Graceful degradation, Error logging
- Modell nicht gefunden → Fallback auf standard model
- API-Error → Semantischer Fehler in Response parsen, nicht nur HTTP status

## 6. Tests (pytest)

```python
import pytest
from backend.llm.ollama import OllamaProvider

@pytest.mark.asyncio
async def test_ollama_provider():
    provider = OllamaProvider()
    result = await provider.chat_completions(
        [{"role": "user", "content": "Hello"}]
    )
    assert len(result["content"]) > 0
```

## 7. Zukünftige Provider

### OpenAI
- API-Key notwendig
- `POST https://api.openai.com/v1/chat/completions`
- Payload: `messages`, `model`, `temperature`

### Custom Provider (HTTP)
- POST /llm/chat
- JSON payload (kompatibel zu Ollama)
- Responseschema anpassbar

## 8. aktueller Status

- ✅ Ollama läuft, Modell vorhanden
- ❌ Kein Provider Code implementiert
- ⏳ Memory & Agent Core nicht implementiert