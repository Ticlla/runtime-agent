import os
import sys
from pathlib import Path

# Agregar el directorio src al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir / "src"))

import asyncio
import os
from dotenv import load_dotenv
from code_review_assistant.main import CodeReviewAssistant
import json
from typing import Dict

async def main():
    try:
        # Cargar variables de entorno desde .env
        load_dotenv()
        
        # Obtener API key de variable de entorno
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY no está configurada en el archivo .env")
            return
        
        # Configuration
        config = {
            "model_config": {
                "model_type": "openai",
                "api_key": api_key,
                "model": "gpt-3.5-turbo",  # Usar gpt-3.5-turbo en lugar de gpt-4
                "system_prompt": "You are a helpful assistant for code review.",
                "temperature": 0.7,
                "max_tokens": 500
            },
            # Agregar configuración de memoria
            "memory_config": {
                "redis": {
                    "url": "redis://localhost:6379",
                    "ttl": 3600
                }
            },
            "review_rules": {
                "max_line_length": 80,
                "max_complexity": 10,
                "style_guide": "pep8"
            }
        }
        
        # Código de ejemplo para revisar
        code_data = {
            "source_code": """
def problematic_function(data):
    try:
        very_long_variable_name_that_exceeds_the_maximum_line_length_limit = 42
        if data:
            if data.get('value'):
                if data['value'] > 0:
                    return True
    except:
        pass
    return False
""",
            "language": "python",
            "file_path": "test.py"
        }
        
        # Inicializar y ejecutar el asistente
        print("Ejecutando revisión de código...")
        assistant = CodeReviewAssistant()
        await assistant.initialize()
        
        # Realizar la revisión
        review = await assistant.review_code(code_data)
        
        if review.get("error"):
            print(f"\nError en la revisión: {review.get('message')}")
            return
        
        # Mostrar resultados
        print("\n=== Resultados de la Revisión de Código ===\n")
        
        # Procesamiento de la síntesis
        if "synthesis" in review:
            try:
                synthesis = review["synthesis"]
                if isinstance(synthesis, str):
                    synthesis = json.loads(synthesis)
                
                print("📊 Síntesis del Análisis:\n")
                
                # Resumen general
                if "quality_assessment" in synthesis:
                    qa = synthesis["quality_assessment"]
                    print("Evaluación de Calidad:")
                    for aspect, details in qa.items():
                        if isinstance(details, dict):
                            print(f"- {aspect.title()}: {details.get('score', 'N/A')}")
                            if "details" in details:
                                print(f"  Detalles: {details['details']}")
                        else:
                            print(f"- {aspect.title()}: {details}")
                    print()
                
                # Problemas críticos
                if "critical_issues" in synthesis:
                    print("Problemas Críticos:")
                    for issue in synthesis["critical_issues"]:
                        print(f"- {issue.get('description', '')}")
                        if "impact" in issue:
                            print(f"  Impacto: {issue['impact']}")
                        if "solution" in issue:
                            print(f"  Solución: {issue['solution']}")
                    print()
                
                # Recomendaciones
                if "recommendations" in synthesis:
                    print("Recomendaciones Principales:")
                    for rec in synthesis["recommendations"]:
                        print(f"- {rec.get('description', '')}")
                        if "priority" in rec:
                            print(f"  Prioridad: {rec['priority']}")
                    print()
                
                # Métricas generales
                if "metrics" in synthesis:
                    print("Métricas Generales:")
                    for metric, value in synthesis["metrics"].items():
                        print(f"- {metric.replace('_', ' ').title()}: {value}")
                    print()
                
            except json.JSONDecodeError as e:
                print("Error al procesar la síntesis:", str(e))
            except Exception as e:
                print("Error inesperado al procesar la síntesis:", str(e))
        
        # Luego mostrar los detalles técnicos usando el nuevo formato
        print("\n=== Detalles Técnicos ===\n")
        
        # Análisis de código
        if "analysis" in review:
            print_tool_results("🔍 Análisis de Código", review["analysis"])
        
        # Revisión de estilo
        if "style" in review:
            print_tool_results("🎨 Revisión de Estilo", review["style"])
        
        # Análisis de seguridad
        if "security" in review:
            print_tool_results("🔒 Análisis de Seguridad", review["security"])
        
        # Análisis de rendimiento
        if "performance" in review:
            print_tool_results("⚡ Análisis de Rendimiento", review["performance"])
        
        # Mejores prácticas
        if "best_practices" in review:
            print_tool_results("✨ Mejores Prácticas", review["best_practices"])

    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        # Para debugging
        import traceback
        print(traceback.format_exc())

def print_tool_results(tool_name: str, results: Dict):
    """Print results from a specific tool."""
    if not results or "error" in results:
        return
        
    print(f"\n{tool_name}")
    print("=" * len(tool_name))
    
    # Score y Summary
    if "score" in results:
        print(f"\nScore: {results['score']:.1f}/10")
    if "summary" in results:
        print(f"Summary: {results['summary']}")
    
    # Issues
    if "issues" in results and results["issues"]:
        print("\nIssues Found:")
        for issue in results["issues"]:
            print(f"\n- Type: {issue['type']}")
            print(f"  Severity: {issue['severity']}")
            print(f"  Line: {issue['line']}")
            print(f"  Message: {issue['message']}")
            if "suggestion" in issue:
                print(f"  Suggestion: {issue['suggestion']}")
    
    # Detailed Metrics
    if "details" in results and results["details"]:
        print("\nDetailed Metrics:")
        for metric, value in results["details"].items():
            if isinstance(value, (int, float)):
                print(f"- {metric.replace('_', ' ').title()}: {value:.1f}/10")
            elif isinstance(value, dict):
                print(f"\n{metric.replace('_', ' ').title()}:")
                for k, v in value.items():
                    print(f"  - {k}: {v}")
            elif isinstance(value, list):
                print(f"\n{metric.replace('_', ' ').title()}:")
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            print(f"  - {k}: {v}")
                    else:
                        print(f"  - {item}")

def _process_response(self, response_text):
    """
    Procesa la respuesta del LLM asegurando que todas las secciones tengan datos.
    """
    if not response_text:
        raise ValueError("La respuesta del modelo está vacía")

    try:
        # Parsear la respuesta completa del LLM
        if isinstance(response_text, str):
            if "LLM Response:" in response_text:
                # Extraer todo el JSON después de "LLM Response:"
                response_text = response_text.split("LLM Response:", 1)[1].strip()
            response_data = json.loads(response_text)
        else:
            response_data = response_text

        # Asegurar que la síntesis se procese correctamente
        synthesis = {
            "quality_assessment": response_data.get("quality_assessment", {}),
            "critical_issues": self._extract_critical_issues(response_data),
            "recommendations": self._extract_recommendations(response_data),
            "metrics": self._calculate_metrics(response_data)
        }

        # Asegurar que las mejores prácticas estén completas
        best_practices = {
            "score": response_data.get("best_practices", {}).get("score", 0),
            "summary": response_data.get("best_practices", {}).get("summary", "No best practices analysis available"),
            "practice_issues": response_data.get("best_practices", {}).get("practice_issues", []),
            "recommendations": response_data.get("best_practices", {}).get("recommendations", [])
        }

        # Construir la respuesta procesada completa
        processed_response = {
            "synthesis": synthesis,
            "analysis": {
                "structure": response_data.get("structure", {}),
                "complexity": response_data.get("complexity", {}),
                "issues": response_data.get("issues", [])
            },
            "style": {
                "score": response_data.get("style", {}).get("score", 0),
                "summary": response_data.get("style", {}).get("summary", ""),
                "style_issues": response_data.get("style", {}).get("style_issues", [])
            },
            "security": {
                "score": response_data.get("security", {}).get("score", 0),
                "summary": response_data.get("security", {}).get("summary", ""),
                "security_issues": response_data.get("security", {}).get("security_issues", [])
            },
            "performance": {
                "score": response_data.get("performance", {}).get("score", 0),
                "summary": response_data.get("performance", {}).get("summary", ""),
                "performance_issues": response_data.get("performance", {}).get("performance_issues", [])
            },
            "best_practices": best_practices
        }

        # Validar que las secciones principales tengan contenido
        if not synthesis["quality_assessment"] or not best_practices["practice_issues"]:
            print("Warning: Algunas secciones del análisis están incompletas")

        return processed_response

    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear la respuesta JSON: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error al procesar la respuesta del modelo: {str(e)}")

def _calculate_maintainability_score(self, data):
    """Calcula el score de mantenibilidad basado en los issues encontrados."""
    issues_count = len(data.get("issues", []))
    style_issues = len(data.get("style", {}).get("style_issues", []))
    return "High" if issues_count + style_issues < 3 else "Medium" if issues_count + style_issues < 6 else "Low"

def _calculate_readability_score(self, data):
    """Calcula el score de legibilidad basado en los problemas de estilo."""
    style_issues = len(data.get("style", {}).get("style_issues", []))
    return "High" if style_issues < 2 else "Medium" if style_issues < 4 else "Low"

def _calculate_reliability_score(self, data):
    """Calcula el score de confiabilidad basado en los problemas de seguridad y mejores prácticas."""
    security_issues = len(data.get("security", {}).get("security_issues", []))
    practice_issues = len(data.get("best_practices", {}).get("practice_issues", []))
    return "High" if security_issues + practice_issues < 2 else "Medium" if security_issues + practice_issues < 4 else "Low"

def _extract_critical_issues(self, data):
    """Extrae los problemas críticos de todas las categorías."""
    critical_issues = []
    
    # Extraer problemas de seguridad críticos
    for issue in data.get("security", {}).get("security_issues", []):
        if issue.get("severity", "").lower() == "high":
            critical_issues.append({
                "description": issue.get("message", ""),
                "impact": "Security vulnerability",
                "solution": issue.get("suggestion", "Review security implications")
            })
    
    # Extraer problemas de rendimiento críticos
    for issue in data.get("performance", {}).get("performance_issues", []):
        if issue.get("severity", "").lower() == "high":
            critical_issues.append({
                "description": issue.get("message", ""),
                "impact": "Performance impact",
                "solution": issue.get("suggestion", "Optimize code")
            })
    
    return critical_issues

def _extract_recommendations(self, data):
    """Extrae recomendaciones basadas en los problemas encontrados."""
    recommendations = []
    
    # Agregar recomendaciones basadas en problemas de estilo
    if data.get("style", {}).get("style_issues"):
        recommendations.append({
            "description": "Mejorar el estilo del código siguiendo PEP 8",
            "priority": "Medium"
        })
    
    # Agregar recomendaciones basadas en problemas de seguridad
    if data.get("security", {}).get("security_issues"):
        recommendations.append({
            "description": "Resolver vulnerabilidades de seguridad",
            "priority": "High"
        })
    
    return recommendations

def _calculate_metrics(self, data):
    """Calcula métricas generales basadas en el análisis."""
    return {
        "code_quality_score": f"{data.get('style', {}).get('score', 0)}/10",
        "security_score": f"{data.get('security', {}).get('score', 0)}/10",
        "performance_score": f"{data.get('performance', {}).get('score', 0)}/10"
    }

if __name__ == "__main__":
    asyncio.run(main()) 