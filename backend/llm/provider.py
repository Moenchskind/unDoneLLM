"""LLM Provider Abstraktion für MönchiBot."""

import logging
from abc import ABC, abstractmethod
from typing_extensions import TypedDict
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class Message(TypedDict):
    """Chat message mit role und content."""
    role: str  # "system", "user", "assistant"
    content: str


class LLMResponse(TypedDict):
    """LLM Antwort mit Inhalt und Token-Nutzung."""
    content: str
    token_usage: Optional[Dict[str, int]]
    model: str


class LLMError(Exception):
    """Basis Fehlerklasse für LLM Provider."""


class OllamaError(LLMError):
    """Ollama spezifischer Fehler."""


class LLMProvider(ABC):
    """Basisinterface für alle LLM Provider."""

    @abstractmethod
    async def chat_completions(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> LLMResponse:
        """Erstelle eine Chat-Completion."""
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Liste verfügbare Modelle auf."""
        pass


class OllamaProvider(LLMProvider):
    """Ollama Provider für lokale LLM Ausführung."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3-coder-instruct-262k:latest",
        timeout: float = 30.0
    ):
        """Initialisiere Ollama Provider."""
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def chat_completions(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> LLMResponse:
        """Sende Chat-Anfrage an Ollama API."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                payload = {
                    "model": model or self.model,
                    "messages": messages,
                    "stream": stream
                }
                if temperature is not None and temperature != 0.7:
                    payload["temperature"] = temperature
                if max_tokens is not None:
                    payload["max_tokens"] = max_tokens
                    
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

            return {
                "content": data["message"]["content"],
                "token_usage": {
                    "prompt": data.get("prompt_eval_count", 0),
                    "completion": data.get("eval_count", 0)
                },
                "model": data["model"]
            }
        except httpx.TimeoutException as e:
            logger.error(f"Ollama timeout: {e}")
            raise OllamaError(f"Request to Ollama timed out after {self.timeout}s")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error {e.response.status_code}: {e}")
            raise OllamaError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Ollama connection failed: {e}")
            raise OllamaError(f"Could not connect to Ollama at {self.base_url}")
        except KeyError as e:
            logger.error(f"Invalid Ollama response format: {e}")
            raise OllamaError("Unexpected response format from Ollama")

    async def get_available_models(self) -> List[str]:
        """Hole Liste verfügbarer Modelle von Ollama."""
        import httpx

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()

            return [m["name"] for m in data.get("models", [])]
        except (httpx.TimeoutException, httpx.RequestError) as e:
            logger.error(f"Ollama models request failed: {e}")
            raise OllamaError(f"Could not fetch models from Ollama")
