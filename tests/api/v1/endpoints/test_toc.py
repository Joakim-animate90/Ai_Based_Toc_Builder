import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints.toc import router, extract_toc, get_toc_service
from app.models.schemas import TOCRequest, TOCResponse, HealthResponse
from app.services.toc_service import TOCService

# Fixtures
@pytest.fixture
def mock_toc_service():
    """Fixture to create a mock TOC service."""
    mock_service = Mock(spec=TOCService)
    mock_service.extract_toc.return_value = ("Sample TOC content", "toc/table_of_contents.txt")
    return mock_service

@pytest.fixture
def valid_toc_request():
    """Fixture for a valid TOC request object."""
    return TOCRequest(
        pdf_path="/path/to/valid.pdf",
        output_file="toc/output.txt",
        max_pages=10
    )

@pytest.fixture
def valid_toc_request_dict():
    """Fixture for a valid TOC request dictionary."""
    return {
        "pdf_path": "/path/to/valid.pdf",
        "output_file": "toc/output.txt",
        "max_pages": 10
    }

# Tests for health endpoint
def test_health_check():
    """Test the health check endpoint returns the expected response."""
    # This test will need to be updated once you have a main.py file
    # with the actual FastAPI app instance
    response = HealthResponse()
    assert response.status_code == "ok"
    assert response.api_version == "1.0"

# Direct function tests (not through API)
def test_extract_toc_direct_success(mock_toc_service, valid_toc_request):
    """Test the extract_toc function directly."""
    # Setup
    background_tasks = MagicMock()
    
    with patch("os.path.exists", return_value=True):
        # Call function
        result = extract_toc(valid_toc_request, background_tasks, mock_toc_service)
        
        # Verify result
        assert isinstance(result, TOCResponse)
        assert result.success is True
        assert result.toc_content == "Sample TOC content"
        assert result.output_file == "toc/table_of_contents.txt"

def test_extract_toc_direct_file_not_found(valid_toc_request):
    """Test extract_toc function with file not found."""
    # Setup
    background_tasks = MagicMock()
    valid_toc_request.pdf_path = "/non/existent/path.pdf"
    
    with patch("os.path.exists", return_value=False):
        # Call and verify exception
        with pytest.raises(HTTPException) as excinfo:
            extract_toc(valid_toc_request, background_tasks, MagicMock())
        
        assert excinfo.value.status_code == 404
        assert "not found" in excinfo.value.detail

def test_extract_toc_direct_service_error(mock_toc_service, valid_toc_request):
    """Test extract_toc function with service error."""
    # Setup
    background_tasks = MagicMock()
    mock_toc_service.extract_toc.side_effect = Exception("Service error")
    
    with patch("os.path.exists", return_value=True):
        # Call and verify exception
        with pytest.raises(HTTPException) as excinfo:
            extract_toc(valid_toc_request, background_tasks, mock_toc_service)
        
        assert excinfo.value.status_code == 500
        assert excinfo.value.detail == "Service error"

# Parametrized tests for different inputs
@pytest.mark.parametrize("max_pages,expected_max_pages", [
    (None, None),
    (5, 5),
    (20, 20)
])
def test_extract_toc_with_different_max_pages(
    mock_toc_service, valid_toc_request, max_pages, expected_max_pages
):
    """Test TOC extraction with different max_pages values."""
    # Setup
    background_tasks = MagicMock()
    valid_toc_request.max_pages = max_pages
    
    with patch("os.path.exists", return_value=True):
        # Call function
        extract_toc(valid_toc_request, background_tasks, mock_toc_service)
        
        # Verify service call
        mock_toc_service.extract_toc.assert_called_once_with(
            valid_toc_request.pdf_path, 
            valid_toc_request.output_file
        )

# Test get_toc_service dependency
def test_get_toc_service():
    """Test the get_toc_service dependency returns a TOCService instance."""
    service = get_toc_service()
    assert isinstance(service, TOCService)
