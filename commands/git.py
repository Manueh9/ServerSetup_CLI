from modules.git import (
    install_git, configure_git, prompt_credentials,
    set_editor, set_default_branch, set_pull_strategy,
    generate_ssh_key, show_config, configure_git_as_real_user
)
from utils import warn_if_root_for_user_config, step, info, RED, RESET, ok

def register_args(parser):
    group = parser.add_argument_group("Git")

    # Instalación
    group.add_argument("--install-git",  action="store_true", help="Install git")

    # Configuración de usuario
    group.add_argument("--git-config",   action="store_true", help="Configure git user.name and user.email")
    group.add_argument("--git-name",     type=str,            help="Git username")
    group.add_argument("--git-email",    type=str,            help="Git email")
    group.add_argument("--git-scope",    type=str,            default="global",
                       choices=["global", "system", "local"],
                       help="Config scope (default: global)")

    # Preferencias
    group.add_argument("--git-editor",   type=str,
                       choices=["nano", "vim", "vi", "code", "micro"],
                       help="Set default git editor")
    group.add_argument("--git-branch",   type=str,            metavar="BRANCH",
                       help="Set default branch name (e.g. main)")
    group.add_argument("--git-pull",     type=str,
                       choices=["merge", "rebase", "ff-only"],
                       help="Set pull strategy")

    # SSH
    group.add_argument("--git-ssh",      action="store_true", help="Generate SSH key for GitHub/GitLab")
    group.add_argument("--ssh-key-type", type=str,            default="ed25519",
                       choices=["ed25519", "rsa"],
                       help="SSH key type (default: ed25519)")

    # Info
    group.add_argument("--git-show",     action="store_true", help="Show current git config")

def handle(args):
    scope = f"--{args.git_scope}"

    # ── Instalar ──────────────────────────────────────
    if args.install_git:
        step("Installing Git...")
        install_git()

    # ── Mostrar config ────────────────────────────────
    if args.git_show:
        step(f"Git config ({args.git_scope}):")
        show_config(scope)
        return

    # ── Configurar usuario ────────────────────────────
    if args.git_config:
        step(f"Configuring Git ({args.git_scope})...")

        if not warn_if_root_for_user_config(scope, "--global config"):
            return

        if bool(args.git_name) != bool(args.git_email):
            print(f"{RED}[ERROR]{RESET} --git-name and --git-email must be used together")
            return

        name, email = args.git_name, args.git_email
        if not name and not email:
            name, email = prompt_credentials()

        configure_git(name, email, scope)

    # ── Editor ────────────────────────────────────────
    if args.git_editor:
        step(f"Setting editor: {args.git_editor}...")
        if not warn_if_root_for_user_config(scope, "core.editor"):
            return
        set_editor(args.git_editor, scope)

    # ── Rama por defecto ──────────────────────────────
    if args.git_branch:
        step(f"Setting default branch: {args.git_branch}...")
        set_default_branch(args.git_branch, scope)

    # ── Pull strategy ─────────────────────────────────
    if args.git_pull:
        step(f"Setting pull strategy: {args.git_pull}...")
        set_pull_strategy(args.git_pull, scope)

    # ── SSH ───────────────────────────────────────────
    if args.git_ssh:
        if not args.git_email:
            print(f"{RED}[ERROR]{RESET} --git-ssh requires --git-email")
            return
        step("Generating SSH key...")
        generate_ssh_key(args.git_email, args.ssh_key_type)

def run_all(name: str = None, email: str = None):
    install_git()

    if not name or not email:
        print()
        info("Git user configuration:")
        name, email = prompt_credentials()

    configure_git_as_real_user(name, email)
    ok(f"Git configured for user: {name} <{email}>")

