from modules.hostname import get_current_hostname, set_hostname,show_hostname_info, prompt_hostname_change
from utils import step, ok, RED, RESET

def register_args(parser):
    group = parser.add_argument_group("Hostname")

    group.add_argument("--show-hostname", action="store_true", help="Show current hostname info")
    group.add_argument("--set-hostname",  type=str, metavar="NAME", help="Set a new hostname")

def handle(args):
    if args.show_hostname:
        step("Hostname info:")
        show_hostname_info()

    if args.set_hostname:
        set_hostname(args.set_hostname)

def run_all():
    """
    Called by --all. Shows the current hostname and asks if the
    user wants to change it. Continues either way.
    """
    step("Hostname configuration...")
    new_hostname = prompt_hostname_change()

    if new_hostname:
        set_hostname(new_hostname)
    else:
        ok("Keeping current hostname")
