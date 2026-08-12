from utils import run_command, ok, warn, error, info, success, step
import subprocess
import re

HOSTS_FILE = "/etc/hosts"

def prompt_hostname_change() -> str | None:
    """
    Shows current hostname and asks if user wants to change it.
    Returns the new hostname if confirmed, None otherwise.
    """
    current = get_current_hostname()

    print()
    info(f"Current hostname: {current}")

    while True:
        choice = input("  Do you want to change it? [y/n]: ").strip().lower()
        if choice == "n":
            return None
        elif choice == "y":
            break
        else:
            error("Please enter y or n")

    while True:
        new_hostname = input("  Enter new hostname: ").strip()
        if is_valid_hostname(new_hostname):
            return new_hostname
        error("Invalid hostname (letters, digits, hyphens only — not at start/end)")

def get_current_hostname() -> str:
    result = subprocess.run(["hostname"], capture_output=True, text=True)
    return result.stdout.strip()

def is_valid_hostname(hostname: str) -> bool:
    """
    Valid hostname: letters, digits, hyphens. 1-63 chars per label.
    Cannot start/end with hyphen.
    """
    if not hostname or len(hostname) > 253:
        return False
    pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$"
    return bool(re.match(pattern, hostname))

def set_hostname(new_hostname: str) -> bool:
    if not is_valid_hostname(new_hostname):
        error(f"Invalid hostname: '{new_hostname}'")
        warn("Hostnames can only contain letters, digits and hyphens (not at start/end)")
        return False

    current = get_current_hostname()
    if current == new_hostname:
        ok(f"Hostname is already set to {new_hostname}")
        return True

    step(f"Changing hostname: {current} → {new_hostname}...")

    # 1. Set via hostnamectl (updates /etc/hostname too)
    run_command(["hostnamectl", "set-hostname", new_hostname])

    # 2. Update /etc/hosts so 127.0.1.1 maps to the new name
    _update_hosts_file(current, new_hostname)

    # 3. Verify
    new_current = get_current_hostname()
    if new_current == new_hostname:
        success(f"Hostname changed to {new_hostname}")
        info("Some services or your shell prompt may need a reconnect to reflect the change")
        return True
    else:
        error(f"Hostname change failed — current: {new_current}")
        return False

def _update_hosts_file(old_hostname: str, new_hostname: str):
    """
    Updates the 127.0.1.1 line in /etc/hosts to match the new hostname.
    This prevents 'sudo: unable to resolve host' warnings.
    """
    try:
        with open(HOSTS_FILE, "r") as f:
            lines = f.readlines()

        updated = []
        found = False

        for line in lines:
            if line.strip().startswith("127.0.1.1"):
                updated.append(f"127.0.1.1\t{new_hostname}\n")
                found = True
            else:
                updated.append(line)

        if not found:
            updated.append(f"127.0.1.1\t{new_hostname}\n")

        with open(HOSTS_FILE, "w") as f:
            f.writelines(updated)

    except PermissionError:
        error(f"Permission denied editing {HOSTS_FILE}. Run with sudo.")
    except Exception as e:
        error(f"Failed to update {HOSTS_FILE}: {e}")

def show_hostname_info():
    result = subprocess.run(["hostnamectl"], capture_output=True, text=True)
    print()
    print(result.stdout.strip())
    print()
