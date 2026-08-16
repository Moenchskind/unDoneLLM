"""Simple Memory Implementation für MönchiBot."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os

logger = logging.getLogger(__name__)


class Memory:
    """In-Memory Storage mit Erweiterbarkeit für SQLite.
    
    KATEGORIEN:
        
        - short_term: Aktuelle Session, wird in long_term kopiert
        - long_term: Persistiert in JSON
        - knowledge: Fakten (z.B. Spielmechaniken)
        - observations: Beobachtungen pro Timestamp
        - goals: Aktive Ziele
        - tasks: Teilzielen zu aktuellen Goals
        - events: Historie wichtiger Ereignisse
        
    PERSISTENZ:
        
        Aktuell: JSON files in data/ directory
        Zukunft: SQLite Migration (dokumentiert, nicht implementiert)
        
        Warnung: Memory ist noch KEINE vollständige Datenbank-Lösung.
        Sie dient als protoypische Speicherung für testing.
    """

    def __init__(self, data_path: str = "./data/memory"):
        """Initialisiere Memory Layer."""
        self.data_path = data_path
        self.short_term: List[Dict[str, Any]] = []
        self.long_term: List[Dict[str, Any]] = []
        self.knowledge: Dict[str, Any] = {}
        self.observations: List[Dict[str, Any]] = []
        self.goals: List[Dict[str, Any]] = []
        self.tasks: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []

        os.makedirs(data_path, exist_ok=True)

    def add_observation(self, observation: Dict[str, Any]) -> None:
        """Füge Beobachtung hinzu."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **observation
        }
        self.short_term.append(entry)
        self.observations.append(entry)

    def retrieve_observations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Hole Neueste Beobachtungen."""
        return self.short_term[-limit:]

    def add_goal(self, goal: Dict[str, Any]) -> None:
        """Füge Ziel hinzu."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **goal
        }
        self.goals.append(entry)
        self.long_term.append(entry)

    def get_active_goals(self) -> List[Dict[str, Any]]:
        """Hole aktive Ziele."""
        return [g for g in self.goals if g.get("status") != "completed"]

    def add_task(self, task: Dict[str, Any]) -> None:
        """Füge Aufgabe hinzu."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **task
        }
        self.tasks.append(entry)
        self.long_term.append(entry)

    def get_memory_for_prompt(self) -> str:
        """Generiere Memory Context für Prompt."""
        prompt_parts = []

        if self.goals:
            prompt_parts.append("\n=== ACTIVE GOALS ===")
            for goal in self.get_active_goals()[:5]:
                prompt_parts.append(f"- {goal.get('description', 'Unknown')}")

        if self.observations:
            prompt_parts.append("\n=== Recent Observations ===")
            for obs in self.retrieve_observations(3):
                timestamp = obs.get("timestamp", "unknown")
                prompt_parts.append(f"[{timestamp}] {obs}")

        return "\n".join(prompt_parts)

    def clear_short_term(self) -> None:
        """Lösche Short-term Memory."""
        self.short_term.clear()

    def save_to_file(self, filename: str = "memory.json") -> None:
        """Speichere Memory in Datei (Mock)."""
        data = {
            "long_term": self.long_term,
            "knowledge": self.knowledge
        }
        filepath = os.path.join(self.data_path, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self, filename: str = "memory.json") -> None:
        """Lade Memory aus Datei (Mock)."""
        filepath = os.path.join(self.data_path, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Memory file does not exist: {filepath}")
            return
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            
            self.long_term = data.get("long_term", [])
            self.knowledge = data.get("knowledge", {})
            logger.info(f"Loaded {len(self.long_term)} long-term entries")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load memory from {filepath}: {e}")
            # Fallback: leeres Memory
            self.long_term = []
            self.knowledge = {}
