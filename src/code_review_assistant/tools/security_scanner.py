from typing import Dict, Any
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI
import os
import json

class SecurityScanner(BaseTool):
    """Tool for security analysis using LLM."""
    
    def __init__(self):
        """Initialize security scanner."""
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def execute(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze security using specialized LLM."""
        try:
            prompt = f"""
            You are a Python security expert. Analyze this code for security vulnerabilities:
            
            ```python
            {code}
            ```
            
            Return a JSON with this EXACT structure:
            {{
                "score": float,  # 0-10 security score
                "summary": "brief security assessment",
                "issues": [
                    {{
                        "type": "vulnerability_type",
                        "message": "detailed explanation",
                        "line": int,
                        "severity": "high|medium|low",
                        "suggestion": "how to fix",
                        "cwe_id": "CWE reference"
                    }}
                ],
                "details": {{
                    "input_validation": float,  # 0-10 score
                    "authentication": float,  # 0-10 score
                    "data_exposure": float,  # 0-10 score
                    "resource_management": float  # 0-10 score
                }}
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Python security expert that responds only in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            llm_response = response.choices[0].message.content
            parsed_response = json.loads(llm_response)
            
            # Convertir a formato estándar
            issues = [
                Issue(
                    type=issue["type"],
                    message=issue["message"],
                    line=issue["line"],
                    severity=Severity(issue["severity"]),
                    suggestion=issue.get("suggestion", "")
                )
                for issue in parsed_response["issues"]
            ]
            
            tool_response = ToolResponse(
                tool_name="security_scanner",
                score=parsed_response["score"],
                summary=parsed_response["summary"],
                issues=issues,
                details=parsed_response["details"]
            )
            
            return tool_response.to_json()
            
        except Exception as e:
            return {
                "tool": "security_scanner",
                "error": f"Security scan failed: {str(e)}",
                "score": 0,
                "summary": "Analysis failed",
                "issues": [],
                "details": {}
            }
    
    def get_description(self) -> str:
        return "Analyzes Python code for security vulnerabilities using specialized LLM" 