from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Issue:
    type: str
    message: str
    line: int
    severity: Severity
    suggestion: str = ""

@dataclass
class ToolResponse:
    """Formato estándar de respuesta para todas las herramientas."""
    
    tool_name: str
    score: float  # 0-10
    summary: str
    issues: List[Issue]
    details: Dict[str, Any]  # Detalles específicos de cada herramienta
    
    def to_json(self) -> Dict[str, Any]:
        """Convertir a formato JSON."""
        return {
            "tool": self.tool_name,
            "score": self.score,
            "summary": self.summary,
            "issues": [
                {
                    "type": issue.type,
                    "message": issue.message,
                    "line": issue.line,
                    "severity": issue.severity.value,
                    "suggestion": issue.suggestion
                }
                for issue in self.issues
            ],
            "details": self.details,
            "status": "success"  # Indicador de éxito
        } 