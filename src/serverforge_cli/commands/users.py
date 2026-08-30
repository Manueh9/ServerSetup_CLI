from serverforge_cli.modules.users import (
    create_user, set_user_password, grant_sudo, revoke_sudo,
    delete_user, setup_ssh_key, list_users, show_user_info,
    prompt_new_user,
)
from serverforge_cli.utils import step, data_table, error

def register_args(parser):
    group = parser.add_argument_group("Users")

    group.add_argument("--create-user",   type=str, metavar="USERNAME", help="Create a new user")
    group.add_argument("--user-password", type=str, metavar="PASSWORD", help="Set password for --create-user")
    group.add_argument("--grant-sudo",    type=str, metavar="USERNAME", help="Grant sudo access to a user")
    group.add_argument("--revoke-sudo",   type=str, metavar="USERNAME", help="Revoke sudo access from a user")
    group.add_argument("--delete-user",   type=str, metavar="USERNAME", help="Delete a user")
    group.add_argument("--keep-home",     action="store_true", help="Keep home directory when deleting (--delete-user)")

    group.add_argument("--add-ssh-key",   type=str, metavar="USERNAME", help="Add an SSH public key to a user")
    group.add_argument("--ssh-key",       type=str, metavar="PUBKEY", help="Public key content for --add-ssh-key")

    group.add_argument("--list-users",    action="store_true", help="List regular (non-system) users")
    group.add_argument("--user-info",     type=str, metavar="USERNAME", help="Show info for a user")

def handle(args):
    if args.create_user:
        step(f"Creating user '{args.create_user}'...")
        if create_user(args.create_user) and args.user_password:
            set_user_password(args.create_user, args.user_password)

    if args.grant_sudo:
        step(f"Granting sudo to '{args.grant_sudo}'...")
        grant_sudo(args.grant_sudo)

    if args.revoke_sudo:
        step(f"Revoking sudo from '{args.revoke_sudo}'...")
        revoke_sudo(args.revoke_sudo)

    if args.delete_user:
        step(f"Deleting user '{args.delete_user}'...")
        delete_user(args.delete_user, remove_home=not args.keep_home)

    if args.add_ssh_key:
        if not args.ssh_key:
            error("--add-ssh-key requires --ssh-key")
            return
        step(f"Adding SSH key for '{args.add_ssh_key}'...")
        setup_ssh_key(args.add_ssh_key, args.ssh_key)

    if args.list_users:
        users = list_users()
        rows = [[u["username"], u["uid"], u["home"], u["shell"]] for u in users]
        data_table("Regular Users", ["Username", "UID", "Home", "Shell"], rows)

    if args.user_info:
        step(f"User info: {args.user_info}")
        show_user_info(args.user_info)

def run_all():
    """
    Called by --all. Asks if the user wants to create a new user
    with sudo access. Skips if declined.
    """
    step("User configuration...")
    result = prompt_new_user()

    if result:
        username, password, sudo = result
        if create_user(username):
            if password:
                set_user_password(username, password)
            if sudo:
                grant_sudo(username)
