import pytest
import asyncio
import inspect
from code_review_assistant.main import CodeReviewAssistant

class TestCodeReviewAssistant:
    @pytest.fixture
    async def assistant(self):
        assistant = CodeReviewAssistant()
        await assistant.initialize()
        
        # Imprimir información detallada sobre los métodos disponibles
        print("\nAvailable attributes:", [attr for attr in dir(assistant) if not attr.startswith('_')])
        
        # Imprimir información sobre el método review_code si existe
        if hasattr(assistant, 'review_code'):
            print("\nreview_code signature:", inspect.signature(assistant.review_code))
        
        yield assistant
    
    @pytest.mark.asyncio
    async def test_initialization(self, assistant):
        assert assistant is not None
        
        # Verificar que al menos una de las herramientas de análisis esté presente
        tools_present = False
        for tool_name in ['code_analyzer', 'security_scanner', 'performance_analyzer', 
                         'style_checker', 'best_practices_checker']:
            if hasattr(assistant, tool_name):
                tools_present = True
                break
        
        assert tools_present, "No se encontró ninguna herramienta de análisis"
    
    @pytest.mark.asyncio
    async def test_code_review_capability(self, assistant):
        """Prueba la capacidad de revisar código, independientemente del nombre del método."""
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""
        # Intentar diferentes métodos que podrían existir para revisar código
        result = None
        
        if hasattr(assistant, 'review_code'):
            try:
                result = await assistant.review_code(code, "factorial.py")
            except Exception as e:
                print(f"Error calling review_code: {e}")
        
        if result is None and hasattr(assistant, 'analyze_single_file'):
            try:
                result = await assistant.analyze_single_file(code, "factorial.py")
            except Exception as e:
                print(f"Error calling analyze_single_file: {e}")
        
        if result is None and hasattr(assistant, 'analyze_code'):
            try:
                result = await assistant.analyze_code(code, "factorial.py")
            except Exception as e:
                print(f"Error calling analyze_code: {e}")
        
        # Si ninguno de los métodos anteriores funcionó, la prueba fallará
        assert result is not None, "No se pudo revisar el código con ningún método disponible"
        
        # Verificar que el resultado tenga alguna estructura (ajustar según la implementación real)
        assert isinstance(result, dict), "El resultado no es un diccionario"
    
    @pytest.mark.asyncio
    async def test_analyze_code(self, assistant):
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
"""
        result = await assistant.review_code(code, "factorial.py")
        
        assert result is not None
        assert "score" in result
        assert "summary" in result
        assert "quality_metrics" in result
        assert "issues" in result
        assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_analyze_diff_added_file(self, assistant):
        diff_data = {
            "summary": {"total_files": 1, "additions": 5, "deletions": 0},
            "files": [
                {
                    "fileName": "factorial.py",
                    "status": "added",
                    "codeContext": {
                        "before": [],
                        "after": [
                            "def factorial(n):",
                            "    if n <= 1:",
                            "        return 1",
                            "    return n * factorial(n-1)"
                        ]
                    }
                }
            ]
        }
        
        try:
            result = await assistant.review_code(diff_data=diff_data)
        except TypeError:
            code = "\n".join(diff_data["files"][0]["codeContext"]["after"])
            filename = diff_data["files"][0]["fileName"]
            result = await assistant.review_code(code, filename)
        
        assert result is not None
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_diff_modified_file(self, assistant):
        diff_data = {
            "summary": {"total_files": 1, "additions": 2, "deletions": 1},
            "files": [
                {
                    "fileName": "factorial.py",
                    "status": "modified",
                    "codeContext": {
                        "before": [
                            "def factorial(n):",
                            "    if n <= 0:",
                            "        return 1",
                            "    return n * factorial(n-1)"
                        ],
                        "after": [
                            "def factorial(n):",
                            "    if n <= 1:  # Changed condition",
                            "        return 1",
                            "    return n * factorial(n-1)",
                            "    # Added comment"
                        ]
                    }
                }
            ]
        }
        
        result = await assistant.review_code(diff_data=diff_data)
        
        assert result is not None
        assert "score" in result
        assert "summary" in result
        assert "file_analyses" in result
        assert len(result["file_analyses"]) == 1
        assert "factorial.py" in [file["file_name"] for file in result["file_analyses"]]
    
    @pytest.mark.asyncio
    async def test_analyze_diff_multiple_files(self, assistant):
        diff_data = {
            "summary": {"total_files": 2, "additions": 8, "deletions": 2},
            "files": [
                {
                    "fileName": "factorial.py",
                    "status": "modified",
                    "codeContext": {
                        "before": [
                            "def factorial(n):",
                            "    if n <= 0:",
                            "        return 1",
                            "    return n * factorial(n-1)"
                        ],
                        "after": [
                            "def factorial(n):",
                            "    if n <= 1:",
                            "        return 1",
                            "    return n * factorial(n-1)"
                        ]
                    }
                },
                {
                    "fileName": "fibonacci.py",
                    "status": "added",
                    "codeContext": {
                        "before": [],
                        "after": [
                            "def fibonacci(n):",
                            "    if n <= 1:",
                            "        return n",
                            "    return fibonacci(n-1) + fibonacci(n-2)"
                        ]
                    }
                }
            ]
        }
        
        result = await assistant.review_code(diff_data=diff_data)
        
        assert result is not None
        assert "score" in result
        assert "summary" in result
        assert "file_analyses" in result
        assert len(result["file_analyses"]) == 2
        file_names = [file["file_name"] for file in result["file_analyses"]]
        assert "factorial.py" in file_names
        assert "fibonacci.py" in file_names 