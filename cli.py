import argparse
from utils import banner, phase_header, console
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
from commands import swap                as cmd_swap

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

    parser = argparse.ArgumentParser(description="Server Setup CLI")
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
