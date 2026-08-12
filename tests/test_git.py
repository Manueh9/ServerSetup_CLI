import pytest
from unittest.mock import patch
from modules.git import (
    is_git_installed, install_git, configure_git,
    set_pull_strategy, prompt_credentials,
)

class TestIsGitInstalled:
    def test_returns_true_when_git_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        assert is_git_installed() is True

    def test_returns_false_when_git_not_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 1
        assert is_git_installed() is False

class TestInstallGit:
    def test_skips_install_if_already_installed(self, mocker, mock_run_command):
        mocker.patch("modules.git.is_git_installed", return_value=True)
        mock = mock_run_command("modules.git")
        install_git()
        mock.assert_not_called()

    def test_installs_if_not_present(self, mocker, mock_run_command):
        mocker.patch("modules.git.is_git_installed", return_value=False)
        mock = mock_run_command("modules.git")
        install_git()
        mock.assert_called_once_with(["apt", "install", "-y", "git"])

class TestConfigureGit:
    def test_sets_name_and_email(self, mock_run_command):
        mock = mock_run_command("modules.git")
        configure_git("Ana", "ana@mail.com", scope="--global")
        assert mock.call_count == 2
        mock.assert_any_call(["git", "config", "--global", "user.name", "Ana"])
        mock.assert_any_call(["git", "config", "--global", "user.email", "ana@mail.com"])

    def test_uses_correct_scope(self, mock_run_command):
        mock = mock_run_command("modules.git")
        configure_git("Ana", "ana@mail.com", scope="--system")
        mock.assert_any_call(["git", "config", "--system", "user.name", "Ana"])

class TestPullStrategy:
    def test_rebase_sets_pull_rebase_true(self, mock_run_command):
        mock = mock_run_command("modules.git")
        set_pull_strategy("rebase")
        mock.assert_called_once_with(["git", "config", "--global", "pull.rebase", "true"])

    def test_ff_only_sets_pull_ff_only(self, mock_run_command):
        mock = mock_run_command("modules.git")
        set_pull_strategy("ff-only")
        mock.assert_called_once_with(["git", "config", "--global", "pull.ff", "only"])

    def test_merge_sets_pull_rebase_false(self, mock_run_command):
        mock = mock_run_command("modules.git")
        set_pull_strategy("merge")
        mock.assert_called_once_with(["git", "config", "--global", "pull.rebase", "false"])
        
class TestPromptCredentials:

    def test_rejects_empty_username(self, monkeypatch, capsys):
        inputs = iter(["", "descartado@mail.com", "Ana", "ana@mail.com"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        username, email = prompt_credentials()
        assert username == "Ana"
        assert email == "ana@mail.com"
        assert "cannot be empty" in capsys.readouterr().out
        
    def test_rejects_invalid_email(self, monkeypatch, capsys):
        inputs = iter(["Ana", "not-an-email", "Ana", "ana@mail.com"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        username, email = prompt_credentials()
        assert email == "ana@mail.com"
        assert "Invalid email" in capsys.readouterr().out

    def test_accepts_valid_input_first_try(self, monkeypatch):
        inputs = iter(["Ana", "ana@mail.com"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        username, email = prompt_credentials()
        assert username == "Ana"
        assert email == "ana@mail.com"
