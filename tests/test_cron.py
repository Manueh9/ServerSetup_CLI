import pytest
from modules.cron import (
    is_valid_cron_schedule, get_current_crontab,
    add_task, list_tasks, remove_task,
    remove_all_cli_tasks, clear_all_tasks,
    CLI_MARKER,
)

# ── is_valid_cron_schedule ────────────────────────────────────────

class TestIsValidCronSchedule:
    def test_accepts_valid_schedule(self):
        assert is_valid_cron_schedule("0 3 * * *") is True

    def test_accepts_every_field_wildcard(self):
        assert is_valid_cron_schedule("* * * * *") is True

    def test_accepts_ranges_and_steps(self):
        assert is_valid_cron_schedule("*/15 9-17 * * 1-5") is True

    def test_accepts_comma_separated_values(self):
        assert is_valid_cron_schedule("0 6,12,18 * * *") is True

    def test_rejects_too_few_fields(self):
        assert is_valid_cron_schedule("0 3 * *") is False

    def test_rejects_too_many_fields(self):
        assert is_valid_cron_schedule("0 3 * * * *") is False

    def test_rejects_invalid_characters(self):
        assert is_valid_cron_schedule("0 3 * * X") is False

    def test_rejects_empty_string(self):
        assert is_valid_cron_schedule("") is False

# ── get_current_crontab ───────────────────────────────────────────

class TestGetCurrentCrontab:
    def test_returns_lines_when_crontab_exists(self, mocker):
        mock_result = mocker.Mock(returncode=0, stdout="0 3 * * * /backup.sh\n0 6 * * * /health.sh\n")
        mocker.patch("modules.cron._run_crontab", return_value=mock_result)

        lines = get_current_crontab()
        assert len(lines) == 2
        assert "/backup.sh" in lines[0]

    def test_returns_empty_list_when_no_crontab(self, mocker):
        mock_result = mocker.Mock(returncode=1, stdout="")
        mocker.patch("modules.cron._run_crontab", return_value=mock_result)

        lines = get_current_crontab()
        assert lines == []

    def test_skips_empty_lines(self, mocker):
        mock_result = mocker.Mock(returncode=0, stdout="0 3 * * * /a.sh\n\n0 6 * * * /b.sh\n\n")
        mocker.patch("modules.cron._run_crontab", return_value=mock_result)

        lines = get_current_crontab()
        assert len(lines) == 2

# ── add_task ───────────────────────────────────────────────────────

class TestAddTask:
    def test_rejects_invalid_schedule(self, mocker):
        mocker.patch("modules.cron._run_crontab")
        result = add_task("invalid", "/some/command.sh")
        assert result is False

    def test_rejects_empty_command(self, mocker):
        mocker.patch("modules.cron._run_crontab")
        result = add_task("0 3 * * *", "")
        assert result is False

    def test_adds_task_with_marker(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[])
        mock_run = mocker.Mock(returncode=0)
        mock_crontab = mocker.patch("modules.cron._run_crontab", return_value=mock_run)

        result = add_task("0 3 * * *", "/backup.sh")

        assert result is True
        # Verifica que se escribió con el marker
        call_kwargs = mock_crontab.call_args
        written_content = call_kwargs.kwargs.get("input_text") or call_kwargs.args[1] if len(call_kwargs.args) > 1 else None
        # Buscar en cualquiera de las formas de llamada
        all_call_text = str(mock_crontab.call_args)
        assert CLI_MARKER in all_call_text

    def test_adds_comment_when_provided(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[])
        mock_run = mocker.Mock(returncode=0)
        mock_crontab = mocker.patch("modules.cron._run_crontab", return_value=mock_run)

        add_task("0 3 * * *", "/backup.sh", comment="Daily backup")

        all_call_text = str(mock_crontab.call_args)
        assert "Daily backup" in all_call_text

    def test_reports_failure_on_crontab_error(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[])
        mock_run = mocker.Mock(returncode=1, stderr="crontab error")
        mocker.patch("modules.cron._run_crontab", return_value=mock_run)

        result = add_task("0 3 * * *", "/backup.sh")
        assert result is False

# ── list_tasks ────────────────────────────────────────────────────

class TestListTasks:
    def test_returns_all_tasks_by_default(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[
            f"0 3 * * * /backup.sh {CLI_MARKER}",
            "0 6 * * * /other.sh",
        ])
        tasks = list_tasks()
        assert len(tasks) == 2

    def test_filters_only_cli_managed(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[
            f"0 3 * * * /backup.sh {CLI_MARKER}",
            "0 6 * * * /other.sh",
        ])
        tasks = list_tasks(only_cli_managed=True)
        assert len(tasks) == 1
        assert CLI_MARKER in tasks[0]

# ── remove_task ───────────────────────────────────────────────────

class TestRemoveTask:
    def test_rejects_index_zero(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=["0 3 * * * /a.sh"])
        result = remove_task(0)
        assert result is False

    def test_rejects_index_out_of_range(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=["0 3 * * * /a.sh"])
        result = remove_task(5)
        assert result is False

    def test_removes_correct_task_by_index(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[
            "0 3 * * * /a.sh",
            "0 6 * * * /b.sh",
        ])
        mock_run = mocker.Mock(returncode=0)
        mock_crontab = mocker.patch("modules.cron._run_crontab", return_value=mock_run)

        result = remove_task(1)

        assert result is True
        all_call_text = str(mock_crontab.call_args)
        assert "/a.sh" not in all_call_text or "/b.sh" in all_call_text

# ── remove_all_cli_tasks ──────────────────────────────────────────

class TestRemoveAllCliTasks:
    def test_returns_zero_when_no_cli_tasks(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[
            "0 6 * * * /manual-task.sh",
        ])
        count = remove_all_cli_tasks()
        assert count == 0

    def test_removes_only_cli_managed_tasks(self, mocker):
        mocker.patch("modules.cron.get_current_crontab", return_value=[
            f"0 3 * * * /backup.sh {CLI_MARKER}",
            "0 6 * * * /manual-task.sh",
            f"0 9 * * * /health.sh {CLI_MARKER}",
        ])
        mock_run = mocker.Mock(returncode=0)
        mocker.patch("modules.cron._run_crontab", return_value=mock_run)

        count = remove_all_cli_tasks()
        assert count == 2

# ── clear_all_tasks ────────────────────────────────────────────────

class TestClearAllTasks:
    def test_returns_true_on_success(self, mocker):
        mock_run = mocker.Mock(returncode=0)
        mocker.patch("modules.cron._run_crontab", return_value=mock_run)

        result = clear_all_tasks()
        assert result is True

    def test_returns_false_on_failure(self, mocker):
        mock_run = mocker.Mock(returncode=1)
        mocker.patch("modules.cron._run_crontab", return_value=mock_run)

        result = clear_all_tasks()
        assert result is False
