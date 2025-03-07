import pytest
from code_review_assistant.main import CodeReviewAssistant
from ai_agent_framework.testing.memory import TestMemory  # Importar desde el paquete

@pytest.mark.asyncio
async def test_code_review():
    """Test code review functionality."""
    config = {
        "model_config": {
            "model_type": "test"
        },
        "memory_config": {
            "redis": {
                "redis_url": "redis://localhost:6379",
                "namespace": "test"
            }
        },
        "review_rules": {
            "max_line_length": 80,
            "max_complexity": 10,
            "style_guide": "pep8"
        }
    }
    
    assistant = CodeReviewAssistant(config)
    await assistant.initialize()
    
    # Mock la memoria para el test usando la clase de prueba
    assistant.runtime.short_term = TestMemory()
    
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
    
    review = await assistant.review_code(code_data)
    
    # Verify review contains all expected sections
    assert "analysis" in review
    assert "style" in review
    assert "security" in review
    assert "performance" in review
    assert "best_practices" in review
    
    # Verify analysis results
    analysis = review["analysis"]
    assert "structure" in analysis
    assert "complexity" in analysis
    assert "issues" in analysis
    
    # Verify specific issues are identified
    issues = analysis["issues"]
    assert any(issue["type"] == "bare_except" for issue in issues) 

@pytest.mark.asyncio
async def test_invalid_input():
    """Test handling of invalid input."""
    assistant = CodeReviewAssistant()
    await assistant.initialize()
    
    result = await assistant.review_code({})
    assert "error" in result
    assert result["error"] == "invalid_input" 