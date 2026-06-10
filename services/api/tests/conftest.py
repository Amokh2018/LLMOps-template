import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.fixture
def mock_rag_service():
    """Mock RAG service for testing."""
    service = MagicMock()
    service.answer_query = AsyncMock()
    return service


@pytest.fixture
def mock_vertex_ai():
    """Mock Vertex AI initialization."""
    with pytest.mock.patch('google.cloud.aiplatform.init'):
        yield
