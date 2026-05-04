import subprocess

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

def run_command(command):
    print_execution(command)

    try:
        result = subprocess.run(
            command,
            check=True,
            text=True,
            capture_output=True
        )
        print_success(command)

    except subprocess.CalledProcessError as e:
        print_execution_failed(command)
        print(e.stderr)
        exit(1)


def print_execution(command):
    print(f"{BLUE}[INFO]{RESET} EXECUTING: {' '.join(command)}")

def print_success(command):
    print(f"{GREEN}[SUCCESS]{RESET} {' '.join(command)}")

def print_execution_failed(command):
    print(f"{RED}[ERROR]{RESET} {' '.join(command)}")
