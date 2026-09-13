import pytest
from serverforge_cli.cli import main


class TestOSGate:
    def test_exits_when_os_unsupported(self, mocker, monkeypatch):
        monkeypatch.setattr("sys.argv", ["sforge", "--all"])
        mocker.patch("serverforge_cli.cli.is_supported_os", return_value=False)
        run_all_mock = mocker.patch("serverforge_cli.cli.run_all")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
        run_all_mock.assert_not_called()

    def test_continues_when_os_supported(self, mocker, monkeypatch):
        monkeypatch.setattr("sys.argv", ["sforge", "--all"])
        mocker.patch("serverforge_cli.cli.is_supported_os", return_value=True)
        run_all_mock = mocker.patch("serverforge_cli.cli.run_all")

        main()

        run_all_mock.assert_called_once()

    def test_not_checked_for_help_flag(self, mocker, monkeypatch):
        monkeypatch.setattr("sys.argv", ["sforge", "--help"])
        os_check_mock = mocker.patch("serverforge_cli.cli.is_supported_os")

        main()

        os_check_mock.assert_not_called()
