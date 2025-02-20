from typing import Dict, Any
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI
import os
import json

class BestPracticesChecker(BaseTool):
    """Tool for checking Python best practices using LLM."""
    
    def __init__(self):
        """Initialize best practices checker."""
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def execute(self, code: str, **kwargs) -> Dict[str, Any]:
        """Check code for best practices using specialized LLM."""
        try:
            prompt = f"""
            You are a Python best practices expert. Analyze this code for adherence to best practices:
            
            ```python
            {code}
            ```
            
            Return a JSON with this EXACT structure:
            {{
                "score": float,  # 0-10 score
                "summary": "brief overall assessment",
                "issues": [
                    {{
                        "type": "practice_type",
                        "message": "detailed explanation",
                        "line": int,
                        "severity": "high|medium|low",
                        "suggestion": "how to fix"
                    }}
                ],
                "details": {{
                    "code_organization": float,  # 0-10 score
                    "maintainability": float,  # 0-10 score
                    "readability": float,  # 0-10 score
                    "modularity": float  # 0-10 score
                }}
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Python best practices expert that responds only in JSON format."},
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
                    suggestion=issue["suggestion"]
                )
                for issue in parsed_response["issues"]
            ]
            
            tool_response = ToolResponse(
                tool_name="best_practices_checker",
                score=parsed_response["score"],
                summary=parsed_response["summary"],
                issues=issues,
                details=parsed_response["details"]
            )
            
            return tool_response.to_json()
            
        except Exception as e:
            return {
                "tool": "best_practices_checker",
                "error": f"Best practices check failed: {str(e)}",
                "score": 0,
                "summary": "Analysis failed",
                "issues": [],
                "details": {}
            }
    
    def get_description(self) -> str:
        return "Checks Python code for adherence to best practices using specialized LLM" 