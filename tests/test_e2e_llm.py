"""E2E Integration Tests mit echtem Ollama (keine Mocks)."""

import pytest
import asyncio

from backend.agent import Agent, AUTONOMOUS, OBSERVE
from backend.llm.provider import OllamaProvider, LLMError
from backend.models.schemas import StructuredPlan


@pytest.fixture
def ollama_provider():
    """Liefert echten OllamaProvider für E2E-Tests."""
    return OllamaProvider(model="qwen3-coder-instruct-262k:latest")


class TestLLME2EIntegration:
    """Echte LLM-E2E-Pipeline Tests mit echtem Ollama."""

    def test_ollama_model_available(self, ollama_provider):
        """Prüft ob das konfigurierte Modell bei Ollama verfügbar ist."""
        models = asyncio.run(ollama_provider.get_available_models())
        
        assert len(models) > 0, "Keine Modelle bei Ollama verfügbar"
        model_name = "qwen3-coder-instruct-262k:latest"
        assert any(model_name in m for m in models), \
            f"Model {model_name} nicht gefunden. Verfügbare: {models}"

    @pytest.mark.asyncio
    async def test_full_llm_pipeline(self, ollama_provider):
        """Testet den kompletten Datenfluss mit echtem Ollama.
        
        Test Observation → Agent/LLMPlanner → OllamaProvider → QwenModel
        → JSON Response → StructuredPlan → Autonomy Gate → Tool Validator
        
        Der Test ruft das ECHTE LLM an (kein Mock!).
        """
        # Setup: Agent mit Registry
        registry = None  # Keine Tests mit Tools in diesem Test
        agent = Agent()
        
        # Echte Observation
        observation = {
            "timestamp": "2026-08-16T10:00:00",
            "player_position": {"x": 0, "y": 0, "z": 0}
        }
        
        # Agent denkt über die Observation nach
        thought = await agent.think(observation)
        
        # LLM planner mit echtem Ollama aufrufen (KEIN MOCK!)
        from backend.agent.planner import get_default_planner
        
        planner = get_default_planner()
        result = await planner.run_plan(
            thought=thought,
            llm_provider=ollama_provider,
            registry=registry,
            autonomy_level=AUTONOMOUS
        )
        
        # Ergebnis prüfen
        assert "plan" in result, "Planner returned no 'plan' field"
        assert isinstance(result["plan"], StructuredPlan), \
            "Result is not a StructuredPlan"
        
        # LLM antwortete mit strukturiertem Plan
        assert len(result["plan"].reasoning) > 0, "No reasoning in plan"

    @pytest.mark.asyncio  
    async def test_llm_pipeline_observed_autonomy(self, ollama_provider):
        """Testet OBSERVE Mode: Plan wird erstellt aber nicht ausgeführt."""
        agent = Agent()
        agent.set_autonomy_level(OBSERVE)
        
        thought = await agent.think({"data": "test"})
        
        from backend.agent.planner import get_default_planner
        planner = get_default_planner()
        result = await planner.run_plan(
            thought=thought,
            llm_provider=ollama_provider,
            registry=None,
            autonomy_level=OBSERVE
        )
        
        # Plan sollte zurückgegeben werden (execution_blocked oder nicht)
        assert "plan" in result

    def test_ollama_unavailable_handling(self):
        """Testet sauberes Fallback wenn Ollama offline ist (falscher Port)."""
        from backend.llm.provider import OllamaProvider, LLMError
        
        # Test mit falschem Port
        provider = OllamaProvider(base_url="http://localhost:9999")
        
        async def run():
            with pytest.raises(LLMError):
                await provider.get_available_models()
        
        asyncio.run(run())
