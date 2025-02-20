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

# Esquema esperado para validación de resultados
EXPECTED_SCHEMA = {
    "score": float,
    "summary": str,
    "issues": List[Dict[str, Any]],
    "metrics": Dict[str, float],
    "recommendations": List[str]
}

class CodeReviewAssistant:
    """AI-powered code review assistant."""
    
    def __init__(self):
        """Initialize CodeReviewAssistant with configuration from environment."""
        self.config = load_config()
        self.runtime = AgentRuntime(self.config)
        self.tools = ToolsManager()
        
        # Inicializar conexiones
        self.redis_client = self._init_redis()
        self.db_session = self._init_database()
    
    def _init_redis(self) -> Redis:
        """Initialize Redis connection with error handling."""
        try:
            return Redis(
                host=self.config["redis"]["host"],
                port=self.config["redis"]["port"],
                password=self.config["redis"]["password"],
                decode_responses=True  # Automáticamente decodifica respuestas a str
            )
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Redis: {str(e)}")
    
    def _init_database(self) -> sessionmaker:
        """Initialize PostgreSQL connection with error handling."""
        try:
            engine = create_engine(self.config["database"]["url"])
            Session = sessionmaker(bind=engine)
            return Session()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to PostgreSQL: {str(e)}")
    
    async def initialize(self):
        """Initialize the assistant and register tools."""
        await self.runtime.initialize()
        
        # Registrar las herramientas
        self.tools.register("code_analyzer", CodeAnalyzer())
        self.tools.register("style_checker", StyleChecker())
        self.tools.register("security_scanner", SecurityScanner())
        self.tools.register("performance_analyzer", PerformanceAnalyzer())
        self.tools.register("best_practices", BestPracticesChecker())
        
        # Asignar nuestro ToolsManager al runtime
        self.runtime.tools = self.tools
    
    async def review_code(self, code_data: Dict) -> Dict:
        """Review code and provide analysis."""
        try:
            if not self.tools:
                raise RuntimeError("Tools not initialized")
            
            analysis_results = {}
            
            # Función auxiliar para procesar y validar resultados
            async def process_tool_result(tool_name: str, code: str) -> Dict:
                result = await self.tools.execute_tool(tool_name, code=code)
                return self._validate_and_clean_result(result)
            
            # Ejecutar herramientas con validación
            tools_to_execute = {
                "analysis": "code_analyzer",
                "style": "style_checker",
                "security": "security_scanner",
                "performance": "performance_analyzer",
                "best_practices": "best_practices"
            }
            
            for key, tool_name in tools_to_execute.items():
                analysis_results[key] = await process_tool_result(
                    tool_name,
                    code_data["source_code"]
                )
            
            # Generar síntesis basada en los resultados
            synthesis = self._generate_synthesis(analysis_results)
            analysis_results["synthesis"] = synthesis
            
            return analysis_results
            
        except Exception as e:
            return {
                "error": "review_error",
                "message": str(e)
            }

    def _validate_and_clean_result(self, result: Dict) -> Dict:
        """Valida y limpia los resultados para evitar duplicación."""
        if not isinstance(result, dict):
            return {"error": "Invalid result format"}
            
        # Asegurar que las secciones principales existan una sola vez
        cleaned_result = {
            "score": self._validate_field(result.get("score"), float, 0.0),
            "summary": self._validate_field(result.get("summary"), str, "No summary available"),
            "issues": self._validate_field(result.get("issues"), list, []),
            "metrics": self._validate_field(result.get("detailed_metrics"), dict, {}),
            "recommendations": self._validate_field(result.get("recommendations"), list, [])
        }
        
        return cleaned_result
    
    def _validate_field(self, value: Any, expected_type: type, default_value: Any) -> Any:
        """Valida un campo específico y retorna un valor por defecto si es inválido."""
        if isinstance(value, expected_type):
            return value
        return default_value

    def _generate_synthesis(self, results: Dict) -> Dict:
        """Genera una síntesis estructurada de todos los resultados."""
        
        # Evaluación de calidad general
        quality_assessment = {
            "maintainability": self._calculate_maintainability_score(results),
            "readability": self._calculate_readability_score(results),
            "reliability": self._calculate_reliability_score(results)
        }
        
        # Extraer problemas críticos
        critical_issues = self._extract_critical_issues(results)
        
        # Generar recomendaciones
        recommendations = self._extract_recommendations(results)
        
        # Calcular métricas generales
        metrics = {
            "overall_quality": self._calculate_overall_score(results),
            "code_quality": results.get("analysis", {}).get("score", 0),
            "style_score": results.get("style", {}).get("score", 0),
            "security_score": results.get("security", {}).get("score", 0),
            "performance_score": results.get("performance", {}).get("score", 0)
        }
        
        return {
            "quality_assessment": quality_assessment,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "metrics": metrics
        }

    def _calculate_overall_score(self, results: Dict) -> float:
        """Calcula el score general basado en todos los análisis."""
        scores = [
            results.get("analysis", {}).get("score", 0),
            results.get("style", {}).get("score", 0),
            results.get("security", {}).get("score", 0),
            results.get("performance", {}).get("score", 0),
            results.get("best_practices", {}).get("score", 0)
        ]
        
        # Filtrar scores válidos y calcular promedio
        valid_scores = [s for s in scores if isinstance(s, (int, float))]
        return round(sum(valid_scores) / len(valid_scores) if valid_scores else 0, 2)

    def _calculate_maintainability_score(self, results: Dict) -> str:
        """Calcula el score de mantenibilidad basado en los issues encontrados."""
        issues_count = len(results.get("analysis", {}).get("issues", []))
        style_issues = len(results.get("style", {}).get("issues", []))
        
        if issues_count + style_issues < 3:
            return "High"
        elif issues_count + style_issues < 6:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_readability_score(self, results: Dict) -> str:
        """Calcula el score de legibilidad basado en los problemas de estilo."""
        style_issues = len(results.get("style", {}).get("issues", []))
        
        if style_issues < 2:
            return "High"
        elif style_issues < 4:
            return "Medium"
        else:
            return "Low"
    
    def _calculate_reliability_score(self, results: Dict) -> str:
        """Calcula el score de confiabilidad basado en problemas de seguridad y mejores prácticas."""
        security_issues = len(results.get("security", {}).get("issues", []))
        practice_issues = len(results.get("best_practices", {}).get("issues", []))
        
        if security_issues + practice_issues < 2:
            return "High"
        elif security_issues + practice_issues < 4:
            return "Medium"
        else:
            return "Low"
    
    def _extract_critical_issues(self, results: Dict) -> List[Dict]:
        """Extrae los problemas críticos de todas las categorías."""
        critical_issues = []
        
        # Revisar cada herramienta por issues críticos
        for tool_name, tool_results in results.items():
            if isinstance(tool_results, dict):
                for issue in tool_results.get("issues", []):
                    if issue.get("severity", "").lower() == "high":
                        critical_issues.append({
                            "description": issue.get("message", ""),
                            "impact": f"Critical {tool_name} issue",
                            "solution": issue.get("suggestion", "Review and fix the issue")
                        })
        
        return critical_issues
    
    def _extract_recommendations(self, results: Dict) -> List[Dict]:
        """Extrae recomendaciones basadas en los problemas encontrados."""
        recommendations = []
        
        # Recomendaciones basadas en problemas de estilo
        if results.get("style", {}).get("issues"):
            recommendations.append({
                "description": "Improve code style following PEP 8",
                "priority": "Medium"
            })
        
        # Recomendaciones basadas en problemas de seguridad
        if results.get("security", {}).get("issues"):
            recommendations.append({
                "description": "Address security vulnerabilities",
                "priority": "High"
            })
        
        # Recomendaciones basadas en problemas de rendimiento
        if results.get("performance", {}).get("issues"):
            recommendations.append({
                "description": "Optimize code performance",
                "priority": "Medium"
            })
        
        # Recomendaciones basadas en mejores prácticas
        if results.get("best_practices", {}).get("issues"):
            recommendations.append({
                "description": "Follow Python best practices",
                "priority": "Medium"
            })
        
        return recommendations 