import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from fastapi import HTTPException, UploadFile

from app.api.v1.endpoints.toc import extract_toc, get_toc_service
from app.models.schemas import TOCRequest, TOCResponse, HealthResponse
from app.services.toc_service import TOCService


# Fixtures
@pytest.fixture
def mock_toc_service():
    """Fixture to create a mock TOC service."""
    mock_service = Mock(spec=TOCService)
    mock_service.extract_toc.return_value = (
        "Sample TOC content",
        None,
    )
    mock_service.extract_toc_from_upload.return_value = (
        "Sample TOC content",
        None,
    )
    return mock_service


@pytest.fixture
def valid_toc_request():
    """Fixture for a valid TOC request object."""
    return TOCRequest(output_file="toc/output.txt", max_pages=10)


@pytest.fixture
def valid_toc_request_dict():
    """Fixture for a valid TOC request dictionary."""
    return {"output_file": "toc/output.txt", "max_pages": 10}


@pytest.fixture
def mock_pdf_file():
    """Fixture for a mock PDF file upload."""
    # Create a mock PDF content
    content = b"PDF content"

    # Create a mock UploadFile object
    upload_file = MagicMock(spec=UploadFile)
    upload_file.filename = "test.pdf"
    upload_file.read = AsyncMock(return_value=content)
    return upload_file


# Tests for health endpoint
def test_health_check():
    """Test the health check endpoint returns the expected response."""
    # This test will need to be updated once you have a main.py file
    # with the actual FastAPI app instance
    response = HealthResponse()
    assert response.status == "ok"
    assert response.api_version == "1.0"


# Direct function tests (not through API)
@pytest.mark.asyncio
async def test_extract_toc_direct_success(
    mock_toc_service, valid_toc_request, mock_pdf_file
):
    """Test the extract_toc function directly."""
    # Setup
    background_tasks = MagicMock()

    # Call function
    result = await extract_toc(
        mock_pdf_file, valid_toc_request, background_tasks, mock_toc_service
    )

    # Verify result
    assert isinstance(result, TOCResponse)
    assert result.success is True
    assert result.toc_content == "Sample TOC content"
    assert result.output_file is None  # No file is saved now

    # Verify service call
    mock_pdf_file.read.assert_awaited_once()
    mock_toc_service.extract_toc_from_upload.assert_called_once_with(
        mock_pdf_file.read.return_value,
        mock_pdf_file.filename,
        valid_toc_request.output_file,
        valid_toc_request.max_pages,
    )


@pytest.mark.asyncio
async def test_extract_toc_invalid_file_type(valid_toc_request):
    """Test extract_toc function with invalid file type."""
    # Setup
    background_tasks = MagicMock()

    # Create invalid file type
    invalid_file = MagicMock(spec=UploadFile)
    invalid_file.filename = "document.txt"

    # Call and verify exception
    with pytest.raises(HTTPException) as excinfo:
        await extract_toc(
            invalid_file, valid_toc_request, background_tasks, MagicMock()
        )

    assert excinfo.value.status_code == 400
    assert "Invalid file" in excinfo.value.detail


@pytest.mark.asyncio
async def test_extract_toc_direct_service_error(
    mock_toc_service, valid_toc_request, mock_pdf_file
):
    """Test extract_toc function with service error."""
    # Setup
    background_tasks = MagicMock()
    mock_toc_service.extract_toc_from_upload.side_effect = Exception("Service error")

    # Call and verify exception
    with pytest.raises(HTTPException) as excinfo:
        await extract_toc(
            mock_pdf_file, valid_toc_request, background_tasks, mock_toc_service
        )

    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Service error"


# Parametrized tests for different inputs
@pytest.mark.parametrize(
    "max_pages,expected_max_pages", [(None, None), (5, 5), (20, 20)]
)
@pytest.mark.asyncio
async def test_extract_toc_with_different_max_pages(
    mock_toc_service, valid_toc_request, mock_pdf_file, max_pages, expected_max_pages
):
    """Test TOC extraction with different max_pages values."""
    # Setup
    background_tasks = MagicMock()
    valid_toc_request.max_pages = max_pages

    # Call function
    await extract_toc(
        mock_pdf_file, valid_toc_request, background_tasks, mock_toc_service
    )

    # Verify service call
    mock_toc_service.extract_toc_from_upload.assert_called_once_with(
        mock_pdf_file.read.return_value,
        mock_pdf_file.filename,
        valid_toc_request.output_file,
        valid_toc_request.max_pages,
    )


# Test get_toc_service dependency
def test_get_toc_service():
    """Test the get_toc_service dependency returns a TOCService instance."""
    service = get_toc_service()
    assert isinstance(service, TOCService)
