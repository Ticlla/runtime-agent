import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

import asyncio
from src.code_review_assistant.main import CodeReviewAssistant

async def test_review():
    # Inicializar el asistente
    assistant = CodeReviewAssistant()
    
    # Importante: inicializar el asistente antes de usarlo
    await assistant.initialize()
    
    # Código de ejemplo para analizar
    test_code = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total
    """
    
    code_data = {
        "source_code": test_code,
        "file_path": "example.py",
        "language": "python"
    }
    
    try:
        print("Iniciando análisis de código...")
        results = await assistant.review_code(code_data)
        
        # Imprimir resultados
        print("\n=== Code Review Results ===")
        if "error" in results:
            print(f"\nError: {results['error']}")
            print(f"Message: {results.get('message', 'No message available')}")
            return

        print(f"\nSummary: {results.get('synthesis', {}).get('summary', 'No summary available')}")
        print("\nIssues Found:")
        for tool, tool_results in results.items():
            if tool != "synthesis" and isinstance(tool_results, dict):
                print(f"\n{tool.upper()}:")
                issues = tool_results.get("issues", [])
                if issues:
                    for issue in issues:
                        print(f"- {issue.get('message', 'No message')} (Severity: {issue.get('severity', 'unknown')})")
                else:
                    print("- No issues found")

    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")
        raise e

if __name__ == "__main__":
    asyncio.run(test_review()) 