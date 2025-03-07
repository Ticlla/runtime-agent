import json
import os
import traceback
import datetime
from typing import Dict, Any, List, Optional
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI

class BestPracticesChecker(BaseTool):
    """Tool for checking Python best practices using LLM."""
    
    def __init__(self):
        """Initialize best practices checker."""
        super().__init__()  # Llamar al constructor base sin argumentos
        self.name = "best_practices_checker"
        self.description = "Checks code against best practices"
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def execute(self, input_data: str) -> str:
        """
        Execute the best practices checker.
        
        Args:
            input_data: JSON string with code data
            
        Returns:
            JSON string with analysis results
        """
        try:
            # Parse input data
            data = json.loads(input_data)
            
            # Check if this is DFF format
            if "dff_data" in data:
                return await self._check_dff_practices(data)
            
            # Handle direct code input
            elif "code" in data:
                code = data["code"]
                filename = data.get("filename", "unknown.txt")
                
                # Analyze code
                result = self._check_practices(code, filename)
                
                # Return result as JSON string
                return json.dumps({
                    "tool_name": "best_practices_checker",
                    "score": result["score"],
                    "issues": result["issues"],
                    "summary": result["summary"]
                })
            
            else:
                return json.dumps({
                    "tool_name": "best_practices_checker",
                    "error": "No code or DFF data provided",
                    "score": 0,
                    "issues": []
                })
        
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Error in BestPracticesChecker.execute: {str(e)}")
            print(error_traceback)
            
            return json.dumps({
                "tool_name": "best_practices_checker",
                "error": str(e),
                "score": 0,
                "issues": []
            })
    
    def _check_practices(self, code: str, filename: str) -> Dict[str, Any]:
        """Check code against best practices."""
        good_practices = []
        issues = []
        
        # Verificar tipos de datos
        if ": " in code and " -> " in code:
            good_practices.append("Uses type hints")
        else:
            issues.append({
                "type": "missing_type_hints",
                "message": "Code does not use type hints",
                "severity": "medium"
            })
        
        # Verificar docstrings
        if '"""' in code or "'''" in code:
            good_practices.append("Has docstrings")
            # Bonus por docstring completo
            if "Args:" in code and "Returns:" in code:
                good_practices.append("Has complete docstring")
            if "Examples:" in code:
                good_practices.append("Has examples in docstring")
        else:
            issues.append({
                "type": "missing_docstrings",
                "message": "Code does not have docstrings",
                "severity": "medium"
            })
        
        # Verificar list comprehensions
        if any(line.strip().startswith("[") and "for" in line and "in" in line and "]" in line 
               for line in code.split("\n")):
            good_practices.append("Uses list comprehensions")
        
        # Calcular puntuación
        score = 5.0  # Base score
        score += len(good_practices) * 1.0  # +1 por cada buena práctica
        score -= len(issues) * 0.5  # -0.5 por cada problema
        
        return {
            "score": max(0, min(10, score)),
            "good_practices": good_practices,
            "issues": issues,
            "summary": f"Found {len(good_practices)} good practices and {len(issues)} issues."
        }
    
    async def _check_dff_practices(self, data: Dict[str, Any]) -> str:
        """
        Check DFF data against best practices.
        
        Args:
            data: DFF data
            
        Returns:
            JSON string with analysis results
        """
        try:
            dff_data = data["dff_data"]
            files = dff_data.get("files", [])
            files_analyzed = 0
            results = []
            
            for file_info in files:
                filename = file_info.get("fileName", "unknown.txt")
                status = file_info.get("status", "UNKNOWN")
                
                code = None
                if status == "ADDED":
                    code = "\n".join(file_info.get("codeContext", {}).get("after", []))
                elif status == "MODIFIED":
                    code = "\n".join(file_info.get("codeContext", {}).get("after", []))
                
                if code:
                    # Analyze this specific file
                    file_result = self._check_practices(code, filename)
                    file_result["filename"] = filename
                    file_result["status"] = status
                    
                    # Check for improvements if this is a modified file
                    if status == "MODIFIED":
                        before_code = "\n".join(file_info.get("codeContext", {}).get("before", []))
                        improvements = self._detect_improvements(before_code, code)
                        file_result["improvements"] = improvements
                    
                    results.append(file_result)
                    files_analyzed += 1
            
            return json.dumps({
                "tool_name": "best_practices_checker",
                "format": "dff",
                "files_analyzed": files_analyzed,
                "results": results
            })
        
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Error in _check_dff_practices: {str(e)}")
            print(error_traceback)
            
            return json.dumps({
                "tool_name": "best_practices_checker",
                "error": str(e),
                "score": 0,
                "issues": []
            })
    
    def _is_code_simplified(self, before_code: str, after_code: str) -> bool:
        """
        Check if code was simplified based on multiple factors.
        """
        # Menos líneas efectivas (ignorando comentarios y docstrings)
        before_lines = len([
            l for l in before_code.split("\n")
            if l.strip() and not l.strip().startswith(("#", "\"\"\"", "'''"))
        ])
        after_lines = len([
            l for l in after_code.split("\n")
            if l.strip() and not l.strip().startswith(("#", "\"\"\"", "'''"))
        ])
        
        # Menos variables locales
        before_vars = len([
            l for l in before_code.split("\n")
            if "=" in l and not l.strip().startswith(("#", "\"\"\"", "'''"))
        ])
        after_vars = len([
            l for l in after_code.split("\n")
            if "=" in l and not l.strip().startswith(("#", "\"\"\"", "'''"))
        ])
        
        # Menos niveles de indentación
        before_indent = max(
            len(l) - len(l.lstrip()) for l in before_code.split("\n")
        )
        after_indent = max(
            len(l) - len(l.lstrip()) for l in after_code.split("\n")
        )
        
        # Menos bucles explícitos
        before_loops = before_code.count("for ") + before_code.count("while ")
        after_loops = after_code.count("for ") + after_code.count("while ")
        
        # Menos estructuras de control anidadas
        before_control = len([
            l for l in before_code.split("\n")
            if any(x in l for x in ["if ", "for ", "while ", "try:"])
        ])
        after_control = len([
            l for l in after_code.split("\n")
            if any(x in l for x in ["if ", "for ", "while ", "try:"])
        ])
        
        # El código se considera simplificado si mejora en cualquiera de estos aspectos
        return (after_lines < before_lines or 
                after_vars < before_vars or 
                after_indent < before_indent or
                after_loops < before_loops or
                after_control < before_control)

    def _detect_improvements(self, before_code: str, after_code: str) -> List[Dict[str, str]]:
        """Detect improvements between code versions."""
        improvements = []
        
        # Detectar type hints añadidos
        if (": " not in before_code and ": " in after_code) or \
           (" -> " not in before_code and " -> " in after_code):
            improvements.append({
                "type": "type_hints_added",
                "description": "Type hints were added to the code"
            })
        
        # Detectar docstrings añadidos
        if ('"""' not in before_code and '"""' in after_code) or \
           ("'''" not in before_code and "'''" in after_code):
            improvements.append({
                "type": "docstring_added",
                "description": "Docstrings were added to the code"
            })
        
        # Detectar list comprehension
        has_for_loop = "for" in before_code and "append" in before_code
        has_list_comp = any(
            "[" in line and "for" in line and "in" in line and "]" in line 
            for line in after_code.split("\n")
        )
        
        if has_for_loop and has_list_comp:
            improvements.append({
                "type": "list_comprehension_used",
                "description": "List comprehensions were used to simplify code"
            })
        
        # Detectar simplificación de código usando múltiples métricas
        if self._is_code_simplified(before_code, after_code):
            improvements.append({
                "type": "code_simplified",
                "description": "Code was simplified through better structure and fewer constructs"
            })
        
        return improvements
    
    def get_description(self) -> str:
        return "Checks Python code for adherence to best practices using specialized LLM" 