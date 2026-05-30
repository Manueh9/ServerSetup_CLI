import subprocess
import os

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
PINK   = "\033[95m"
BLUE   = "\033[94m"
RESET  = "\033[0m"



def ok(msg):      print(f"{GREEN}[OK]{RESET} {msg}")
def info(msg):    print(f"{CYAN}[INFO]{RESET} {msg}")
def warn(msg):    print(f"{YELLOW}[WARNING]{RESET} {msg}")
def error(msg):   print(f"{RED}[ERROR]{RESET} {msg}")
def success(msg): print(f"{GREEN}[SUCCESS]{RESET} {msg}")
def step(msg):    print(f"\n{PINK}[STEP]{RESET} {msg}\n")




def is_running_as_root() -> bool:
    return os.geteuid() == 0

def get_real_user() -> tuple[str, str]:
    """
    Returns (username, home) of the real user behind sudo.
    If not running as sudo, returns the current user.
    """
    username = os.environ.get("SUDO_USER") or os.environ.get("USER")
    home     = os.path.expanduser(f"~{username}")
    return username, home

def warn_if_root_for_user_config(scope: str, text) -> bool:
    """
    Warns if running as root with --global scope.
    Returns True if execution should continue, False if it should stop.
    """
    if not is_running_as_root() or scope != "--global":
        return True

    print(f"{YELLOW}[WARNING]{RESET} You are running as root (sudo).")
    print(f"          {text} will be applied to root's ~/.gitconfig,")
    print(f"          NOT to your regular user.")
    print(f"          Run without sudo, or use --git-scope system to apply to all users.\n")

    while True:
        choice = input("  Continue anyway? [y/n]: ").strip().lower()
        if choice == "y":
            return True
        elif choice == "n":
            print(f"\n{CYAN}[INFO]{RESET} Aborted. Run without sudo to configure your user:\n")
            print(f"  python3 cli.py --git-config\n")
            return False
        else:
            print(f"{RED}[ERROR]{RESET} Please enter y or n")
            
def run_command(command):
    print_execution(command)

    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=True
        )
        print_success(command)

    except subprocess.CalledProcessError as e:
        print_execution_failed(command)
        print(e.stderr)
        exit(1)


def print_execution(command):
    print(f"{BLUE}[INFO]{RESET} EXECUTING: {' '.join(command)}")

def print_success(command):
    print(f"{GREEN}[SUCCESS]{RESET} {' '.join(command)}")

def print_execution_failed(command):
    print(f"{RED}[ERROR]{RESET} {' '.join(command)}")
