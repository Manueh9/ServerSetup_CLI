import pytest
from serverforge_cli.modules.timezone import (
    get_current_timezone, show_current_timezone, list_timezones,
    set_timezone, get_ntp_status, show_ntp_status, enable_ntp, disable_ntp,
)

# ── get_current_timezone ─────────────────────────────────────────

class TestGetCurrentTimezone:
    def test_returns_stripped_timezone_on_success(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\n"
        mock_subprocess_run.return_value.returncode = 0
        assert get_current_timezone() == "Europe/Madrid"

    def test_returns_unknown_on_failure(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.returncode = 1
        assert get_current_timezone() == "unknown"

# ── show_current_timezone ────────────────────────────────────────

class TestShowCurrentTimezone:
    def test_runs_without_raising(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\n"
        mock_subprocess_run.return_value.returncode = 0
        show_current_timezone()

# ── list_timezones ───────────────────────────────────────────────

class TestListTimezones:
    def test_lists_all_zones_without_region(self, mock_subprocess_run, capsys):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\nAmerica/New_York\n"
        mock_subprocess_run.return_value.returncode = 0
        list_timezones()
        out = capsys.readouterr().out
        assert "Europe/Madrid" in out
        assert "America/New_York" in out
        assert "2 timezone(s) found" in out

    def test_filters_by_region_case_insensitive(self, mock_subprocess_run, capsys):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\nEurope/Paris\nAmerica/New_York\n"
        mock_subprocess_run.return_value.returncode = 0
        list_timezones(region="europe")
        out = capsys.readouterr().out
        assert "Europe/Madrid" in out
        assert "Europe/Paris" in out
        assert "America/New_York" not in out
        assert "2 timezone(s) found" in out

    def test_warns_when_region_has_no_matches(self, mock_subprocess_run, capsys):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\n"
        mock_subprocess_run.return_value.returncode = 0
        list_timezones(region="Nowhere")
        out = capsys.readouterr().out
        assert "No timezones found for region: Nowhere" in out

    def test_errors_when_command_fails(self, mock_subprocess_run, capsys):
        mock_subprocess_run.return_value.returncode = 1
        list_timezones()
        out = capsys.readouterr().out
        assert "Could not retrieve timezone list" in out

# ── set_timezone ─────────────────────────────────────────────────

class TestSetTimezone:
    def test_rejects_invalid_timezone(self, mock_subprocess_run, mock_run_command):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\nAmerica/New_York\n"
        mock_subprocess_run.return_value.returncode = 0
        mock = mock_run_command("serverforge_cli.modules.timezone")

        result = set_timezone("Not/AZone")

        mock.assert_not_called()
        assert result is False

    def test_skips_if_already_set(self, mocker, mock_subprocess_run, mock_run_command):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\nAmerica/New_York\n"
        mock_subprocess_run.return_value.returncode = 0
        mocker.patch(
            "serverforge_cli.modules.timezone.get_current_timezone",
            return_value="Europe/Madrid",
        )
        mock = mock_run_command("serverforge_cli.modules.timezone")

        result = set_timezone("Europe/Madrid")

        mock.assert_not_called()
        assert result is True

    def test_changes_timezone_when_valid_and_different(self, mocker, mock_subprocess_run, mock_run_command):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\nAmerica/New_York\n"
        mock_subprocess_run.return_value.returncode = 0
        mocker.patch(
            "serverforge_cli.modules.timezone.get_current_timezone",
            side_effect=["America/New_York", "Europe/Madrid"],
        )
        mocker.patch("serverforge_cli.modules.timezone.show_current_timezone")
        mock = mock_run_command("serverforge_cli.modules.timezone")

        result = set_timezone("Europe/Madrid")

        mock.assert_called_once_with(["timedatectl", "set-timezone", "Europe/Madrid"], requires_sudo=True)
        assert result is True

    def test_reports_failure_if_verification_mismatch(self, mocker, mock_subprocess_run, mock_run_command):
        mock_subprocess_run.return_value.stdout = "Europe/Madrid\nAmerica/New_York\n"
        mock_subprocess_run.return_value.returncode = 0
        mocker.patch(
            "serverforge_cli.modules.timezone.get_current_timezone",
            side_effect=["America/New_York", "America/New_York"],
        )
        mock_run_command("serverforge_cli.modules.timezone")

        result = set_timezone("Europe/Madrid")

        assert result is False

# ── get_ntp_status ───────────────────────────────────────────────

class TestGetNtpStatus:
    def test_returns_true_when_yes(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "yes\n"
        assert get_ntp_status() is True

    def test_returns_false_when_no(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "no\n"
        assert get_ntp_status() is False

# ── show_ntp_status ──────────────────────────────────────────────

class TestShowNtpStatus:
    def test_runs_without_raising(self, mock_subprocess_run):
        mock_subprocess_run.return_value.stdout = "yes\n"
        show_ntp_status()

# ── enable_ntp ───────────────────────────────────────────────────

class TestEnableNtp:
    def test_skips_if_already_enabled(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.timezone.get_ntp_status", return_value=True)
        mock = mock_run_command("serverforge_cli.modules.timezone")

        enable_ntp()

        mock.assert_not_called()

    def test_enables_when_disabled(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.timezone.get_ntp_status", return_value=False)
        mocker.patch("serverforge_cli.modules.timezone.show_ntp_status")
        mock = mock_run_command("serverforge_cli.modules.timezone")

        enable_ntp()

        mock.assert_called_once_with(["timedatectl", "set-ntp", "true"], requires_sudo=True)

# ── disable_ntp ──────────────────────────────────────────────────

class TestDisableNtp:
    def test_skips_if_already_disabled(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.timezone.get_ntp_status", return_value=False)
        mock = mock_run_command("serverforge_cli.modules.timezone")

        disable_ntp()

        mock.assert_not_called()

    def test_disables_when_enabled(self, mocker, mock_run_command):
        mocker.patch("serverforge_cli.modules.timezone.get_ntp_status", return_value=True)
        mocker.patch("serverforge_cli.modules.timezone.show_ntp_status")
        mock = mock_run_command("serverforge_cli.modules.timezone")

        disable_ntp()

        mock.assert_called_once_with(["timedatectl", "set-ntp", "false"], requires_sudo=True)
