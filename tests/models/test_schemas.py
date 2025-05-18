import pytest
from pydantic import ValidationError

from app.models.schemas import TOCRequest, TOCResponse, HealthResponse

def test_toc_request_valid():
    """Test TOCRequest with valid data."""
    # Test with all fields
    request = TOCRequest(
        output_file="toc/output.txt",
        max_pages=10
    )
    assert request.output_file == "toc/output.txt"
    assert request.max_pages == 10
    
    # Test with no fields (all optional now)
    request = TOCRequest()
    assert request.output_file is None
    assert request.max_pages == 10  # Default value

def test_toc_request_invalid():
    """Test TOCRequest validation."""
    # Test invalid type for max_pages
    with pytest.raises(ValidationError):
        TOCRequest(max_pages="not a number")
    
    # Test negative value for max_pages
    with pytest.raises(ValidationError):
        TOCRequest(max_pages=-1)

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
