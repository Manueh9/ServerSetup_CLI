from modules.system import update_system, upgrade_system, full_upgrade_system

class TestSystemCommands:
    def test_update_calls_apt_update(self, mock_run_command):
        mock = mock_run_command("modules.system")
        update_system()
        mock.assert_called_once_with(["apt", "update"])

    def test_upgrade_calls_apt_upgrade_with_yes(self, mock_run_command):
        mock = mock_run_command("modules.system")
        upgrade_system()
        mock.assert_called_once_with(["apt", "upgrade", "-y"])

    def test_full_upgrade_calls_apt_full_upgrade_with_yes(self, mock_run_command):
        mock = mock_run_command("modules.system")
        full_upgrade_system()
        mock.assert_called_once_with(["apt", "full-upgrade", "-y"])
