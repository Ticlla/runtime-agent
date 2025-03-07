import os
import sys
from pathlib import Path

# Add src directory to PYTHONPATH
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
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY not set in .env file")
            return
        
        # Example code to review
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
        
        # Initialize and run assistant
        print("Starting code review...")
        assistant = CodeReviewAssistant()
        await assistant.initialize()
        
        # Execute review
        review = await assistant.review_code(code_data)
        
        if review.get("error"):
            print(f"\nReview Error: {review.get('message')}")
            return
        
        # Display results
        print("\n=== Code Review Results ===\n")
        
        # Process synthesis
        if "synthesis" in review:
            try:
                synthesis = review["synthesis"]
                if isinstance(synthesis, str):
                    synthesis = json.loads(synthesis)
                
                print("📊 Analysis Summary:\n")
                
                if "quality_assessment" in synthesis:
                    print("Quality Assessment:")
                    for metric, value in synthesis["quality_assessment"].items():
                        print(f"- {metric}: {value}")
                
                if "critical_issues" in synthesis:
                    print("\nCritical Issues:")
                    for issue in synthesis["critical_issues"]:
                        print(f"- {issue['description']}")
                        print(f"  Impact: {issue['impact']}")
                        print(f"  Solution: {issue['solution']}")
                
                if "recommendations" in synthesis:
                    print("\nRecommendations:")
                    for rec in synthesis["recommendations"]:
                        print(f"- {rec['description']} (Priority: {rec['priority']})")
            
            except json.JSONDecodeError:
                print("Error: Could not parse synthesis results")
        
        # Technical details
        print("\n=== Technical Details ===\n")
        
        # Code analysis
        if "analysis" in review:
            print_tool_results("🔍 Code Analysis", review["analysis"])
        
        # Style review
        if "style" in review:
            print_tool_results("🎨 Style Review", review["style"])
        
        # Security analysis
        if "security" in review:
            print_tool_results("🔒 Security Analysis", review["security"])
        
        # Performance analysis
        if "performance" in review:
            print_tool_results("⚡ Performance Analysis", review["performance"])
        
        # Best practices
        if "best_practices" in review:
            print_tool_results("✨ Best Practices", review["best_practices"])

    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        print(traceback.format_exc())

def print_tool_results(tool_name: str, results: Dict):
    """Print results from a specific tool."""
    if not results or "error" in results:
        return
        
    print(f"\n{tool_name}")
    print("=" * len(tool_name))
    
    # Score and Summary
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