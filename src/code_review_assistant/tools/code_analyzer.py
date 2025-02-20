from typing import Dict, Any
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI
import ast
import os
import json

class CodeAnalyzer(BaseTool):
    """Tool for analyzing code structure and complexity."""
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def execute(self, code: str, **kwargs) -> Dict[str, Any]:
        """Analyze code structure and complexity."""
        try:
            # 1. Análisis estático básico
            tree = ast.parse(code)
            static_analysis = self._perform_static_analysis(tree)
            
            # 2. Análisis con LLM
            prompt = f"""
            You are a Python code analysis expert. Analyze this code and its metrics:

            Code:
            ```python
            {code}
            ```

            Static Analysis Results:
            {json.dumps(static_analysis, indent=2)}

            Return a JSON with this EXACT structure:
            {{
                "score": float,  # 0-10 overall code quality score
                "summary": "brief overall assessment",
                "issues": [
                    {{
                        "type": "issue_type",
                        "message": "detailed explanation",
                        "line": int,
                        "severity": "high|medium|low",
                        "suggestion": "how to fix"
                    }}
                ],
                "details": {{
                    "code_structure": {{
                        "functions": int,
                        "classes": int,
                        "complexity": float
                    }},
                    "maintainability": float,  # 0-10 score
                    "readability": float,  # 0-10 score
                    "modularity": float,  # 0-10 score
                    "patterns": [
                        {{
                            "name": "pattern name",
                            "description": "pattern description"
                        }}
                    ]
                }}
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a Python code analysis expert that responds only in JSON format."},
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
                tool_name="code_analyzer",
                score=parsed_response["score"],
                summary=parsed_response["summary"],
                issues=issues,
                details=parsed_response["details"]
            )
            
            return tool_response.to_json()
            
        except Exception as e:
            return {
                "tool": "code_analyzer",
                "error": f"Analysis failed: {str(e)}",
                "score": 0,
                "summary": "Analysis failed",
                "issues": [],
                "details": {}
            }
    
    def _perform_static_analysis(self, tree: ast.AST) -> Dict[str, Any]:
        """Perform static code analysis."""
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "args": len(node.args.args)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "line": node.lineno
                })
        
        return {
            "total_functions": len(functions),
            "total_classes": len(classes),
            "functions": functions,
            "classes": classes
        }
    
    def get_description(self) -> str:
        return "Analyzes Python code structure, complexity and identifies potential issues" 