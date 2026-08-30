from serverforge_cli.modules.ssh import install_ssh, enable_ssh, change_ssh_port, restart_ssh, check_ssh_status
from serverforge_cli.utils import step, error

DEFAULT_PORT = 22

def register_args(parser):
    group = parser.add_argument_group("SSH")
    group.add_argument("--ssh",      action="store_true", help="Install and configure OpenSSH")
    group.add_argument("--ssh-port", type=int,            help="SSH listening port")

def handle(args):
    if args.ssh_port and not args.ssh:
        error("--ssh-port requires --ssh")
        return

    if not args.ssh:
        return

    _install_and_configure(args.ssh_port)

def run_all(port=DEFAULT_PORT):
    """Called by --all. Runs all SSH steps in order."""
    _install_and_configure(port)

def _install_and_configure(port=None):
    """Shared logic between handle() and run_all()."""
    step("Installing OpenSSH Server...")
    install_ssh()

    step("Enabling SSH service...")
    enable_ssh()

    if port and port != DEFAULT_PORT:
        step(f"Changing SSH port to {port}...")
        change_ssh_port(port)

        step("Restarting SSH service...")
        restart_ssh()

    step("Checking SSH status...")
    check_ssh_status()
