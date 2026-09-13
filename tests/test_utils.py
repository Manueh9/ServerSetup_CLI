from serverforge_cli.utils import run_command, is_supported_os


class TestRunCommandInputText:
    def test_passes_input_text_to_subprocess(self, mocker):
        mock_run = mocker.patch("subprocess.run")
        mocker.patch("serverforge_cli.utils.is_running_as_root", return_value=True)

        run_command(["chpasswd"], input_text="devuser:s3cret")

        _, kwargs = mock_run.call_args
        assert kwargs["input"] == "devuser:s3cret"

    def test_defaults_to_no_input(self, mocker):
        mock_run = mocker.patch("subprocess.run")
        mocker.patch("serverforge_cli.utils.is_running_as_root", return_value=True)

        run_command(["apt", "update"])

        _, kwargs = mock_run.call_args
        assert kwargs["input"] is None


class TestIsSupportedOS:
    def test_returns_true_for_debian(self, tmp_path):
        os_release = tmp_path / "os-release"
        os_release.write_text('ID=debian\nID_LIKE=""\n')
        assert is_supported_os(str(os_release)) is True

    def test_returns_true_for_ubuntu(self, tmp_path):
        os_release = tmp_path / "os-release"
        os_release.write_text('ID=ubuntu\nID_LIKE=debian\n')
        assert is_supported_os(str(os_release)) is True

    def test_returns_false_for_unsupported_distro(self, tmp_path):
        os_release = tmp_path / "os-release"
        os_release.write_text('ID=fedora\nID_LIKE="rhel fedora"\n')
        assert is_supported_os(str(os_release)) is False

    def test_returns_false_when_file_missing(self, tmp_path):
        missing = tmp_path / "does-not-exist"
        assert is_supported_os(str(missing)) is False
