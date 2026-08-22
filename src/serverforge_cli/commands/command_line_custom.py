from serverforge_cli.modules.command_line_custom import (
    show_git_actual_branch, remove_git_actual_branch,
    show_timestamp, remove_timestamp,
    show_venv, remove_venv,
    show_current_prompt,
)

def register_args(parser):
    group = parser.add_argument_group("Prompt Customization")

    # Git branch
    group.add_argument("--show-branch",   action="store_true", help="Show git branch in prompt")
    group.add_argument("--remove-branch", action="store_true", help="Remove git branch from prompt")

    # Timestamp
    group.add_argument("--show-time",     action="store_true", help="Show timestamp [HH:MM:SS] in prompt")
    group.add_argument("--remove-time",   action="store_true", help="Remove timestamp from prompt")

    # Virtualenv
    group.add_argument("--show-venv",     action="store_true", help="Show active virtualenv name in prompt")
    group.add_argument("--remove-venv",   action="store_true", help="Remove virtualenv name from prompt")

    # Status
    group.add_argument("--prompt-status", action="store_true", help="Show active prompt customizations")

def handle(args):
    if args.prompt_status:
        show_current_prompt()

    if args.show_branch:
        show_git_actual_branch()

    if args.remove_branch:
        remove_git_actual_branch()

    if args.show_time:
        show_timestamp()

    if args.remove_time:
        remove_timestamp()

    if args.show_venv:
        show_venv()

    if args.remove_venv:
        remove_venv()

def run_all():
    """Called by --all. Applies all prompt customizations."""
    show_git_actual_branch()
    show_timestamp()
    show_venv()
