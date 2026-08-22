from modules.system import update_system, upgrade_system, full_upgrade_system
from utils import step


def register_args(parser):
    group = parser.add_argument_group("System")
    group.add_argument("--update",       action="store_true", help="Run apt update")
    group.add_argument("--upgrade",      action="store_true", help="Run apt upgrade")
    group.add_argument("--full-upgrade", action="store_true", help="Run apt full-upgrade")

def handle(args):
    if args.update:
        step("Running apt update...")
        update_system()

    if args.upgrade:
        step("Running apt upgrade...")
        upgrade_system()

    if args.full_upgrade:
        step("Running apt full-upgrade...")
        full_upgrade_system()

def run_all():
    """Called by --all. Runs all system steps in order."""
    step("Running apt update...")
    update_system()

    step("Running apt upgrade...")
    upgrade_system()

    step("Running apt full-upgrade...")
    full_upgrade_system()

