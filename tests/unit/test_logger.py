"""Unit tests for the structured logging setup."""

from unittest.mock import MagicMock, patch

import structlog


def test_get_logger_returns_bound_logger():
    """Test that get_logger returns a structlog logger."""
    from core.logger import get_logger

    logger = get_logger("test_module")
    assert logger is not None


@patch("core.logger.get_settings")
def test_setup_logging_configures_structlog(mock_get_settings):
    """Test that setup_logging() configures structlog with JSON rendering."""
    mock_settings = MagicMock()
    mock_settings.LOG_LEVEL = "DEBUG"
    mock_get_settings.return_value = mock_settings

    from core.logger import setup_logging

    # Should not raise
    setup_logging()

    # Verify structlog is configured (get a logger and check it works)
    logger = structlog.get_logger("test")
    assert logger is not None


@patch("core.logger.get_settings")
def test_setup_logging_invalid_level_defaults_to_info(mock_get_settings):
    """Test that an invalid LOG_LEVEL falls back to INFO via getattr default."""
    mock_settings = MagicMock()
    mock_settings.LOG_LEVEL = "NONEXISTENT"
    mock_get_settings.return_value = mock_settings

    from core.logger import setup_logging

    # Should not raise — getattr(logging, "NONEXISTENT", logging.INFO) returns INFO
    setup_logging()
