"""Tool Registry für MönchiBot."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class Tool(ABC):
    """Basis Klasse für alle Tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool Name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool Beschreibung."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Führe Tool aus."""
        pass


class MockObservationTool(Tool):
    """Mock Tool für Weltbeobachtung."""

    @property
    def name(self) -> str:
        return "observe_world"

    @property
    def description(self) -> str:
        return "Beobachte die aktuelle Spielwelt (Mock)"

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Gib Mock-Daten zurück."""
        return {
            "timestamp": "2026-08-16T...",
            "player_position": {"x": 0, "y": 0, "z": 0},
            "buildings": []
        }


class ToolRegistry:
    """Verwaltet alle verfügbaren Tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        from backend.tools.validator import Validator
        self.validator = Validator(self)

    def register(self, tool: Tool) -> None:
        """Registriere ein Tool."""
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """Hole Tool by Name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """Liste alle registrierten Tools."""
        return list(self._tools.keys())

    @property
    def available_tools(self) -> Dict[str, Dict[str, Any]]:
        """Gib Metadata aller Tools zurück."""
        return {
            name: {"description": tool.description}
            for name, tool in self._tools.items()
        }


def create_default_registry() -> ToolRegistry:
    """Erstelle Registry mit Standard-Tools (Mock)."""
    registry = ToolRegistry()
    registry.register(MockObservationTool())
    return registry
