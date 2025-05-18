import pytest
from pydantic import ValidationError

from app.models.schemas import TOCRequest, TOCResponse, HealthResponse

def test_toc_request_valid():
    """Test TOCRequest with valid data."""
    # Test with all fields
    request = TOCRequest(
        pdf_path="/path/to/document.pdf",
        output_file="toc/output.txt",
        max_pages=10
    )
    assert request.pdf_path == "/path/to/document.pdf"
    assert request.output_file == "toc/output.txt"
    assert request.max_pages == 10
    
    # Test with only required fields
    request = TOCRequest(pdf_path="/path/to/document.pdf")
    assert request.pdf_path == "/path/to/document.pdf"
    assert request.output_file is None
    assert request.max_pages == 10  # Default value

def test_toc_request_invalid():
    """Test TOCRequest validation."""
    # Test missing required field
    with pytest.raises(ValidationError):
        TOCRequest()
    
    # Test invalid type for max_pages
    with pytest.raises(ValidationError):
        TOCRequest(pdf_path="/path/to/doc.pdf", max_pages="not a number")

def test_toc_response_valid():
    """Test TOCResponse with valid data."""
    response = TOCResponse(
        success=True,
        toc_content="Sample TOC",
        output_file="toc/output.txt"
    )
    assert response.success is True
    assert response.toc_content == "Sample TOC"
    assert response.output_file == "toc/output.txt"

def test_toc_response_invalid():
    """Test TOCResponse validation."""
    # Test missing required fields
    with pytest.raises(ValidationError):
        TOCResponse()
    
    with pytest.raises(ValidationError):
        TOCResponse(success=True)
    
    with pytest.raises(ValidationError):
        TOCResponse(success=True, toc_content="Sample")

def test_health_response():
    """Test HealthResponse default values."""
    response = HealthResponse()
    assert response.status == "ok"
    assert response.api_version == "1.0"
    
    # Test with custom values
    response = HealthResponse(status="error", api_version="2.0")
    assert response.status == "error"
    assert response.api_version == "2.0"
