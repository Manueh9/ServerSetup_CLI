import pytest
from unittest.mock import call
from types import SimpleNamespace
from serverforge_cli.modules.ssh import (
    change_ssh_port,
    _verify_config_port,
    install_ssh,
    enable_ssh,
    restart_ssh,
    check_ssh_status,
)

SAMPLE_CONFIG_COMMENTED = """#Port 22
#AddressFamily any
PermitRootLogin prohibit-password
"""

SAMPLE_CONFIG_ACTIVE = """Port 22
PermitRootLogin prohibit-password
"""

SAMPLE_CONFIG_NO_PORT = """PermitRootLogin prohibit-password
Subsystem sftp /usr/lib/openssh/sftp-server
"""

class TestChangeSSHPort:
    def test_invalid_port_too_low(self, capsys):
        with pytest.raises(SystemExit):
            change_ssh_port(0)
        assert "Invalid port" in capsys.readouterr().out

    def test_invalid_port_too_high(self, capsys):
        with pytest.raises(SystemExit):
            change_ssh_port(70000)
        assert "Invalid port" in capsys.readouterr().out

    def test_replaces_commented_port_line(self, tmp_path, monkeypatch, mocker):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_COMMENTED)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        change_ssh_port(2222)

        content = config_file.read_text()
        assert "Port 2222" in content
        assert "#Port 22" not in content

    def test_replaces_active_port_line(self, tmp_path, monkeypatch):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_ACTIVE)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        change_ssh_port(2222)

        content = config_file.read_text()
        assert "Port 2222" in content
        assert content.count("Port") == 1

    def test_appends_port_when_missing(self, tmp_path, monkeypatch):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_NO_PORT)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        change_ssh_port(2222)

        content = config_file.read_text()
        assert "Port 2222" in content

    def test_permission_error_exits(self, monkeypatch):
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", "/root/protected_file_that_does_not_exist")
        with pytest.raises(SystemExit):
            change_ssh_port(2222)

    def test_privileged_port_warns_but_does_not_exit(self, tmp_path, monkeypatch, capsys):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_ACTIVE)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        change_ssh_port(80)

        assert "privileged port" in capsys.readouterr().out
        assert "Port 80" in config_file.read_text()

    def test_port_22_does_not_trigger_privileged_warning(self, tmp_path, monkeypatch, capsys):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_NO_PORT)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        change_ssh_port(22)

        assert "privileged port" not in capsys.readouterr().out

    def test_multiple_existing_port_lines_collapse_to_one(self, tmp_path, monkeypatch):
        config_file = tmp_path / "sshd_config"
        config_file.write_text("Port 22\n#Port 2200\nPermitRootLogin prohibit-password\n")
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        change_ssh_port(2222)

        content = config_file.read_text()
        assert content.count("Port") == 1
        assert "Port 2222" in content
        assert "2200" not in content

    def test_reports_verification_success(self, tmp_path, monkeypatch, capsys):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_ACTIVE)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        change_ssh_port(2222)

        assert "Verified: Port 2222" in capsys.readouterr().out


class TestVerifyConfigPort:
    def test_verified_when_port_matches(self, tmp_path, monkeypatch, capsys):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_ACTIVE)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        _verify_config_port(22)

        assert "Verified: Port 22" in capsys.readouterr().out

    def test_warns_when_port_mismatches(self, tmp_path, monkeypatch, capsys):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_ACTIVE)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        _verify_config_port(2222)

        assert "Config file has Port 22, expected 2222" in capsys.readouterr().out

    def test_warns_when_no_active_port_line(self, tmp_path, monkeypatch, capsys):
        config_file = tmp_path / "sshd_config"
        config_file.write_text(SAMPLE_CONFIG_COMMENTED)
        monkeypatch.setattr("serverforge_cli.modules.ssh.SSH_CONFIG_FILE", str(config_file))

        _verify_config_port(2222)

        assert "No active 'Port' line found" in capsys.readouterr().out


class TestInstallSSH:
    def test_installs_openssh_server(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ssh")

        install_ssh()

        mock.assert_called_once_with(["apt", "install", "-y", "openssh-server"], requires_sudo=True)


class TestEnableSSH:
    def test_enables_and_starts_service(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ssh")

        enable_ssh()

        assert mock.call_args_list == [
            call(["systemctl", "enable", "ssh"], requires_sudo=True),
            call(["systemctl", "start", "ssh"], requires_sudo=True),
        ]


class TestRestartSSH:
    def test_stops_reloads_and_starts_in_order(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.ssh")

        restart_ssh()

        assert mock.call_args_list == [
            call(["systemctl", "stop", "ssh.socket"], requires_sudo=True),
            call(["systemctl", "stop", "ssh"], requires_sudo=True),
            call(["systemctl", "daemon-reload"], requires_sudo=True),
            call(["systemctl", "start", "ssh.socket"], requires_sudo=True),
            call(["systemctl", "start", "ssh"], requires_sudo=True),
        ]


class TestCheckSSHStatus:
    def test_active_service_and_matching_ports(self, mock_subprocess_run, capsys):
        mock_subprocess_run.side_effect = [
            SimpleNamespace(stdout="active\n"),
            SimpleNamespace(stdout="LISTEN 0 128 0.0.0.0:22 0.0.0.0:* users:((\"sshd\",pid=1,fd=3))\n"),
        ]

        check_ssh_status()

        out = capsys.readouterr().out
        assert "SSH service: active" in out
        assert "Active SSH ports:" in out
        assert "sshd" in out

    def test_inactive_service(self, mock_subprocess_run, capsys):
        mock_subprocess_run.side_effect = [
            SimpleNamespace(stdout="inactive\n"),
            SimpleNamespace(stdout=""),
        ]

        check_ssh_status()

        assert "SSH service: inactive" in capsys.readouterr().out

    def test_no_ssh_ports_detected(self, mock_subprocess_run, capsys):
        mock_subprocess_run.side_effect = [
            SimpleNamespace(stdout="active\n"),
            SimpleNamespace(stdout="LISTEN 0 128 0.0.0.0:80 0.0.0.0:*\n"),
        ]

        check_ssh_status()

        assert "No SSH ports detected" in capsys.readouterr().out
