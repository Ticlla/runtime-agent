import sys
import os
import asyncio
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add src directory to path to import the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from code_review_assistant.main import CodeReviewAssistant

async def test_dff_analysis():
    """Test CodeReviewAssistant with a complex DFF example."""
    print("\n🔍 Testing DFF analysis with multiple file types...")
    
    # Create CodeReviewAssistant instance
    assistant = CodeReviewAssistant()
    await assistant.initialize()
    print("✅ CodeReviewAssistant initialized")
    
    # Sample DFF data with multiple file types
    dff_data = {
        "summary": {
            "total_files": 4,
            "added": 1,
            "modified": 2,
            "deleted": 1
        },
        "files": [
            {
                "fileName": "src/utils/helpers.py",
                "status": "MODIFIED",
                "codeContext": {
                    "before": [
                        "def calculate_average(numbers):",
                        "    if not numbers:",
                        "        return 0",
                        "    return sum(numbers) / len(numbers)",
                        "",
                        "def find_duplicates(items):",
                        "    seen = {}",
                        "    dupes = []",
                        "    for item in items:",
                        "        if item in seen:",
                        "            dupes.append(item)",
                        "        else:",
                        "            seen[item] = 1",
                        "    return dupes"
                    ],
                    "after": [
                        "def calculate_average(numbers):",
                        "    if not numbers:",
                        "        return 0",
                        "    return sum(numbers) / len(numbers)",
                        "",
                        "def find_duplicates(items):",
                        "    seen = {}",
                        "    dupes = []",
                        "    for item in items:",
                        "        if item in seen:",
                        "            dupes.append(item)",
                        "        else:",
                        "            seen[item] = 1",
                        "    return dupes",
                        "",
                        "def safe_divide(a, b):",
                        "    if b == 0:",
                        "        return 0",
                        "    return a / b"
                    ]
                }
            },
            {
                "fileName": "config/settings.xml",
                "status": "MODIFIED",
                "codeContext": {
                    "before": [
                        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                        "<settings>",
                        "    <database>",
                        "        <host>localhost</host>",
                        "        <port>5432</port>",
                        "        <user>admin</user>",
                        "        <password>secret</password>",
                        "    </database>",
                        "    <logging>",
                        "        <level>INFO</level>",
                        "        <file>app.log</file>",
                        "    </logging>",
                        "</settings>"
                    ],
                    "after": [
                        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
                        "<settings>",
                        "    <database>",
                        "        <host>db.example.com</host>",
                        "        <port>5432</port>",
                        "        <user>admin</user>",
                        "        <password>secret</password>",
                        "    </database>",
                        "    <logging>",
                        "        <level>DEBUG</level>",
                        "        <file>app.log</file>",
                        "    </logging>",
                        "    <cache>",
                        "        <enabled>true</enabled>",
                        "        <ttl>3600</ttl>",
                        "    </cache>",
                        "</settings>"
                    ]
                }
            },
            {
                "fileName": "src/frontend/app.js",
                "status": "ADDED",
                "codeContext": {
                    "after": [
                        "function initApp() {",
                        "    console.log('Initializing app...');",
                        "    ",
                        "    // Set up event listeners",
                        "    document.getElementById('submit-btn').addEventListener('click', function() {",
                        "        const data = {",
                        "            name: document.getElementById('name-input').value,",
                        "            email: document.getElementById('email-input').value",
                        "        };",
                        "        ",
                        "        submitForm(data);",
                        "    });",
                        "}",
                        "",
                        "function submitForm(data) {",
                        "    console.log('Submitting form with data:', data);",
                        "    ",
                        "    // TODO: Implement form submission",
                        "    alert('Form submitted!');",
                        "}",
                        "",
                        "// Initialize the app when the DOM is loaded",
                        "document.addEventListener('DOMContentLoaded', initApp);"
                    ]
                }
            },
            {
                "fileName": "tests/test_helpers.py",
                "status": "DELETED",
                "codeContext": {
                    "before": [
                        "import unittest",
                        "from src.utils.helpers import calculate_average, find_duplicates",
                        "",
                        "class TestHelpers(unittest.TestCase):",
                        "    def test_calculate_average(self):",
                        "        self.assertEqual(calculate_average([1, 2, 3, 4, 5]), 3)",
                        "        self.assertEqual(calculate_average([]), 0)",
                        "        ",
                        "    def test_find_duplicates(self):",
                        "        self.assertEqual(find_duplicates([1, 2, 3, 2, 1]), [2, 1])",
                        "        self.assertEqual(find_duplicates([1, 2, 3]), [])",
                        "",
                        "if __name__ == '__main__':",
                        "    unittest.main()"
                    ]
                }
            }
        ]
    }
    
    try:
        # Review the code - IMPORTANT: Pass DFF data correctly
        result = await assistant.review_code({
            "dff_data": dff_data  # Make sure this matches what review_code expects
        })
        
        # Print the result
        print("\n📊 Analysis result:")
        print(f"Overall score: {result.get('score', 'N/A')}/10")
        
        # Print quality metrics
        print("\n🔍 Quality metrics:")
        quality_metrics = result.get("quality_metrics", {})
        for metric, value in quality_metrics.items():
            print(f"- {metric}: {value}")
        
        # Add debug logging to identify why file results aren't showing
        print("\n📊 Tool Results:")
        if "raw_results" in result:
            for tool_name in ["analysis", "style", "performance", "security"]:
                if tool_name in result["raw_results"]:
                    print(f"  - {tool_name}: {type(result['raw_results'][tool_name])}")
                    if isinstance(result["raw_results"][tool_name], dict):
                        print(f"    - Keys: {list(result['raw_results'][tool_name].keys())}")
                        if "format" in result["raw_results"][tool_name]:
                            print(f"    - Format: {result['raw_results'][tool_name]['format']}")
                        if "error" in result["raw_results"][tool_name]:
                            print(f"    - Error: {result['raw_results'][tool_name]['error']}")
                else:
                    print(f"  - {tool_name}: Not present in raw_results")
        else:
            print("  - raw_results key not found in result")
        
        # Print issues summary
        total_issues = result.get("total_issues", 0)
        critical_issues = result.get("critical_issues_count", 0)
        print(f"\n⚠️ Issues found: {total_issues} (critical: {critical_issues})")
        
        # Print critical issues
        if result.get("critical_issues"):
            print("\n🚨 Critical issues:")
            for issue in result.get("critical_issues"):
                print(f"- {issue.get('description')}")
                print(f"  File: {issue.get('file', 'N/A')}")
                print(f"  Line: {issue.get('line', 'N/A')}")
                print(f"  Impact: {issue.get('impact')}")
                print(f"  Solution: {issue.get('solution')}")
        
        # Print recommendations
        if result.get("recommendations"):
            print("\n💡 Recommendations:")
            for rec in result.get("recommendations"):
                print(f"- {rec.get('description')} (Priority: {rec.get('priority')})")
        
        # Print synthesis
        if "synthesis" in result:
            print("\n📝 Synthesis:")
            print(result["synthesis"].get("summary", "No summary available"))
        
        # Print raw results for debugging
        print("\n🔍 Raw results for debugging:")
        print(f"Keys in result: {list(result.keys())}")
        if "analysis" in result:
            print(f"Keys in analysis: {list(result['analysis'].keys())}")
        
        print("\n📁 Results by file:")
        if "raw_results" in result:
            # Collect all files from all tools
            all_files = set()
            for tool_name in ["analysis", "style", "performance", "security"]:
                if tool_name in result["raw_results"] and "results" in result["raw_results"][tool_name]:
                    for file_result in result["raw_results"][tool_name].get("results", []):
                        if "filename" in file_result:
                            all_files.add(file_result["filename"])
            
            # Display results for each file
            for filename in sorted(all_files):
                print(f"\n  📄 {filename}:")
                for tool_name in ["analysis", "style", "performance", "security"]:
                    if tool_name in result["raw_results"] and "results" in result["raw_results"][tool_name]:
                        for file_result in result["raw_results"][tool_name].get("results", []):
                            if file_result.get("filename") == filename:
                                issues_count = len(file_result.get("issues", []))
                                score = file_result.get("score", "N/A")
                                print(f"    - {tool_name}: Score {score}, Issues: {issues_count}")
                                
                                # Show top issues
                                if issues_count > 0:
                                    print(f"      Top issues:")
                                    for i, issue in enumerate(file_result.get("issues", [])[:3]):  # Show top 3
                                        severity = issue.get("severity", "unknown")
                                        message = issue.get("message", "No description")
                                        print(f"      {i+1}. [{severity}] {message}")
                                    
                                    if issues_count > 3:
                                        print(f"      ... and {issues_count - 3} more issues")
        else:
            print("  - raw_results key not found in result")
        
        print("\n✨ DFF analysis test completed!")
        return True
    
    except Exception as e:
        print(f"❌ Error during DFF analysis: {str(e)}")
        import traceback
        print("Stack trace:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        # Run the test
        success = asyncio.run(test_dff_analysis())
        
        if success:
            print("\n✅ Test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Test failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error in main: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1) 