import subprocess
import shlex
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

# ── Message helpers (Rich-powered) ────────────────────────────────

def ok(msg):
    console.print(f"[green]✔[/green] {msg}")

def info(msg):
    console.print(f"[cyan]ℹ[/cyan] {msg}")

def warn(msg):
    console.print(f"[yellow]⚠[/yellow] {msg}")

def error(msg):
    console.print(f"[red]✘[/red] {msg}")

def success(msg):
    console.print(f"[bold green]✔[/bold green] {msg}")

def step(msg):
    console.print(f"\n[bold magenta]▸[/bold magenta] {msg}\n")

# ── Structural helpers ────────────────────────────────────────────

def banner(title: str, subtitle: str = None):
    """Renders the main CLI banner."""
    text = f"[bold cyan]{title}[/bold cyan]"
    if subtitle:
        text += f"\n[dim]{subtitle}[/dim]"
    console.print(Panel(text, border_style="cyan", box=box.DOUBLE, expand=False))

def phase_header(number: int, total: int, title: str):
    """Renders a phase header for the --all flow."""
    console.print(Panel(
        f"[bold white]{title}[/bold white]",
        title=f"[cyan]PHASE {number}/{total}[/cyan]",
        border_style="magenta",
        box=box.ROUNDED,
        expand=False,
    ))

def make_table(title: str, columns: list[str]) -> Table:
    """Creates a Rich table with the given title and column headers."""
    table = Table(title=title, box=box.ROUNDED, header_style="bold cyan", title_style="bold")
    for col in columns:
        table.add_column(col)
    return table

# ── User detection (behind sudo) ──────────────────────────────────

def is_running_as_root() -> bool:
    return os.geteuid() == 0

def get_real_user() -> tuple[str, str]:
    """
    Returns (username, home) of the real user behind sudo.
    If not running as sudo, returns the current user.
    """
    username = os.environ.get("SUDO_USER") or os.environ.get("USER")
    home     = os.path.expanduser(f"~{username}")
    return username, home

def warn_if_root_for_user_config(scope: str, text) -> bool:
    """
    Warns if running as root with --global scope.
    Returns True if execution should continue, False if it should stop.
    """
    if not is_running_as_root() or scope != "--global":
        return True

    warn("You are running as root (sudo).")
    console.print(f"          [dim]{text} will be applied to root's config,[/dim]")
    console.print("          [dim]NOT to your regular user.[/dim]")
    console.print("          [dim]Run without sudo, or use system scope to apply to all users.[/dim]\n")

    while True:
        choice = console.input("  Continue anyway? [bold]\\[y/n][/bold]: ").strip().lower()
        if choice == "y":
            return True
        elif choice == "n":
            info("Aborted. Run without sudo to configure your user.")
            return False
        else:
            error("Please enter y or n")

# ── System command runner ─────────────────────────────────────────

def run_command(command, requires_sudo=False):
    """
    Execute a system command.

    Args:
        command: Command and arguments as a list.
        requires_sudo: If True, execute with sudo when not already running as root.
    """
    if requires_sudo and not is_running_as_root():
        command = ["sudo"] + command

    cmd_str = " ".join(command)

    try:
        with console.status(f"[dim]{cmd_str}[/dim]", spinner="dots"):
            result = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True
            )

        console.print(f"[bold green]✔[/bold green] {cmd_str}")
        return result

    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]✘[/bold red] {cmd_str}")

        if e.stderr:
            console.print(f"[dim red]{e.stderr.strip()}[/dim red]")

        raise SystemExit(1)

# ── Presentation helpers ──────────────────────────────────────────

from rich.progress_bar import ProgressBar

def status_table(title: str, rows: list[tuple], columns: list[str] = None):
    """
    Renders a key-value style table for status output.
    rows: list of tuples, e.g. [("Total", "2.0 GiB"), ("Used", "0 B")]
    columns: optional custom headers, defaults to ["Property", "Value"]
    """
    cols = columns or ["Property", "Value"]
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan",
                  header_style="bold cyan", show_header=True)
    table.add_column(cols[0], style="dim")
    for c in cols[1:]:
        table.add_column(c)
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print()
    console.print(table)
    console.print()

def data_table(title: str, columns: list[str], rows: list[list]):
    """
    Renders a multi-column table for lists (users, cron tasks, ports...).
    """
    table = Table(title=title, box=box.ROUNDED, title_style="bold cyan",
                  header_style="bold cyan")
    for c in columns:
        table.add_column(c)
    if not rows:
        console.print()
        info(f"No entries for: {title}")
        console.print()
        return
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    console.print()
    console.print(table)
    console.print()

def _parse_size_to_bytes(size_str: str) -> float:
    """
    Converts a human-readable size (e.g. '2.0Gi', '512M', '0B') to bytes.
    Used to compute usage percentages for bars.
    """
    import re
    s = size_str.strip().upper().replace("I", "")  # 'Gi' -> 'G'
    match = re.match(r"^([\d.]+)\s*([KMGT]?)B?$", s)
    if not match:
        return 0.0
    value = float(match.group(1))
    unit = match.group(2)
    multipliers = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    return value * multipliers.get(unit, 1)

def usage_bar(label: str, used: str, total: str, width: int = 30):
    """
    Renders a visual usage bar with percentage.
    used/total are human-readable strings (e.g. '0.8Gi', '2.0Gi').
    """
    used_b = _parse_size_to_bytes(used)
    total_b = _parse_size_to_bytes(total)
    pct = (used_b / total_b * 100) if total_b > 0 else 0

    # Color by usage level
    if pct >= 90:
        color = "red"
    elif pct >= 70:
        color = "yellow"
    else:
        color = "green"

    filled = int((pct / 100) * width)
    bar = f"[{color}]{'█' * filled}[/{color}][dim]{'░' * (width - filled)}[/dim]"

    console.print(
        f"  [bold]{label:<8}[/bold] {bar} "
        f"[{color}]{pct:.0f}%[/{color}] "
        f"[dim]· {used} / {total}[/dim]"
    )
