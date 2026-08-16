"""Basic Integration Tests für MönchiBot."""

import pytest
import asyncio

from backend.agent import Agent, AUTONOMOUS
from backend.memory import Memory
from backend.tools.registry import create_default_registry
from backend.tools.validator import Validator


class TestMemory:
    """Tests für Memory Layer."""

    def test_add_observation(self):
        mem = Memory()
        before_count = len(mem.short_term)
        mem.add_observation({"test": "data"})
        assert len(mem.short_term) == before_count + 1

    def test_get_active_goals(self):
        mem = Memory()
        mem.goals.append({"status": "active", "description": "Test Goal"})
        goals = mem.get_active_goals()
        assert len(goals) == 1


class TestRegistry:
    """Tests für Tool Registry."""

    def test_list_tools(self):
        registry = create_default_registry()
        tools = registry.list_tools()
        assert "observe_world" in tools

    def test_get_tool(self):
        registry = create_default_registry()
        tool = registry.get_tool("observe_world")
        assert tool is not None


class TestValidator:
    """Tests für Validator."""

    def test_validate_existing_tool(self):
        registry = create_default_registry()
        validator = registry.validator
        result = validator.validate_tool_exists("observe_world")
        assert result.valid

    def test_validate_unknown_tool(self):
        registry = create_default_registry()
        validator = registry.validator
        result = validator.validate_tool_exists("unknown_tool")
        assert not result.valid
        assert "unknown_tool" in result.reason


class TestAgent:
    """Tests für Agent Loop."""

    @pytest.mark.asyncio
    async def test_agent_cycle_autonomous(self):
        """Agent cycle mit AUTONOMOUS level ( fügt hinzu, mock plan executed=0)."""
        agent = Agent()
        agent.set_autonomy_level(AUTONOMOUS)
        
        obs = {"data": 123}
        result = await agent.run_cycle(obs)
        
        assert "verification" in result
        # Mock plan mit blocked=True → actions_executed=0, verification.status="unknown"
        assert result["actions"]["actions_executed"] == 0

    @pytest.mark.asyncio  
    async def test_agent_cycle_observe(self):
        """Agent cycle mit OBSERVE level ( fügt nur hinzu, führt nicht aus)."""
        agent = Agent()  # default: OBSERVE
        
        obs = {"data": 123}
        result = await agent.run_cycle(obs)
        
        assert "verification" in result
        # In OBSERVE mode wird nichts ausgeführt
        assert result["actions"]["actions_executed"] == 0

    def test_agent_registry_has_validator(self):
        """Agent hat Registry mit Validator."""
        agent = Agent()
        assert hasattr(agent.registry, "validator")
        assert agent.validator is not None
