import os
from serverforge_cli.utils import ok, info, error, success, step, warn, get_real_user, console

PROMPT_BLOCK_START = "# === PROMPT CONFIGURED BY SERVERSETUP_CLI ==="
PROMPT_BLOCK_END   = "# ============================================="

def _get_bashrc_path() -> str | None:
    _, home = get_real_user()
    path = os.path.join(home, ".bashrc")
    if not os.path.exists(path):
        error(f".bashrc not found at {path}")
        return None
    return path

def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _write(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def _remove_block(content: str) -> str:
    lines     = content.splitlines(keepends=True)
    new_lines = []
    inside    = False
    for line in lines:
        if PROMPT_BLOCK_START in line:
            inside = True
            continue
        if PROMPT_BLOCK_END in line:
            inside = False
            continue
        if not inside:
            new_lines.append(line)
    return "".join(new_lines)

def _block_exists(content: str) -> bool:
    return PROMPT_BLOCK_START in content

def _reload_hint():
    console.print("   Run: [cyan]source ~/.bashrc[/cyan]")

# ── Read current state ────────────────────────────────────────────

def _get_current_state(content: str) -> dict:
    """Reads which features are currently active from the block."""
    return {
        "branch": "# FEATURE:branch" in content,
        "time":   "# FEATURE:time"   in content,
        "venv":   "# FEATURE:venv"   in content,
    }

# ── Build and write the single PS1 block ─────────────────────────

def _build_block(branch: bool, time: bool, venv: bool) -> str:
    """Builds a single PS1 block combining all active features."""

    parts = []

    functions = ""

    if branch:
        functions += """
parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \\(.*\\)/ (\\1)/'
}
parse_git_dirty() {
    git status --porcelain 2> /dev/null | grep -q . && echo " *"
}"""

    if venv:
        functions += """
show_venv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "($(basename $VIRTUAL_ENV)) "
    fi
}"""

    # Build PS1 parts in order: venv + time + user@host:path + branch + dirty
    color_ps1   = ""
    nocolor_ps1 = ""

    if venv:
        color_ps1   += "\\[\\033[00;35m\\]$(show_venv)\\[\\033[00m\\]"
        nocolor_ps1 += "$(show_venv)"

    if time:
        color_ps1   += "\\[\\033[00;37m\\][\\t]\\[\\033[00m\\] "
        nocolor_ps1 += "[\\t] "

    # user@host:path — always present
    color_ps1   += "\\[\\033[01;32m\\]\\u@\\h\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]"
    nocolor_ps1 += "\\u@\\h:\\w"

    if branch:
        color_ps1   += "\\[\\033[01;33m\\]$(parse_git_branch)\\[\\033[01;31m\\]$(parse_git_dirty)\\[\\033[00m\\]"
        nocolor_ps1 += "$(parse_git_branch)$(parse_git_dirty)"

    color_ps1   += "\\$ "
    nocolor_ps1 += "\\$ "

    # Feature flags (used to track state)
    flags = ""
    if branch: flags += "# FEATURE:branch\n"
    if time:   flags += "# FEATURE:time\n"
    if venv:   flags += "# FEATURE:venv\n"

    return f"""
{PROMPT_BLOCK_START}
{flags}{functions}
if [ "$color_prompt" = yes ]; then
    PS1='{color_ps1}'
else
    PS1='{nocolor_ps1}'
fi
{PROMPT_BLOCK_END}
"""

def _apply(branch: bool, time: bool, venv: bool):
    """Removes existing block and writes a new one with updated features."""
    path = _get_bashrc_path()
    if not path:
        return False

    content = _read(path)
    clean   = _remove_block(content)

    # If all features are off, just remove the block
    if not branch and not time and not venv:
        _write(path, clean.rstrip() + "\n")
        success("All prompt customizations removed")
        _reload_hint()
        return True

    block = _build_block(branch, time, venv)
    _write(path, clean.rstrip() + "\n" + block)
    return True

def _current_state() -> dict:
    path = _get_bashrc_path()
    if not path:
        return {"branch": False, "time": False, "venv": False}
    return _get_current_state(_read(path))

# ── Public API ────────────────────────────────────────────────────

def show_git_actual_branch():
    state = _current_state()
    if state["branch"]:
        ok("Git branch is already active in prompt")
        return
    step("Adding git branch to prompt...")
    _apply(branch=True, time=state["time"], venv=state["venv"])
    success("Git branch added to prompt")
    _reload_hint()

def remove_git_actual_branch():
    state = _current_state()
    if not state["branch"]:
        warn("Git branch is not active — nothing to remove")
        return
    step("Removing git branch from prompt...")
    _apply(branch=False, time=state["time"], venv=state["venv"])
    success("Git branch removed from prompt")
    _reload_hint()

def show_timestamp():
    state = _current_state()
    if state["time"]:
        ok("Timestamp is already active in prompt")
        return
    step("Adding timestamp to prompt...")
    _apply(branch=state["branch"], time=True, venv=state["venv"])
    success("Timestamp added to prompt")
    _reload_hint()

def remove_timestamp():
    state = _current_state()
    if not state["time"]:
        warn("Timestamp is not active — nothing to remove")
        return
    step("Removing timestamp from prompt...")
    _apply(branch=state["branch"], time=False, venv=state["venv"])
    success("Timestamp removed from prompt")
    _reload_hint()

def show_venv():
    state = _current_state()
    if state["venv"]:
        ok("Venv name is already active in prompt")
        return
    step("Adding venv name to prompt...")
    _apply(branch=state["branch"], time=state["time"], venv=True)
    success("Venv name added to prompt")
    _reload_hint()

def remove_venv():
    state = _current_state()
    if not state["venv"]:
        warn("Venv name is not active — nothing to remove")
        return
    step("Removing venv name from prompt...")
    _apply(branch=state["branch"], time=state["time"], venv=False)
    success("Venv name removed from prompt")
    _reload_hint()

def show_current_prompt():
    state = _current_state()
    print()
    info("Active prompt customizations:")
    print(f"  Git branch : {'✓' if state['branch'] else '✗'}")
    print(f"  Timestamp  : {'✓' if state['time']   else '✗'}")
    print(f"  Virtualenv : {'✓' if state['venv']   else '✗'}")
    print()
