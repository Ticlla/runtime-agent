from typing import Dict, Any, List
from ai_agent_framework.core.tools import BaseTool
from .base_response import ToolResponse, Issue, Severity
from openai import OpenAI
import os
import json
import datetime

class PerformanceAnalyzer(BaseTool):
    """Tool for performance analysis using LLM."""
    
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
        "scala": ["scala"]
    }
    
    def __init__(self):
        """Initialize performance analyzer."""
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
        
        # Default to unknown if no match found
        print(f"No language match for extension '{ext}', returning 'unknown'")
        return "unknown"
    
    def _detect_language(self, code: str, filename: str = None) -> str:
        """
        Detect the programming language from code and/or filename.
        
        Args:
            code: The code to analyze
            filename: Optional filename for better detection
            
        Returns:
            The detected language name
        """
        # First try to detect from filename if provided
        if filename:
            language = self._detect_language_from_filename(filename)
            if language != "unknown":
                return language
        
        # If we couldn't detect from filename or no filename provided,
        # we could implement heuristic detection based on code content
        # For now, default to Python as it's the primary focus
        return "python"
    
    def _get_language_specific_criteria(self, language: str) -> Dict[str, str]:
        """
        Get language-specific performance criteria.
        
        Args:
            language: The programming language
            
        Returns:
            Dictionary of criteria names and descriptions
        """
        # Default criteria for all languages
        base_criteria = {
            "time_complexity": "Efficiency of algorithms in terms of execution time",
            "space_complexity": "Memory usage and allocation efficiency",
            "algorithm_efficiency": "Selection of appropriate algorithms for the task",
            "resource_usage": "Efficient use of system resources"
        }
        
        # Language-specific criteria
        if language == "python":
            return {
                **base_criteria,
                "python_specific": "Use of Python-specific optimizations (list comprehensions, generators, etc.)",
                "library_usage": "Efficient use of standard and third-party libraries",
                "concurrency": "Proper use of threading, multiprocessing, or async"
            }
        elif language == "javascript":
            return {
                **base_criteria,
                "dom_manipulation": "Efficient DOM operations",
                "event_handling": "Proper event delegation and handling",
                "async_patterns": "Effective use of promises, async/await"
            }
        elif language == "java":
            return {
                **base_criteria,
                "jvm_optimization": "Effective use of JVM features",
                "garbage_collection": "Minimizing GC overhead",
                "concurrency": "Proper use of threads and concurrent collections"
            }
        elif language in ["c", "cpp"]:
            return {
                **base_criteria,
                "memory_management": "Proper allocation and deallocation",
                "pointer_usage": "Efficient use of pointers",
                "compiler_optimization": "Code amenable to compiler optimizations"
            }
        else:
            # For other languages, use the base criteria
            return base_criteria
    
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
    
    async def _analyze_code(self, code: str, language: str, filename: str = None, line_mapping: Dict[int, int] = None) -> Dict[str, Any]:
        """
        Analyze code for performance issues.
        
        Args:
            code: The code to analyze
            language: The programming language
            filename: Optional filename for better language detection
            line_mapping: Optional mapping of line numbers
            
        Returns:
            Analysis results
        """
        # If language is not provided or is unknown, try to detect it
        if not language or language == "unknown":
            detected_language = self._detect_language(code, filename)
        else:
            detected_language = language
        
        print(f"Analyzing code with language: {detected_language}")  # Diagnóstico
        
        # Get language-specific criteria
        criteria = self._get_language_specific_criteria(detected_language)
        
        # Create a criteria string for the prompt
        criteria_str = ", ".join([f"{key} ({desc})" for key, desc in criteria.items()])
        
        prompt = f"""
        You are a performance optimization expert specializing in {detected_language.upper()} programming language. 
        Analyze this code for performance issues:
        
        ```{detected_language}
        {code}
        ```
        
        Evaluate the code based on these criteria: {criteria_str}
        
        Return a JSON with this EXACT structure. All text must be in English:
        {{
            "language": "{detected_language}",
            "score": float,  # 0-10 overall performance score
            "summary": "brief performance assessment",
            "issues": [
                {{
                    "type": "performance_issue_type",
                    "message": "detailed explanation",
                    "line": int,  # Must be a valid integer, not null or None
                    "severity": "high|medium|low",
                    "suggestion": "how to optimize",
                    "complexity": "Big O notation if applicable"
                }}
            ],
            "details": {{
                # Scores for each criterion (0-10)
                {', '.join([f'"{key}": float' for key in criteria.keys()])},
                "bottlenecks": [
                    {{
                        "type": "bottleneck type",
                        "description": "detailed description"
                    }}
                ]
            }}
        }}
        
        Important: For the "line" field in issues, always provide a valid integer. If you can't determine the exact line, use 1.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a performance optimization expert specializing in {detected_language.upper()} programming. You respond only in JSON format. All text must be in English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        llm_response = response.choices[0].message.content
        parsed_response = json.loads(llm_response)
        
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
                suggestion=issue.get("suggestion", "")
            )
            for issue in parsed_response["issues"]
        ]
        
        tool_response = ToolResponse(
            tool_name="performance_analyzer",
            score=parsed_response["score"],
            summary=parsed_response["summary"],
            issues=issues,
            details=parsed_response["details"],
            language=parsed_response["language"]  # Include detected language in response
        )
        
        return json.loads(tool_response.to_json())
    
    async def execute(self, input_data: str) -> str:
        """
        Execute the performance analyzer tool.
        
        Args:
            input_data: JSON string with code to analyze
            
        Returns:
            JSON string with analysis results
        """
        try:
            data = json.loads(input_data)
            
            # Check if we have DFF data
            if "dff_data" in data:
                print("PerformanceAnalyzer: Processing DFF data")
                dff_data = data["dff_data"]
                
                # Process each file individually
                results = []
                files_analyzed = 0
                
                for file_info in dff_data.get("files", []):
                    filename = file_info.get("fileName", "unknown")
                    status = file_info.get("status", "unknown")
                    
                    print(f"PerformanceAnalyzer: Processing file {filename} with status {status}")
                    
                    # Skip deleted files
                    if status == "DELETED":
                        print(f"PerformanceAnalyzer: Skipping deleted file {filename}")
                        continue
                    
                    code = None
                    if status in ["ADDED", "MODIFIED"]:
                        code = "\n".join(file_info.get("codeContext", {}).get("after", []))
                    
                    if code:
                        # Detect language for this specific file
                        language = self._detect_language(code, filename)
                        print(f"PerformanceAnalyzer: Detected language for {filename}: {language}")
                        
                        # Skip non-supported languages for performance analysis
                        if language not in self.SUPPORTED_LANGUAGES and language != "unknown":
                            print(f"PerformanceAnalyzer: Skipping unsupported language: {language}")
                            continue
                        
                        # Analyze this specific file
                        file_result = await self._analyze_code(code, language, filename)
                        file_result["filename"] = filename
                        file_result["status"] = status
                        
                        results.append(file_result)
                        files_analyzed += 1
                
                print(f"PerformanceAnalyzer: Analysis completed for {files_analyzed} files")
                
                return json.dumps({
                    "tool_name": "performance_analyzer",
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
                    "tool_name": "performance_analyzer",
                    **result
                })
            
            else:
                return json.dumps({
                    "tool_name": "performance_analyzer",
                    "error": "No code or DFF data provided",
                    "score": 0,
                    "summary": "No code to analyze",
                    "issues": []
                })
        
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(f"Error in PerformanceAnalyzer.execute: {str(e)}")
            print(error_traceback)
            
            return json.dumps({
                "tool_name": "performance_analyzer",
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
        return f"Analyzes code for performance issues and optimization opportunities across multiple programming languages including: {supported_langs}" 