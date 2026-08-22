import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture
def mock_run_command(mocker):
    """
    Returns a function so each test can patch run_command
    in the correct module namespace.
    Usage: mock = mock_run_command("modules.system")
    """
    def _patch(module_path: str):
        return mocker.patch(f"{module_path}.run_command")
    return _patch

@pytest.fixture
def mock_subprocess_run(mocker):
    """Mocks subprocess.run for direct subprocess calls."""
    return mocker.patch("subprocess.run")
