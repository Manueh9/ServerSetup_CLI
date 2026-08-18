import argparse
import sys
from rich.table import Table
from utils import banner, phase_header, console, error
from commands import MODULES
from commands import system              as cmd_system
from commands import ssh                 as cmd_ssh
from commands import git                 as cmd_git
from commands import command_line_custom as cmd_prompt
from commands import timezone            as cmd_timezone
from commands import ufw                 as cmd_ufw
from commands import fail2ban            as cmd_fail2ban
from commands import hostname            as cmd_hostname
from commands import users               as cmd_users
from commands import cron                as cmd_cron
from commands import swap                as cmd_swap

# ── Module registry for the two-tier --help (key, module, one-liner) ─
# Order matches commands.MODULES so both stay in sync.
MODULE_HELP = [
    ("system",   cmd_system,   "apt update / upgrade / full-upgrade"),
    ("ssh",      cmd_ssh,      "Install & configure OpenSSH, change port"),
    ("git",      cmd_git,      "Install, configure user/editor/branch, generate SSH key"),
    ("prompt",   cmd_prompt,   "Customize bash prompt (branch, timestamp, venv)"),
    ("timezone", cmd_timezone, "Timezone & NTP sync"),
    ("ufw",      cmd_ufw,      "Firewall rules"),
    ("fail2ban", cmd_fail2ban, "Brute-force protection"),
    ("hostname", cmd_hostname, "Hostname management"),
    ("users",    cmd_users,    "Create/manage users, SSH keys, sudo"),
    ("cron",     cmd_cron,     "Scheduled cron tasks"),
    ("swap",     cmd_swap,     "Swap file management"),
]

# ── Phases executed by --all, in order ────────────────────────────
# Each entry: (title, callable). Numbering is derived automatically.
PHASES = [
    ("System Update",               lambda args: cmd_system.run_all()),
    ("SSH Setup",                   lambda args: cmd_ssh.run_all(port=args.ssh_port)),
    ("Git Setup",                   lambda args: cmd_git.run_all()),
    ("Command Line Customization",  lambda args: cmd_prompt.run_all()),
    ("Timezone & NTP",              lambda args: cmd_timezone.run_all()),
    ("Firewall (UFW)",              lambda args: cmd_ufw.run_all()),
    ("fail2ban",                    lambda args: cmd_fail2ban.run_all()),
    ("Hostname",                    lambda args: cmd_hostname.run_all()),
    ("Users",                       lambda args: cmd_users.run_all()),
    ("Swap",                        lambda args: cmd_swap.run_all()),
]

def print_overview_help():
    console.print("[bold]USAGE[/bold]")
    console.print("  cli.py --all                  Run the full guided setup")
    console.print("  cli.py <flags>                Run specific actions")
    console.print("  cli.py --help <module>        Show full options for one module\n")

    console.print("[bold]MODULES[/bold]")
    table = Table(box=None, show_header=False, padding=(0, 2, 0, 2))
    table.add_column(style="bold cyan")
    table.add_column()
    for key, _, description in MODULE_HELP:
        table.add_row(key, description)
    console.print(table)

    console.print("\nRun [bold cyan]cli.py --help <module>[/bold cyan] for that module's full flag list.\n")

def print_module_help(key: str):
    match = next(((k, m) for k, m, _ in MODULE_HELP if k == key), None)
    if not match:
        valid = ", ".join(k for k, _, _ in MODULE_HELP)
        error(f"Unknown module '{key}'. Valid modules: {valid}")
        exit(1)

    _, module = match
    temp_parser = argparse.ArgumentParser(prog="cli.py", add_help=False)
    module.register_args(temp_parser)
    console.print(temp_parser.format_help(), markup=False, highlight=False)

def run_all(args):
    total = len(PHASES)
    console.print("\n[bold magenta]▸ Starting full server setup...[/bold magenta]\n")

    for i, (title, action) in enumerate(PHASES, start=1):
        phase_header(i, total, title)
        action(args)
        console.rule(style="dim")

    console.print("\n[bold green]✔ Full setup completed.[/bold green]\n")

def main():
    banner("Server Setup CLI v1.0", "Automated Linux server configuration & hardening")

    argv = sys.argv[1:]
    if "-h" in argv or "--help" in argv:
        flag_index = argv.index("-h") if "-h" in argv else argv.index("--help")
        topic = argv[flag_index + 1] if flag_index + 1 < len(argv) and not argv[flag_index + 1].startswith("-") else None

        if topic:
            print_module_help(topic)
        else:
            print_overview_help()
        return

    parser = argparse.ArgumentParser(description="Server Setup CLI", add_help=False)
    parser.add_argument("--all", action="store_true", help="Run full setup (all phases)")

    for module in MODULES:
        module.register_args(parser)

    args = parser.parse_args()

    if args.all:
        run_all(args)
        return

    for module in MODULES:
        module.handle(args)

if __name__ == "__main__":
    main()
