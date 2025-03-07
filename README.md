# Code Review Assistant

An API for automatic code analysis using advanced AI techniques.

## Features

- Source code analysis in multiple languages
- Security issue detection
- Performance evaluation
- Best practices verification
- Synchronous and asynchronous analysis

## Installation

```bash
# Clone the repository
git clone https://****.com/your-username/code-review-assistant.git
cd code-review-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Start the server

```bash
python src/run_api.py
```

The server will be available at http://localhost:8000

### API Documentation

Interactive documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Usage Examples

#### Synchronous Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "code_data": {
      "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n",
      "filename": "factorial.py"
    }
  }'
```

#### Asynchronous Analysis

```bash
curl -X POST http://localhost:8000/analyze/async \
  -H "Content-Type: application/json" \
  -d '{
    "code_data": {
      "code": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)\n",
      "filename": "factorial.py"
    }
  }'
```

## Project Structure

```
code-review-assistant/
├── src/
│   ├── code_review_assistant/
│   │   ├── __init__.py
│   │   ├── api.py            # REST API
│   │   ├── main.py           # Main assistant
│   │   ├── tools/            # Analysis tools
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py
│   │   │   ├── security.py
│   │   │   ├── performance.py
│   │   │   └── best_practices.py
│   ├── run_api.py            # Script to run the API
├── tests/                    # Tests
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 