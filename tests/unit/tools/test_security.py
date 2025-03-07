import pytest
from code_review_assistant.tools.security import SecurityScanner

class TestSecurityScanner:
    def test_initialization(self):
        scanner = SecurityScanner()
        assert scanner is not None
    
    def test_scan_secure_code(self):
        scanner = SecurityScanner()
        code = "def safe_function(validated_input):\n    return validated_input.strip()"
        result = scanner.scan(code, "test.py")
        
        assert result is not None
        assert "vulnerabilities" in result
        assert len(result["vulnerabilities"]) == 0
    
    def test_scan_insecure_code(self):
        scanner = SecurityScanner()
        code = "def unsafe_function(user_input):\n    return eval(user_input)"
        result = scanner.scan(code, "test.py")
        
        assert result is not None
        assert "vulnerabilities" in result
        assert len(result["vulnerabilities"]) > 0
        assert any("eval" in vuln.get("description", "").lower() for vuln in result["vulnerabilities"]) 