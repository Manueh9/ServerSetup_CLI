from utils import ok, warn, error, info, success, step, get_real_user
import subprocess
import re

# Marker to identify tasks added by this CLI, so we can find/remove them safely
CLI_MARKER = "# added-by-serversetup-cli"

def _run_crontab(args: list[str], input_text: str = None) -> subprocess.CompletedProcess:
    """
    Runs crontab as the real user (not root), even if the CLI was invoked with sudo.
    """
    real_user, _ = get_real_user()
    cmd = ["sudo", "-u", real_user, "crontab"] + args
    return subprocess.run(cmd, capture_output=True, text=True, input=input_text)

def is_valid_cron_schedule(schedule: str) -> bool:
    """
    Validates a 5-field cron schedule: minute hour day month weekday.
    Accepts digits, *, /, -, , in each field.
    """
    parts = schedule.strip().split()
    if len(parts) != 5:
        return False
    field_pattern = r"^(\*|[\d\*/,-]+)$"
    return all(re.match(field_pattern, part) for part in parts)

def get_current_crontab() -> list[str]:
    """Returns the current crontab lines for the real user, or empty list if none."""
    result = _run_crontab(["-l"])
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]

def add_task(schedule: str, command: str, comment: str = None) -> bool:
    if not is_valid_cron_schedule(schedule):
        error(f"Invalid cron schedule: '{schedule}'")
        warn("Format must be: 'minute hour day month weekday' (e.g. '0 3 * * *')")
        return False

    if not command.strip():
        error("Command cannot be empty")
        return False

    lines = get_current_crontab()

    new_line = f"{schedule} {command} {CLI_MARKER}"
    if comment:
        new_line = f"# {comment}\n{new_line}"

    if any(command in line for line in lines):
        warn(f"A task with this command already exists — adding anyway")

    lines.append(new_line)

    new_crontab = "\n".join(lines) + "\n"
    result = _run_crontab(["-"], input_text=new_crontab)

    if result.returncode == 0:
        success(f"Cron task added: {schedule} {command}")
        return True
    else:
        error(f"Failed to add cron task: {result.stderr.strip()}")
        return False

def list_tasks(only_cli_managed: bool = False) -> list[str]:
    lines = get_current_crontab()

    if only_cli_managed:
        lines = [l for l in lines if CLI_MARKER in l]

    return lines

def show_tasks(only_cli_managed: bool = False):
    lines = list_tasks(only_cli_managed)

    print()
    if not lines:
        info("No cron tasks found" + (" (managed by this CLI)" if only_cli_managed else ""))
    else:
        info(f"Cron tasks{' (managed by this CLI)' if only_cli_managed else ''}:")
        for i, line in enumerate(lines, 1):
            print(f"  [{i}] {line}")
    print()

def remove_task(index: int) -> bool:
    """
    Removes a task by its 1-based index as shown in show_tasks().
    """
    lines = get_current_crontab()

    if index < 1 or index > len(lines):
        error(f"Invalid task index: {index}. Use --list-cron to see valid indices.")
        return False

    removed = lines.pop(index - 1)
    new_crontab = "\n".join(lines) + "\n" if lines else ""

    result = _run_crontab(["-"], input_text=new_crontab)

    if result.returncode == 0:
        success(f"Removed: {removed.strip()}")
        return True
    else:
        error(f"Failed to remove task: {result.stderr.strip()}")
        return False

def remove_all_cli_tasks() -> int:
    """Removes only the tasks that were added by this CLI. Returns count removed."""
    lines = get_current_crontab()
    kept = [l for l in lines if CLI_MARKER not in l]
    removed_count = len(lines) - len(kept)

    if removed_count == 0:
        ok("No CLI-managed tasks to remove")
        return 0

    new_crontab = "\n".join(kept) + "\n" if kept else ""
    result = _run_crontab(["-"], input_text=new_crontab)

    if result.returncode == 0:
        success(f"Removed {removed_count} CLI-managed task(s)")
    else:
        error(f"Failed to remove tasks: {result.stderr.strip()}")

    return removed_count

def clear_all_tasks() -> bool:
    """Removes ALL cron tasks for the user, including ones not managed by this CLI."""
    result = _run_crontab(["-r"])
    if result.returncode == 0:
        success("All cron tasks removed")
        return True
    else:
        warn("No crontab to remove or removal failed")
        return False
