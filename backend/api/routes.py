"""FastAPI Routes für MönchiBot."""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter(prefix="/api/v1")


class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "qwen3-coder-instruct-262k:latest"


class ThinkRequest(BaseModel):
    observation: Dict[str, Any]


@router.post("/chat")
async def chat(request: ChatRequest):
    """Chat Completion Endpoint."""
    raise NotImplementedError("LLM Integration noch nicht implementiert")


@router.post("/think")
async def think_endpoint(request: ThinkRequest):
    """Agent Denkprozess starten (ohne LLM)."""
    # TODO: Agent.run_cycle() aufrufen
    return {
        "status": "pending",
        "message": "Agent Integration nicht vollständig implementiert",
        " observation_received": len(request.observation)
    }


@router.get("/agent/state")
async def agent_state():
    """Aktuellen Agenten Status abrufen."""
    return {
        "memory_entries": 0,
        "active_goals": [],
        "autonomy_level": "OBSERVE"
    }


@router.get("/tools/available")
async def list_tools():
    """Liste verfügbare Tools."""
    return {"tools": ["observe_world"]}
