"""Tests für LLM Integration Schema."""

import pytest
import asyncio

from backend.models.schemas import (
    PlanAction, StructuredPlan, PlanResponse
)


class TestLLMIntegrationSchemas:
    """Tests für Pydantic Models der LLM Integration."""

    def test_plan_action_valid(self):
        action = PlanAction(
            tool_name="build",
            parameters={"building_type": "ConstructorMK3"}
        )
        
        assert action.tool_name == "build"
        assert action.parameters["building_type"] == "ConstructorMK3"

    def test_structured_plan_empty_actions(self):
        plan = StructuredPlan(
            reasoning="Keine Aktion erforderlich.",
            confidence=None,
            actions=[]
        )
        
        assert plan.reasoning == "Keine Aktion erforderlich."
        assert plan.confidence is None
        assert len(plan.actions) == 0

    def test_structured_plan_with_actions(self):
        plan = StructuredPlan(
            reasoning="Baue Constructor.",
            confidence=0.95,
            actions=[
                PlanAction(tool_name="build", parameters={"building_type": "ConstructorMK3"})
            ]
        )
        
        assert len(plan.actions) == 1
        assert plan.actions[0].tool_name == "build"
        assert plan.confidence == 0.95

    def test_structured_plan_confidence_range(self):
        p1 = StructuredPlan(reasoning="Test", confidence=0.0, actions=[])
        assert p1.confidence == 0.0
        
        p2 = StructuredPlan(reasoning="Test", confidence=1.0, actions=[])
        assert p2.confidence == 1.0

    def test_plan_response(self):
        plan = StructuredPlan(reasoning="Test", confidence=None, actions=[])
        response = PlanResponse(plan=plan, executed=False)
        
        assert response.executed is False
        assert response.plan == plan


class TestPlanner:
    """Tests für Planner Abstraktion."""

    def test_llm_planner_exists(self):
        """LLMPlannerklasse existiert."""
        from backend.agent.planner import LLMPlanner
        
        planner = LLMPlanner()
        assert planner is not None

    def test_mock_planner_returns_empty_plan(self):
        """MockPlanner returnt leerer Plan."""
        from backend.agent.planner import MockPlanner
        
        planner = MockPlanner()
        
        async def run():
            registry = None
            result = await planner.run_plan(
                {"test": "data"}, 
                llm_provider=None,
                registry=registry,
                autonomy_level="AUTONOMOUS"
            )
            assert "plan" in result
            assert len(result["plan"].actions) == 0
        
        asyncio.run(run())


class TestValidator:
    """Tests für Validator mit Registry."""

    def test_tool_registry_validator(self):
        from backend.tools.registry import create_default_registry
        
        registry = create_default_registry()
        
        assert hasattr(registry, "validator")
        assert registry.validator is not None


class TestLLMIntegration:
    """E2E Tests mit echtem Ollama (optional)."""

    def test_ollama_available(self):
        """Prüft ob Ollama erreichbar ist."""
        import httpx
        try:
            with httpx.Client(timeout=1.0) as client:
                response = client.get("http://localhost:11434/api/tags")
                assert response.status_code == 200, "Ollama nicht erreichbar"
        except (httpx.TimeoutException, httpx.RequestError):
            pytest.skip("Ollama nicht verfügbar - Test übersprungen")

    def test_llm_planner_calls_provider(self):
        """Testet LLMPlanner ruft Provider auf (mit Mock für Test)."""
        from backend.agent.planner import LLMPlanner
        from backend.llm.provider import OllamaProvider
        
        # Wir testen nur die API, nicht den echten Aufruf
        planner = LLMPlanner()
        
        class FakeLLM:
            async def chat_completions(self, messages, model=None, **kwargs):
                return {
                    "content": '{"reasoning":"test","confidence":0.9,"actions":[]}',
                    "model": "test"
                }
        
        # Test durchführen
        import asyncio
        
        async def run():
            result = await planner.run_plan(
                {"analysis": "Test", "memory_context": "", "active_goals_count": 0},
                llm_provider=FakeLLM(),
                registry=None,
                autonomy_level="AUTONOMOUS"
            )
            assert "plan" in result
            assert result["execution_blocked"] is False
        
        asyncio.run(run())

    def test_invalid_json_returns_error(self):
        """Testet ungültiges JSON wird abgelehnt."""
        from backend.agent.planner import LLMPlanner
        import asyncio
        
        class FakeLLM:
            async def chat_completions(self, messages, model=None, **kwargs):
                return {"content": "this is not json", "model": "test"}
        
        async def run():
            planner = LLMPlanner()
            result = await planner.run_plan(
                {"analysis": "Test"}, llm_provider=FakeLLM(), registry=None,
                autonomy_level="AUTONOMOUS"
            )
            assert "error" in result
            assert result["execution_blocked"] is True
        
        asyncio.run(run())

    def test_empty_actions_allowed(self):
        """Testet leeres actions-Array ist gültig."""
        from backend.agent.planner import LLMPlanner
        import asyncio
        
        class FakeLLM:
            async def chat_completions(self, messages, model=None, **kwargs):
                return {
                    "content": '{"reasoning":"keine Aktion","actions":[]}',
                    "model": "test"
                }
        
        async def run():
            planner = LLMPlanner()
            result = await planner.run_plan(
                {"analysis": "Test"}, llm_provider=FakeLLM(), registry=None,
                autonomy_level="AUTONOMOUS"
            )
            assert len(result["plan"].actions) == 0
        
        asyncio.run(run())

    def test_unknown_tool_rejected(self):
        """Testet unbekanntes Tool wird abgelehnt."""
        from backend.agent.planner import LLMPlanner
        from backend.tools.registry import create_default_registry
        import asyncio
        
        registry = create_default_registry()
        
        class FakeLLM:
            async def chat_completions(self, messages, model=None, **kwargs):
                return {
                    "content": '{"reasoning":"test","actions":[{"tool_name":"unknown_tool"}]}',
                    "model": "test"
                }
        
        async def run():
            planner = LLMPlanner()
            result = await planner.run_plan(
                {"analysis": "Test"}, llm_provider=FakeLLM(), registry=registry,
                autonomy_level="AUTONOMOUS"
            )
            # Validator sollte das unbekannte Tool ablehnen
            assert len(result.get("valid_actions", [])) == 0
        
        asyncio.run(run())
