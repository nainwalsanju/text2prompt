"""Tests for engine module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from text2prompt.engine.model import ModelEngine, ModelError


@patch('text2prompt.engine.model.fm')
def test_model_engine_init(mock_fm):
    """ModelEngine should initialize without error."""
    mock_model = Mock()
    mock_model.is_available.return_value = (True, None)
    mock_fm.SystemLanguageModel.return_value = mock_model

    engine = ModelEngine()
    assert engine is not None


@patch('text2prompt.engine.model.fm')
def test_check_availability_available(mock_fm):
    """check_availability should return True when model is available."""
    mock_model = Mock()
    mock_model.is_available.return_value = (True, None)
    mock_fm.SystemLanguageModel.return_value = mock_model

    engine = ModelEngine()
    available, reason = engine.check_availability()

    assert available is True
    assert reason is None


@patch('text2prompt.engine.model.fm')
def test_check_availability_unavailable(mock_fm):
    """check_availability should return False with reason when unavailable."""
    mock_model = Mock()
    mock_model.is_available.return_value = (False, "Apple Intelligence not enabled")
    mock_fm.SystemLanguageModel.return_value = mock_model

    engine = ModelEngine()
    available, reason = engine.check_availability()

    assert available is False
    assert reason == "Apple Intelligence not enabled"


@patch('text2prompt.engine.model.fm')
def test_generate_response(mock_fm):
    """generate_response should return model response."""
    mock_model = Mock()
    mock_session = Mock()
    mock_session.respond.return_value = "Enhanced prompt here"
    mock_fm.SystemLanguageModel.return_value = mock_model
    mock_fm.LanguageModelSession.return_value = mock_session

    engine = ModelEngine()
    response = engine.generate_response("test prompt")

    assert response == "Enhanced prompt here"
    mock_fm.LanguageModelSession.assert_called_once()
    mock_session.respond.assert_called_once_with("test prompt")


@patch('text2prompt.engine.model.fm')
def test_generate_response_error(mock_fm):
    """generate_response should raise ModelError on failure."""
    mock_model = Mock()
    mock_session = Mock()
    mock_session.respond.side_effect = Exception("Model error")
    mock_fm.SystemLanguageModel.return_value = mock_model
    mock_fm.LanguageModelSession.return_value = mock_session

    engine = ModelEngine()

    with pytest.raises(ModelError, match="Model error"):
        engine.generate_response("test prompt")
