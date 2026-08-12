import pytest
from modules.fail2ban import (
    is_fail2ban_installed, install_fail2ban,
    is_fail2ban_active, enable_fail2ban, disable_fail2ban,
    configure_ssh_jail, restart_fail2ban,
)

# ── is_fail2ban_installed ────────────────────────────────────────

class TestIsFail2banInstalled:
    def test_returns_true_when_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        assert is_fail2ban_installed() is True

    def test_returns_false_when_not_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 1
        assert is_fail2ban_installed() is False

# ── install_fail2ban ─────────────────────────────────────────────

class TestInstallFail2ban:
    def test_skips_if_already_installed(self, mocker, mock_run_command):
        mocker.patch("modules.fail2ban.is_fail2ban_installed", return_value=True)
        mock = mock_run_command("modules.fail2ban")
        install_fail2ban()
        mock.assert_not_called()

    def test_installs_if_not_present(self, mocker, mock_run_command):
        mocker.patch("modules.fail2ban.is_fail2ban_installed", return_value=False)
        mock = mock_run_command("modules.fail2ban")
        install_fail2ban()
        mock.assert_called_once_with(["apt", "install", "-y", "fail2ban"])

# ── is_fail2ban_active ───────────────────────────────────────────

class TestIsFail2banActive:
    def test_returns_true_when_active(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        assert is_fail2ban_active() is True

    def test_returns_false_when_inactive(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 1
        assert is_fail2ban_active() is False

# ── enable_fail2ban / disable_fail2ban ──────────────────────────

class TestEnableFail2ban:
    def test_skips_if_already_active(self, mocker, mock_run_command):
        mocker.patch("modules.fail2ban.is_fail2ban_active", return_value=True)
        mock = mock_run_command("modules.fail2ban")
        enable_fail2ban()
        mock.assert_not_called()

    def test_enables_and_starts_if_inactive(self, mocker, mock_run_command):
        mocker.patch("modules.fail2ban.is_fail2ban_active", return_value=False)
        mock = mock_run_command("modules.fail2ban")
        enable_fail2ban()
        assert mock.call_count == 2
        mock.assert_any_call(["systemctl", "enable", "fail2ban"])
        mock.assert_any_call(["systemctl", "start", "fail2ban"])

class TestDisableFail2ban:
    def test_skips_if_already_inactive(self, mocker, mock_run_command):
        mocker.patch("modules.fail2ban.is_fail2ban_active", return_value=False)
        mock = mock_run_command("modules.fail2ban")
        disable_fail2ban()
        mock.assert_not_called()

    def test_stops_and_disables_if_active(self, mocker, mock_run_command):
        mocker.patch("modules.fail2ban.is_fail2ban_active", return_value=True)
        mock = mock_run_command("modules.fail2ban")
        disable_fail2ban()
        assert mock.call_count == 2
        mock.assert_any_call(["systemctl", "stop", "fail2ban"])
        mock.assert_any_call(["systemctl", "disable", "fail2ban"])

# ── configure_ssh_jail ───────────────────────────────────────────

class TestConfigureSshJail:
    def test_writes_jail_local_file_with_defaults(self, tmp_path, monkeypatch):
        jail_file = tmp_path / "jail.local"
        monkeypatch.setattr("modules.fail2ban.JAIL_LOCAL_FILE", str(jail_file))

        configure_ssh_jail()

        content = jail_file.read_text()
        assert "[sshd]" in content
        assert "enabled = true" in content
        assert "maxretry = 5" in content
        assert "bantime = 10m" in content
        assert "findtime = 10m" in content

    def test_writes_custom_values(self, tmp_path, monkeypatch):
        jail_file = tmp_path / "jail.local"
        monkeypatch.setattr("modules.fail2ban.JAIL_LOCAL_FILE", str(jail_file))

        configure_ssh_jail(max_retry=3, ban_time="1h", find_time="5m")

        content = jail_file.read_text()
        assert "maxretry = 3" in content
        assert "bantime = 1h" in content
        assert "findtime = 5m" in content

    def test_overwrites_existing_file(self, tmp_path, monkeypatch):
        jail_file = tmp_path / "jail.local"
        jail_file.write_text("old content that should be replaced")
        monkeypatch.setattr("modules.fail2ban.JAIL_LOCAL_FILE", str(jail_file))

        configure_ssh_jail(max_retry=10)

        content = jail_file.read_text()
        assert "old content" not in content
        assert "maxretry = 10" in content

# ── restart_fail2ban ─────────────────────────────────────────────

class TestRestartFail2ban:
    def test_restarts_service(self, mock_run_command):
        mock = mock_run_command("modules.fail2ban")
        restart_fail2ban()
        mock.assert_called_once_with(["systemctl", "restart", "fail2ban"])
