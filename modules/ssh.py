from utils import run_command
import subprocess
import re

SSH_CONFIG_FILE = "/etc/ssh/sshd_config"

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
PINK   = "\033[95m"
RESET  = "\033[0m"

def ok(msg):      print(f"{GREEN}[OK]{RESET} {msg}")
def info(msg):    print(f"{CYAN}[INFO]{RESET} {msg}")
def warn(msg):    print(f"{YELLOW}[WARNING]{RESET} {msg}")
def error(msg):   print(f"{RED}[ERROR]{RESET} {msg}")
def success(msg): print(f"{GREEN}[SUCCESS]{RESET} {msg}")


def install_ssh():
    run_command(["apt", "install", "-y", "openssh-server"])

def enable_ssh():
    run_command(["systemctl", "enable", "ssh"])
    run_command(["systemctl", "start", "ssh"])

def change_ssh_port(port: int):
    if port < 1 or port > 65535:
        error("Invalid port (range: 1-65535)")
        exit(1)

    if port < 1024 and port != 22:
        warn(f"Port {port} is a privileged port (<1024)")

    try:
        with open(SSH_CONFIG_FILE, "r") as f:
            config = f.readlines()

        updated = []
        port_set = False

        for line in config:
            stripped = line.strip()
            if re.match(r"^#?\s*Port\s+\d+", stripped):
                if not port_set:
                    updated.append(f"Port {port}\n")
                    port_set = True
                    info(f"Original line: {line.rstrip()!r} → replaced")
            else:
                updated.append(line)

        if not port_set:
            updated.append(f"\nPort {port}\n")
            info("No Port line found — appended at the end")

        with open(SSH_CONFIG_FILE, "w") as f:
            f.writelines(updated)

        success(f"SSH port changed to {port} in {SSH_CONFIG_FILE}")
        _verify_config_port(port)

    except PermissionError:
        error(f"Permission denied: cannot edit {SSH_CONFIG_FILE}. Run with sudo.")
        exit(1)
    except Exception as e:
        error(str(e))
        exit(1)

def _verify_config_port(expected_port: int):
    with open(SSH_CONFIG_FILE, "r") as f:
        for line in f:
            if re.match(r"^\s*Port\s+\d+", line):
                actual = int(line.split()[1])
                if actual == expected_port:
                    ok(f"Verified: Port {actual} in sshd_config")
                else:
                    warn(f"Config file has Port {actual}, expected {expected_port}")
                return
    warn("No active 'Port' line found in config")

def restart_ssh():
    run_command(["systemctl", "stop", "ssh.socket"])
    run_command(["systemctl", "stop", "ssh"])
    run_command(["systemctl", "daemon-reload"])
    run_command(["systemctl", "start", "ssh.socket"])
    run_command(["systemctl", "start", "ssh"])
    ok("SSH service and socket restarted")

def check_ssh_status():
    result = subprocess.run(
        ["systemctl", "is-active", "ssh"],
        capture_output=True, text=True
    )
    status = result.stdout.strip()
    if status == "active":
        ok(f"SSH service: {status}")
    else:
        warn(f"SSH service: {status}")

    result2 = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
    ssh_lines = [l for l in result2.stdout.splitlines()
                 if "sshd" in l or ":22" in l or "ssh" in l.lower()]

    if ssh_lines:
        info("Active SSH ports:")
        for line in ssh_lines:
            print(f"  {line}")
    else:
        warn("No SSH ports detected")
