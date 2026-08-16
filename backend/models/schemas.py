"""Pydantic Modelle für API Requests/Responses."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """Chat message."""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message text")


class ChatRequest(BaseModel):
    """Anfrage für Chat Completion."""
    messages: List[Message] = Field(..., description="Chat history")
    model: Optional[str] = Field(None, description="Model name override")
    temperature: float = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, description="Max output tokens")


class TokenUsage(BaseModel):
    """Token Nutzungsstatistik."""
    prompt: int = Field(default=0, description=" Prompt tokens used")
    completion: int = Field(default=0, description="Completion tokens used")


class ChatResponse(BaseModel):
    """Chat Completion Antwort."""
    content: str = Field(..., description="ASSISTANT response text")
    token_usage: Optional[TokenUsage] = Field(None, description="Token usage stats")
    model: str = Field(..., description="Used model name")


class ObservationData(BaseModel):
    """Weltbeobachtung (Mock/Demo Daten)."""
    timestamp: str
    player_position: Dict[str, float]
    player_rotation: Optional[Dict[str, float]] = None
    buildings: List[Dict[str, Any]] = []
    inventory: Dict[str, int] = {}
    power_status: Dict[str, Any] = {}


class ToolRequest(BaseModel):
    """Tool Aufruf Request."""
    tool_name: str
    parameters: Dict[str, Any]


class ValidationResult(BaseModel):
    """Validierungsergebnis."""
    valid: bool
    reason: Optional[str] = None


class AgentResponse(BaseModel):
    """Aggregator Antwort mit Plan/Action."""
    thought: str
    plan: List[Dict[str, Any]]
    actions: List[ToolRequest]
    validation_results: List[ValidationResult]


# =========================================
# LLM Integration Models (Phase D+)
# =========================================

class PlanAction(BaseModel):
    """Einzelaktion aus LLM-Plan."""
    tool_name: str
    parameters: Dict[str, Any]


class StructuredPlan(BaseModel):
    """Strukturierter Plan von LLM.
    
    WICHTIG: Backend validiert IMMER!
    Das LLM ist unvertrauenswürdig - Always validate!
    """
    reasoning: str
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    actions: List[PlanAction]


class PlanResponse(BaseModel):
    """Response von Planner mit LLM Integration."""
    plan: StructuredPlan
    executed: bool = False  # Wurden Aktionen ausgeführt?
    execution_result: Optional[Dict[str, Any]] = None
