import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from app.services.openai_service import OpenAIService
from openai import OpenAI


@pytest.fixture
def mock_openai_client():
    """Fixture for a mock OpenAI client."""
    mock = Mock(spec=OpenAI)
    # Setup chat completions mock
    chat_mock = MagicMock()
    mock_json_response = json.dumps(
        {
            "toc_entries": [
                {
                    "case_number": "123/456",
                    "case_id": "123",
                    "plaintiff": "John Doe",
                    "defendant": "Company XYZ",
                    "page_number": "45",
                    "raw_text": "Juicio nº 123 a instancia de John Doe contra Company XYZ .................. Página 45",
                }
            ],
            "section_headers": [
                "Juzgado de lo Social Número 3 de Santa Cruz de Tenerife"
            ],
        }
    )
    chat_mock.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content=mock_json_response))]
    )
    mock.chat = chat_mock
    return mock


@pytest.fixture
def openai_service_with_mock(mock_openai_client):
    """Fixture for an OpenAI service with a mocked client."""
    service = OpenAIService()
    service._client = mock_openai_client
    return service


def test_openai_service_init():
    """Test OpenAIService initialization."""
    service = OpenAIService()
    assert service._client is None


def test_client_property_lazy_loading():
    """Test that the client property lazy-loads the OpenAI client."""
    # Arrange
    service = OpenAIService()
    mock_client = Mock()

    # Initial state - client should be None
    assert service._client is None

    # Setup - patch the _setup_client method to return our mock
    with patch.object(service, "_setup_client", return_value=mock_client) as mock_setup:
        # Act - First access should trigger _setup_client
        client1 = service.client

        # Assert - Client should be set and _setup_client should have been called once
        assert service._client is mock_client
        mock_setup.assert_called_once()

        # Act - Second access should reuse the existing client
        client2 = service.client

        # Assert - Client should still be the same and _setup_client should not be called again
        assert client2 is client1
        assert mock_setup.call_count == 1  # Still only called once


@patch("app.core.config.settings.OPENAI_API_KEY", "")
def test_setup_client_no_api_key():
    """Test that _setup_client raises an error when no API key is provided."""
    # Arrange
    service = OpenAIService()

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        service._setup_client()

    assert "OPENAI_API_KEY is not set" in str(excinfo.value)


@patch("app.core.config.settings.OPENAI_MODEL", "test-model")
def test_extract_toc_from_images(openai_service_with_mock):
    """Test OpenAIService.extract_toc_from_images."""
    # Arrange
    base64_images = ["image1", "image2"]

    # Act
    result = openai_service_with_mock.extract_toc_from_images(base64_images)

    # Assert
    assert isinstance(result, dict)
    assert "toc_entries" in result
    assert "section_headers" in result

    # Verify OpenAI API calls (should be called once for all pages)
    openai_service_with_mock._client.chat.completions.create.assert_called_once()

    # Get the call arguments
    call_args = openai_service_with_mock._client.chat.completions.create.call_args[1]

    # Verify model
    assert call_args["model"] == "test-model"

    # Verify message structure
    assert len(call_args["messages"]) == 2
    assert call_args["messages"][0]["role"] == "system"
    assert call_args["messages"][1]["role"] == "user"

    # Verify content structure (should contain all images)
    content = call_args["messages"][1]["content"]
    assert len(content) == 3  # Text prompt + 2 images
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
    assert content[2]["type"] == "image_url"
    assert content[1]["image_url"]["url"] == "data:image/png;base64,image1"
    assert content[2]["image_url"]["url"] == "data:image/png;base64,image2"


@patch("app.core.config.settings.OPENAI_MODEL", "test-model")
def test_extract_toc_from_images_api_error(openai_service_with_mock):
    """Test OpenAIService.extract_toc_from_images with API error."""
    # Arrange
    base64_images = ["image1", "image2"]
    openai_service_with_mock._client.chat.completions.create.side_effect = Exception(
        "API error"
    )

    # Act
    # The method should handle the error and return a dict with error info
    result = openai_service_with_mock.extract_toc_from_images(base64_images)

    # Assert
    assert isinstance(result, dict)
    assert "toc_entries" in result
    assert len(result["toc_entries"]) == 0  # Should be empty when errors occur
    assert "section_headers" in result
    assert "error" in result
    assert result["error"] is True
    assert "error_message" in result
    assert "API error" in result["error_message"]


# Test for _process_single_page method has been removed since the method no longer exists


@patch("app.core.config.settings.OPENAI_MODEL", "test-model")
def test_extract_toc_empty_images(openai_service_with_mock):
    """Test OpenAIService.extract_toc_from_images with empty image list."""
    # Arrange
    base64_images = []

    # Act
    result = openai_service_with_mock.extract_toc_from_images(base64_images)

    # Assert
    assert isinstance(result, dict)
    assert "toc_entries" in result
    assert len(result["toc_entries"]) == 0  # Should be empty for empty input
    assert "section_headers" in result
    assert "raw_content" in result
    assert "No content to process" in result["raw_content"]

    # Should not call OpenAI API
    openai_service_with_mock._client.chat.completions.create.assert_not_called()
