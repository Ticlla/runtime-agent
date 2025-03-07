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

from code_review_assistant.tools.style_checker import StyleChecker

async def test_dff_only():
    """Script to test the StyleChecker with specific DFF data."""
    print("Starting StyleChecker DFF test with specific data...")
    
    # Create StyleChecker instance
    style_checker = StyleChecker()
    print("✅ StyleChecker instance created")
    
    try:
        # Datos DFF específicos
        dff_data = {
            "files": [
                {
                    "fileName": "service/src/main/resources/default.config.xml",
                    "status": "MODIFIED",
                    "codeContext": {
                        "before": [
                            "            <!-- Allow unsigned/plain JWT -->",
                            "            <allowPlainTokens>true</allowPlainTokens>  <!-- TODO: change this after ensuring that all clients provide proper token -->",
                            "        </signature>",
                            "        <!-- Options switched on only for gradual rollout period. | end -->",
                            ""
                        ],
                        "after": [
                            "        <secureResources>",
                            "            <ad>/ad/**</ad>",
                            "        </secureResources>",
                            "        <entityPermissions>",
                            "  <swagger>*:*</swagger>",
                            "+             <apiGqlDomainGateway>ad:*</apiGqlDomainGateway>",
                            "        </entityPermissions>",
                            "        <entauth>",
                            "            <accessControlEnabled>true</accessControlEnabled>",
                            "            <secureResources>",
                            "                <ad>/ad/**</ad>",
                            "            </secureResources>",
                            "            <entityPermissions>",
                            "                <swagger>*:*</swagger>",
                            "+                 <apiGqlDomainGateway>ad:*</apiGqlDomainGateway>",
                            "            </entityPermissions>",
                            "        </entauth>",
                            "        <idt>",
                            "            <secureResources>",
                            "                <ad>/ad/**</ad>",
                            "            </secureResources>",
                            "        </idt>",
                            "    </security>",
                            "",
                            "    <apsSearcherDS>"
                        ]
                    },
                    "addedLines": [
                        "            <apiGqlDomainGateway>ad:*</apiGqlDomainGateway>",
                        "                <apiGqlDomainGateway>ad:*</apiGqlDomainGateway>"
                    ],
                    "removedLines": []
                }
            ],
            "summary": {
                "totalFiles": 1,
                "added": 0,
                "modified": 1,
                "deleted": 0
            }
        }
        
        # Analizar los datos DFF
        print("\nAnalyzing DFF data...")
        result = await style_checker.execute(dff_data=dff_data)
        
        # Convert result to dictionary if it's a JSON string
        if isinstance(result, str):
            result = json.loads(result)
        
        # Display results
        print("\nDFF analysis results:")
        print("-" * 50)
        print(f"Files analyzed: {result.get('files_analyzed', 'N/A')}")
        
        # Display results for each file
        if 'results' in result:
            for file_result in result['results']:
                print(f"\nFile: {file_result.get('filename', 'Unknown')}")
                print(f"Status: {file_result.get('status', 'Unknown')}")
                print(f"Language: {file_result.get('language', 'Unknown')}")
                print(f"Score: {file_result.get('score', 'N/A')}/10")
                print(f"Summary: {file_result.get('summary', 'No summary available')}")
                
                # Display details if available
                if 'details' in file_result:
                    print("\nDetails:")
                    for key, value in file_result['details'].items():
                        print(f"- {key}: {value}/10")
                
                # Display issues found
                if 'issues' in file_result:
                    print("\nIssues found:")
                    for issue in file_result['issues']:
                        severity = issue.get('severity', 'unknown')
                        severity_marker = "🔴" if severity == "high" else "🟠" if severity == "medium" else "🟡"
                        
                        print(f"{severity_marker} Line {issue.get('line', 'N/A')}: {issue.get('message', 'No message')}")
                        print(f"   Type: {issue.get('type', 'N/A')}")
                        print(f"   Suggestion: {issue.get('suggestion', 'No suggestion')}")
                        print("-" * 50)
        
        # Display diagnostic info if available
        if 'diagnostic_info' in result:
            print("\nDiagnostic Info:")
            print(json.dumps(result['diagnostic_info'], indent=2))
        
        print("\n✨ DFF test completed!")
        return True
    
    except Exception as e:
        print(f"❌ Error during DFF test: {str(e)}")
        import traceback
        print("Stack trace:")
        print(traceback.format_exc())
        return False

async def main():
    try:
        success = await test_dff_only()
        if not success:
            print("\n❌ Test failed")
            sys.exit(1)
        else:
            print("\n✅ Test succeeded")
    except Exception as e:
        print(f"❌ Error in main: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 