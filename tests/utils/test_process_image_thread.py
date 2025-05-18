import pytest
import os
from unittest.mock import patch, Mock, MagicMock
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
    mock_pixmap.tobytes.return_value = b"test_image_bytes"

    return mock_doc


@pytest.fixture
def thread_converter():
    """Fixture for a PDFToBase64Thread instance."""
    return PDFToBase64Thread(num_threads=2)


@patch("base64.b64encode")
def test_process_page(mock_b64encode, thread_converter, mock_pdf_document):
    """Test _process_page method."""
    # Arrange
    mock_b64encode.return_value = b"base64_encoded_test"

    # Act
    page_num, base64_image = thread_converter._process_page(mock_pdf_document, 0, 5)

    # Assert
    assert page_num == 0
    assert base64_image == "base64_encoded_test"

    # Verify PDF processing
    mock_pdf_document.load_page.assert_called_once_with(0)
    page = mock_pdf_document.load_page.return_value
    page.get_pixmap.assert_called_once()
    pixmap = page.get_pixmap.return_value
    pixmap.tobytes.assert_called_once_with("png")
    mock_b64encode.assert_called_once_with(b"test_image_bytes")


def test_process_page_error(thread_converter, mock_pdf_document):
    """Test _process_page error handling."""
    # Arrange
    mock_pdf_document.load_page.side_effect = Exception("PDF error")

    # Act
    page_num, base64_image = thread_converter._process_page(mock_pdf_document, 0, 5)

    # Assert
    assert page_num == 0
    assert base64_image is None


@patch("fitz.open")
def test_convert_pdf_to_base64_images(mock_open, thread_converter):
    """Test convert_pdf_to_base64_images method."""
    # Arrange
    mock_pdf = MagicMock()
    mock_pdf.page_count = 3
    mock_open.return_value = mock_pdf

    # Setup expected results
    expected_images = ["base64_0", "base64_1", "base64_2"]

    # Create mock futures
    def create_mock_future(page_num):
        mock_future = MagicMock()
        mock_future.result.return_value = (page_num, f"base64_{page_num}")
        return mock_future

    mock_futures = {
        create_mock_future(0): 0,
        create_mock_future(1): 1,
        create_mock_future(2): 2,
    }

    # Act
    # Mock ThreadPoolExecutor to return our mock futures
    mock_executor = MagicMock()
    mock_executor.__enter__.return_value.submit.side_effect = (
        lambda func, pdf, page, total: list(mock_futures.keys())[page]
    )

    with patch(
        "app.utils.process_image_thread.ThreadPoolExecutor", return_value=mock_executor
    ):
        # Execute the method being tested
        result = thread_converter.convert_pdf_to_base64_images("test.pdf", max_pages=3)

    # Assert
    assert result == expected_images
    mock_open.assert_called_once_with("test.pdf")
    mock_pdf.close.assert_called_once()


@patch("fitz.open")
def test_convert_pdf_with_max_pages_limit(mock_open, thread_converter):
    """Test that max_pages limits the number of pages processed."""
    # Arrange
    mock_pdf = MagicMock()
    mock_pdf.page_count = 10  # PDF has 10 pages but we'll limit to 3
    mock_open.return_value = mock_pdf

    # Act - test with max_pages=3
    with patch("concurrent.futures.ThreadPoolExecutor"), patch.object(
        thread_converter, "_process_page"
    ) as mock_process_page:
        # Setup process_page mock
        mock_process_page.return_value = (0, "base64_test")

        # Execute the method being tested
        thread_converter.convert_pdf_to_base64_images("test.pdf", max_pages=3)

    # Assert - verify pages processed matches max_pages limit, not total PDF pages
    assert mock_process_page.call_count == 3

    # Also confirm that the mock PDF was opened and closed
    mock_open.assert_called_once_with("test.pdf")
    mock_pdf.close.assert_called_once()


@patch("fitz.open")
def test_convert_pdf_error_handling(mock_open, thread_converter):
    """Test error handling in convert_pdf_to_base64_images."""
    # Arrange - PDF object raises exception
    mock_open.side_effect = Exception("Failed to open PDF")

    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        thread_converter.convert_pdf_to_base64_images("test.pdf")

    assert "Failed to open PDF" in str(excinfo.value)


@pytest.mark.parametrize(
    "explicit_thread_count,expected",
    [
        (None, None),  # Should use default (cpu_count-1)
        (4, 4),  # Should use exactly 4 threads
        (0, 1),  # Should use minimum of 1 thread
    ],
)
def test_thread_converter_init(explicit_thread_count, expected, thread_count=None):
    """Test initialization with different thread counts.

    Args:
        explicit_thread_count: The thread count value passed directly to the constructor
        expected: Expected thread count or None for default
        thread_count: Optional fixture that provides thread count from command line or environment
    """
    # Use CI-provided thread count for non-None expected values only if explicitly testing default behavior
    if expected is None and thread_count is not None:
        # Skip the test if both CI has a thread count and we're testing default behavior
        pytest.skip("Skipping default thread count test when CI provides thread count")

    # For expected value tests, use the explicit thread count from the test parameters
    # Arrange & Act
    converter = PDFToBase64Thread(num_threads=explicit_thread_count)

    # Assert
    if expected is None:
        # Should use CPU count - 1 with minimum of 1
        assert converter.num_threads == max(1, os.cpu_count() - 1)
    else:
        assert converter.num_threads == expected
