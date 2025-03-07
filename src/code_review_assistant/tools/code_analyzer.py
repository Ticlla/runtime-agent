from typing import Dict, Any, List, Optional
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI
import ast
import os
import json
import datetime
import re
import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError
import asyncio

class CodeAnalyzer(BaseTool):
    """Tool for analyzing code structure and complexity."""
    
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
        "xml": ["xml", "xsd", "xsl", "xslt", "svg"],
        "markdown": ["md", "markdown"],
        "shell": ["sh", "bash", "zsh"],
        "powershell": ["ps1"],
        "dockerfile": ["dockerfile"],
        "terraform": ["tf", "tfvars"],
        "r": ["r", "rmd"]
    }
    
    def __init__(self):
        """Initialize the code analyzer."""
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
        
        print(f"Extracted extension from {filename}: '{ext}'")
        
        # Check if the extension matches any in our supported languages
        for lang, extensions in self.SUPPORTED_LANGUAGES.items():
            if ext in extensions:
                print(f"Matched extension '{ext}' to language '{lang}'")
                return lang
        
        # Si llegamos aquí, no se encontró coincidencia
        print(f"No language match for extension '{ext}', returning 'unknown'")
        return "unknown"  # Retornamos "unknown" en lugar de defaultear a Python
    
    def _detect_language(self, code: str, filename: str = None) -> str:
        """Mejorar la detección de lenguaje."""
        if filename:
            language = self._detect_language_from_filename(filename)
            if language != "unknown":
                return language
            
        # Mejorar la detección basada en contenido
        patterns = {
            "python": ["def ", "import ", "class "],
            "javascript": ["function", "const ", "let "],
            # Agregar más patrones...
        }
        
        for lang, patterns in patterns.items():
            if any(pattern in code for pattern in patterns):
                return lang
            
        return "unknown"
    
    def _get_language_specific_criteria(self, language: str) -> Dict[str, str]:
        """
        Get language-specific criteria for code analysis.
        
        Args:
            language: The programming language
            
        Returns:
            Dictionary of criteria and their descriptions
        """
        # Default criteria for all languages
        default_criteria = {
            "maintainability": "Code is easy to maintain and modify",
            "readability": "Code is easy to read and understand",
            "modularity": "Code is organized into logical modules or components"
        }
        
        # Language-specific criteria
        if language == "python":
            return {
                **default_criteria,
                "pythonic": "Code follows Python idioms and best practices",
                "imports": "Imports are organized and appropriate",
                "docstrings": "Functions and classes have proper docstrings"
            }
        elif language == "javascript" or language == "typescript":
            return {
                **default_criteria,
                "es_features": "Appropriate use of modern JavaScript features",
                "async_patterns": "Proper handling of asynchronous operations",
                "dom_interaction": "Clean DOM manipulation (if applicable)"
            }
        elif language == "java":
            return {
                **default_criteria,
                "oop_principles": "Adherence to OOP principles",
                "exception_handling": "Proper exception handling",
                "concurrency": "Appropriate use of concurrency features"
            }
        elif language in ["c", "cpp"]:
            return {
                **default_criteria,
                "memory_management": "Proper memory allocation and deallocation",
                "error_handling": "Consistent error handling approach",
                "preprocessor_usage": "Appropriate use of preprocessor directives"
            }
        elif language == "xml":
            return {
                **default_criteria,
                "structure": "Well-formed XML structure",
                "validation": "Adherence to schema or DTD if applicable",
                "namespaces": "Proper use of namespaces",
                "attributes": "Appropriate use of attributes vs. elements",
                "formatting": "Consistent indentation and formatting"
            }
        elif language == "html":
            return {
                **default_criteria,
                "semantic_markup": "Use of semantic HTML elements",
                "accessibility": "Adherence to accessibility standards",
                "structure": "Logical document structure"
            }
        elif language == "css":
            return {
                **default_criteria,
                "selectors": "Efficient and appropriate CSS selectors",
                "reusability": "Reusable and modular CSS",
                "responsiveness": "Support for different screen sizes"
            }
        elif language == "sql":
            return {
                **default_criteria,
                "query_efficiency": "Efficient SQL queries",
                "indexing": "Appropriate use of indexes",
                "transactions": "Proper transaction handling"
            }
        
        # Return default criteria for other languages
        return default_criteria
    
    def _extract_code_from_dff(self, dff_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract code from DFF data.
        
        Args:
            dff_data: DFF data from Bitbucket
            
        Returns:
            List of extracted file information
        """
        extracted_files = []
        
        for file_data in dff_data.get("files", []):
            filename = file_data.get("fileName", "unknown")
            status = file_data.get("status", "UNKNOWN")
            
            # Detect language from filename
            language = self._detect_language_from_filename(filename)
            
            # Extract code based on status
            if status == "ADDED":
                # For added files, use the entire content
                code = "\n".join(file_data.get("codeContext", {}).get("after", []))
                line_mapping = {}  # No mapping needed for added files
            
            elif status == "MODIFIED":
                # For modified files, use the "after" context
                code = "\n".join(file_data.get("codeContext", {}).get("after", []))
                
                # Create line mapping for modified files
                line_mapping = {}
                for i, line in enumerate(file_data.get("codeContext", {}).get("after", []), 1):
                    line_mapping[i] = i  # Simple 1:1 mapping
            
            elif status == "DELETED":
                # For deleted files, use the "before" context
                code = "\n".join(file_data.get("codeContext", {}).get("before", []))
                line_mapping = {}  # No mapping needed for deleted files
            
            else:
                # Unknown status, skip this file
                print(f"Unknown file status: {status} for {filename}")
                continue
            
            extracted_files.append({
                "filename": filename,
                "status": status,
                "language": language,
                "code": code,
                "line_mapping": line_mapping
            })
        
        return extracted_files
    
    def _perform_static_analysis(self, code: str, language: str) -> Dict[str, Any]:
        """
        Perform static analysis on the code.
        
        Args:
            code: The code to analyze
            language: The programming language
            
        Returns:
            Analysis results
        """
        result = {
            "functions": 0,
            "classes": 0,
            "complexity": "low"
        }
        
        # Python-specific static analysis
        if language == "python":
            try:
                tree = ast.parse(code)
                
                # Count functions and classes
                result["functions"] = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
                result["classes"] = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
                
                # Simple complexity heuristic
                if result["functions"] + result["classes"] > 10:
                    result["complexity"] = "high"
                elif result["functions"] + result["classes"] > 5:
                    result["complexity"] = "medium"
                else:
                    result["complexity"] = "low"
                
            except SyntaxError:
                # Handle Python syntax errors
                result["error"] = "Syntax error in Python code"
        
        # XML-specific static analysis
        elif language == "xml":
            try:
                # Try to parse the XML
                root = ET.fromstring(code)
                
                # Count elements, attributes, and namespaces
                elements = 0
                attributes = 0
                namespaces = set()
                
                for elem in root.iter():
                    elements += 1
                    attributes += len(elem.attrib)
                    
                    # Check for namespaces
                    if "}" in elem.tag:
                        ns = elem.tag.split("}")[0].strip("{")
                        namespaces.add(ns)
                
                result["elements"] = elements
                result["attributes"] = attributes
                result["namespaces"] = len(namespaces)
                
                # Check for schema or DTD references
                has_schema = "xsi:schemaLocation" in code or "noNamespaceSchemaLocation" in code
                has_dtd = "<!DOCTYPE" in code
                
                result["has_schema"] = has_schema
                result["has_dtd"] = has_dtd
                
                # Simple complexity heuristic for XML
                if elements > 100 or attributes > 50 or len(namespaces) > 3:
                    result["complexity"] = "high"
                elif elements > 30 or attributes > 20 or len(namespaces) > 1:
                    result["complexity"] = "medium"
                else:
                    result["complexity"] = "low"
                
                # Find XML issues with line numbers
                xml_issues = self._find_xml_issues(code)
                if xml_issues:
                    result["issues"] = xml_issues
                
            except ExpatError as e:
                # Handle XML parsing errors
                line, column = e.lineno, e.offset
                result["error"] = f"XML parsing error at line {line}, column {column}: {str(e)}"
                result["complexity"] = "unknown"
            except Exception as e:
                # Handle other errors
                result["error"] = f"Error analyzing XML: {str(e)}"
                result["complexity"] = "unknown"
        
        # For other languages, we'll rely on the LLM analysis
        # We could add language-specific static analyzers here in the future
        
        return result
    
    def _find_xml_issues(self, code: str) -> List[Dict[str, Any]]:
        """
        Find issues in XML code with line numbers.
        
        Args:
            code: The XML code to analyze
            
        Returns:
            List of issues with line numbers
        """
        issues = []
        
        # Split code into lines for analysis
        lines = code.split('\n')
        
        # Check for unclosed tags
        open_tags = []
        for i, line in enumerate(lines, 1):
            # Skip comments and processing instructions
            if "<!--" in line or "<?xml" in line:
                continue
                
            # Find opening tags
            for match in re.finditer(r'<([a-zA-Z0-9_:-]+)(?:\s+[^>]*)?(?<!/)>', line):
                tag = match.group(1)
                if tag:
                    open_tags.append((tag, i))
            
            # Find self-closing tags
            for match in re.finditer(r'<([a-zA-Z0-9_:-]+)(?:\s+[^>]*)?\s*/>', line):
                pass  # Self-closing tags don't need to be tracked
            
            # Find closing tags
            for match in re.finditer(r'</([a-zA-Z0-9_:-]+)>', line):
                tag = match.group(1)
                if tag and open_tags:
                    if open_tags[-1][0] == tag:
                        open_tags.pop()
                    else:
                        # Mismatched closing tag
                        issues.append({
                            "type": "xml_structure",
                            "message": f"Mismatched closing tag: expected </{open_tags[-1][0]}>, found </{tag}>",
                            "line": i,
                            "severity": "high",
                            "suggestion": f"Replace </{tag}> with </{open_tags[-1][0]}> or fix the nesting structure"
                        })
        
        # Report unclosed tags
        for tag, line in open_tags:
            issues.append({
                "type": "xml_structure",
                "message": f"Unclosed tag: <{tag}> opened at line {line} is never closed",
                "line": line,
                "severity": "high",
                "suggestion": f"Add a closing tag </{tag}> at the appropriate position"
            })
        
        # Check for inconsistent indentation
        indent_pattern = None
        for i, line in enumerate(lines, 1):
            if line.strip() and not line.strip().startswith("<!--"):
                current_indent = len(line) - len(line.lstrip())
                if current_indent > 0:
                    # Check if this is a closing tag
                    if re.match(r'\s*</[a-zA-Z0-9_:-]+>', line):
                        # Closing tags should have the same indentation as their opening tag
                        # This is a simplified check; a full check would require tracking opening tags
                        pass
                    elif indent_pattern is None:
                        # First indented line sets the pattern
                        indent_pattern = current_indent
                    elif current_indent % indent_pattern != 0:
                        issues.append({
                            "type": "xml_formatting",
                            "message": f"Inconsistent indentation at line {i}",
                            "line": i,
                            "severity": "low",
                            "suggestion": f"Use consistent indentation (multiples of {indent_pattern} spaces)"
                        })
        
        # Check for missing XML declaration
        if not any("<?xml" in line for line in lines[:3]):
            issues.append({
                "type": "xml_structure",
                "message": "Missing XML declaration",
                "line": 1,
                "severity": "medium",
                "suggestion": "Add <?xml version=\"1.0\" encoding=\"UTF-8\"?> at the beginning of the file"
            })
        
        return issues
    
    async def _analyze_code(self, code: str, language: Optional[str] = None, filename: Optional[str] = None, line_mapping: Optional[Dict[int, int]] = None) -> Dict[str, Any]:
        """
        Analyze code and return detailed results.
        
        Args:
            code: The code to analyze
            language: Optional language hint
            filename: Optional filename
            line_mapping: Optional mapping from line numbers in the snippet to line numbers in the original file
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Detect language if not provided
            if not language or language == "unknown":
                language = self._detect_language(code, filename)
                print(f"Detected language for {filename or 'code'}: {language}")
            
            # Si el lenguaje sigue siendo desconocido, usamos un análisis genérico
            if language == "unknown":
                print(f"Warning: Using generic analysis for unknown language in {filename or 'code'}")
                return {
                    "language": "unknown",
                    "score": 5.0,  # Puntuación neutral
                    "summary": "No se pudo determinar el lenguaje del código para un análisis específico.",
                    "issues": [],
                    "patterns": [],
                    "metrics": {
                        "maintainability": 5.0,
                        "readability": 5.0,
                        "reliability": 5.0
                    },
                    "static_analysis": {
                        "functions": 0,
                        "classes": 0,
                        "complexity": "unknown"
                    }
                }
            
            print(f"Analyzing code with language: {language}")
            
            # Perform static analysis
            static_analysis = self._perform_static_analysis(code, language)
            
            # Get language-specific criteria
            criteria = self._get_language_specific_criteria(language)
            
            # For XML, perform specific XML analysis
            xml_issues = []
            if language == "xml":
                xml_issues = self._find_xml_issues(code)
            
            # Create a criteria string for the prompt
            criteria_str = ", ".join([f"{key} ({desc})" for key, desc in criteria.items()])
            
            # Add static analysis results to the prompt if available
            static_analysis_str = ""
            if "error" not in static_analysis:
                if language == "python":
                    static_analysis_str = f"Static analysis found {static_analysis['functions']} functions and {static_analysis['classes']} classes with {static_analysis['complexity']} complexity."
                elif language == "xml":
                    static_analysis_str = f"Static analysis found {static_analysis.get('elements', 0)} elements, {static_analysis.get('attributes', 0)} attributes, and {static_analysis.get('namespaces', 0)} namespaces with {static_analysis['complexity']} complexity."
                    if static_analysis.get("has_schema"):
                        static_analysis_str += " The XML references a schema."
                    if static_analysis.get("has_dtd"):
                        static_analysis_str += " The XML includes a DTD."
                    if static_analysis.get("issues"):
                        static_analysis_str += f" Found {len(static_analysis['issues'])} structural issues."
            
            prompt = f"""
            You are a code analysis expert specializing in {language.upper()} programming language. 
            Analyze this code for structure, complexity, and potential issues:
            
            ```{language}
            {code}
            ```
            
            {static_analysis_str}
            
            Evaluate the code based on these criteria: {criteria_str}
            
            Return a JSON with this EXACT structure. All text must be in English:
            {{
                "language": "{language}",
                "score": float,  # 0-10 overall score
                "summary": "brief overall assessment",
                "issues": [
                    {{
                        "type": "issue_type",
                        "message": "detailed explanation",
                        "line": int,  # Must be a valid integer, not null or None
                        "severity": "high|medium|low",
                        "suggestion": "how to fix"
                    }}
                ],
                "details": {{
                    # Scores for each criterion (0-10)
                    {', '.join([f'"{key}": float' for key in criteria.keys()])},
                    "code_structure": {{
                        # Structure details
                    }}
                }}
            }}
            
            Important: For the "line" field in issues, always provide a valid integer. If you can't determine the exact line, use 1.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are a code analysis expert specializing in {language.upper()} programming. You respond only in JSON format. All text must be in English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            llm_response = response.choices[0].message.content
            parsed_response = json.loads(llm_response)
            
            # Merge static analysis results if available
            if "code_structure" in parsed_response.get("details", {}):
                # Only override if we have valid static analysis results
                if "error" not in static_analysis:
                    parsed_response["details"]["code_structure"].update(static_analysis)
            else:
                parsed_response.setdefault("details", {})["code_structure"] = static_analysis
            
            # Add static analysis issues to LLM issues if available
            if "issues" in static_analysis:
                parsed_response.setdefault("issues", []).extend(static_analysis["issues"])
            
            # Apply line mapping if provided
            if line_mapping:
                for issue in parsed_response.get("issues", []):
                    original_line = issue.get("line")
                    if original_line is not None and original_line in line_mapping:
                        issue["line"] = line_mapping[original_line]
                    elif original_line is None or not isinstance(original_line, int):
                        # If line is None or not an integer, set it to 1
                        issue["line"] = 1
            
            # Convert to standard format
            issues = [
                Issue(
                    type=issue["type"],
                    message=issue["message"],
                    line=issue.get("line", 1),  # Default to line 1 if not provided
                    severity=Severity(issue["severity"]),
                    suggestion=issue["suggestion"]
                )
                for issue in parsed_response["issues"]
            ]
            
            tool_response = ToolResponse(
                tool_name="code_analyzer",
                score=parsed_response["score"],
                summary=parsed_response["summary"],
                issues=issues,
                details=parsed_response["details"],
                language=parsed_response["language"]  # Include detected language in response
            )
            
            return json.loads(tool_response.to_json())
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            
            return json.dumps({
                "tool_name": "code_analyzer",
                "error": f"Code analysis failed: {str(e)}",
                "score": 0,
                "summary": "Analysis failed",
                "issues": [],
                "details": {},
                "diagnostic_info": {
                    "error_traceback": error_traceback,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }, indent=2)
    
    async def execute(self, input_data: str) -> str:
        """
        Execute the code analysis tool.
        
        Args:
            input_data: JSON string with code to analyze
            
        Returns:
            JSON string with analysis results
        """
        try:
            data = json.loads(input_data)
            
            # Check if we have DFF data
            if "dff_data" in data:
                print("CodeAnalyzer: Processing DFF data")
                dff_data = data["dff_data"]
                
                # Process each file individually
                results = []
                files_analyzed = 0
                
                for file_info in dff_data.get("files", []):
                    filename = file_info.get("fileName", "unknown")
                    status = file_info.get("status", "unknown")
                    
                    print(f"CodeAnalyzer: Processing file {filename} with status {status}")
                    
                    # Get the code to analyze based on status
                    if status == "DELETED":
                        # Skip deleted files or analyze them differently
                        print(f"CodeAnalyzer: Skipping deleted file {filename}")
                        continue
                    
                    code = None
                    if status == "ADDED":
                        code = "\n".join(file_info.get("codeContext", {}).get("after", []))
                    elif status == "MODIFIED":
                        code = "\n".join(file_info.get("codeContext", {}).get("after", []))
                    
                    if code:
                        # Detect language for this specific file
                        language = self._detect_language(code, filename)
                        print(f"CodeAnalyzer: Detected language for {filename}: {language}")
                        
                        # Analyze this specific file
                        file_result = await self._analyze_code(code, language, filename)
                        file_result["filename"] = filename
                        file_result["status"] = status
                        
                        results.append(file_result)
                        files_analyzed += 1
                
                print(f"CodeAnalyzer: Analysis completed for {files_analyzed} files")
                
                return json.dumps({
                    "tool_name": "code_analyzer",
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
                
                # Analyze code
                result = await self._analyze_code(code, language, filename)
                
                if filename:
                    result["filename"] = filename
                
                return json.dumps({
                    "tool_name": "code_analyzer",
                    **result
                })
            
            else:
                return json.dumps({
                    "tool_name": "code_analyzer",
                    "error": "No code or DFF data provided",
                    "score": 0,
                    "summary": "No code to analyze",
                    "issues": []
                })
        
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Error in CodeAnalyzer.execute: {str(e)}")
            print(error_traceback)
            
            return json.dumps({
                "tool_name": "code_analyzer",
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
    
    def get_description(self) -> str:
        """Get tool description."""
        supported_langs = ", ".join(self.SUPPORTED_LANGUAGES.keys())
        return f"Analyzes code structure, complexity and identifies potential issues across multiple programming languages including: {supported_langs}"

    def analyze(self, code_or_data, filename=None):
        """
        Analiza el código fuente proporcionado.
        
        Args:
            code_or_data: Puede ser una cadena de código o un diccionario con datos del código
            filename: Nombre del archivo (opcional si code_or_data es un diccionario)
            
        Returns:
            dict: Resultados del análisis con métricas de calidad y problemas detectados
        """
        try:
            # Preparar los datos para execute()
            if isinstance(code_or_data, dict):
                input_data = json.dumps(code_or_data)
            else:
                input_data = json.dumps({
                    "code": code_or_data,
                    "filename": filename
                })
            
            # Ejecutar el análisis de forma síncrona
            result_json = asyncio.run(self.execute(input_data))
            
            # Convertir el resultado de JSON a diccionario
            result = json.loads(result_json)
            
            # Verificar si hay un error en el resultado
            if "error" in result:
                print(f"Error en analyze(): {result['error']}")
            
            return result
        except Exception as e:
            import traceback
            print(f"Exception en analyze(): {str(e)}")
            print(traceback.format_exc())
            
            # Devolver un resultado de error
            return {
                "tool_name": "code_analyzer",
                "error": str(e),
                "issues": [],
                "quality_metrics": {},
                "language": "unknown"
            } 