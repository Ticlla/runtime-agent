from typing import Dict, List, Any, Optional
import json
from ai_agent_framework.core.agent_runtime import AgentRuntime
from ai_agent_framework.core.tools.tools_manager import ToolsManager
from code_review_assistant.tools import (
    CodeAnalyzer,
    StyleChecker,
    SecurityScanner,
    PerformanceAnalyzer,
    BestPracticesChecker
)
from redis import Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import load_config
import datetime
import traceback

# Esquema esperado para validación de resultados
EXPECTED_SCHEMA = {
    "score": float,
    "summary": str,
    "issues": List[Dict[str, Any]],
    "metrics": Dict[str, float],
    "recommendations": List[str]
}

class CodeReviewAssistant:
    """Assistant for code review and analysis."""
    
    def __init__(self, config: Dict = None):
        """Initialize the assistant."""
        self.config = config or {}
        self.tools_manager = ToolsManager()
    
    async def initialize(self):
        """Initialize the assistant and load tools."""
        try:
            print("Initializing CodeReviewAssistant...")
            
            # Inicializar y registrar todas las herramientas disponibles
            from .tools.code_analyzer import CodeAnalyzer
            from .tools.best_practices_checker import BestPracticesChecker
            from .tools.security_scanner import SecurityScanner
            from .tools.performance_analyzer import PerformanceAnalyzer
            from .tools.style_checker import StyleChecker
            
            # Registrar herramientas en el gestor
            self.tools_manager.register("code_analyzer", CodeAnalyzer())
            self.tools_manager.register("best_practices_checker", BestPracticesChecker())
            self.tools_manager.register("security_scanner", SecurityScanner())
            self.tools_manager.register("performance_analyzer", PerformanceAnalyzer())
            self.tools_manager.register("style_checker", StyleChecker())
            
            print(f"CodeReviewAssistant initialized successfully with {len(self.tools_manager.get_tools())} tools")
            print(f"Available tools: {', '.join(self.tools_manager.get_tools().keys())}")
        except Exception as e:
            print(f"Error initializing CodeReviewAssistant: {str(e)}")
            print(traceback.format_exc())
    
    async def review_code(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review code and provide analysis.
        
        Args:
            code_data: Dictionary with code and metadata
            
        Returns:
            Dict with analysis results
        """
        try:
            # Extract code and metadata
            code = code_data.get("code", "")
            filename = code_data.get("filename", "unknown.txt")
            
            if not code:
                return {
                    "error": "No code provided for analysis",
                    "score": 0,
                    "summary": "Analysis could not be performed"
                }
            
            # Analyze code using all available tools
            results = {}
            
            # Get all tools
            tools = self.tools_manager.get_tools()
            
            # Execute each tool
            for tool_name, tool in tools.items():
                try:
                    print(f"Executing tool: {tool_name}")
                    tool_input = json.dumps({
                        "code": code,
                        "filename": filename
                    })
                    tool_result_json = await tool.execute(tool_input)
                    tool_result = json.loads(tool_result_json)
                    results[tool_name] = tool_result
                except Exception as e:
                    print(f"Error executing tool {tool_name}: {str(e)}")
                    results[tool_name] = {
                        "error": str(e),
                        "score": 0
                    }
            
            # Synthesize results
            final_result = self._synthesize_results(results)
            
            return final_result
        
        except Exception as e:
            print(f"Error in review_code: {str(e)}")
            print(traceback.format_exc())
            
            return {
                "error": str(e),
                "score": 0,
                "summary": "Analysis could not be performed"
            }
    
    async def analyze_diff(self, dff_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza un diff en formato DFF.
        
        Args:
            dff_data: Datos del diff en formato DFF
            
        Returns:
            Dict con los resultados del análisis
        """
        try:
            # Imprimir los datos recibidos para depuración
            print(f"DFF data received: {json.dumps(dff_data, indent=2)}")
            
            # Verificar que los datos DFF son válidos
            if not dff_data or "files" not in dff_data:
                print("Invalid DFF data: 'files' key not found")
                return {
                    "error": "Invalid DFF data format - 'files' key not found",
                    "score": 0,
                    "summary": "Analysis could not be performed"
                }
            
            files = dff_data.get("files", [])
            if not files:
                print("Invalid DFF data: 'files' array is empty")
                return {
                    "error": "Invalid DFF data format - 'files' array is empty",
                    "score": 0,
                    "summary": "Analysis could not be performed"
                }
            
            # Analizar cada archivo en el diff
            results = []
            for file_info in files:
                filename = file_info.get("fileName", "unknown.txt")
                status = file_info.get("status", "UNKNOWN")
                
                # Obtener el código según el estado del archivo
                code = None
                before_code = None
                
                if "codeContext" in file_info:
                    if status == "ADDED" and "after" in file_info["codeContext"]:
                        code = "\n".join(file_info["codeContext"]["after"])
                    elif status == "MODIFIED":
                        if "after" in file_info["codeContext"]:
                            code = "\n".join(file_info["codeContext"]["after"])
                        if "before" in file_info["codeContext"]:
                            before_code = "\n".join(file_info["codeContext"]["before"])
                
                if code:
                    # Analizar el código de este archivo
                    file_result = await self._analyze_file_code(code, filename, before_code)
                    file_result["filename"] = filename
                    file_result["status"] = status
                    results.append(file_result)
                else:
                    print(f"No code found for file: {filename}, status: {status}")
            
            if not results:
                return {
                    "error": "No valid code found in DFF data",
                    "score": 0,
                    "summary": "Analysis could not be performed"
                }
            
            # Calcular puntuación global y generar resumen
            avg_score = sum(r.get("score", 0) for r in results) / len(results)
            total_issues = sum(len(r.get("issues", [])) for r in results)
            
            return {
                "format": "dff",
                "files_analyzed": len(results),
                "average_score": avg_score,
                "total_issues": total_issues,
                "results": results,
                "summary": f"Analyzed {len(results)} files with an average score of {avg_score:.1f} and found {total_issues} issues."
            }
        
        except Exception as e:
            print(f"Error in analyze_diff: {str(e)}")
            print(traceback.format_exc())
            
            return {
                "error": f"Error analyzing DFF data: {str(e)}",
                "score": 0,
                "summary": "Analysis could not be performed"
            }
    
    async def _analyze_file_code(self, code: str, filename: str, before_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Analiza el código de un archivo individual.
        
        Args:
            code: Código fuente
            filename: Nombre del archivo
            before_code: Código anterior (opcional, para comparación)
            
        Returns:
            Dict con los resultados del análisis
        """
        # Usar las herramientas disponibles para analizar el código
        results = {}
        issues = []
        improvements = []
        
        # Obtener todas las herramientas
        tools = self.tools_manager.get_tools()
        
        # Ejecutar cada herramienta
        for tool_name, tool in tools.items():
            try:
                print(f"Executing tool {tool_name} for file {filename}")
                
                # Preparar input según si tenemos código anterior o no
                if before_code and hasattr(tool, 'supports_diff') and tool.supports_diff:
                    tool_input = json.dumps({
                        "code": code,
                        "filename": filename,
                        "before_code": before_code
                    })
                else:
                    tool_input = json.dumps({
                        "code": code,
                        "filename": filename
                    })
                
                # Ejecutar la herramienta
                tool_result_json = await tool.execute(tool_input)
                tool_result = json.loads(tool_result_json)
                
                # Incorporar resultados
                results[tool_name] = tool_result
                
                # Recopilar problemas
                if "issues" in tool_result:
                    issues.extend(tool_result["issues"])
                
                # Recopilar mejoras (si es una comparación)
                if before_code and "improvements" in tool_result:
                    improvements.extend(tool_result["improvements"])
            
            except Exception as e:
                print(f"Error executing tool {tool_name} for file {filename}: {str(e)}")
                results[tool_name] = {
                    "error": str(e),
                    "score": 0
                }
        
        # Calcular puntuación basada en los resultados
        score = 7.0  # Puntuación base
        
        # Ajustar según los problemas encontrados
        critical_issues = sum(1 for i in issues if i.get("severity") == "high")
        medium_issues = sum(1 for i in issues if i.get("severity") == "medium")
        low_issues = sum(1 for i in issues if i.get("severity") == "low")
        
        score -= critical_issues * 1.5
        score -= medium_issues * 0.5
        score -= low_issues * 0.2
        
        # Limitar la puntuación entre 0 y 10
        score = max(0, min(10, score))
        
        # Preparar resultado
        result = {
            "score": score,
            "issues": issues,
            "details": results,
            "summary": f"Found {len(issues)} issues ({critical_issues} critical, {medium_issues} medium, {low_issues} low)"
        }
        
        # Añadir mejoras si hay código anterior
        if before_code and improvements:
            result["improvements"] = improvements
        
        return result
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """Calculate overall score from results."""
        # Default score
        score = 5.0
        
        # Calculate based on tool scores
        tool_scores = []
        
        for tool_name, tool_result in results.items():
            if isinstance(tool_result, dict) and "score" in tool_result:
                tool_scores.append(tool_result["score"])
        
        # Average scores if we have any
        if tool_scores:
            score = sum(tool_scores) / len(tool_scores)
        
        return round(score, 2)
    
    def _calculate_maintainability_score(self, results: Dict) -> float:
        """Calculate maintainability score from results."""
        # Default score
        score = 5.0
        
        # Calculate based on analysis results
        if "code_analyzer" in results and isinstance(results["code_analyzer"], dict):
            # Extract complexity
            complexity = results["code_analyzer"].get("details", {}).get("code_structure", {}).get("complexity", "medium")
            
            # Assign score based on complexity
            if complexity == "low":
                score = 8.0
            elif complexity == "medium":
                score = 5.0
            elif complexity == "high":
                score = 3.0
        
        return round(score, 2)
    
    def _calculate_readability_score(self, results: Dict) -> float:
        """Calculate readability score from results."""
        # Default score
        score = 5.0
        
        # Calculate based on style results
        if "style_checker" in results and isinstance(results["style_checker"], dict):
            score = results["style_checker"].get("score", 5.0)
        
        return round(score, 2)
    
    def _calculate_reliability_score(self, results: Dict) -> float:
        """Calculate reliability score from results."""
        # Default score
        score = 5.0
        
        # Calculate based on issues count
        total_issues = sum(
            len(tool_result.get("issues", []))
            for tool_name, tool_result in results.items()
            if isinstance(tool_result, dict)
        )
        
        if total_issues == 0:
            score = 10.0
        else:
            # Deduct points for each issue, with a minimum of 1.0
            score = max(1.0, 10.0 - total_issues * 0.5)
        
        return round(score, 2)
    
    def _extract_critical_issues(self, results: Dict) -> List[Dict]:
        """Extract critical issues from all categories."""
        critical_issues = []
        
        # Extract from each tool's results
        for tool_name, tool_result in results.items():
            if not isinstance(tool_result, dict):
                continue
            
            for issue in tool_result.get("issues", []):
                if issue.get("severity", "").lower() in ["high", "critical"]:
                    critical_issues.append({
                        "description": issue.get("message", ""),
                        "impact": f"Critical {tool_name} issue",
                        "solution": issue.get("suggestion", "Review and fix the issue"),
                        "file": issue.get("file", "unknown"),
                        "line": issue.get("line", "N/A"),
                        "tool": tool_name
                    })
        
        return critical_issues
    
    def _extract_recommendations(self, results: Dict) -> List[Dict]:
        """Extrae recomendaciones basadas en los problemas encontrados."""
        recommendations = []
        
        # Función auxiliar para determinar si hay issues en una herramienta
        def has_issues(tool_result):
            if not isinstance(tool_result, dict):
                return False
            return bool(tool_result.get("issues", []))
        
        # Recomendaciones basadas en problemas de estilo
        if "style_checker" in results and has_issues(results["style_checker"]):
            recommendations.append({
                "description": "Improve code style following language conventions",
                "priority": "Medium"
            })
        
        # Recomendaciones basadas en problemas de seguridad
        if "security_scanner" in results and has_issues(results["security_scanner"]):
            recommendations.append({
                "description": "Address security vulnerabilities",
                "priority": "High"
            })
        
        # Recomendaciones basadas en problemas de rendimiento
        if "performance_analyzer" in results and has_issues(results["performance_analyzer"]):
            recommendations.append({
                "description": "Optimize code performance",
                "priority": "Medium"
            })
        
        # Recomendaciones basadas en mejores prácticas
        if "best_practices_checker" in results and has_issues(results["best_practices_checker"]):
            recommendations.append({
                "description": "Follow language best practices",
                "priority": "Medium"
            })
        
        # Recomendaciones basadas en problemas de estructura
        if "code_analyzer" in results and has_issues(results["code_analyzer"]):
            recommendations.append({
                "description": "Improve code structure and organization",
                "priority": "Medium"
            })
        
        return recommendations
    
    def _count_total_issues(self, results: Dict) -> int:
        """Count total number of issues across all tools."""
        total_issues = 0
        
        # Count issues from each tool
        for tool_result in results.values():
            if isinstance(tool_result, dict):
                total_issues += len(tool_result.get("issues", []))
        
        return total_issues
    
    def _count_critical_issues(self, results: Dict) -> int:
        """Count number of critical (high severity) issues."""
        critical_count = 0
        
        # Count high severity issues from each tool
        for tool_result in results.values():
            if isinstance(tool_result, dict):
                critical_count += sum(
                    1 for issue in tool_result.get("issues", [])
                    if issue.get("severity", "").lower() == "high"
                )
        
        return critical_count
    
    def _extract_quality_metrics(self, results: Dict) -> Dict[str, Any]:
        """Extract quality metrics from tool results."""
        quality_metrics = {
            "maintainability": self._calculate_maintainability_score(results),
            "readability": self._calculate_readability_score(results),
            "reliability": self._calculate_reliability_score(results)
        }
        
        return quality_metrics
    
    def _generate_summary(self, results: Dict) -> str:
        """Generate a summary based on results from all tools."""
        # Count total issues
        total_issues = self._count_total_issues(results)
        
        # Count critical issues
        critical_issues = self._count_critical_issues(results)
        
        # Calculate overall score
        score = self._calculate_overall_score(results)
        
        # Generate summary based on counts and score
        if score >= 8.0:
            quality_level = "high"
        elif score >= 6.0:
            quality_level = "medium"
        else:
            quality_level = "low"
        
        summary = f"The analysis found {total_issues} issues (including {critical_issues} critical ones). "
        summary += f"The overall code quality is {quality_level} with a score of {score}/10."
        
        return summary
    
    def _extract_key_findings(self, results: Dict) -> List[str]:
        """Extract key findings from tool results."""
        key_findings = []
        
        # Add findings about critical issues
        critical_count = self._count_critical_issues(results)
        if critical_count > 0:
            key_findings.append(f"Found {critical_count} critical issues that require immediate attention.")
        
        # Add findings about style
        if "style_checker" in results and isinstance(results["style_checker"], dict):
            style_issues = len(results["style_checker"].get("issues", []))
            if style_issues > 0:
                key_findings.append(f"There are {style_issues} style issues affecting readability.")
        
        # Add findings about security
        if "security_scanner" in results and isinstance(results["security_scanner"], dict):
            security_issues = len(results["security_scanner"].get("issues", []))
            if security_issues > 0:
                key_findings.append(f"Detected {security_issues} security issues.")
        
        # Add findings about performance
        if "performance_analyzer" in results and isinstance(results["performance_analyzer"], dict):
            performance_issues = len(results["performance_analyzer"].get("issues", []))
            if performance_issues > 0:
                key_findings.append(f"There are {performance_issues} performance issues that could be optimized.")
        
        # If no specific findings, add a generic one
        if not key_findings:
            key_findings.append("No significant issues were found in the analyzed code.")
        
        return key_findings
    
    def _synthesize_results(self, results: Dict) -> Dict:
        """Synthesize results from all tools."""
        try:
            # Extract quality metrics
            quality_metrics = self._extract_quality_metrics(results)
            
            # Calculate overall score
            score = self._calculate_overall_score(results)
            
            # Count total issues
            total_issues = self._count_total_issues(results)
            
            # Extract critical issues
            critical_issues = self._extract_critical_issues(results)
            critical_issues_count = len(critical_issues)
            
            # Generate recommendations
            recommendations = self._extract_recommendations(results)
            
            # Create synthesis
            synthesis = {
                "summary": self._generate_summary(results),
                "key_findings": self._extract_key_findings(results)
            }
            
            # Combine all results
            final_result = {
                "score": score,
                "quality_metrics": quality_metrics,
                "total_issues": total_issues,
                "critical_issues_count": critical_issues_count,
                "critical_issues": critical_issues,
                "recommendations": recommendations,
                "synthesis": synthesis,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Include raw results for debugging if needed
            if self.config.get("debug", {}).get("include_raw_results", False):
                final_result["raw_results"] = results
            
            return final_result
        
        except Exception as e:
            print(f"Error in _synthesize_results: {str(e)}")
            print(traceback.format_exc())
            
            return {
                "score": 0,
                "summary": f"Error synthesizing results: {str(e)}",
                "quality_metrics": {},
                "total_issues": 0,
                "critical_issues_count": 0,
                "error": str(e)
            }
    
    async def analyze_code(self, code_data: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for review_code to maintain API compatibility."""
        print(f"analyze_code called with: {code_data.keys() if isinstance(code_data, dict) else type(code_data)}")
        
        # Si code_data tiene un método dict(), usarlo
        if hasattr(code_data, "dict") and callable(code_data.dict):
            code_data = code_data.dict()
        
        # Asegurarse de que code_data sea un diccionario
        if not isinstance(code_data, dict):
            raise ValueError(f"Expected dict, got {type(code_data)}")
        
        return await self.review_code(code_data) 