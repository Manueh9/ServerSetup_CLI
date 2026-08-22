import pytest
from serverforge_cli.modules.ssh import change_ssh_port, _verify_config_port

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
