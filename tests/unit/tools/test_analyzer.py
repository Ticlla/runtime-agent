import pytest
import json
import asyncio
from code_review_assistant.tools.code_analyzer import CodeAnalyzer

class TestCodeAnalyzer:
    def test_initialization(self):
        analyzer = CodeAnalyzer()
        assert analyzer is not None
    
    def test_analyze_python_code(self):
        analyzer = CodeAnalyzer()
        code = "def test_function():\n    return 'test'"
        result = analyzer.analyze(code, "test.py")
        
        assert result is not None
        assert "details" in result
        assert "issues" in result
        
    def test_analyze_invalid_code(self):
        analyzer = CodeAnalyzer()
        code = "def test_function() return 'test'"  # Missing colon
        result = analyzer.analyze(code, "test.py")
        
        assert result is not None
        assert "issues" in result
        assert any("syntax" in str(issue).lower() for issue in result["issues"])
    
    def test_analyze_with_code_data_dict(self):
        """Prueba el análisis con un diccionario de datos de código."""
        analyzer = CodeAnalyzer()
        code_data = {
            "code": "def test_function():\n    return 'test'",
            "filename": "test.py"
        }
        result = analyzer.analyze(code_data)
        
        assert result is not None
        assert "details" in result
        assert "issues" in result
    
    def test_analyze_with_different_languages(self):
        """Prueba el análisis con diferentes lenguajes de programación."""
        analyzer = CodeAnalyzer()
        
        # Python
        python_code = "def test_function():\n    return 'test'"
        python_result = analyzer.analyze(python_code, "test.py")
        assert python_result is not None
        
        # JavaScript
        js_code = "function testFunction() { return 'test'; }"
        js_result = analyzer.analyze(js_code, "test.js")
        assert js_result is not None
        
        # Asegurarse de que los resultados son diferentes para diferentes lenguajes
        assert python_result.get("language", "") != js_result.get("language", "") 

    def test_analyze_with_dff_format(self):
        """Prueba el análisis con formato DFF (Differential File Format)."""
        analyzer = CodeAnalyzer()
        
        # Crear datos de prueba en formato DFF
        dff_data = {
            "dff_data": {
                "summary": {
                    "changes": 2,
                    "additions": 10,
                    "deletions": 5
                },
                "files": [
                    {
                        "fileName": "test.py",
                        "status": "MODIFIED",
                        "codeContext": {
                            "before": [
                                "def old_function():",
                                "    return 'old'"
                            ],
                            "after": [
                                "def new_function():",
                                "    return 'new'"
                            ]
                        }
                    },
                    {
                        "fileName": "new_file.js",
                        "status": "ADDED",
                        "codeContext": {
                            "after": [
                                "function testFunction() {",
                                "    return 'test';",
                                "}"
                            ]
                        }
                    }
                ]
            }
        }
        
        # Analizar los datos DFF
        result = analyzer.analyze(dff_data)
        
        # Verificar el resultado
        assert result is not None
        assert "format" in result
        assert result["format"] == "dff"
        assert "files_analyzed" in result
        assert result["files_analyzed"] > 0
        assert "results" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) > 0
        
        # Verificar que cada archivo analizado tiene la estructura correcta
        for file_result in result["results"]:
            assert "filename" in file_result
            assert "status" in file_result
            assert "issues" in file_result 