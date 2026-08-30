from serverforge_cli.utils import run_command, ok, warn, error, info, success, step
import subprocess
import os
import re

def is_valid_username(username: str) -> bool:
    """
    Linux username rules: lowercase letters, digits, underscore, hyphen.
    Must start with a letter or underscore. Max 32 chars.
    """
    if not username or len(username) > 32:
        return False
    pattern = r"^[a-z_][a-z0-9_-]*$"
    return bool(re.match(pattern, username))

def user_exists(username: str) -> bool:
    result = subprocess.run(["id", username], capture_output=True, text=True)
    return result.returncode == 0

def create_user(username: str) -> bool:
    if not is_valid_username(username):
        error(f"Invalid username: '{username}'")
        warn("Usernames must be lowercase, start with a letter/underscore, and contain only letters, digits, - or _")
        return False

    if user_exists(username):
        ok(f"User '{username}' already exists")
        return True

    step(f"Creating user '{username}'...")
    run_command(["adduser", "--disabled-password", "--gecos", "", username])

    if user_exists(username):
        success(f"User '{username}' created")
        return True
    else:
        error(f"Failed to create user '{username}'")
        return False

def set_user_password(username: str, password: str):
    """Sets a password non-interactively via chpasswd."""
    step(f"Setting password for '{username}'...")
    proc = subprocess.run(
        ["chpasswd"],
        input=f"{username}:{password}",
        capture_output=True, text=True
    )
    if proc.returncode == 0:
        success(f"Password set for '{username}'")
    else:
        error(f"Failed to set password: {proc.stderr.strip()}")

def add_to_group(username: str, group: str):
    if not user_exists(username):
        error(f"User '{username}' does not exist")
        return False

    run_command(["usermod", "-aG", group, username])
    success(f"User '{username}' added to group '{group}'")
    return True

def grant_sudo(username: str):
    return add_to_group(username, "sudo")

def revoke_sudo(username: str):
    if not user_exists(username):
        error(f"User '{username}' does not exist")
        return False

    run_command(["deluser", username, "sudo"])
    success(f"Sudo access revoked for '{username}'")
    return True

def delete_user(username: str, remove_home: bool = True):
    if not user_exists(username):
        warn(f"User '{username}' does not exist — nothing to delete")
        return False

    cmd = ["deluser"]
    if remove_home:
        cmd.append("--remove-home")
    cmd.append(username)

    run_command(cmd)
    success(f"User '{username}' deleted" + (" (home removed)" if remove_home else ""))
    return True

def setup_ssh_key(username: str, public_key: str, home_dir: str = None) -> bool:
    """
    Adds a public key to the user's authorized_keys.
    home_dir: optional override for testing — defaults to /home/{username}.
    """
    if not user_exists(username):
        error(f"User '{username}' does not exist")
        return False

    home = home_dir or f"/home/{username}"
    ssh_dir = f"{home}/.ssh"
    auth_keys = f"{ssh_dir}/authorized_keys"

    try:
        os.makedirs(ssh_dir, mode=0o700, exist_ok=True)

        with open(auth_keys, "a") as f:
            f.write(public_key.strip() + "\n")

        os.chmod(auth_keys, 0o600)

        run_command(["chown", "-R", f"{username}:{username}", ssh_dir])

        success(f"SSH key added for '{username}'")
        return True
    except Exception as e:
        error(f"Failed to setup SSH key: {e}")
        return False

def list_users(min_uid: int = 1000, passwd_file: str = "/etc/passwd") -> list[dict]:
    """
    Lists regular (non-system) users, i.e. UID >= min_uid.
    passwd_file: optional override for testing.
    """
    users = []
    with open(passwd_file, "r") as f:
        for line in f:
            parts = line.strip().split(":")
            if len(parts) < 7:
                continue
            username, _, uid, gid, _, home, shell = parts[:7]
            if int(uid) >= min_uid and shell not in ("/usr/sbin/nologin", "/bin/false"):
                users.append({"username": username, "uid": uid, "home": home, "shell": shell})
    return users

def show_user_info(username: str):
    if not user_exists(username):
        error(f"User '{username}' does not exist")
        return

    result = subprocess.run(["id", username], capture_output=True, text=True)
    print()
    print(result.stdout.strip())
    print()

def prompt_new_user():
    """
    Asks if the user wants to create a new user during --all.
    Returns (username, password, grant_sudo) or None if declined.
    """
    print()
    while True:
        choice = input("  Do you want to create a new user? [y/n]: ").strip().lower()
        if choice == "n":
            return None
        elif choice == "y":
            break
        else:
            error("Please enter y or n")

    while True:
        username = input("  Username: ").strip()
        if is_valid_username(username):
            break
        error("Invalid username (lowercase letters, digits, - or _, starting with a letter)")

    import getpass
    while True:
        password = getpass.getpass("  Password: ")
        password_confirm = getpass.getpass("  Confirm password: ")
        if password != password_confirm:
            error("Passwords do not match")
            continue
        if len(password) < 8:
            warn("Password is shorter than 8 characters")
        break

    while True:
        sudo_choice = input("  Grant sudo access? [y/n]: ").strip().lower()
        if sudo_choice in ("y", "n"):
            break
        error("Please enter y or n")

    return username, password, sudo_choice == "y"
