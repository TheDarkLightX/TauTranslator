import sys
from unittest.mock import Mock, patch

from returns.pipeline import is_successful

from backend.unified.api.nlp import NLPServiceLoader
from backend.unified.core.domain_types import AppError


class TestNLPServiceLoader:
    """Test the NLP service loader infrastructure."""

    def teardown_method(self):
        """Reset class state after each test to ensure test isolation."""
        NLPServiceLoader._service_instance = None

    def test_load_nlp_service_async_WhenSuccessful_ReturnsCachedInstance(self):
        # Given: NLP module is available and NLPTranslationService instantiates successfully
        mock_nlp_instance = Mock()
        
        mock_nlp_integration_module = Mock()
        # Simulate NLPTranslationService class within the mocked module
        mock_nlp_integration_module.NLPTranslationService = Mock(return_value=mock_nlp_instance)
        
        with patch.dict(sys.modules, {'nlp.nlp_integration': mock_nlp_integration_module}):
            # When: Loading service twice
            result1 = NLPServiceLoader.load_nlp_service_async()
            result2 = NLPServiceLoader.load_nlp_service_async()
            
            # Then: Same instance is returned (cached) and service was initialized only once
            assert is_successful(result1)
            assert result1.unwrap() is mock_nlp_instance
            assert result2.unwrap() is mock_nlp_instance # Should be the same instance
            mock_nlp_integration_module.NLPTranslationService.assert_called_once()  # Ensure it was only called once

    def test_load_nlp_service_async_WhenImportFails_ReturnsSuccessWithNone(self):
        # Given: The 'nlp.nlp_integration' module is not in sys.modules, which will cause an ImportError
        # We patch it to None to ensure it's not found.
        with patch.dict(sys.modules, {'nlp.nlp_integration': None}):
            # When: Loading the service
            result = NLPServiceLoader.load_nlp_service_async()

            # Then: The result is a success with a value of None, indicating graceful failure
            assert is_successful(result)
            assert result.unwrap() is None

    def test_load_nlp_service_async_WhenInitFails_ReturnsErrorResult(self):
        # Given: NLP module imports but NLPTranslationService fails to initialize
        mock_nlp_integration_module = Mock()
        mock_nlp_integration_module.NLPTranslationService = Mock(side_effect=Exception("Init failed"))
        
        with patch.dict(sys.modules, {'nlp.nlp_integration': mock_nlp_integration_module}):
            # When: Loading service
            result = NLPServiceLoader.load_nlp_service_async()
            
            # Then: Failure result with error details
            assert not is_successful(result)
            error = result.failure()
            assert isinstance(error, AppError)
            assert error.error_code == "SERVICE_LOAD_ERROR"
            assert "Failed to load NLP service" in error.message
import sys
from unittest.mock import Mock, patch

from returns.pipeline import is_successful

from backend.unified.api.nlp import NLPServiceLoader
from backend.unified.core.domain_types import AppError


class TestNLPServiceLoader:
    """Test the NLP service loader infrastructure."""

    def teardown_method(self):
        """Reset class state after each test to ensure test isolation."""
        NLPServiceLoader._service_instance = None

    def test_load_nlp_service_async_WhenSuccessful_ReturnsCachedInstance(self):
        # Given: NLP module is available and NLPTranslationService instantiates successfully
        mock_nlp_instance = Mock()
        
        mock_nlp_integration_module = Mock()
        # Simulate NLPTranslationService class within the mocked module
        mock_nlp_integration_module.NLPTranslationService = Mock(return_value=mock_nlp_instance)
        
        with patch.dict(sys.modules, {'nlp.nlp_integration': mock_nlp_integration_module}):
            # When: Loading service twice
            result1 = NLPServiceLoader.load_nlp_service_async()
            result2 = NLPServiceLoader.load_nlp_service_async()
            
            # Then: Same instance is returned (cached) and service was initialized only once
            assert is_successful(result1)
            assert result1.unwrap() is mock_nlp_instance
            assert result2.unwrap() is mock_nlp_instance # Should be the same instance
            mock_nlp_integration_module.NLPTranslationService.assert_called_once()  # Ensure it was only called once

    def test_load_nlp_service_async_WhenImportFails_ReturnsSuccessWithNone(self):
        # Given: The 'nlp.nlp_integration' module is not in sys.modules, which will cause an ImportError
        # We patch it to None to ensure it's not found.
        with patch.dict(sys.modules, {'nlp.nlp_integration': None}):
            # When: Loading the service
            result = NLPServiceLoader.load_nlp_service_async()

            # Then: The result is a success with a value of None, indicating graceful failure
            assert is_successful(result)
            assert result.unwrap() is None

    def test_load_nlp_service_async_WhenInitFails_ReturnsErrorResult(self):
        # Given: NLP module imports but NLPTranslationService fails to initialize
        mock_nlp_integration_module = Mock()
        mock_nlp_integration_module.NLPTranslationService = Mock(side_effect=Exception("Init failed"))
        
        with patch.dict(sys.modules, {'nlp.nlp_integration': mock_nlp_integration_module}):
            # When: Loading service
            result = NLPServiceLoader.load_nlp_service_async()
            
            # Then: Failure result with error details
            assert not is_successful(result)
            error = result.failure()
            assert isinstance(error, AppError)
            assert error.error_code == "SERVICE_LOAD_ERROR"
            assert "Failed to load NLP service" in error.message
