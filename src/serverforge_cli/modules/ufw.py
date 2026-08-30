from serverforge_cli.utils import run_command, ok, warn, error, info, success, step, status_table, data_table
import subprocess
import re

def is_ufw_installed() -> bool:
    result = subprocess.run(["which", "ufw"], capture_output=True, text=True)
    return result.returncode == 0

def install_ufw():
    if is_ufw_installed():
        ok("UFW is already installed")
        return
    run_command(["apt", "install", "-y", "ufw"])

def is_ufw_active() -> bool:
    result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
    return "Status: active" in result.stdout

def enable_ufw():
    if is_ufw_active():
        ok("UFW is already active")
        return
    # --force evita el prompt interactivo de confirmación
    run_command(["ufw", "--force", "enable"])

def disable_ufw():
    if not is_ufw_active():
        ok("UFW is already inactive")
        return
    run_command(["ufw", "disable"])

def allow_port(port: int, protocol: str = None):
    """
    Opens a port. protocol can be 'tcp', 'udp', or None (both).
    """
    if port < 1 or port > 65535:
        error("Invalid port (range: 1-65535)")
        return False

    rule = f"{port}/{protocol}" if protocol else str(port)
    run_command(["ufw", "allow", rule])
    success(f"Port {rule} allowed")
    return True

def deny_port(port: int, protocol: str = None):
    if port < 1 or port > 65535:
        error("Invalid port (range: 1-65535)")
        return False

    rule = f"{port}/{protocol}" if protocol else str(port)
    run_command(["ufw", "deny", rule])
    success(f"Port {rule} denied")
    return True

def delete_rule(port: int, protocol: str = None):
    rule = f"{port}/{protocol}" if protocol else str(port)
    run_command(["ufw", "delete", "allow", rule])
    success(f"Rule for {rule} deleted")

def show_status(verbose: bool = False):
    cmd = ["ufw", "status"]
    if verbose:
        cmd.append("verbose")
    result = subprocess.run(cmd, capture_output=True, text=True)
    lines = [l for l in result.stdout.strip().splitlines() if l.strip()]

    if not lines:
        status_table("UFW Status", [("State", "unknown")])
        return

    rows = []
    rule_lines = []
    in_rules = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("To") and "Action" in stripped and "From" in stripped:
            in_rules = True
            continue
        if stripped.startswith("--") and "------" in stripped:
            continue
        if in_rules:
            rule_lines.append(stripped)
        elif ":" in stripped:
            key, _, value = stripped.partition(":")
            rows.append((key.strip(), value.strip()))
        else:
            rows.append(("Info", stripped))

    status_table(f"UFW Status{' (Verbose)' if verbose else ''}", rows)

    if rule_lines:
        rule_rows = [re.split(r"\s{2,}", l) for l in rule_lines]
        data_table("Firewall Rules", ["To", "Action", "From"], rule_rows)
    else:
        info("No firewall rules configured")
