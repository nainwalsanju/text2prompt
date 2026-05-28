"""Tests for CLI mode and app dispatch."""

from unittest.mock import Mock, patch

import pytest

from text2prompt.app import MODE_SEPARATOR, run_app, run_cli


class TestModeSeparator:
    """MODE_SEPARATOR should be unambiguous."""

    def test_separator_is_pipe(self):
        """Separator should be '|' to avoid confusion with ':' in context."""
        assert MODE_SEPARATOR == "|"

    def test_separator_not_in_context_prefix(self):
        """Pipe should not appear in typical context prefixes."""
        # Typical context: "Safari::Google"
        assert "|" not in "Safari::Google"


class TestRunAppDispatch:
    """run_app should dispatch to CLI or GUI mode."""

    @patch("text2prompt.app.run_cli")
    def test_text_args_dispatch_to_cli(self, mock_cli):
        """Text arguments should dispatch to CLI mode."""
        run_app(["hello world"])
        mock_cli.assert_called_once_with("hello world", "general")

    @patch("text2prompt.app.run_cli")
    def test_image_flag_dispatch_to_cli(self, mock_cli):
        """--image flag with text should dispatch to CLI mode."""
        run_app(["--image", "a sunset"])
        mock_cli.assert_called_once_with("a sunset", "image")

    @patch("text2prompt.app.run_gui")
    def test_no_args_dispatch_to_gui(self, mock_gui):
        """No arguments should dispatch to GUI mode."""
        run_app([])
        mock_gui.assert_called_once_with([])

    @patch("text2prompt.app.run_gui")
    def test_gui_flag_dispatch_to_gui(self, mock_gui):
        """--gui flag should force GUI mode even with text."""
        run_app(["--gui", "hello"])
        mock_gui.assert_called_once_with(["hello"])


class TestRunCli:
    """run_cli should generate a prompt and print it."""

    @patch("text2prompt.app.pyperclip")
    @patch("text2prompt.app.init_db")
    @patch("text2prompt.app.get_history", return_value=[])
    @patch("text2prompt.app.save_interaction")
    @patch("text2prompt.app.get_config")
    @patch("text2prompt.app.ModelEngine")
    @patch("text2prompt.app.get_registry")
    def test_cli_prints_response(
        self,
        mock_registry_fn,
        mock_engine_cls,
        mock_config_fn,
        mock_save,
        mock_history,
        mock_init_db,
        mock_pyperclip,
        capsys,
    ):
        """CLI mode should print the generated response to stdout."""
        # Setup mocks
        mock_config = Mock()
        mock_config.db_path = "/tmp/test.db"
        mock_config.auto_copy = False
        mock_config.save_history = False
        mock_config_fn.return_value = mock_config

        mock_engine = Mock()
        mock_engine.check_availability.return_value = (True, None)
        mock_engine.generate_response.return_value = "Enhanced prompt output"
        mock_engine_cls.return_value = mock_engine

        mock_registry = Mock()
        mock_registry.format_prompt.return_value = "formatted prompt"
        mock_registry_fn.return_value = mock_registry

        mock_conn = Mock()
        mock_init_db.return_value = mock_conn

        run_cli("test idea", "general")

        captured = capsys.readouterr()
        assert "Enhanced prompt output" in captured.out
        mock_conn.close.assert_called_once()

    @patch("text2prompt.app.init_db")
    @patch("text2prompt.app.get_config")
    @patch("text2prompt.app.ModelEngine")
    def test_cli_exits_on_unavailable_model(
        self, mock_engine_cls, mock_config_fn, mock_init_db
    ):
        """CLI should exit with code 1 when model is unavailable."""
        mock_config = Mock()
        mock_config.db_path = "/tmp/test.db"
        mock_config_fn.return_value = mock_config

        mock_engine = Mock()
        mock_engine.check_availability.return_value = (False, "Not supported")
        mock_engine_cls.return_value = mock_engine

        with pytest.raises(SystemExit) as exc_info:
            run_cli("test", "general")
        assert exc_info.value.code == 1

    @patch("text2prompt.app.pyperclip")
    @patch("text2prompt.app.init_db")
    @patch("text2prompt.app.get_history", return_value=[])
    @patch("text2prompt.app.save_interaction")
    @patch("text2prompt.app.get_config")
    @patch("text2prompt.app.ModelEngine")
    @patch("text2prompt.app.get_registry")
    def test_cli_auto_copy(
        self,
        mock_registry_fn,
        mock_engine_cls,
        mock_config_fn,
        mock_save,
        mock_history,
        mock_init_db,
        mock_pyperclip,
        capsys,
    ):
        """CLI mode should copy to clipboard when auto_copy is enabled."""
        mock_config = Mock()
        mock_config.db_path = "/tmp/test.db"
        mock_config.auto_copy = True
        mock_config.save_history = False
        mock_config_fn.return_value = mock_config

        mock_engine = Mock()
        mock_engine.check_availability.return_value = (True, None)
        mock_engine.generate_response.return_value = "result"
        mock_engine_cls.return_value = mock_engine

        mock_registry = Mock()
        mock_registry.format_prompt.return_value = "prompt"
        mock_registry_fn.return_value = mock_registry

        mock_conn = Mock()
        mock_init_db.return_value = mock_conn

        run_cli("test", "general")

        mock_pyperclip.copy.assert_called_once_with("result")


def test_gui_imports_and_instantiation():
    """Verify that gui.py can be imported and AppDelegate can be instantiated."""
    from text2prompt.gui import AppDelegate, start_gui
    assert start_gui is not None
    delegate = AppDelegate.alloc().init()
    assert delegate is not None

