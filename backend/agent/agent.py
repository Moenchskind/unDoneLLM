"""MönchiBot Agent Core."""

from typing import List, Dict, Any, Optional
from backend.memory.memory import Memory
from backend.tools.registry import ToolRegistry, create_default_registry
from backend.tools.validator import Validator
from backend.agent.planner import get_default_planner


class Agent:
    """Haupt-Agentenklasse mit Agent Loop."""

    def __init__(
        self,
        memory: Optional[Memory] = None,
        registry: Optional[ToolRegistry] = None,
        validator: Optional[Validator] = None
    ):
        """Initialisiere Agent."""
        self.memory = memory or Memory()
        self.registry = registry or create_default_registry()
        
        # Validator mit Registry verbinden
        self.validator = validator or Validator(self.registry)
        
        # Planner instance
        self.planner = get_default_planner()

        # Konfiguration
        self.autonomy_level = "OBSERVE"  # OBSERVE, ASSISTED, AUTONOMOUS, FULL_AUTONOMOUS

    async def think(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """THINK Phase: Beobachtung analysieren."""
        # Memory aktualisieren
        self.memory.add_observation(observation)

        # Aktive Ziele aus Memory holen
        active_goals = self.memory.get_active_goals()

        return {
            "analysis": f"Beobachtet {len(observation)} Datenpunkte",
            "active_goals_count": len(active_goals),
            "memory_context": self.memory.get_memory_for_prompt()
        }

    async def plan_with_llm(self, thought: Dict[str, Any], llm_provider) -> Dict[str, Any]:
        """PLAN Phase mit echter LLM Integration."""
        return await self.planner.run_plan(
            thought=thought,
            llm_provider=llm_provider,
            registry=self.registry,
            autonomy_level=self.autonomy_level
        )

    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """ACT Phase: Aktionen ausführen basierend auf Autonomiestufe.
        
        WICHTIG:
            - OBSERVE/ASSISTED: keine Ausführung!
            - AUTONOMOUS/FULL_AUTONOMOUS: nur VALIDIERTE actions ausführen
        """
        # Prüfe, ob Ausführung geblockt (OBSERVE / ASSISTED)
        if plan.get("execution_blocked"):
            return {
                "actions_executed": 0,
                "actions_planned": len(plan.get("valid_actions", [])),
                "actions_failed": 0,
                "details": [],
                "blocked": True
            }

        # Prüfe Autonomy Gate (nur AUTONOMOUS führt aus)
        if self.autonomy_level not in ["AUTONOMOUS", "FULL_AUTONOMOUS"]:
            return {
                "actions_executed": 0,
                "actions_planned": len(plan.get("valid_actions", [])),
                "actions_failed": 0,
                "details": [{
                    "tool": a.tool_name if hasattr(a, 'tool_name') else str(a),
                    "plan_only": True,
                    "autonomy_level": self.autonomy_level,
                    "status": "planned"
                } for a in plan.get("valid_actions", [])],
                "blocked": False
            }

        # AUTONOMOUS: Führe validierte Aktionen aus!
        actions = []
        
        for action in plan.get("valid_actions", []):
            tool_name = action.tool_name if hasattr(action, 'tool_name') else None
            
            if not tool_name:
                continue
                
            tool = self.registry.get_tool(tool_name)
            
            if not tool:
                actions.append({
                    "tool": tool_name,
                    "error": "Tool nicht in Registry",
                    "status": "not_found"
                })
                continue

            try:
                # Extract parameters from Pydantic model
                parameters = {}
                if hasattr(action, 'parameters') and action.parameters:
                    parameters = dict(action.parameters)
                    
                action_result = tool.execute(**parameters)
                actions.append({
                    "tool": tool_name,
                    "result": action_result,
                    "status": "success"
                })
            except Exception as e:
                actions.append({
                    "tool": tool_name,
                    "error": str(e),
                    "status": "execution_error"
                })

        return {
            "actions_executed": len([a for a in actions if a["status"] == "success"]),
            "actions_planned": len(actions),
            "actions_failed": len([a for a in actions if a["status"] not in ["success"]]),
            "details": actions
        }

    async def verify(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """VERIFY Phase: Ergebnis prüfen."""
        success_count = action_result.get("actions_executed", 0)
        total_count = len(action_result.get("details", []))

        if total_count == 0:
            status = "unknown"
        elif success_count == total_count:
            status = "success"
        elif success_count > 0:
            status = "partial_success"
        else:
            status = "failure"

        return {
            "status": status,
            "summary": action_result
        }

    async def run_cycle_with_llm(self, observation: Dict[str, Any], llm_provider) -> Dict[str, Any]:
        """Führe EINEN kompletten Agent Cycle mit LLM Integration aus.
        
        OBSERVE → THINK → PLAN (LLM) → ACT → VERIFY
        """
        # 1. OBSERVE → THINGS
        thought = await self.think(observation)

        # 2. THINK → PLAN (mit LLM!)
        plan_result = await self.plan_with_llm(thought, llm_provider)

        # Prüfe auf errors im planning phase
        if "error" in plan_result:
            return {
                "observation": observation,
                "thought": thought,
                "plan_error": plan_result["error"],
                "verification": {"status": "error"}
            }

        # 3. PLAN → ACT
        action_result = await self.act(plan_result)

        # 4. ACT → VERIFY  
        verification = await self.verify(action_result)

        return {
            "observation": observation,
            "thought": thought,
            "plan_result": plan_result,
            "actions": action_result,
            "verification": verification
        }

    async def run_cycle(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Führe EINEN kompletten Agent Cycle aus (OHNE LLM - MOCK).
        
        Die Methode führt genau EINEN Zyklus aus:
        OBSERVE → THINK → PLAN → ACT → VERIFY → return
        
        Ein kontinuierlicher Endlos-Loop ist NICHT Teil dieser Methode.
        Spätere Implementierung könnte einen Scheduler/Trigger hinzufügen,
        der run_cycle() wiederholt aufruft.
        
        Args:
            observation: Wird beim Aufruf verarbeitet (keine automatische Neuaufnahme)
            
        Returns:
            Dict mit allen Phasen-Ergebnissen
        """
        thought = await self.think(observation)

        # PLAN (Mock - kein echtes LLM)
        plan_result = {
            "plan": None,
            "execution_blocked": True
        }

        action_result = await self.act(plan_result)

        verification = await self.verify(action_result)

        return {
            "observation": observation,
            "thought": thought,
            "plan_result": plan_result,
            "actions": action_result,
            "verification": verification
        }

    def set_autonomy_level(self, level: str) -> None:
        """Setze Autonomiestufe für Aktionen.
        
        AUTONOMY LEVELS:
        
        OBSERVE (default):
            - Beobachtungen dürfen verarbeitet und gespeichert werden
            - Keine mutierenden Spielaktionen ausführen
            - Aktionen werden NUR geplant, nicht ausgeführt
            
        ASSISTED:
            - Aktionen dürfen geplant und validiert werden
            - Aktionen werden NICHT automatisch ausgeführt
            - System gibt geplante Aktionen zurück für Benutzer-Freigabe
            
        AUTONOMOUS:
            - Validierte und erlaubte Aktionen DÜRFEN ausgeführt werden
            - Keine menschliche Eingriff erforderlich
            
        FULL_AUTONOMOUS:
            - Wie AUTONOMOUS, aber für zukünftige eigenständige Zielverfolgung
            - Noch KEINE zusätzliche Ziel-Engine implementiert
            - Reserviert für spätere Erweiterungen
        """
        valid_levels = ["OBSERVE", "ASSISTED", "AUTONOMOUS", "FULL_AUTONOMOUS"]
        if level not in valid_levels:
            raise ValueError(f"Ungültige Autonomiestufe: {level}")
        self.autonomy_level = level

    def clear_memory(self) -> None:
        """Lösche Short-term Memory."""
        self.memory.clear_short_term()
