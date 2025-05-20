# AI-Based Table of Contents Builder

[![codecov](https://codecov.io/gh/Joakim-animate90/Ai_Based_Toc_Builder/branch/main/graph/badge.svg)](https://codecov.io/gh/Joakim-animate90/Ai_Based_Toc_Builder)

An intelligent, scalable API for extracting tables of contents from PDF documents using AI.

**[➡️ Check out the UI repository here](https://github.com/Joakim-animate90/Ai_Based_Toc_Builder_ui)**

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

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed on your system
- OpenAI API key

### Environment Configuration
Create a `.env` file in the project root with the following variables:
```bash
PORT=8000
APP_VERSION=1.0.0
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

### Building the Docker Image
```bash
# Build the image
docker build -t ai_toc_builder:latest .

# Build with a specific tag
docker build -t ai_toc_builder:1.0.0 .
```

### Running with Docker Compose

#### Development Mode
Development mode mounts your local code directory, enabling live code reload:
```bash
# Start the service in development mode
docker-compose up

# Run in detached mode
docker-compose up -d
```

#### Production Mode
For production deployment with no code mounting:
```bash
# Create a docker-compose.prod.yml file with no volume mounts for app code
# Then run:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Container Management

#### View Logs
```bash
# View logs
docker-compose logs

# Follow logs
docker-compose logs -f app

# Show only the last 100 lines
docker-compose logs --tail=100 app
```

#### Execute Commands Inside Container
```bash
# Open a shell
docker-compose exec app bash

# Run a one-off command
docker-compose exec app python -m pytest
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
