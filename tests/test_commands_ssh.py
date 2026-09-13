from serverforge_cli.commands.ssh import _install_and_configure


class TestInstallAndConfigureRestartGuard:
    def test_restarts_when_config_is_valid(self, mocker):
        mocker.patch("serverforge_cli.commands.ssh.install_ssh")
        mocker.patch("serverforge_cli.commands.ssh.enable_ssh")
        mocker.patch("serverforge_cli.commands.ssh.change_ssh_port")
        mocker.patch("serverforge_cli.commands.ssh.validate_ssh_config", return_value=(True, ""))
        restart_mock = mocker.patch("serverforge_cli.commands.ssh.restart_ssh")
        mocker.patch("serverforge_cli.commands.ssh.check_ssh_status")

        _install_and_configure(2222)

        restart_mock.assert_called_once()

    def test_skips_restart_when_config_is_invalid(self, mocker, capsys):
        mocker.patch("serverforge_cli.commands.ssh.install_ssh")
        mocker.patch("serverforge_cli.commands.ssh.enable_ssh")
        mocker.patch("serverforge_cli.commands.ssh.change_ssh_port")
        mocker.patch(
            "serverforge_cli.commands.ssh.validate_ssh_config",
            return_value=(False, "line 42: Bad configuration option"),
        )
        restart_mock = mocker.patch("serverforge_cli.commands.ssh.restart_ssh")
        mocker.patch("serverforge_cli.commands.ssh.check_ssh_status")

        _install_and_configure(2222)

        restart_mock.assert_not_called()
        assert "Bad configuration option" in capsys.readouterr().out

    def test_does_not_validate_when_port_unchanged(self, mocker):
        mocker.patch("serverforge_cli.commands.ssh.install_ssh")
        mocker.patch("serverforge_cli.commands.ssh.enable_ssh")
        validate_mock = mocker.patch("serverforge_cli.commands.ssh.validate_ssh_config")
        mocker.patch("serverforge_cli.commands.ssh.check_ssh_status")

        _install_and_configure(22)

        validate_mock.assert_not_called()
