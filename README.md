# AI-Based Table of Contents Builder

[![codecov](https://codecov.io/gh/Joakim-animate90/Ai_Based_Toc_Builder/branch/main/graph/badge.svg)](https://codecov.io/gh/Joakim-animate90/Ai_Based_Toc_Builder)

An intelligent, scalable API for extracting tables of contents from PDF documents using AI.

**[➡️ Check out the UI repository here](https://github.com/Joakim-animate90/Ai_Based_Toc_Builder_ui)**

## Features

- Extract tables of contents from PDF documents using OpenAI Vision API
- Thread-based PDF processing for optimal performance
- RESTful API with FastAPI with comprehensive Swagger documentation
- Support for multiple input methods: direct file upload, URL, and browser form upload
- Comprehensive test suite with pytest and Codecov integration
- Production-ready Docker deployment with optimized settings
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

The API provides three main endpoints for extracting tables of contents:

1. `/api/v1/toc/extract` - Upload a PDF file directly
2. `/api/v1/toc/extract-from-url` - Process a PDF from a URL
3. `/api/v1/toc/extract-from-browser` - Upload from browser forms (optimized for multipart/form-data)

Example curl command for browser uploads:
```bash
curl -X POST "http://localhost:8000/api/v1/toc/extract-from-browser" \
  -H "accept: application/json" \
  -F "file=@your_file.pdf" \
  -F "filename=your_file.pdf" \
  -F "max_pages=10"
```

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

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed on your system
- OpenAI API key

### Environment Configuration
The Docker configuration expects environment variables for the API key and other settings. These can be provided in two ways:

1. **Environment variables in docker-compose.yml**:
```yaml
environment:
  - OPENAI_API_KEY=your_api_key_here
  - OPENAI_MODEL=gpt-4.1-mini
  - PDF_MAX_PAGES=10
  - DEFAULT_THREAD_COUNT=4
  - LOG_LEVEL=warning
```

2. **Command line when running Docker**:
```bash
OPENAI_API_KEY=your_api_key_here sudo -E docker compose up
```

### Building the Docker Image
```bash
# Build the image
docker compose build

# Or manually
docker build -t joakimanimate90/ai_based_toc_builder:latest .
```

### Running with Docker Compose

#### Development Mode
Development mode mounts your local code directory, enabling live code reload:
```bash
# Start the service in development mode
docker compose up

# Run in detached mode
docker compose up -d
```

#### Production Mode
For production deployment:
```bash
# Build and run with optimized settings
docker compose up --build -d

# With explicit API key
OPENAI_API_KEY=your_api_key_here sudo -E docker compose up -d
```

The production configuration in the Dockerfile includes:
- Multiple worker processes for better performance
- Optimized logging settings
- Proper proxy header handling
- Security improvements with non-root user

### Container Management

#### View Logs
```bash
# View logs
docker compose logs

# Follow logs
docker compose logs -f app

# Show only the last 100 lines
docker compose logs --tail=100 app
```

#### Execute Commands Inside Container
```bash
# Open a shell
docker compose exec app bash

# Run a one-off command
docker compose exec app python -m pytest
```

#### Using Version Tags
You can create and use version tags for your image:

```bash
# Create a git tag
git tag v1.0.0
git push origin v1.0.0

# This will trigger the CI/CD workflow to build and push a tagged Docker image
# You can then run a specific version:
docker pull joakimanimate90/ai_based_toc_builder:v1.0.0
docker run -e OPENAI_API_KEY=your_key joakimanimate90/ai_based_toc_builder:v1.0.0
```

#### Rebuild After Code Changes
In development mode with mounted volumes, most changes apply automatically. For changes to dependencies:
```bash
# Rebuild the container
docker-compose up --build app

# Restart the service
docker-compose restart app
```

### Stopping Services
```bash
# Stop the service
docker-compose down

# Stop and remove volumes (will delete persistent TOC data)
docker-compose down -v
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [PyMuPDF](https://pymupdf.readthedocs.io/)
- [OpenAI](https://openai.com/)
