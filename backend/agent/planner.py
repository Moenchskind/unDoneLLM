"""Planner Abstraktion fM-CM-<r MM-CM-6nchiBot.

ARCHITEKTUR:
    
    Agent
      M-bM-^FM-^S (requests planning)
    Planner  
      M-bM-^FM-^S (queries LLMProvider)
    LLMProvider (Ollama, OpenAI, etc.)
      M-bM-^FM-^S (API calls)
    LLM Model

DALENFLUSS:

    Observation → think() → thought
                        ↓
                  Planner.run_plan(thought, llm_provider)
                        ↓
                  messages = build_prompt(thought, registry, autonomy_level)
                        ↓
                  llm.chat_completions(messages)  ← UNVERTRAUENSWÜRDIG!
                        ↓
                  response.content (JSON string)
                        ↓
                  StructuredPlan.model_validate_json(response.content) ← BACKEND VALIDIERT!
                        ↓
                  Autonomy Gate ← BACKEND CHECK!
                        ↓
                  Tool Validator ← BACKEND CHECK!
                        ↓
                  Tool Execution

FEHLERBEHANDLUNG:

    - Ollama Error → return error in response
    - JSON ValidationError → return error in response  
    - Autonomy Gate (OBSERVE/ASSISTED) → plan zurück, keine Ausführung
    - Tool Validator → invalid tools abgelehnt
"""

from abc import ABC, abstractmethod
import json
from typing import Dict, List, Any, Optional

from backend.llm.provider import OllamaProvider, LLMError, LLMResponse
from backend.models.schemas import StructuredPlan, PlanAction
from pydantic import ValidationError


class Planner(ABC):
    """Basisinterface fM-CM-<r Planners."""

    @abstractmethod
    async def run_plan(
        self, 
        thought: Dict[str, Any], 
        llm_provider: OllamaProvider,
        registry,
        autonomy_level: str
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def set_llm_provider(self, provider) -> None:
        pass


class LLMPlanner(Planner):
    """LLM-basierter Planner der echte Plans erstellt."""

    def __init__(self, model: str = "qwen3-coder-instruct-262k:latest"):
        self.model = model

    async def run_plan(
        self,
        thought: Dict[str, Any],
        llm_provider: OllamaProvider,
        registry,
        autonomy_level: str
    ) -> Dict[str, Any]:
        """Erstelle echten Plan mit LLM."""
        try:
            messages = self._build_prompt(thought, registry, autonomy_level)
            
            response: LLMResponse = await llm_provider.chat_completions(
                messages=messages,
                model=self.model,
                temperature=0.7
            )
            
            raw_content = response["content"]
            
            try:
                plan = StructuredPlan.model_validate_json(raw_content)
                
                valid_actions, validation_results = self._validate_actions(plan.actions, registry)
                
                return {
                    "plan": plan,
                    "valid_actions": valid_actions,
                    "validation_results": validation_results,
                    "execution_blocked": False
                }
                
            except json.JSONDecodeError as e:
                return {
                    "error": f"Invalid JSON from LLM: {str(e)}",
                    "raw_content": raw_content,
                    "execution_blocked": True
                }
            except ValidationError as e:
                return {
                    "error": f"Validation error in plan structure: {str(e)}",
                    "raw_content": raw_content,
                    "execution_blocked": True
                }
                
        except OllamaError as e:
            return {
                "error": f"Ollama error: {str(e)}",
                "execution_blocked": True
            }

    def _build_prompt(
        self,
        thought: Dict[str, Any],
        registry,
        autonomy_level: str
    ) -> List[Dict[str, str]]:
        """Baue Prompt für LLM."""
        memory_context = thought.get("memory_context", "")
        active_goals_count = thought.get("active_goals_count", 0)
        
        available_tools = registry.available_tools if registry else {}
        
        tools_description = "\n".join([
            f"- {name}: {info['description']}"
            for name, info in available_tools.items()
        ])
        
        schema_example = json.dumps({
            "reasoning": "Kurze Erklärung des Plans",
            "confidence": 0.95,
            "actions": [
                {
                    "tool_name": "observe_world",
                    "parameters": {}
                }
            ]
        }, indent=2, ensure_ascii=False)
        
        return [
            {
                "role": "system",
                "content": f"""Du bist ein Planer fM-CM-<r M=C3=B6nchiBot Satisfactory Agent.
        
VERFüGBARE TOOLS:
{tools_description}

AUTONOMY LEVEL: {autonomy_level}

FORMAT REQUIREMENTS:
- Gib NUR gM-CM-<ltiges JSON zurM-CM-<FCk
- Nutze ausschlieM-C3=9Flich die bereitgestellten Tools
- Leere actions Liste ist erlaubt (keine Aktion)

GIB NUR G=C3=<CLTIGES JSON ZUR=C3=BCCK:
{schema_example}"""
            },
            {
                "role": "user",
                "content": f"""ANALYSIS: {thought.get('analysis', 'No analysis')}
MEMORY CONTEXT: {memory_context}
ACTIVE GOALS COUNT: {active_goals_count}

Erstelle einen strukturierten Plan."""
            }
        ]

    def _validate_actions(
        self,
        actions: List[Any],
        registry
    ) -> tuple:
        """Validiere actions gegen Registry."""
        from backend.tools.validator import ValidationResult
        
        valid_actions = []
        validation_results = []
        
        for action in actions:
            if not hasattr(action, 'tool_name'):
                continue
                
            result = ValidationResult(
                valid=True,
                reason=None
            )
            
            if registry:
                tool_validator = registry.validator if hasattr(registry, 'validator') else None
                if tool_validator:
                    result = tool_validator.validate_action(
                        action.tool_name, 
                        getattr(action, 'parameters', {}) or {}
                    )
            
            validation_results.append({
                "tool": action.tool_name,
                "valid": result.valid,
                "reason": result.reason
            })
            
            if result.valid:
                valid_actions.append(action)
        
        return valid_actions, validation_results

    def set_llm_provider(self, provider) -> None:
        pass


class MockPlanner(Planner):
    """Mock Planner fM-CM-<r testing ohne LLM."""

    def __init__(self, model: str = "qwen3-coder-instruct-262k:latest"):
        self.model = model

    async def run_plan(
        self,
        thought: Dict[str, Any],
        llm_provider: OllamaProvider,
        registry,
        autonomy_level: str
    ) -> Dict[str, Any]:
        """Erstelle Mock-Plan (KEINE echte LLM Integration!)."""
        return {
            "plan": StructuredPlan(
                reasoning="Mock: Kein LLM integriert",
                confidence=None,
                actions=[]
            ),
            "mock": True
        }

    def set_llm_provider(self, provider) -> None:
        self.llm_provider = provider


planner_instance = LLMPlanner()


def get_default_planner() -> Planner:
    """Hole default Planner instance."""
    return planner_instance
