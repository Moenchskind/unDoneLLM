"""Konfiguration für MönchiBot."""

from pydantic import BaseModel, Field


class Config(BaseModel):
    """Hauptkonfigurationsklasse."""
    
    class LLMConfig(BaseModel):
        provider: str = "ollama"
        base_url: str = "http://localhost:11434"
        model: str = "qwen3-coder-instruct-262k:latest"
    
    class AgentConfig(BaseModel):
        autonomy_level: str = "OBSERVE"  # OBSERVE, ASSISTED, AUTONOMOUS, FULL_AUTONOMOUS
    
    llm: LLMConfig = Field(default_factory=LLMConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)


config = Config()

if __name__ == "__main__":
    print(config.model_dump_json(indent=2))
