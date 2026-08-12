import pytest
from modules.hostname import (
    is_valid_hostname, set_hostname,
    get_current_hostname, prompt_hostname_change,
)

# ── is_valid_hostname ────────────────────────────────────────────

class TestIsValidHostname:
    def test_accepts_simple_name(self):
        assert is_valid_hostname("webserver") is True

    def test_accepts_name_with_hyphens(self):
        assert is_valid_hostname("web-prod-01") is True

    def test_accepts_name_with_digits(self):
        assert is_valid_hostname("server123") is True

    def test_rejects_empty_string(self):
        assert is_valid_hostname("") is False

    def test_rejects_starting_with_hyphen(self):
        assert is_valid_hostname("-webserver") is False

    def test_rejects_ending_with_hyphen(self):
        assert is_valid_hostname("webserver-") is False

    def test_rejects_spaces(self):
        assert is_valid_hostname("web server") is False

    def test_rejects_underscore(self):
        assert is_valid_hostname("web_server") is False

    def test_rejects_too_long(self):
        assert is_valid_hostname("a" * 254) is False

    def test_accepts_single_character(self):
        assert is_valid_hostname("a") is True

# ── get_current_hostname ─────────────────────────────────────────

class TestGetCurrentHostname:
    def test_returns_stripped_hostname(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "myserver\n"
        assert get_current_hostname() == "myserver"

# ── set_hostname ─────────────────────────────────────────────────

class TestSetHostname:
    def test_rejects_invalid_hostname(self, mock_run_command):
        mock = mock_run_command("modules.hostname")
        result = set_hostname("-invalid-")
        mock.assert_not_called()
        assert result is False

    def test_skips_if_already_set(self, mocker, mock_run_command):
        mocker.patch("modules.hostname.get_current_hostname", return_value="webserver")
        mock = mock_run_command("modules.hostname")
        result = set_hostname("webserver")
        mock.assert_not_called()
        assert result is True

    def test_changes_hostname_when_different(self, mocker, mock_run_command, tmp_path, monkeypatch):
        hosts_file = tmp_path / "hosts"
        hosts_file.write_text("127.0.0.1\tlocalhost\n127.0.1.1\toldname\n")
        monkeypatch.setattr("modules.hostname.HOSTS_FILE", str(hosts_file))

        # Simula: primera llamada devuelve "oldname" (antes), segunda "newname" (verificación)
        mocker.patch(
            "modules.hostname.get_current_hostname",
            side_effect=["oldname", "newname"]
        )
        mock = mock_run_command("modules.hostname")

        result = set_hostname("newname")

        mock.assert_called_once_with(["hostnamectl", "set-hostname", "newname"])
        assert result is True

        content = hosts_file.read_text()
        assert "127.0.1.1\tnewname" in content
        assert "oldname" not in content

    def test_reports_failure_if_verification_mismatch(self, mocker, mock_run_command, tmp_path, monkeypatch):
        hosts_file = tmp_path / "hosts"
        hosts_file.write_text("127.0.1.1\toldname\n")
        monkeypatch.setattr("modules.hostname.HOSTS_FILE", str(hosts_file))

        # La verificación final NO coincide con lo esperado
        mocker.patch(
            "modules.hostname.get_current_hostname",
            side_effect=["oldname", "somethingelse"]
        )
        mock_run_command("modules.hostname")

        result = set_hostname("newname")
        assert result is False

# ── prompt_hostname_change ───────────────────────────────────────

class TestPromptHostnameChange:
    def test_returns_none_when_user_declines(self, mocker, monkeypatch):
        mocker.patch("modules.hostname.get_current_hostname", return_value="current-host")
        monkeypatch.setattr("builtins.input", lambda _: "n")
        result = prompt_hostname_change()
        assert result is None

    def test_returns_new_hostname_when_confirmed(self, mocker, monkeypatch):
        mocker.patch("modules.hostname.get_current_hostname", return_value="current-host")
        inputs = iter(["y", "new-host"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_hostname_change()
        assert result == "new-host"

    def test_reprompts_on_invalid_choice(self, mocker, monkeypatch):
        mocker.patch("modules.hostname.get_current_hostname", return_value="current-host")
        inputs = iter(["maybe", "n"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_hostname_change()
        assert result is None

    def test_reprompts_on_invalid_new_hostname(self, mocker, monkeypatch):
        mocker.patch("modules.hostname.get_current_hostname", return_value="current-host")
        inputs = iter(["y", "-invalid-", "valid-name"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_hostname_change()
        assert result == "valid-name"
