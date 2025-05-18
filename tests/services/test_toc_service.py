import pytest
from unittest.mock import Mock, patch

from app.services.toc_service import TOCService
from app.services.pdf_service import PDFService
from app.services.openai_service import OpenAIService


@pytest.fixture
def mock_pdf_service():
    """Fixture for a mock PDF service."""
    mock = Mock(spec=PDFService)
    mock.convert_pdf_to_images.return_value = ["base64_image1", "base64_image2"]
    mock.save_toc_to_file.return_value = "toc/output.txt"
    return mock


@pytest.fixture
def mock_openai_service():
    """Fixture for a mock OpenAI service."""
    mock = Mock(spec=OpenAIService)
    mock.extract_toc_from_images.return_value = "Sample TOC content"
    return mock


@pytest.fixture
def toc_service_with_mocks(mock_pdf_service, mock_openai_service):
    """Fixture for a TOC service with mocked dependencies."""
    service = TOCService()
    service.pdf_service = mock_pdf_service
    service.openai_service = mock_openai_service
    return service


def test_toc_service_init():
    """Test TOCService initialization."""
    # Test with default thread count
    service = TOCService()
    assert hasattr(service, "pdf_service")
    assert hasattr(service, "openai_service")
    assert isinstance(service.pdf_service, PDFService)
    assert isinstance(service.openai_service, OpenAIService)

    # Test with custom thread count
    service = TOCService(thread_count=4)
    assert hasattr(service, "pdf_service")
    assert hasattr(service, "openai_service")
    assert service.pdf_service.thread_count == 4


def test_extract_toc_with_output_file(toc_service_with_mocks):
    """Test TOCService.extract_toc with specified output file."""
    # Arrange
    pdf_path = "/path/to/document.pdf"
    output_file = "custom/output.txt"

    # Act
    toc_content, file_path = toc_service_with_mocks.extract_toc(pdf_path, output_file)

    # Assert
    assert toc_content == "Sample TOC content"
    assert file_path == "toc/output.txt"

    # Verify service calls
    toc_service_with_mocks.pdf_service.convert_pdf_to_images.assert_called_once_with(
        pdf_path, max_pages=None
    )
    toc_service_with_mocks.openai_service.extract_toc_from_images.assert_called_once_with(
        ["base64_image1", "base64_image2"]
    )
    toc_service_with_mocks.pdf_service.save_toc_to_file.assert_called_once_with(
        "Sample TOC content", output_file
    )


def test_extract_toc_without_output_file(toc_service_with_mocks):
    """Test TOCService.extract_toc without specified output file."""
    # Arrange
    pdf_path = "/path/to/document.pdf"

    # Act
    toc_content, file_path = toc_service_with_mocks.extract_toc(pdf_path)

    # Assert
    assert toc_content == "Sample TOC content"
    assert file_path == "toc/output.txt"

    # Verify service calls
    toc_service_with_mocks.pdf_service.convert_pdf_to_images.assert_called_once_with(
        pdf_path, max_pages=None
    )
    toc_service_with_mocks.openai_service.extract_toc_from_images.assert_called_once_with(
        ["base64_image1", "base64_image2"]
    )
    toc_service_with_mocks.pdf_service.save_toc_to_file.assert_called_once_with(
        "Sample TOC content"
    )


@patch.object(PDFService, "convert_pdf_to_images")
@patch.object(OpenAIService, "extract_toc_from_images")
def test_extract_toc_error_handling(mock_extract, mock_convert):
    """Test TOCService error handling."""
    # Arrange
    service = TOCService()
    mock_convert.side_effect = Exception("PDF conversion error")

    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        service.extract_toc("/path/to/document.pdf")

    assert "PDF conversion error" in str(excinfo.value)


@patch("tempfile.NamedTemporaryFile")
def test_extract_toc_from_upload(mock_tempfile, toc_service_with_mocks):
    """Test extract_toc_from_upload method with file content."""
    # Arrange
    pdf_content = b"%PDF-1.4 test content"
    filename = "test_document.pdf"
    output_file = "custom/output.txt"
    max_pages = 5

    # Setup mock tempfile
    mock_temp_instance = Mock()
    mock_temp_instance.name = "/tmp/temp_file.pdf"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_instance

    # Act
    with patch("os.path.exists", return_value=True), patch("os.unlink"):
        toc_content, file_path = toc_service_with_mocks.extract_toc_from_upload(
            pdf_content, filename, output_file, max_pages
        )

    # Assert
    assert toc_content == "Sample TOC content"
    assert file_path == "toc/output.txt"

    # Verify service calls
    mock_temp_instance.write.assert_called_once_with(pdf_content)
    toc_service_with_mocks.pdf_service.convert_pdf_to_images.assert_called_once_with(
        mock_temp_instance.name, max_pages=max_pages
    )
    toc_service_with_mocks.openai_service.extract_toc_from_images.assert_called_once_with(
        ["base64_image1", "base64_image2"]
    )
    toc_service_with_mocks.pdf_service.save_toc_to_file.assert_called_once_with(
        "Sample TOC content", output_file
    )


@patch("tempfile.NamedTemporaryFile")
def test_extract_toc_from_upload_no_output_file(mock_tempfile, toc_service_with_mocks):
    """Test extract_toc_from_upload method without specifying an output file."""
    # Arrange
    pdf_content = b"%PDF-1.4 test content"
    filename = "test_document.pdf"

    # Setup mock tempfile
    mock_temp_instance = Mock()
    mock_temp_instance.name = "/tmp/temp_file.pdf"
    mock_tempfile.return_value.__enter__.return_value = mock_temp_instance

    # Act
    with patch("os.path.exists", return_value=True), patch("os.unlink"), patch(
        "os.path.basename", return_value="test_document.pdf"
    ), patch("os.path.splitext", return_value=("test_document", ".pdf")):
        toc_content, file_path = toc_service_with_mocks.extract_toc_from_upload(
            pdf_content, filename
        )

    # Assert
    assert toc_content == "Sample TOC content"
    assert file_path == "toc/output.txt"

    # Verify temp file is used properly
    mock_temp_instance.write.assert_called_once_with(pdf_content)


@patch("tempfile.NamedTemporaryFile")
def test_extract_toc_from_upload_cleanup(mock_tempfile, toc_service_with_mocks):
    """Test that temporary file is cleaned up after extraction."""
    # Arrange
    pdf_content = b"%PDF-1.4 test content"
    filename = "test_document.pdf"
    temp_path = "/tmp/temp_file.pdf"

    # Setup mock tempfile
    mock_temp_instance = Mock()
    mock_temp_instance.name = temp_path
    mock_tempfile.return_value.__enter__.return_value = mock_temp_instance

    # Setup mock os functions
    mock_exists = Mock(return_value=True)
    mock_unlink = Mock()

    # Act
    with patch("os.path.exists", mock_exists), patch("os.unlink", mock_unlink):
        toc_content, file_path = toc_service_with_mocks.extract_toc_from_upload(
            pdf_content, filename
        )

    # Assert - verify cleanup occurs
    mock_exists.assert_called_with(temp_path)
    mock_unlink.assert_called_with(temp_path)
