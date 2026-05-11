import argparse

from modules.system import update_system, upgrade_system, full_upgrade_system
from modules.ssh import install_ssh, enable_ssh, change_ssh_port, restart_ssh, check_ssh_status


PINK = "\033[95m"
RESET = "\033[0m"


def full_setup():
    print(f"\n{PINK}[STEP]{RESET} Running full system setup...\n")

    update_system()
    upgrade_system()
    full_upgrade_system()

def create_parser():
    parser = argparse.ArgumentParser(description="Server Setup CLI")

    group = parser.add_mutually_exclusive_group()

    group.add_argument("--all", action="store_true", help="Run full setup")

    # SYSTEM
    group.add_argument("--update", action="store_true", help="Run apt update")
    group.add_argument("--upgrade", action="store_true", help="Run apt upgrade")
    group.add_argument("--full-upgrade", action="store_true", help="Run apt full-upgrade")

    # SSH
    group.add_argument("--ssh", action="store_true", help="Run apt install -y openssh-server")
    parser.add_argument("--ssh-port", type=int, help="SSH listening port")
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.all:
        full_setup()
        
    if args.update:
        print(f"\n{PINK}[STEP]{RESET} Running apt update...\n")
        update_system()
        
    if args.upgrade:
        print(f"\n{PINK}[STEP]{RESET} Running apt upgrade...\n")
        upgrade_system()

    if args.full_upgrade:
        print(f"\n{PINK}[STEP]{RESET} Running apt full-upgrade...\n")
        full_upgrade_system()


    if args.ssh_port and not args.ssh:
        print("[ERROR] --ssh-port requires --ssh")
        return
    if args.ssh:
        print(f"\n{PINK}[STEP]{RESET} Installing OpenSSH Server...\n")
        install_ssh()

        print(f"\n{PINK}[STEP]{RESET} Enabling SSH service...\n")
        enable_ssh()

        if args.ssh_port:
            print(f"\n{PINK}[STEP]{RESET} Changing SSH port to {args.ssh_port}...\n")
            change_ssh_port(args.ssh_port)

            print(f"\n{PINK}[STEP]{RESET} Restarting SSH service...\n")
            restart_ssh()

        print(f"\n{PINK}[STEP]{RESET} Checking SSH status...\n")
        check_ssh_status()


if __name__ == "__main__":
    main()
