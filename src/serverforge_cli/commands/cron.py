from serverforge_cli.modules.cron import (
    add_task, show_tasks, remove_task,
    remove_all_cli_tasks, clear_all_tasks,
)
from serverforge_cli.utils import step, error

def register_args(parser):
    group = parser.add_argument_group("Cron")

    group.add_argument("--add-cron",       type=str, metavar="SCHEDULE",
                       help="Add a cron task. Requires --cron-command. Example: --add-cron '0 3 * * *'")
    group.add_argument("--cron-command",   type=str, metavar="COMMAND",
                       help="Command to run for --add-cron")
    group.add_argument("--cron-comment",   type=str, metavar="TEXT",
                       help="Optional comment/label for the cron task")

    group.add_argument("--list-cron",      action="store_true", help="List all cron tasks")
    group.add_argument("--list-cron-cli",  action="store_true", help="List only tasks added by this CLI")

    group.add_argument("--remove-cron",    type=int, metavar="INDEX",
                       help="Remove a cron task by its index (see --list-cron)")
    group.add_argument("--remove-cron-cli", action="store_true",
                       help="Remove all cron tasks added by this CLI")
    group.add_argument("--clear-cron",     action="store_true",
                       help="Remove ALL cron tasks (including non-CLI ones) — use with caution")

def handle(args):
    if args.add_cron:
        if not args.cron_command:
            error("--add-cron requires --cron-command")
            return
        step(f"Adding cron task: {args.add_cron} {args.cron_command}")
        add_task(args.add_cron, args.cron_command, args.cron_comment)

    if args.list_cron:
        step("Cron tasks:")
        show_tasks()

    if args.list_cron_cli:
        step("CLI-managed cron tasks:")
        show_tasks(only_cli_managed=True)

    if args.remove_cron:
        step(f"Removing cron task #{args.remove_cron}...")
        remove_task(args.remove_cron)

    if args.remove_cron_cli:
        step("Removing CLI-managed cron tasks...")
        remove_all_cli_tasks()

    if args.clear_cron:
        step("Removing ALL cron tasks...")
        clear_all_tasks()

def run_all():
    """Called by --all. Cron tasks are too specific to add automatically — left untouched."""
    pass
