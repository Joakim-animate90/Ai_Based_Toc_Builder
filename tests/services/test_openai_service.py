import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.openai_service import OpenAIService
from openai import OpenAI

@pytest.fixture
def mock_openai_client():
    """Fixture for a mock OpenAI client."""
    mock = Mock(spec=OpenAI)
    # Setup chat completions mock
    chat_mock = MagicMock()
    chat_mock.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="Sample TOC content"
                )
            )
        ]
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

@patch('app.core.config.settings.OPENAI_API_KEY', 'fake-api-key')
@patch('openai.OpenAI')
def test_client_property_lazy_loading(mock_openai_class):
    """Test that the client property lazy-loads the OpenAI client."""
    # Arrange
    mock_client = Mock()
    mock_openai_class.return_value = mock_client
    service = OpenAIService()
    
    # Act - first access creates client
    client1 = service.client
    
    # Assert first client creation
    assert client1 is mock_client
    mock_openai_class.assert_called_once_with(api_key='fake-api-key')
    
    # Act - second access reuses existing client
    client2 = service.client
    
    # Assert client reuse
    assert client2 is client1
    assert mock_openai_class.call_count == 1  # Still only called once

@patch('app.core.config.settings.OPENAI_API_KEY', '')
def test_setup_client_no_api_key():
    """Test that _setup_client raises an error when no API key is provided."""
    # Arrange
    service = OpenAIService()
    
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        service._setup_client()
    
    assert "OPENAI_API_KEY is not set" in str(excinfo.value)

@patch('app.core.config.settings.OPENAI_MODEL', 'test-model')
def test_extract_toc_from_images(openai_service_with_mock):
    """Test OpenAIService.extract_toc_from_images."""
    # Arrange
    base64_images = ["image1", "image2"]
    
    # Act
    result = openai_service_with_mock.extract_toc_from_images(base64_images)
    
    # Assert
    assert result == "Sample TOC content"
    
    # Verify OpenAI API call
    openai_service_with_mock._client.chat.completions.create.assert_called_once()
    args, kwargs = openai_service_with_mock._client.chat.completions.create.call_args
    
    # Verify model
    assert kwargs["model"] == "test-model"
    
    # Verify message structure
    assert len(kwargs["messages"]) == 2
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][1]["role"] == "user"
    
    # Verify content structure
    content = kwargs["messages"][1]["content"]
    assert len(content) == 3  # Text prompt + 2 images
    assert content[0]["type"] == "text"
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"] == "data:image/png;base64,image1"
    assert content[2]["type"] == "image_url"
    assert content[2]["image_url"]["url"] == "data:image/png;base64,image2"

@patch('app.core.config.settings.OPENAI_MODEL', 'test-model')
def test_extract_toc_from_images_api_error(openai_service_with_mock):
    """Test OpenAIService.extract_toc_from_images with API error."""
    # Arrange
    base64_images = ["image1", "image2"]
    openai_service_with_mock._client.chat.completions.create.side_effect = Exception("API error")
    
    # Act & Assert
    with pytest.raises(Exception) as excinfo:
        openai_service_with_mock.extract_toc_from_images(base64_images)
    
    assert "API error" in str(excinfo.value)
