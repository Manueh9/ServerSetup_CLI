from utils import run_command, ok, warn, error, info, success, step
import subprocess
import os

JAIL_LOCAL_FILE = "/etc/fail2ban/jail.local"

def is_fail2ban_installed() -> bool:
    result = subprocess.run(["which", "fail2ban-client"], capture_output=True, text=True)
    return result.returncode == 0

def install_fail2ban():
    if is_fail2ban_installed():
        ok("fail2ban is already installed")
        return
    run_command(["apt", "install", "-y", "fail2ban"])

def is_fail2ban_active() -> bool:
    result = subprocess.run(
        ["systemctl", "is-active", "--quiet", "fail2ban"],
        capture_output=True, text=True
    )
    return result.returncode == 0

def enable_fail2ban():
    if is_fail2ban_active():
        ok("fail2ban is already active")
        return
    run_command(["systemctl", "enable", "fail2ban"])
    run_command(["systemctl", "start", "fail2ban"])

def disable_fail2ban():
    if not is_fail2ban_active():
        ok("fail2ban is already inactive")
        return
    run_command(["systemctl", "stop", "fail2ban"])
    run_command(["systemctl", "disable", "fail2ban"])

def configure_ssh_jail(max_retry: int = 5, ban_time: str = "10m", find_time: str = "10m"):
    """
    Creates/updates jail.local with SSH protection.
    max_retry: failed attempts before ban
    ban_time:  how long the IP stays banned (e.g. '10m', '1h', '-1' = permanent)
    find_time: window of time in which max_retry attempts are counted
    """
    step("Configuring SSH jail...")

    config = f"""[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = {max_retry}
bantime = {ban_time}
findtime = {find_time}
"""

    with open(JAIL_LOCAL_FILE, "w", encoding="utf-8") as f:
        f.write(config)

    success(f"SSH jail configured: maxretry={max_retry}, bantime={ban_time}, findtime={find_time}")

def restart_fail2ban():
    run_command(["systemctl", "restart", "fail2ban"])
    ok("fail2ban restarted")

def show_status(jail: str = None):
    """
    Shows global status, or a specific jail's status if given.
    """
    cmd = ["fail2ban-client", "status"]
    if jail:
        cmd.append(jail)

    result = subprocess.run(cmd, capture_output=True, text=True)
    print()
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        warn(f"Could not get status: {result.stderr.strip()}")
    print()
