"""Action Validator für MönchiBot."""

from typing import Dict, List, Optional, Any


class ValidationResult:
    """Validierungsergebnis."""

    def __init__(self, valid: bool, reason: Optional[str] = None):
        self.valid = valid
        self.reason = reason

    def to_dict(self) -> Dict[str, Any]:
        return {"valid": self.valid, "reason": self.reason}


class Validator:
    """Validiert Tool Requests vor Ausführung."""

    def __init__(self, registry=None):
        self.registry = registry

    def validate_tool_exists(self, tool_name: str) -> ValidationResult:
        """Prüfe ob Tool registriert ist."""
        if not self.registry or tool_name not in self.registry.list_tools():
            return ValidationResult(False, f"Tool '{tool_name}' nicht registriert")
        return ValidationResult(True)

    def validate_parameters(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> ValidationResult:
        """Prüfe Parameter (simuliert, da keine echte Satisfactory API)."""
        # In realer Implementation:
        # - Prüfe auf benötigte Parameter
        # - Prüfe Typen und Range
        # - Prüfe Kollisionen, Ressourcen etc.

        tool = self.registry.get_tool(tool_name) if self.registry else None
        if not tool:
            return ValidationResult(False, f"Tool '{tool_name}' nicht gefunden")

        # Mock: Alle Parameters für Mock Tools erlaubt
        return ValidationResult(True)

    def validate_action(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> ValidationResult:
        """Komplette Validierung einer Aktion."""
        result1 = self.validate_tool_exists(tool_name)
        if not result1.valid:
            return result1

        return self.validate_parameters(tool_name, parameters)

    def validate_batch(
        self,
        actions: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Validiere mehrere Aktionen."""
        return [
            self.validate_action(a["tool"], a.get("parameters", {}))
            for a in actions
        ]
