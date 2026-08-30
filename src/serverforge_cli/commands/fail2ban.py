from serverforge_cli.modules.fail2ban import (
    install_fail2ban, enable_fail2ban, disable_fail2ban,
    configure_ssh_jail, restart_fail2ban, show_status,
)
from serverforge_cli.utils import step, warn_if_root_for_user_config

def register_args(parser):
    group = parser.add_argument_group("fail2ban")

    group.add_argument("--install-fail2ban", action="store_true", help="Install fail2ban")
    group.add_argument("--enable-fail2ban",  action="store_true", help="Enable fail2ban service")
    group.add_argument("--disable-fail2ban", action="store_true", help="Disable fail2ban service")

    group.add_argument("--protect-ssh",  action="store_true",
                       help="Configure fail2ban to protect SSH from brute force attacks")
    group.add_argument("--max-retry",    type=int, default=5,   metavar="N",
                       help="Failed attempts before ban (default: 5)")
    group.add_argument("--ban-time",     type=str, default="10m", metavar="TIME",
                       help="Ban duration, e.g. 10m, 1h, -1 for permanent (default: 10m)")
    group.add_argument("--find-time",    type=str, default="10m", metavar="TIME",
                       help="Time window to count failed attempts (default: 10m)")

    group.add_argument("--fail2ban-status", action="store_true", help="Show fail2ban status")
    group.add_argument("--jail",            type=str, metavar="JAIL_NAME",
                       help="Show status for a specific jail (e.g. sshd)")

def handle(args):
    if args.install_fail2ban:
        step("Installing fail2ban...")
        install_fail2ban()

    if args.protect_ssh:
        configure_ssh_jail(args.max_retry, args.ban_time, args.find_time)
        step("Restarting fail2ban to apply changes...")
        restart_fail2ban()

    if args.enable_fail2ban:
        step("Enabling fail2ban...")
        enable_fail2ban()

    if args.disable_fail2ban:
        step("Disabling fail2ban...")
        disable_fail2ban()

    if args.fail2ban_status:
        step("fail2ban status:")
        show_status(args.jail)

def run_all():
    """Called by --all. Installs fail2ban and protects SSH with sensible defaults."""
    install_fail2ban()
    configure_ssh_jail()
    enable_fail2ban()
