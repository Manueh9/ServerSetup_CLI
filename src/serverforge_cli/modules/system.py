from serverforge_cli.utils import run_command

def update_system():
    run_command(["apt", "update"], requires_sudo=True)

    
def upgrade_system():
    run_command(["apt", "upgrade", "-y"], requires_sudo=True)


def full_upgrade_system():
    run_command(["apt", "full-upgrade", "-y"], requires_sudo=True)