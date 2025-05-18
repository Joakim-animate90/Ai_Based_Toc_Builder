import os
import pytest
from unittest.mock import Mock, patch, mock_open

from app.services.pdf_service import PDFService
from app.utils.process_image_thread import PDFToBase64Thread

@pytest.fixture
def mock_pdf_converter():
    """Fixture for a mock PDF converter."""
    mock = Mock(spec=PDFToBase64Thread)
    mock.convert_pdf_to_base64_images.return_value = ["base64_image1", "base64_image2"]
    return mock

@pytest.fixture
def pdf_service_with_mock(mock_pdf_converter):
    """Fixture for a PDF service with mocked converter."""
    service = PDFService()
    service.pdf_converter = mock_pdf_converter
    return service

def test_pdf_service_init():
    """Test PDFService initialization."""
    # Test with default thread count
    service = PDFService()
    assert hasattr(service, 'thread_count')
    assert hasattr(service, 'pdf_converter')
    assert isinstance(service.pdf_converter, PDFToBase64Thread)
    
    # Test with custom thread count
    service = PDFService(thread_count=4)
    assert service.thread_count == 4

def test_convert_pdf_to_images(pdf_service_with_mock):
    """Test PDFService.convert_pdf_to_images."""
    # Arrange
    pdf_path = "/path/to/document.pdf"
    max_pages = 15
    
    # Act
    result = pdf_service_with_mock.convert_pdf_to_images(pdf_path, max_pages)
    
    # Assert
    assert result == ["base64_image1", "base64_image2"]
    
    # Verify converter call
    pdf_service_with_mock.pdf_converter.convert_pdf_to_base64_images.assert_called_once_with(
        pdf_path, max_pages
    )

def test_convert_pdf_to_images_default_max_pages(pdf_service_with_mock):
    """Test PDFService.convert_pdf_to_images with default max_pages."""
    # Arrange
    pdf_path = "/path/to/document.pdf"
    
    # Act
    result = pdf_service_with_mock.convert_pdf_to_images(pdf_path)
    
    # Assert
    assert result == ["base64_image1", "base64_image2"]
    
    # Verify converter call uses default value from settings
    pdf_service_with_mock.pdf_converter.convert_pdf_to_base64_images.assert_called_once()

@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
def test_save_toc_to_file_with_path(mock_file, mock_makedirs, pdf_service_with_mock):
    """Test PDFService.save_toc_to_file with specified path."""
    # Arrange
    toc_content = "Sample TOC content"
    output_path = "custom/output.txt"
    
    # Act
    result = pdf_service_with_mock.save_toc_to_file(toc_content, output_path)
    
    # Assert
    assert result == output_path
    
    # Verify directory creation
    mock_makedirs.assert_called_once_with(os.path.dirname(output_path), exist_ok=True)
    
    # Verify file writing
    mock_file.assert_called_once_with(output_path, 'w')
    mock_file().write.assert_called_once_with("```\nSample TOC content\n```")

@patch('os.makedirs')
@patch('builtins.open', new_callable=mock_open)
def test_save_toc_to_file_default_path(mock_file, mock_makedirs, pdf_service_with_mock):
    """Test PDFService.save_toc_to_file with default path."""
    # Arrange
    toc_content = "Sample TOC content"
    
    # Act
    with patch('app.core.config.settings.PDF_OUTPUT_DIR', 'toc'):
        result = pdf_service_with_mock.save_toc_to_file(toc_content)
    
    # Assert - check that it uses the default path from settings
    assert "table_of_contents.txt" in result
    
    # Verify directory creation
    mock_makedirs.assert_called_once()
    
    # Verify file writing
    mock_file.assert_called_once()
    mock_file().write.assert_called_once_with("```\nSample TOC content\n```")
