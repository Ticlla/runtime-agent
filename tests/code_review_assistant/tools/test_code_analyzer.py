import pytest
from code_review_assistant.tools.code_analyzer import CodeAnalyzer

@pytest.mark.asyncio
async def test_code_analysis():
    """Test code analysis functionality."""
    analyzer = CodeAnalyzer()
    
    # Código de prueba válido con un problema conocido (bare except)
    code = """
def test_function():
    try:
        pass
    except:
        pass
"""
    
    result = await analyzer.execute(code=code)
    
    # Verificar estructura del resultado
    assert "structure" in result
    assert "complexity" in result
    assert "issues" in result
    
    # Verificar que se detectó el bare except
    assert any(
        issue["type"] == "bare_except" 
        for issue in result["issues"]
    )
    
    # Verificar análisis de estructura
    structure = result["structure"]
    assert len(structure["functions"]) == 1
    assert structure["functions"][0]["name"] == "test_function"

@pytest.mark.asyncio
async def test_code_analysis_syntax_error():
    """Test handling of syntax errors."""
    analyzer = CodeAnalyzer()
    
    # Código con error de sintaxis
    code = """
def invalid_function()
    print("Missing colon")
"""
    
    result = await analyzer.execute(code=code)
    assert "error" in result
    assert result["error"] == "syntax_error" 