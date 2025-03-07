import sys
import os
import asyncio
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add src directory to path to import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from code_review_assistant.main import CodeReviewAssistant

async def test_direct_code():
    """Test CodeReviewAssistant with direct code input."""
    print("\n🔍 Probando CodeReviewAssistant con código directo...")
    
    # Create CodeReviewAssistant instance
    assistant = CodeReviewAssistant()
    await assistant.initialize()
    print("✅ CodeReviewAssistant inicializado")
    
    # Sample Python code with some issues
    python_code = """
def calculate_sum(numbers):
    result = 0
    for i in range(len(numbers)):
        result = result + numbers[i]
    return result

def find_max(numbers):
    if len(numbers) == 0:
        return None
    max_value = numbers[0]
    for num in numbers:
        if num > max_value:
            max_value = num
    return max_value

# Test the functions
test_numbers = [1, 2, 3, 4, 5]
print("Sum:", calculate_sum(test_numbers))
print("Max:", find_max(test_numbers))
"""
    
    try:
        # Review the code
        result = await assistant.review_code({
            "source_code": python_code,
            "file_extension": ".py"
        })
        
        # Print the result in a readable format
        print("\n📊 Resultado del análisis:")
        print(f"Score general: {result.get('score', 'N/A')}/10")
        
        # Print quality metrics
        print("\n🔍 Métricas de calidad:")
        for metric, value in result.get("quality_metrics", {}).items():
            print(f"- {metric}: {value}")
        
        # Print issues summary
        total_issues = result.get("total_issues", 0)
        critical_issues = result.get("critical_issues_count", 0)
        print(f"\n⚠️ Problemas encontrados: {total_issues} (críticos: {critical_issues})")
        
        # Print critical issues
        if result.get("critical_issues"):
            print("\n🚨 Problemas críticos:")
            for issue in result.get("critical_issues"):
                print(f"- {issue.get('description')}")
                print(f"  Impacto: {issue.get('impact')}")
                print(f"  Solución: {issue.get('solution')}")
        
        # Print recommendations
        if result.get("recommendations"):
            print("\n💡 Recomendaciones:")
            for rec in result.get("recommendations"):
                print(f"- {rec.get('description')} (Prioridad: {rec.get('priority')})")
        
        # Print synthesis
        if "synthesis" in result:
            print("\n📝 Síntesis:")
            print(result["synthesis"].get("summary", "No summary available"))
        
        print("\n✨ Prueba con código directo completada!")
        return True
    
    except Exception as e:
        print(f"❌ Error durante la prueba con código directo: {str(e)}")
        import traceback
        print("Stack trace:")
        print(traceback.format_exc())
        return False

async def test_dff_data():
    """Test CodeReviewAssistant with DFF data."""
    print("\n🔍 Probando CodeReviewAssistant con datos DFF...")
    
    # Create CodeReviewAssistant instance
    assistant = CodeReviewAssistant()
    await assistant.initialize()
    print("✅ CodeReviewAssistant inicializado")
    
    # Sample DFF data
    dff_data = {
        "summary": {
            "total_files": 2,
            "added": 1,
            "modified": 1,
            "deleted": 0
        },
        "files": [
            {
                "fileName": "example.py",
                "status": "ADDED",
                "codeContext": {
                    "before": [],
                    "after": [
                        "def calculate_sum(numbers):",
                        "    result = 0",
                        "    for i in range(len(numbers)):",
                        "        result = result + numbers[i]",
                        "    return result",
                        "",
                        "def find_max(numbers):",
                        "    if len(numbers) == 0:",
                        "        return None",
                        "    max_value = numbers[0]",
                        "    for num in numbers:",
                        "        if num > max_value:",
                        "            max_value = num",
                        "    return max_value",
                        "",
                        "# Test the functions",
                        "test_numbers = [1, 2, 3, 4, 5]",
                        "print(\"Sum:\", calculate_sum(test_numbers))",
                        "print(\"Max:\", find_max(test_numbers))"
                    ]
                }
            },
            {
                "fileName": "config.xml",
                "status": "MODIFIED",
                "codeContext": {
                    "before": [
                        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                        "<config>",
                        "    <app>",
                        "        <name>MyApp</name>",
                        "        <version>1.0</version>",
                        "    </app>",
                        "</config>"
                    ],
                    "after": [
                        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                        "<config>",
                        "    <app>",
                        "        <name>MyApp</name>",
                        "        <version>1.1</version>",
                        "        <debug>true</debug>",
                        "    </app>",
                        "</config>"
                    ]
                }
            }
        ]
    }
    
    try:
        # Review the code
        result = await assistant.review_code({
            "dff_data": dff_data
        })
        
        # Print the result in a readable format
        print("\n📊 Resultado del análisis:")
        print(f"Score general: {result.get('score', 'N/A')}/10")
        
        # Print quality metrics
        print("\n🔍 Métricas de calidad:")
        for metric, value in result.get("quality_metrics", {}).items():
            print(f"- {metric}: {value}")
        
        # Print files analyzed
        files_analyzed = 0
        for tool_result in result.values():
            if isinstance(tool_result, dict) and tool_result.get("format") == "dff":
                files_analyzed = tool_result.get("files_analyzed", 0)
                break
        
        print(f"\n📁 Archivos analizados: {files_analyzed}")
        
        # Print issues summary
        total_issues = result.get("total_issues", 0)
        critical_issues = result.get("critical_issues_count", 0)
        print(f"\n⚠️ Problemas encontrados: {total_issues} (críticos: {critical_issues})")
        
        # Print critical issues
        if result.get("critical_issues"):
            print("\n🚨 Problemas críticos:")
            for issue in result.get("critical_issues"):
                print(f"- {issue.get('description')}")
                print(f"  Archivo: {issue.get('file', 'N/A')}")
                print(f"  Línea: {issue.get('line', 'N/A')}")
                print(f"  Impacto: {issue.get('impact')}")
                print(f"  Solución: {issue.get('solution')}")
        
        # Print recommendations
        if result.get("recommendations"):
            print("\n💡 Recomendaciones:")
            for rec in result.get("recommendations"):
                print(f"- {rec.get('description')} (Prioridad: {rec.get('priority')})")
        
        # Print synthesis
        if "synthesis" in result:
            print("\n📝 Síntesis:")
            print(result["synthesis"].get("summary", "No summary available"))
        
        print("\n✨ Prueba con datos DFF completada!")
        return True
    
    except Exception as e:
        print(f"❌ Error durante la prueba con datos DFF: {str(e)}")
        import traceback
        print("Stack trace:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        # Run the tests
        success_direct = asyncio.run(test_direct_code())
        success_dff = asyncio.run(test_dff_data())
        
        if success_direct and success_dff:
            print("\n✅ Todas las pruebas completadas con éxito!")
            sys.exit(0)
        else:
            print("\n❌ Algunas pruebas fallaron")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error en main: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1) 