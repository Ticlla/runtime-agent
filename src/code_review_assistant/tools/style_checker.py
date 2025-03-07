from typing import Dict, Any, Optional, List
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI
import os
import json
import re
import datetime
import traceback

class StyleChecker(BaseTool):
    """Tool for checking code style across multiple programming languages."""
    
    # Dictionary of supported languages and their file extensions
    SUPPORTED_LANGUAGES = {
        "python": ["py", "pyw", "ipynb"],
        "javascript": ["js", "jsx", "ts", "tsx"],
        "java": ["java"],
        "c": ["c", "h"],
        "cpp": ["cpp", "hpp", "cc", "hh", "cxx", "hxx"],
        "csharp": ["cs"],
        "go": ["go"],
        "ruby": ["rb"],
        "php": ["php"],
        "swift": ["swift"],
        "rust": ["rs"],
        "kotlin": ["kt", "kts"],
        "scala": ["scala"],
        "html": ["html", "htm"],
        "css": ["css", "scss", "sass", "less"],
        "sql": ["sql"],
        "yaml": ["yml", "yaml"],
        "json": ["json"],
        "xml": ["xml"],
        "markdown": ["md", "markdown"],
        "shell": ["sh", "bash", "zsh"],
        "powershell": ["ps1"],
        "dockerfile": ["dockerfile"],
        "terraform": ["tf", "tfvars"],
        "r": ["r", "rmd"]
    }
    
    def __init__(self):
        """Initialize style checker."""
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def _detect_language_from_filename(self, filename: str) -> str:
        """
        Detect the programming language based on the file name or extension.
        
        Args:
            filename: The name of the file
            
        Returns:
            The detected language name
        """
        # Extract extension from filename
        _, ext = os.path.splitext(filename)
        ext = ext.lstrip('.').lower()
        
        print(f"Extracted extension from {filename}: '{ext}'")  # Diagnóstico
        
        # Check if the extension matches any in our supported languages
        for lang, extensions in self.SUPPORTED_LANGUAGES.items():
            if ext in extensions:
                print(f"Matched extension '{ext}' to language '{lang}'")  # Diagnóstico
                return lang
        
        # Special cases for files without extensions
        if filename.lower() == "dockerfile":
            return "dockerfile"
        elif filename.lower() in ["makefile", "gnumakefile"]:
            return "makefile"
        
        # Try to infer from filename patterns
        if "build.gradle" in filename.lower():
            return "groovy"
        elif "package.json" in filename.lower():
            return "json"
        elif "docker-compose" in filename.lower() and ext in ["yml", "yaml"]:
            return "yaml"
        
        # Additional special cases for common extensions
        if ext == "xml":
            return "xml"
        elif ext == "java":
            return "java"
        elif ext == "js":
            return "javascript"
        elif ext == "py":
            return "python"
        elif ext == "rb":
            return "ruby"
        elif ext == "php":
            return "php"
        elif ext == "go":
            return "go"
        elif ext == "cs":
            return "csharp"
        elif ext == "ts":
            return "typescript"
        
        # If we can't determine the language, return "unknown"
        print(f"Could not determine language for extension '{ext}'")  # Diagnóstico
        return "unknown"
    
    def _detect_language(self, code: str, filename: Optional[str] = None) -> str:
        """
        Detect the programming language of the code.
        
        Args:
            code: The code to analyze
            filename: Optional filename to help determine the language
            
        Returns:
            The detected language name
        """
        # First try to detect from filename if provided
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.py':
                return "python"
            elif ext in ['.js', '.jsx']:
                return "javascript"
            elif ext in ['.html', '.htm']:
                return "html"
            elif ext in ['.css']:
                return "css"
            elif ext in ['.xml', '.svg']:
                return "xml"
            elif ext in ['.json']:
                return "json"
        
        # If no filename or couldn't detect from extension, try to detect from content
        if "def " in code and "import " in code:
            return "python"
        elif "function " in code or "const " in code or "let " in code:
            return "javascript"
        elif "<html" in code.lower() or "<!doctype html" in code.lower():
            return "html"
        elif "<svg" in code.lower():
            return "xml"
        elif "{" in code and ":" in code and "\"" in code:
            return "json"
        
        # Default to generic if we can't determine
        return "generic"
    
    def _get_language_specific_criteria(self, language: str) -> Dict[str, Any]:
        """
        Get language-specific evaluation criteria.
        
        Args:
            language: The programming language
            
        Returns:
            Dictionary of language-specific criteria
        """
        # Common criteria for all languages
        common_criteria = {
            "formatting": "Code formatting and indentation",
            "naming_conventions": "Naming conventions for variables, functions, classes, etc.",
            "comments": "Quality and quantity of comments",
            "complexity": "Code complexity and readability"
        }
        
        # Language-specific criteria
        language_criteria = {
            "python": {
                "pep8_compliance": "Adherence to PEP 8 style guide",
                "docstrings": "Quality of docstrings",
                "imports": "Organization of imports"
            },
            "javascript": {
                "es6_features": "Use of modern JavaScript features",
                "dom_manipulation": "DOM manipulation practices",
                "async_patterns": "Asynchronous code patterns"
            },
            "java": {
                "java_conventions": "Adherence to Java coding conventions",
                "exception_handling": "Exception handling practices",
                "oop_principles": "Object-oriented programming principles"
            },
            "sql": {
                "query_structure": "SQL query structure and formatting",
                "index_usage": "Proper use of indexes",
                "join_efficiency": "Efficiency of joins"
            },
            "html": {
                "semantic_markup": "Use of semantic HTML elements",
                "accessibility": "Accessibility compliance",
                "responsive_design": "Responsive design principles"
            },
            "css": {
                "selector_specificity": "Appropriate use of selector specificity",
                "reusability": "CSS reusability and modularity",
                "browser_compatibility": "Cross-browser compatibility"
            },
            "yaml": {
                "indentation": "Proper YAML indentation",
                "key_naming": "Key naming conventions",
                "structure": "Overall structure and organization"
            },
            "json": {
                "structure": "JSON structure and organization",
                "validation": "JSON schema validation"
            },
            "xml": {
                "element_naming": "Element naming conventions",
                "structure": "XML structure and organization",
                "validation": "XML schema validation"
            },
            "markdown": {
                "heading_structure": "Proper heading structure",
                "link_usage": "Proper use of links",
                "formatting": "Text formatting and readability"
            },
            "shell": {
                "error_handling": "Error handling practices",
                "variable_usage": "Variable usage and naming",
                "command_structure": "Command structure and organization"
            },
            "powershell": {
                "cmdlet_usage": "Proper use of cmdlets",
                "error_handling": "Error handling practices",
                "variable_usage": "Variable usage and naming"
            },
            "dockerfile": {
                "layer_optimization": "Docker layer optimization",
                "instruction_ordering": "Proper ordering of instructions",
                "best_practices": "Docker best practices"
            },
            "terraform": {
                "resource_organization": "Resource organization",
                "variable_usage": "Variable usage and naming",
                "module_structure": "Module structure and organization"
            },
            "r": {
                "tidyverse_practices": "Tidyverse best practices",
                "function_design": "Function design and organization",
                "data_manipulation": "Data manipulation practices"
            }
        }
        
        # Get the criteria for the specified language, or use empty dict if not found
        specific_criteria = language_criteria.get(language, {})
        
        # Combine common and language-specific criteria
        # Use a new dictionary to avoid modifying the original dictionaries
        combined_criteria = {}
        combined_criteria.update(common_criteria)
        combined_criteria.update(specific_criteria)
        
        return combined_criteria
    
    def _extract_code_from_dff(self, dff_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract code from DFF data format.
        
        Args:
            dff_data: The DFF data from Bitbucket
            
        Returns:
            List of dictionaries with extracted code information
        """
        extracted_files = []
        
        for file_data in dff_data.get("files", []):
            filename = file_data.get("fileName", "unknown")
            status = file_data.get("status", "UNKNOWN")
            
            # Detect language from filename
            language = self._detect_language_from_filename(filename)
            print(f"Detected language for {filename}: {language}")  # Diagnóstico
            
            code_context = file_data.get("codeContext", {})
            added_lines = file_data.get("addedLines", [])
            removed_lines = file_data.get("removedLines", [])
            
            # Extract code based on status
            if status == "ADDED":
                # For added files, use the "after" context or addedLines
                code_lines = code_context.get("after", added_lines)
                extracted_code = "\n".join(code_lines)
            elif status == "MODIFIED":
                # For modified files, use the "after" context with markers for added lines
                after_lines = code_context.get("after", [])
                
                # Create a set of added lines for quick lookup
                added_lines_set = set(added_lines)
                
                # Mark added lines with a comment for better visibility
                marked_lines = []
                for line in after_lines:
                    # Check if this line or a similar line is in addedLines
                    is_added = any(line.strip() == added.strip() for added in added_lines_set)
                    
                    if line.startswith("+"):
                        # Line is already marked as added in the diff
                        marked_lines.append(line[1:].rstrip())  # Remove the '+' marker
                    elif is_added:
                        # Line is in addedLines but not marked in the diff
                        marked_lines.append(line.rstrip())
                    else:
                        # Regular line
                        marked_lines.append(line.rstrip())
                
                extracted_code = "\n".join(marked_lines)
            elif status == "DELETED":
                # For deleted files, use the "before" context or removedLines
                code_lines = code_context.get("before", removed_lines)
                extracted_code = "\n".join(code_lines)
            else:
                # Unknown status, try to use whatever is available
                after_lines = code_context.get("after", [])
                before_lines = code_context.get("before", [])
                
                if after_lines:
                    extracted_code = "\n".join(after_lines)
                elif before_lines:
                    extracted_code = "\n".join(before_lines)
                else:
                    extracted_code = ""
            
            # Create a mapping of line numbers for error reporting
            line_mapping = {}
            for i, line in enumerate(extracted_code.split("\n"), 1):
                line_mapping[i] = i
            
            extracted_files.append({
                "filename": filename,
                "status": status,
                "language": language,
                "code": extracted_code,
                "line_mapping": line_mapping
            })
        
        return extracted_files
    
    async def execute(self, input_data: str) -> str:
        """Execute the style checker tool."""
        try:
            data = json.loads(input_data)
            
            # Check if we have DFF data
            if "dff_data" in data:
                print("StyleChecker: Processing DFF data")
                dff_data = data["dff_data"]
                
                # Process each file individually
                results = []
                files_analyzed = 0
                
                for file_info in dff_data.get("files", []):
                    filename = file_info.get("fileName", "unknown")
                    status = file_info.get("status", "unknown")
                    
                    print(f"StyleChecker: Processing file {filename} with status {status}")
                    
                    # Skip deleted files
                    if status == "DELETED":
                        print(f"StyleChecker: Skipping deleted file {filename}")
                        continue
                    
                    code = None
                    if status in ["ADDED", "MODIFIED"]:
                        code = "\n".join(file_info.get("codeContext", {}).get("after", []))
                    
                    if code:
                        # Detect language for this specific file
                        language = self._detect_language(code, filename)
                        print(f"StyleChecker: Detected language for {filename}: {language}")
                        
                        # Check style for this specific file
                        file_result = self._check_style(code, language, filename)
                        file_result["filename"] = filename
                        file_result["status"] = status
                        file_result["language"] = language
                        
                        results.append(file_result)
                        files_analyzed += 1
                
                print(f"StyleChecker: Style checking completed for {files_analyzed} files")
                
                return json.dumps({
                    "tool_name": "style_checker",
                    "format": "dff",
                    "files_analyzed": files_analyzed,
                    "results": results
                })
            
            # Handle direct code input
            elif "code" in data:
                code = data["code"]
                filename = data.get("filename")
                file_extension = data.get("file_extension")
                
                # Detect language
                language = None
                if filename:
                    language = self._detect_language(code, filename)
                elif file_extension:
                    language = self._detect_language(code, f"file{file_extension}")
                else:
                    language = self._detect_language(code)
                
                # Check style
                result = self._check_style(code, language, filename)
                
                if filename:
                    result["filename"] = filename
                
                return json.dumps({
                    "tool_name": "style_checker",
                    **result
                })
            
            else:
                return json.dumps({
                    "tool_name": "style_checker",
                    "error": "No code or DFF data provided",
                    "score": 0,
                    "summary": "No code to analyze",
                    "issues": []
                })
        
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Error in StyleChecker.execute: {str(e)}")
            print(error_traceback)
            
            return json.dumps({
                "tool_name": "style_checker",
                "error": str(e),
                "score": 0,
                "summary": "Analysis failed",
                "issues": [],
                "details": {},
                "diagnostic_info": {
                    "error_traceback": error_traceback,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            })

    def _check_style(self, code: str, language: str, filename: str = None) -> Dict[str, Any]:
        """Check code style based on language-specific rules."""
        print(f"StyleChecker: Checking style with language: {language}")
        
        # Initialize result structure
        result = {
            "language": language,
            "score": 0,
            "issues": [],
            "summary": ""
        }
        
        # Apply language-specific style checking
        if language == "python":
            return self._check_python_style(code, filename, result)
        elif language == "javascript":
            return self._check_javascript_style(code, filename, result)
        elif language == "xml":
            return self._check_xml_style(code, filename, result)
        else:
            # Generic style checking for unknown languages
            return self._check_generic_style(code, filename, result)

    def _check_python_style(self, code: str, filename: str, result: Dict) -> Dict:
        """Check Python code style."""
        issues = []
        
        # Check line length
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if len(line) > 79:
                issues.append({
                    "line": i + 1,
                    "message": "Line too long (> 79 characters)",
                    "severity": "low",
                    "suggestion": "Break long lines into multiple lines"
                })
        
        # Check indentation (should be 4 spaces)
        for i, line in enumerate(lines):
            if line.startswith(" ") and not line.startswith("    ") and not line.startswith("        "):
                issues.append({
                    "line": i + 1,
                    "message": "Inconsistent indentation (should use 4 spaces)",
                    "severity": "low",
                    "suggestion": "Use 4 spaces for indentation"
                })
        
        # Calculate score based on issues
        score = max(0, 10 - len(issues) * 0.5)
        
        result["issues"] = issues
        result["score"] = score
        result["summary"] = f"Found {len(issues)} style issues in Python code"
        
        return result

    def _check_javascript_style(self, code: str, filename: str, result: Dict) -> Dict:
        """Check JavaScript code style."""
        issues = []
        
        # Check line length
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if len(line) > 100:
                issues.append({
                    "line": i + 1,
                    "message": "Line too long (> 100 characters)",
                    "severity": "low",
                    "suggestion": "Break long lines into multiple lines"
                })
        
        # Check for missing semicolons
        for i, line in enumerate(lines):
            line = line.strip()
            if line and not line.endswith('{') and not line.endswith('}') and \
               not line.endswith(';') and not line.endswith(',') and \
               not line.startswith('//') and not line.startswith('/*') and \
               not line.endswith('*/') and not line.startswith('import') and \
               not line.startswith('export') and not line.startswith('function') and \
               not line.startswith('if') and not line.startswith('else') and \
               not line.startswith('for') and not line.startswith('while'):
                issues.append({
                    "line": i + 1,
                    "message": "Missing semicolon at end of line",
                    "severity": "low",
                    "suggestion": "Add a semicolon at the end of the line"
                })
        
        # Calculate score based on issues
        score = max(0, 10 - len(issues) * 0.5)
        
        result["issues"] = issues
        result["score"] = score
        result["summary"] = f"Found {len(issues)} style issues in JavaScript code"
        
        return result

    def _check_xml_style(self, code: str, filename: str, result: Dict) -> Dict:
        """Check XML code style."""
        issues = []
        
        # Check for proper indentation
        lines = code.split("\n")
        indent_level = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Check if this line has proper indentation
            expected_indent = " " * (indent_level * 2)
            if not line.startswith(expected_indent) and indent_level > 0:
                issues.append({
                    "line": i + 1,
                    "message": f"Improper indentation (expected {indent_level * 2} spaces)",
                    "severity": "low",
                    "suggestion": "Use consistent indentation (2 spaces per level)"
                })
            
            # Update indent level for next line
            if stripped.startswith("</"):
                # Closing tag, decrease indent for this line
                indent_level = max(0, indent_level - 1)
            elif stripped.endswith("/>"):
                # Self-closing tag, indent level stays the same
                pass
            elif "</" in stripped and stripped.startswith("<"):
                # Combined open/close tag on same line, indent level stays the same
                pass
            elif stripped.startswith("<"):
                # Opening tag, increase indent for next line
                indent_level += 1
        
        # Calculate score based on issues
        score = max(0, 10 - len(issues) * 0.5)
        
        result["issues"] = issues
        result["score"] = score
        result["summary"] = f"Found {len(issues)} style issues in XML code"
        
        return result

    def _check_generic_style(self, code: str, filename: str, result: Dict) -> Dict:
        """Check generic code style."""
        issues = []
        
        # Check line length
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if len(line) > 100:
                issues.append({
                    "line": i + 1,
                    "message": "Line too long (> 100 characters)",
                    "severity": "low",
                    "suggestion": "Break long lines into multiple lines"
                })
        
        # Check for trailing whitespace
        for i, line in enumerate(lines):
            if line.rstrip() != line:
                issues.append({
                    "line": i + 1,
                    "message": "Line has trailing whitespace",
                    "severity": "low",
                    "suggestion": "Remove trailing whitespace"
                })
        
        # Calculate score based on issues
        score = max(0, 10 - len(issues) * 0.5)
        
        result["issues"] = issues
        result["score"] = score
        result["summary"] = f"Found {len(issues)} style issues in code"
        
        return result

    def get_description(self) -> str:
        """Get tool description."""
        supported_langs = ", ".join(self.SUPPORTED_LANGUAGES.keys())
        return f"Checks code style and formatting for multiple programming languages including: {supported_langs}" 