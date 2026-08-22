from utils import run_command

def update_system():
    run_command(["apt", "update"])

    
def upgrade_system():
    run_command(["apt", "upgrade", "-y"])


def full_upgrade_system():
    run_command(["apt", "full-upgrade", "-y"])

