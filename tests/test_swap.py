import pytest
from serverforge_cli.modules.swap import (
    is_valid_size, has_swap, create_swap,
    disable_swap, remove_swap, set_swappiness,
    prompt_swap_setup, get_swap_info,
)

# ── is_valid_size ──────────────────────────────────────────────────

class TestIsValidSize:
    def test_accepts_megabytes(self):
        assert is_valid_size("512M") is True

    def test_accepts_gigabytes(self):
        assert is_valid_size("2G") is True

    def test_accepts_lowercase(self):
        assert is_valid_size("2g") is True

    def test_accepts_kilobytes(self):
        assert is_valid_size("1024K") is True

    def test_rejects_no_unit(self):
        assert is_valid_size("512") is False

    def test_rejects_invalid_unit(self):
        assert is_valid_size("512X") is False

    def test_rejects_empty_string(self):
        assert is_valid_size("") is False

    def test_rejects_negative(self):
        assert is_valid_size("-2G") is False

# ── has_swap ──────────────────────────────────────────────────────

class TestHasSwap:
    def test_returns_true_when_swap_active(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "/swapfile  file  2097148  0  -2\n"
        assert has_swap() is True

    def test_returns_false_when_no_swap(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = ""
        assert has_swap() is False

# ── get_swap_info ─────────────────────────────────────────────────

class TestGetSwapInfo:
    def test_parses_swap_line_from_free(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = (
            "              total        used        free\n"
            "Mem:           7.7Gi       1.2Gi       5.1Gi\n"
            "Swap:          2.0Gi       0B          2.0Gi\n"
        )
        info = get_swap_info()
        assert info["total"] == "2.0Gi"
        assert info["used"] == "0B"
        assert info["free"] == "2.0Gi"

    def test_returns_zeros_when_no_swap_line(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "Mem:  7.7Gi  1.2Gi  5.1Gi\n"
        info = get_swap_info()
        assert info["total"] == "0"

# ── create_swap ───────────────────────────────────────────────────

class TestCreateSwap:
    def test_rejects_invalid_size(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.swap")
        result = create_swap("invalid")
        mock.assert_not_called()
        assert result is False

    def test_skips_if_swap_already_active(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.has_swap", return_value=True)
        mock = mock_run_command("serverforge_cli.modules.swap")
        result = create_swap("2G")
        mock.assert_not_called()
        assert result is True

    def test_creates_swapfile_when_none_exists(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.has_swap", side_effect=[False, True])
        mocker.patch("serverforge_cli.modules.swap._swapfile_exists", return_value=False)
        mocker.patch("serverforge_cli.modules.swap._add_to_fstab")
        mock = mock_run_command("serverforge_cli.modules.swap")

        result = create_swap("2G")

        mock.assert_any_call(["fallocate", "-l", "2G", "/swapfile"])
        mock.assert_any_call(["chmod", "600", "/swapfile"])
        mock.assert_any_call(["mkswap", "/swapfile"])
        mock.assert_any_call(["swapon", "/swapfile"])
        assert result is True

    def test_activates_existing_swapfile_without_recreating(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.has_swap", side_effect=[False, True])
        mocker.patch("serverforge_cli.modules.swap._swapfile_exists", return_value=True)
        mocker.patch("serverforge_cli.modules.swap._add_to_fstab")
        mock = mock_run_command("serverforge_cli.modules.swap")

        result = create_swap("2G")

        # No debe volver a crear el archivo con fallocate
        all_calls = str(mock.call_args_list)
        assert "fallocate" not in all_calls
        assert result is True

    def test_reports_failure_if_activation_fails(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.has_swap", side_effect=[False, False])
        mocker.patch("serverforge_cli.modules.swap._swapfile_exists", return_value=False)
        mocker.patch("serverforge_cli.modules.swap._add_to_fstab")
        mock_run_command("serverforge_cli.modules.swap")

        result = create_swap("2G")
        assert result is False

# ── disable_swap ──────────────────────────────────────────────────

class TestDisableSwap:
    def test_skips_if_no_active_swap(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.has_swap", return_value=False)
        mock = mock_run_command("serverforge_cli.modules.swap")
        result = disable_swap()
        mock.assert_not_called()
        assert result is True

    def test_disables_active_swap(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.has_swap", side_effect=[True, False])
        mock = mock_run_command("serverforge_cli.modules.swap")

        result = disable_swap()

        mock.assert_called_once_with(["swapoff", "/swapfile"])
        assert result is True

    def test_reports_failure_if_still_active(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.has_swap", side_effect=[True, True])
        mock_run_command("serverforge_cli.modules.swap")

        result = disable_swap()
        assert result is False

# ── remove_swap ───────────────────────────────────────────────────

class TestRemoveSwap:
    def test_removes_file_and_fstab_entry(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.disable_swap")
        mocker.patch("serverforge_cli.modules.swap._swapfile_exists", return_value=True)
        mocker.patch("serverforge_cli.modules.swap._remove_from_fstab")
        mock = mock_run_command("serverforge_cli.modules.swap")

        result = remove_swap()

        mock.assert_called_once_with(["rm", "/swapfile"])
        assert result is True

    def test_skips_rm_if_file_does_not_exist(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.swap.disable_swap")
        mocker.patch("serverforge_cli.modules.swap._swapfile_exists", return_value=False)
        mocker.patch("serverforge_cli.modules.swap._remove_from_fstab")
        mock = mock_run_command("serverforge_cli.modules.swap")

        remove_swap()

        mock.assert_not_called()

# ── set_swappiness ────────────────────────────────────────────────

class TestSetSwappiness:
    def test_rejects_value_below_zero(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.swap")
        result = set_swappiness(-1)
        mock.assert_not_called()
        assert result is False

    def test_rejects_value_above_100(self, mock_run_command):
        mock = mock_run_command("serverforge_cli.modules.swap")
        result = set_swappiness(101)
        mock.assert_not_called()
        assert result is False

    def test_sets_valid_value(self, mock_run_command, tmp_path, monkeypatch):
        sysctl_file = tmp_path / "sysctl.conf"
        sysctl_file.write_text("")

        # set_swappiness usa una ruta hardcodeada "/etc/sysctl.conf" — necesitamos
        # que el test escriba en un archivo temporal en su lugar
        original_open = open
        def fake_open(path, mode="r"):
            if path == "/etc/sysctl.conf":
                return original_open(str(sysctl_file), mode)
            return original_open(path, mode)
        monkeypatch.setattr("builtins.open", fake_open)

        mock = mock_run_command("serverforge_cli.modules.swap")
        result = set_swappiness(10)

        mock.assert_called_once_with(["sysctl", "vm.swappiness=10"])
        assert result is True
        assert "vm.swappiness=10" in sysctl_file.read_text()

    def test_updates_existing_swappiness_line(self, mock_run_command, tmp_path, monkeypatch):
        sysctl_file = tmp_path / "sysctl.conf"
        sysctl_file.write_text("vm.swappiness=60\nnet.ipv4.ip_forward=1\n")

        original_open = open
        def fake_open(path, mode="r"):
            if path == "/etc/sysctl.conf":
                return original_open(str(sysctl_file), mode)
            return original_open(path, mode)
        monkeypatch.setattr("builtins.open", fake_open)

        mock_run_command("serverforge_cli.modules.swap")
        set_swappiness(10)

        content = sysctl_file.read_text()
        assert "vm.swappiness=10" in content
        assert "vm.swappiness=60" not in content
        assert "net.ipv4.ip_forward=1" in content  # no debe tocar otras líneas

# ── prompt_swap_setup ─────────────────────────────────────────────

class TestPromptSwapSetup:
    def test_returns_none_when_declined(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "n")
        result = prompt_swap_setup()
        assert result is None

    def test_returns_default_size_when_confirmed_with_empty_input(self, monkeypatch):
        inputs = iter(["y", ""])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_swap_setup()
        assert result == "2G"

    def test_returns_custom_size_when_confirmed(self, monkeypatch):
        inputs = iter(["y", "1G"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_swap_setup()
        assert result == "1G"

    def test_reprompts_on_invalid_size(self, monkeypatch):
        inputs = iter(["y", "invalid", "2G"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        result = prompt_swap_setup()
        assert result == "2G"
