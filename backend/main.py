"""MönchiBot FastAPI Server.

WARNUNG: Dies ist ein PROTOTYPE.
Die SML/Unreal Integration existiert NICHT!

START:
    
    Die Anwendung läuft aktuell als Host-Python-Prozess.
    Für Containerisierung mit Podman (später):
        
        container build -f Containerfile . -t mönchibot
        podman run -p 8000:8000 mönchibot
        
    ACHTUNG:
        - NO CHANGES TO THIS FILE required for podman
        - Podman setup wird in separatem Schritt konfiguriert
        - Docker ist NICHT die Zielplattform (nur Podman)
        
API ENDPOINTS:
    
    GET  /              Root info
    GET  /health        Health check
    POST /api/v1/think  Agent run_cycle (ohne LLM)
    GET  /api/v1/agent/state  agent status
    GET  /api/v1/tools/available  available tools
    
"""

import uvicorn

from fastapi import FastAPI
from backend.api.routes import router as api_router


app = FastAPI(
    title="MönchiBot Agent Runtime",
    description="Backend API für MönchiBot Satisfactory Agent",
    version="0.1.0"
)


@app.get("/")
async def root():
    """Root Endpoint."""
    return {
        "name": "MönchiBot",
        "status": "INITIALIZING",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health Check Endpoint."""
    return {"status": "ok"}


app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
