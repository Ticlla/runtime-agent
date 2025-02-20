import asyncio
from code_review_assistant.main import CodeReviewAssistant

async def main():
    # Configuration
    config = {
        "model_config": {
            "model_type": "openai",
            "api_key": "your-api-key",
            "model": "gpt-4"
        },
        "memory_config": {
            "redis": {
                "url": "redis://localhost:6379",
                "namespace": "code_review"
            }
        },
        "review_rules": {
            "max_line_length": 80,
            "max_complexity": 10,
            "style_guide": "pep8",
            "security_level": "high"
        }
    }
    
    # Create and initialize assistant
    assistant = CodeReviewAssistant(config)
    await assistant.initialize()
    
    # Code to review
    code_data = {
        "source_code": """
def process_data(data):
    try:
        result = []
        for item in data:
            # Complex processing
            if item.get('value') > 0:
                if item.get('type') == 'special':
                    if item.get('priority') == 'high':
                        result.append(item)
    except:
        pass
    return result
        """,
        "language": "python",
        "file_path": "process.py",
        "context": {
            "module": "data_processing",
            "criticality": "high"
        }
    }
    
    # Review code
    review = await assistant.review_code(code_data)
    print(review)

if __name__ == "__main__":
    asyncio.run(main()) 