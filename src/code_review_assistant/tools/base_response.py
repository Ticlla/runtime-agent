from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json

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
    cwe_id: str = ""

    def to_dict(self):
        return {
            "type": self.type,
            "message": self.message,
            "line": self.line,
            "severity": self.severity.value,
            "suggestion": self.suggestion,
            "cwe_id": self.cwe_id
        }

class ToolResponse:
    """Base class for tool responses."""
    
    def __init__(
        self,
        tool_name: str,
        score: float,
        summary: str,
        issues: List[Issue],
        details: Dict[str, float] = None,
        language: str = None,
        diagnostic_info: Dict[str, Any] = None
    ):
        """
        Initialize tool response.
        
        Args:
            tool_name: Name of the tool
            score: Overall score (0-10)
            summary: Summary of the analysis
            issues: List of issues found
            details: Detailed scores for specific criteria
            language: Detected programming language
            diagnostic_info: Additional diagnostic information
        """
        self.tool_name = tool_name
        self.score = score
        self.summary = summary
        self.issues = issues
        self.details = details or {}
        self.language = language
        self.diagnostic_info = diagnostic_info or {}
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps({
            "tool_name": self.tool_name,
            "score": self.score,
            "summary": self.summary,
            "issues": [issue.to_dict() for issue in self.issues],
            "details": self.details,
            "language": self.language,
            "diagnostic_info": self.diagnostic_info
        }, indent=2) 