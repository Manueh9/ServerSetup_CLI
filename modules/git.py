from utils import run_command, GREEN, RESET, YELLOW, RED, CYAN, ok, warn, error, info, success, get_real_user
import subprocess
import os

# ── Checks ────────────────────────────────────────────────────────

def is_git_installed() -> bool:
    result = subprocess.run(["which", "git"], capture_output=True, text=True)
    return result.returncode == 0

# ── Install ───────────────────────────────────────────────────────

def install_git():
    if is_git_installed():
        ok("Git is already installed")
        return
    run_command(["apt", "install", "-y", "git"])

# ── User config ───────────────────────────────────────────────────

def configure_git(username: str, email: str, scope: str = "--global"):
    run_command(["git", "config", scope, "user.name",  username])
    run_command(["git", "config", scope, "user.email", email])

def set_editor(editor: str, scope: str = "--global"):
    run_command(["git", "config", scope, "core.editor", editor])

def set_default_branch(branch: str = "main", scope: str = "--global"):
    run_command(["git", "config", scope, "init.defaultBranch", branch])

def set_pull_strategy(strategy: str, scope: str = "--global"):
    if strategy == "rebase":
        run_command(["git", "config", scope, "pull.rebase", "true"])
    elif strategy == "ff-only":
        run_command(["git", "config", scope, "pull.ff", "only"])
    else:
        # merge — default
        run_command(["git", "config", scope, "pull.rebase", "false"])

# ── SSH ───────────────────────────────────────────────────────────

def generate_ssh_key(email: str, key_type: str = "ed25519"):
    key_path = os.path.expanduser(f"~/.ssh/id_{key_type}")

    if os.path.exists(key_path):
        warn(f"SSH key already exists at {key_path} — skipping")
        return

    os.makedirs(os.path.expanduser("~/.ssh"), mode=0o700, exist_ok=True)

    run_command([
        "ssh-keygen", "-t", key_type,
        "-C", email,
        "-f", key_path,
        "-N", ""          # sin passphrase
    ])

    pub_key_path = f"{key_path}.pub"
    if os.path.exists(pub_key_path):
        with open(pub_key_path) as f:
            pub_key = f.read().strip()

        ok(f"SSH key generated: {key_path}")
        print(f"\n{CYAN}  Add this key to GitHub → Settings → SSH Keys:{RESET}")
        print(f"\n  {pub_key}\n")
    else:
        error("Key generation failed — .pub file not found")

# ── Show config ───────────────────────────────────────────────────

def show_config(scope: str = "--global"):
    result = subprocess.run(
        ["git", "config", scope, "--list"],
        capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        print()
        for line in result.stdout.strip().splitlines():
            key, _, value = line.partition("=")
            print(f"  {CYAN}{key}{RESET} = {value}")
        print()
    else:
        warn(f"No git config found for scope '{scope.lstrip('-')}'")

# ── Prompt ───────────────────────────────────────────────────────

def prompt_credentials() -> tuple[str, str]:
    while True:
        username = input("  Git username: ").strip()
        email    = input("  Git email:    ").strip()

        if not username:
            error("Username cannot be empty")
            continue
        if "@" not in email or "." not in email.split("@")[-1]:
            error("Invalid email format")
            continue

        return username, email


def configure_git_as_real_user(username: str, email: str):
    """
    Runs git config as the real user, not root.
    Uses sudo -u to switch to the real user.
    """
    real_user, _ = get_real_user()

    run_command(["sudo", "-u", real_user, "git", "config", "--global", "user.name",  username])
    run_command(["sudo", "-u", real_user, "git", "config", "--global", "user.email", email])
    run_command(["sudo", "-u", real_user, "git", "config", "--global", "init.defaultBranch", "main"])
