from types import SimpleNamespace
from serverforge_cli.commands.fail2ban import handle, run_all


class TestHandleProtectSshRestartGuard:
    def _args(self, **overrides):
        defaults = dict(
            install_fail2ban=False, protect_ssh=True, max_retry=5, ban_time="10m", find_time="10m",
            enable_fail2ban=False, disable_fail2ban=False, fail2ban_status=False, jail=None,
        )
        defaults.update(overrides)
        return SimpleNamespace(**defaults)

    def test_restarts_when_configure_succeeds(self, mocker):
        mocker.patch("serverforge_cli.commands.fail2ban.configure_ssh_jail", return_value=True)
        restart_mock = mocker.patch("serverforge_cli.commands.fail2ban.restart_fail2ban")

        handle(self._args())

        restart_mock.assert_called_once()

    def test_skips_restart_when_configure_fails(self, mocker):
        mocker.patch("serverforge_cli.commands.fail2ban.configure_ssh_jail", return_value=False)
        restart_mock = mocker.patch("serverforge_cli.commands.fail2ban.restart_fail2ban")

        handle(self._args())

        restart_mock.assert_not_called()


class TestRunAllRestartGuard:
    def test_restarts_when_configure_succeeds(self, mocker):
        mocker.patch("serverforge_cli.commands.fail2ban.install_fail2ban")
        mocker.patch("serverforge_cli.commands.fail2ban.enable_fail2ban")
        mocker.patch("serverforge_cli.commands.fail2ban.configure_ssh_jail", return_value=True)
        restart_mock = mocker.patch("serverforge_cli.commands.fail2ban.restart_fail2ban")

        run_all()

        restart_mock.assert_called_once()

    def test_skips_restart_when_configure_fails(self, mocker):
        mocker.patch("serverforge_cli.commands.fail2ban.install_fail2ban")
        mocker.patch("serverforge_cli.commands.fail2ban.enable_fail2ban")
        mocker.patch("serverforge_cli.commands.fail2ban.configure_ssh_jail", return_value=False)
        restart_mock = mocker.patch("serverforge_cli.commands.fail2ban.restart_fail2ban")

        run_all()

        restart_mock.assert_not_called()
