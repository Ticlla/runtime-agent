import pytest
from code_review_assistant.tools.performance import PerformanceAnalyzer

class TestPerformanceAnalyzer:
    def test_initialization(self):
        analyzer = PerformanceAnalyzer()
        assert analyzer is not None
    
    def test_analyze_efficient_code(self):
        analyzer = PerformanceAnalyzer()
        code = "def efficient_function(items):\n    return [x * 2 for x in items]"
        result = analyzer.analyze(code, "test.py")
        
        assert result is not None
        assert "performance_metrics" in result
        assert result["performance_score"] >= 7.0  # Assuming a 0-10 scale
    
    def test_analyze_inefficient_code(self):
        analyzer = PerformanceAnalyzer()
        code = """
def inefficient_function(n):
    result = []
    for i in range(n):
        for j in range(n):
            for k in range(n):
                result.append(i * j * k)
    return result
"""
        result = analyzer.analyze(code, "test.py")
        
        assert result is not None
        assert "performance_metrics" in result
        assert "issues" in result
        assert any("complexity" in issue.get("description", "").lower() for issue in result["issues"]) 