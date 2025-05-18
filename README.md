# AI-Based Table of Contents Builder

An intelligent, scalable API for extracting tables of contents from PDF documents using AI.

## Features

- Extract tables of contents from PDF documents using OpenAI Vision API
- Thread-based PDF processing for optimal performance
- RESTful API with FastAPI
- Comprehensive test suite with pytest
- Proper separation of concerns with a modular architecture

## Project Structure

```
app/
├── api/                # API endpoints
│   └── v1/             # API version 1
│       ├── endpoints/  # API route handlers
│       └── api.py      # API router
├── core/               # Core application components
│   └── config.py       # Application configuration
├── models/             # Pydantic data models
│   └── schemas.py      # Request and response schemas
├── services/           # Business logic services
│   ├── openai_service.py  # OpenAI API integration
│   ├── pdf_service.py     # PDF processing
│   └── toc_service.py     # TOC extraction orchestration
├── utils/              # Utility functions and helpers
│   ├── decorators.py      # Function decorators
│   └── process_image_thread.py  # Threaded PDF processing
└── main.py             # Application entry point

tests/                  # Test suite
├── api/                # API tests
├── models/             # Model tests
├── services/           # Service tests
└── utils/              # Utility tests
```

## Getting Started

### Prerequisites

- Python 3.8+
- [OpenAI API key](https://platform.openai.com/)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Ai_Based_Toc_Builder.git
   cd Ai_Based_Toc_Builder
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4.1-mini
   ```

### Running the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once the application is running, access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage Example

### Extracting a TOC from a PDF

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/toc/extract",
    json={
        "pdf_path": "/path/to/your/document.pdf",
        "output_file": "toc/my_toc.txt",
        "max_pages": 10
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"TOC extracted: {result['success']}")
    print(f"Saved to: {result['output_file']}")
    print(result['toc_content'])
else:
    print(f"Error: {response.json()}")
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test category
pytest tests/api/
pytest tests/services/
pytest tests/utils/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [OpenAI](https://openai.com/)
