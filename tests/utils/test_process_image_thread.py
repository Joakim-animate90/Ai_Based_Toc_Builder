import pytest
import base64
from unittest.mock import Mock, patch, MagicMock
import threading
from concurrent.futures import ThreadPoolExecutor

from app.utils.process_image_thread import PDFToBase64Thread

@pytest.fixture
def mock_pdf_document():
    """Fixture for a mock PDF document."""
    mock_doc = Mock()
    
    # Setup page count
    mock_doc.page_count = 5
    
    # Setup page loading
    mock_page = Mock()
    mock_doc.load_page.return_value = mock_page
    
    # Setup pixmap
    mock_pixmap = Mock()
    mock_page.get_pixmap.return_value = mock_pixmap
    mock_pixmap.tobytes.return_value = b'test_image_bytes'
    
    return mock_doc

@pytest.fixture
def thread_converter():
    """Fixture for a PDFToBase64Thread instance."""
    return PDFToBase64Thread(num_threads=2)

@patch('base64.b64encode')
def test_process_page(mock_b64encode, thread_converter, mock_pdf_document):
    """Test _process_page method."""
    # Arrange
    mock_b64encode.return_value = b'base64_encoded_test'
    
    # Act
    page_num, base64_image = thread_converter._process_page(mock_pdf_document, 0, 5)
    
    # Assert
    assert page_num == 0
    assert base64_image == 'base64_encoded_test'
    
    # Verify PDF processing
    mock_pdf_document.load_page.assert_called_once_with(0)
    page = mock_pdf_document.load_page.return_value
    page.get_pixmap.assert_called_once()
    pixmap = page.get_pixmap.return_value
    pixmap.tobytes.assert_called_once_with("png")
    mock_b64encode.assert_called_once_with(b'test_image_bytes')

def test_process_page_error(thread_converter, mock_pdf_document):
    """Test _process_page error handling."""
    # Arrange
    mock_pdf_document.load_page.side_effect = Exception("PDF error")
    
    # Act
    page_num, base64_image = thread_converter._process_page(mock_pdf_document, 0, 5)
    
    # Assert
    assert page_num == 0
    assert base64_image is None

@patch('fitz.open')
@patch('concurrent.futures.ThreadPoolExecutor')
def test_convert_pdf_to_base64_images(mock_executor_class, mock_open, thread_converter):
    """Test convert_pdf_to_base64_images method."""
    # Arrange
    mock_pdf = MagicMock()
    mock_pdf.page_count = 3
    mock_open.return_value = mock_pdf
    
    # Setup mock executor
    mock_executor = MagicMock()
    mock_executor_class.return_value.__enter__.return_value = mock_executor
    
    # Setup mock futures
    future1, future2, future3 = MagicMock(), MagicMock(), MagicMock()
    future1.result.return_value = (0, "base64_0")
    future2.result.return_value = (1, "base64_1")
    future3.result.return_value = (2, "base64_2")
    
    # Mock the __iter__ method of the executor to return our futures
    mock_executor.__iter__.return_value = [future1, future2, future3]
    
    # Mock the submit method to return futures
    def mock_submit(func, *args, **kwargs):
        page_num = args[1]  # Second arg to _process_page is page_num
        if page_num == 0:
            return future1
        elif page_num == 1:
            return future2
        else:
            return future3
    
    mock_executor.submit = mock_submit
    
    # Act
    result = thread_converter.convert_pdf_to_base64_images("test.pdf", max_pages=3)
    
    # Assert
    assert result == ["base64_0", "base64_1", "base64_2"]
    mock_open.assert_called_once_with("test.pdf")
    mock_pdf.close.assert_called_once()
    
    # Verify futures were accessed
    future1.result.assert_called_once()
    future2.result.assert_called_once()
    future3.result.assert_called_once()

@patch('fitz.open')
@patch('concurrent.futures.ThreadPoolExecutor')
def test_convert_pdf_with_max_pages_limit(mock_executor_class, mock_open, thread_converter):
    """Test that max_pages limits the number of pages processed."""
    # Arrange
    mock_pdf = MagicMock()
    mock_pdf.page_count = 10  # PDF has 10 pages
    mock_open.return_value = mock_pdf
    
    # Setup mock executor
    mock_executor = MagicMock()
    mock_executor_class.return_value.__enter__.return_value = mock_executor
    
    # Mock submit to verify number of calls
    mock_executor.submit = MagicMock()
    
    # Act - test with max_pages=3
    thread_converter.convert_pdf_to_base64_images("test.pdf", max_pages=3)
    
    # Assert - should only create futures for 3 pages
    assert mock_executor.submit.call_count == 3

@patch('fitz.open')
def test_convert_pdf_error_handling(mock_open, thread_converter):
    """Test error handling in convert_pdf_to_base64_images."""
    # Arrange - PDF object raises exception
    mock_open.side_effect = Exception("Failed to open PDF")
    
    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        thread_converter.convert_pdf_to_base64_images("test.pdf")
    
    assert "Failed to open PDF" in str(excinfo.value)

@pytest.mark.parametrize("thread_count,expected", [
    (None, None),  # Should use default (cpu_count-1)
    (4, 4),        # Should use exactly 4 threads
    (0, 1)         # Should use minimum of 1 thread
])
def test_thread_converter_init(thread_count, expected):
    """Test initialization with different thread counts."""
    # Arrange & Act
    converter = PDFToBase64Thread(num_threads=thread_count)
    
    # Assert
    if expected is None:
        # Should use CPU count - 1 with minimum of 1
        assert converter.num_threads == max(1, threading.cpu_count() - 1)
    else:
        assert converter.num_threads == expected
