import pytest
from code_review_assistant.tools.best_practices_checker import BestPracticesChecker
import json

class TestBestPracticesChecker:
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test checker initialization."""
        checker = BestPracticesChecker()
        assert checker is not None
    
    @pytest.mark.asyncio
    async def test_check_good_practices(self):
        """Test analysis of well-written code."""
        checker = BestPracticesChecker()
        code = """
def calculate_average(numbers: list[float]) -> float | None:
    \"\"\"Calculate the average of a list of numbers.
    
    Args:
        numbers: A list of numeric values
        
    Returns:
        float: The average value
        None: If the list is empty
        
    Examples:
        >>> calculate_average([1, 2, 3])
        2.0
        >>> calculate_average([])
        None
    \"\"\"
    if not numbers:
        return None
        
    total = sum(numbers)
    count = len(numbers)
    return total / count
"""
        result = await checker.execute(json.dumps({
            "code": code,
            "filename": "test.py"
        }))
        
        result = json.loads(result)
        assert result is not None
        assert "score" in result
        assert result["score"] >= 7.5  # Ajustado el umbral a 7.5
        
        # Verificar que no hay problemas críticos
        issues = result.get("issues", [])
        critical_issues = [i for i in issues if i.get("severity") == "high"]
        assert len(critical_issues) == 0
    
    @pytest.mark.asyncio
    async def test_check_bad_practices(self):
        """Test analysis of poorly written code."""
        checker = BestPracticesChecker()
        code = """
def x(a):
    if a == None: return 0
    b = []
    for i in range(len(a)):
        b.append(a[i] * 2)
    return b
"""
        result = await checker.execute(json.dumps({
            "code": code,
            "filename": "test.py"
        }))
        
        result = json.loads(result)
        assert result is not None
        assert "score" in result
        assert "issues" in result
        assert len(result["issues"]) > 0 

    @pytest.mark.asyncio
    async def test_check_dff_practices(self):
        """Test analysis of DFF data."""
        checker = BestPracticesChecker()
        
        dff_data = {
            "dff_data": {
                "files": [
                    {
                        "fileName": "utils.py",
                        "status": "MODIFIED",
                        "codeContext": {
                            "before": [
                                "def process_data(data):",
                                "    result = []",
                                "    for i in range(len(data)):",
                                "        result.append(data[i] * 2)",
                                "    return result"
                            ],
                            "after": [
                                "def process_data(data: list) -> list:",
                                "    \"\"\"Process data by doubling each element.",
                                "    Args:",
                                "        data: Input list of numbers",
                                "    Returns:",
                                "        List with doubled values",
                                "    \"\"\"",
                                "    return [x * 2 for x in data]"
                            ]
                        }
                    }
                ],
                "summary": {
                    "totalFiles": 1,
                    "added": 0,
                    "modified": 1,
                    "deleted": 0
                }
            }
        }
        
        result = await checker.execute(json.dumps(dff_data))
        result = json.loads(result)
        
        assert result is not None
        assert "tool_name" in result
        assert result["tool_name"] == "best_practices_checker"
        assert "format" in result
        assert result["format"] == "dff"
        assert "files_analyzed" in result
        assert result["files_analyzed"] == 1
        
        # Verificar resultados por archivo
        assert "results" in result
        file_results = result["results"]
        assert len(file_results) == 1
        
        file_result = file_results[0]
        assert "filename" in file_result
        assert file_result["filename"] == "utils.py"
        assert "score" in file_result
        assert file_result["score"] >= 7.5  # El código mejorado debería tener buena puntuación
        
        # Verificar que detecta las mejoras
        assert "improvements" in file_result
        improvements = file_result.get("improvements", [])
        improvement_types = [imp.get("type") for imp in improvements]
        
        # Debería detectar estas mejoras específicas
        expected_improvements = [
            "type_hints_added",
            "docstring_added",
            "list_comprehension_used",
            "code_simplified"
        ]
        
        for expected in expected_improvements:
            assert any(imp == expected for imp in improvement_types), f"No se detectó la mejora: {expected}" 