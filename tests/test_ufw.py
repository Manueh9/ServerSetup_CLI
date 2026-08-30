import pytest
from serverforge_cli.modules.ufw import (
    is_ufw_installed, install_ufw,
    is_ufw_active, enable_ufw, disable_ufw,
    allow_port, deny_port, delete_rule,
)

# ── is_ufw_installed ────────────────────────────────────────────

class TestIsUfwInstalled:
    def test_returns_true_when_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 0
        assert is_ufw_installed() is True

    def test_returns_false_when_not_found(self, mock_subprocess_run):
        mock_subprocess_run.return_value.returncode = 1
        assert is_ufw_installed() is False

# ── install_ufw ──────────────────────────────────────────────────

class TestInstallUfw:
    def test_skips_if_already_installed(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.ufw.is_ufw_installed", return_value=True)
        mock = mock_run_command("serverforge_cli.modules.ufw")
        install_ufw()
        mock.assert_not_called()

    def test_installs_if_not_present(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.ufw.is_ufw_installed", return_value=False)
        mock = mock_run_command("serverforge_cli.modules.ufw")
        install_ufw()
        mock.assert_called_once_with(["apt", "install", "-y", "ufw"])

# ── is_ufw_active ────────────────────────────────────────────────

class TestIsUfwActive:
    def test_returns_true_when_active(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "Status: active\n\nTo  Action  From\n--  ------  ----"
        assert is_ufw_active() is True

    def test_returns_false_when_inactive(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "Status: inactive"
        assert is_ufw_active() is False

# ── enable_ufw / disable_ufw ────────────────────────────────────

class TestEnableUfw:
    def test_skips_if_already_active(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.ufw.is_ufw_active", return_value=True)
        mock = mock_run_command("serverforge_cli.modules.ufw")
        enable_ufw()
        mock.assert_not_called()

    def test_enables_with_force_flag_if_inactive(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.ufw.is_ufw_active", return_value=False)
        mock = mock_run_command("serverforge_cli.modules.ufw")
        enable_ufw()
        mock.assert_called_once_with(["ufw", "--force", "enable"])

class TestDisableUfw:
    def test_skips_if_already_inactive(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.ufw.is_ufw_active", return_value=False)
        mock = mock_run_command("serverforge_cli.modules.ufw")
        disable_ufw()
        mock.assert_not_called()

    def test_disables_if_active(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.ufw.is_ufw_active", return_value=True)
        mock = mock_run_command("serverforge_cli.modules.ufw")
        disable_ufw()
        mock.assert_called_once_with(["ufw", "disable"])

# ── allow_port ───────────────────────────────────────────────────

class TestAllowPort:
    def test_allows_port_without_protocol(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        result = allow_port(22)
        mock.assert_called_once_with(["ufw", "allow", "22"])
        assert result is True

    def test_allows_port_with_tcp_protocol(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        allow_port(22, "tcp")
        mock.assert_called_once_with(["ufw", "allow", "22/tcp"])

    def test_allows_port_with_udp_protocol(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        allow_port(53, "udp")
        mock.assert_called_once_with(["ufw", "allow", "53/udp"])

    def test_rejects_port_too_low(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        result = allow_port(0)
        mock.assert_not_called()
        assert result is False

    def test_rejects_port_too_high(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        result = allow_port(70000)
        mock.assert_not_called()
        assert result is False

# ── deny_port ────────────────────────────────────────────────────

class TestDenyPort:
    def test_denies_port_without_protocol(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        deny_port(8080)
        mock.assert_called_once_with(["ufw", "deny", "8080"])

    def test_denies_port_with_protocol(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        deny_port(8080, "tcp")
        mock.assert_called_once_with(["ufw", "deny", "8080/tcp"])

    def test_rejects_invalid_port(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        result = deny_port(-1)
        mock.assert_not_called()
        assert result is False

# ── delete_rule ──────────────────────────────────────────────────

class TestDeleteRule:
    def test_deletes_rule_without_protocol(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        delete_rule(22)
        mock.assert_called_once_with(["ufw", "delete", "allow", "22"])

    def test_deletes_rule_with_protocol(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ufw")
        delete_rule(22, "tcp")
        mock.assert_called_once_with(["ufw", "delete", "allow", "22/tcp"])
