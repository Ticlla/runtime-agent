from typing import Dict, Any
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI
import os
import json

class PerformanceAnalyzer(BaseTool):
    """Tool for performance analysis using LLM."""
    
    def __init__(self):
        """Initialize performance analyzer."""
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def execute(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze performance using specialized LLM."""
        try:
            prompt = f"""
            You are a Python performance expert. Analyze this code for performance issues:
            
            ```python
            {code}
            ```
            
            Return a JSON with this EXACT structure:
            {{
                "score": float,  # 0-10 performance score
                "summary": "brief performance assessment",
                "issues": [
                    {{
                        "type": "performance_issue_type",
                        "message": "detailed explanation",
                        "line": int,
                        "severity": "high|medium|low",
                        "suggestion": "how to optimize",
                        "complexity": "Big O notation if applicable"
                    }}
                ],
                "details": {{
                    "time_complexity": float,  # 0-10 score
                    "space_complexity": float,  # 0-10 score
                    "algorithm_efficiency": float,  # 0-10 score
                    "resource_usage": float,  # 0-10 score
                    "bottlenecks": [
                        {{
                            "type": "bottleneck type",
                            "description": "detailed description"
                        }}
                    ]
                }}
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Python performance expert that responds only in JSON format."},
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
                tool_name="performance_analyzer",
                score=parsed_response["score"],
                summary=parsed_response["summary"],
                issues=issues,
                details=parsed_response["details"]
            )
            
            return tool_response.to_json()
            
        except Exception as e:
            return {
                "tool": "performance_analyzer",
                "error": f"Performance analysis failed: {str(e)}",
                "score": 0,
                "summary": "Analysis failed",
                "issues": [],
                "details": {}
            }
    
    def get_description(self) -> str:
        return "Analyzes Python code for performance issues and optimization opportunities" 