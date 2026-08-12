from modules.ufw import (
    install_ufw, enable_ufw, disable_ufw,
    allow_port, deny_port, delete_rule, show_status,
)
from utils import step, RED, RESET

def register_args(parser):
    group = parser.add_argument_group("UFW")

    group.add_argument("--install-ufw", action="store_true", help="Install UFW firewall")
    group.add_argument("--enable-ufw",  action="store_true", help="Enable the firewall")
    group.add_argument("--disable-ufw", action="store_true", help="Disable the firewall")

    group.add_argument("--allow-port",  type=int, metavar="PORT", help="Allow a port")
    group.add_argument("--deny-port",   type=int, metavar="PORT", help="Deny a port")
    group.add_argument("--delete-rule", type=int, metavar="PORT", help="Delete a rule for a port")
    group.add_argument("--protocol",    type=str, choices=["tcp", "udp"],
                       help="Protocol for --allow-port/--deny-port (default: both)")

    group.add_argument("--ufw-status",  action="store_true", help="Show firewall status")
    group.add_argument("--ufw-verbose", action="store_true", help="Show detailed firewall status")

def handle(args):
    if args.install_ufw:
        step("Installing UFW...")
        install_ufw()

    if args.enable_ufw:
        step("Enabling UFW...")
        enable_ufw()

    if args.disable_ufw:
        step("Disabling UFW...")
        disable_ufw()

    if args.allow_port:
        step(f"Allowing port {args.allow_port}...")
        allow_port(args.allow_port, args.protocol)

    if args.deny_port:
        step(f"Denying port {args.deny_port}...")
        deny_port(args.deny_port, args.protocol)

    if args.delete_rule:
        step(f"Deleting rule for port {args.delete_rule}...")
        delete_rule(args.delete_rule, args.protocol)

    if args.ufw_status or args.ufw_verbose:
        step("Firewall status:")
        show_status(verbose=args.ufw_verbose)

def run_all():
    """Called by --all. Installs UFW and allows SSH by default so you don't lock yourself out."""
    install_ufw()
    allow_port(22, "tcp")   # crítico: si no, --all te deja fuera del servidor
    enable_ufw()
