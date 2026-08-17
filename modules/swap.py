from utils import run_command, ok, warn, error, info, success, step
import subprocess
import re
import os

SWAP_FILE = "/swapfile"
FSTAB_FILE = "/etc/fstab"

def get_swap_info() -> dict:
    """Returns current swap size and usage from /proc/meminfo."""
    result = subprocess.run(["free", "-h"], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if line.startswith("Swap:"):
            parts = line.split()
            return {"total": parts[1], "used": parts[2], "free": parts[3]}
    return {"total": "0", "used": "0", "free": "0"}

def has_swap() -> bool:
    """Checks if any swap is currently active (file or partition)."""
    result = subprocess.run(["swapon", "--show"], capture_output=True, text=True)
    return bool(result.stdout.strip())

def is_valid_size(size: str) -> bool:
    """
    Validates size format used by fallocate: number + unit (K, M, G, T).
    Examples: '512M', '2G', '1024K'
    """
    return bool(re.match(r"^\d+[KMGT]$", size.upper()))

def _swapfile_exists() -> bool:
    return os.path.exists(SWAP_FILE)

def create_swap(size: str = "2G") -> bool:
    """
    Creates a swap file of the given size, activates it, and makes it
    persistent across reboots via /etc/fstab.
    """
    if not is_valid_size(size):
        error(f"Invalid size format: '{size}'. Use e.g. '512M', '2G', '1024K'")
        return False

    if has_swap():
        ok("Swap is already active")
        show_swap_status()
        return True

    if _swapfile_exists():
        warn(f"{SWAP_FILE} already exists but is not active — activating it")
        return _activate_existing_swapfile()

    step(f"Creating swap file of {size}...")

    # fallocate is faster than dd, works on most modern filesystems
    result = run_command(["fallocate", "-l", size, SWAP_FILE])

    run_command(["chmod", "600", SWAP_FILE])
    run_command(["mkswap", SWAP_FILE])
    run_command(["swapon", SWAP_FILE])

    _add_to_fstab()

    if has_swap():
        success(f"Swap file created and activated ({size})")
        show_swap_status()
        return True
    else:
        error("Swap file created but activation failed")
        return False

def _activate_existing_swapfile() -> bool:
    run_command(["swapon", SWAP_FILE])
    _add_to_fstab()
    return has_swap()

def _add_to_fstab():
    """Adds the swapfile entry to /etc/fstab if not already present, so it persists on reboot."""
    entry = f"{SWAP_FILE} none swap sw 0 0\n"

    try:
        with open(FSTAB_FILE, "r") as f:
            content = f.read()

        if SWAP_FILE in content:
            return  # already there

        with open(FSTAB_FILE, "a") as f:
            f.write(entry)

        info("Swap entry added to /etc/fstab (persists across reboots)")
    except PermissionError:
        error(f"Permission denied editing {FSTAB_FILE}. Run with sudo.")
    except Exception as e:
        error(f"Failed to update {FSTAB_FILE}: {e}")

def disable_swap() -> bool:
    if not has_swap():
        ok("No active swap to disable")
        return True

    step("Disabling swap...")
    run_command(["swapoff", SWAP_FILE])

    if not has_swap():
        success("Swap disabled")
        return True
    else:
        error("Failed to disable swap")
        return False

def remove_swap() -> bool:
    """Disables swap, removes the file, and cleans up /etc/fstab."""
    disable_swap()

    if _swapfile_exists():
        run_command(["rm", SWAP_FILE])
        success(f"Removed {SWAP_FILE}")

    _remove_from_fstab()
    return True

def _remove_from_fstab():
    try:
        with open(FSTAB_FILE, "r") as f:
            lines = f.readlines()

        updated = [line for line in lines if SWAP_FILE not in line]

        with open(FSTAB_FILE, "w") as f:
            f.writelines(updated)
    except PermissionError:
        error(f"Permission denied editing {FSTAB_FILE}. Run with sudo.")
    except Exception as e:
        error(f"Failed to update {FSTAB_FILE}: {e}")

def set_swappiness(value: int) -> bool:
    """
    Sets vm.swappiness (0-100). Lower = less aggressive swapping.
    Common values: 10 (servers/databases), 60 (default), 100 (aggressive).
    """
    if value < 0 or value > 100:
        error("Swappiness must be between 0 and 100")
        return False

    run_command(["sysctl", f"vm.swappiness={value}"])

    # Persist across reboots
    sysctl_conf = "/etc/sysctl.conf"
    try:
        with open(sysctl_conf, "r") as f:
            content = f.read()

        if "vm.swappiness" in content:
            lines = content.splitlines()
            updated = [
                f"vm.swappiness={value}" if line.strip().startswith("vm.swappiness") else line
                for line in lines
            ]
            content = "\n".join(updated) + "\n"
        else:
            content += f"\nvm.swappiness={value}\n"

        with open(sysctl_conf, "w") as f:
            f.write(content)

        success(f"Swappiness set to {value}")
        return True
    except PermissionError:
        error(f"Permission denied editing {sysctl_conf}. Run with sudo.")
        return False

def show_swap_status():
    info_dict = get_swap_info()
    print()
    info(f"Swap total : {info_dict['total']}")
    info(f"Swap used  : {info_dict['used']}")
    info(f"Swap free  : {info_dict['free']}")
    print()

def prompt_swap_setup() -> str | None:
    """
    Asks if the user wants to create swap during --all.
    Returns the size string if confirmed, None if declined.
    """
    print()
    info("No active swap detected")

    while True:
        choice = input("  Do you want to create a swap file? [y/n]: ").strip().lower()
        if choice == "n":
            return None
        elif choice == "y":
            break
        else:
            error("Please enter y or n")

    while True:
        size = input("  Swap size (e.g. 1G, 2G, 512M) [default: 2G]: ").strip()
        if not size:
            return "2G"
        if is_valid_size(size):
            return size.upper()
        error("Invalid format. Use e.g. '512M', '2G', '1024K'")
