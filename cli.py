import argparse
from utils import CYAN, PINK, RESET

from commands import MODULES
from commands import system as cmd_system
from commands import ssh    as cmd_ssh
from commands import git    as cmd_git



def print_banner():
    print(f"""
{CYAN}╔══════════════════════════════════╗
║      Server Setup CLI v1.0       ║
╚══════════════════════════════════╝{RESET}
""")

def run_all(args):
    print(f"\n{PINK}[ALL]{RESET} Starting full server setup...\n")

    print(f"{PINK}{'─'*40}{RESET}")
    print(f"{PINK} PHASE 1 — System Update{RESET}")
    print(f"{PINK}{'─'*40}{RESET}")
    cmd_system.run_all()

    print(f"{PINK}{'─'*40}{RESET}")
    print(f"{PINK} PHASE 2 — SSH Setup{RESET}")
    print(f"{PINK}{'─'*40}{RESET}")
    cmd_ssh.run_all(port=args.ssh_port)

    print(f"{PINK}{'─'*40}{RESET}")
    print(f"{PINK} PHASE3 — GIT Setup{RESET}")
    cmd_git.run_all()

    print(f"\n{CYAN}[DONE]{RESET} Full setup completed.\n")

def main():
    print_banner()

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
