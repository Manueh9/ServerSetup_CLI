# ServerSetup CLI

![Tests](https://github.com/Manueh9/ServerSetup_CLI/actions/workflows/tests.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/serverforge-cli)](https://pypi.org/project/serverforge-cli/)
![Python](https://img.shields.io/badge/python-3.11%20|%203.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

[🇪🇸 Español](README.md) · 🇬🇧 English

A Python CLI to automate the initial configuration and hardening of Linux servers
(Ubuntu Server). It cuts the time to get a fresh server ready from hours to
minutes, with reproducible, validated configuration and no forgotten manual
steps.

## The problem it solves

Preparing a Linux server from scratch always means repeating the same steps:
updating the system, installing and securing SSH, configuring Git, creating
users with the right permissions, setting up a firewall, protecting against
brute-force attacks, adjusting the timezone... Doing this by hand is slow and
error-prone. ServerSetup CLI packages that whole process into clear commands
and an `--all` flow that leaves the server ready in a single run.

## Quick install

The package is published on PyPI as [`serverforge-cli`](https://pypi.org/project/serverforge-cli/)
(requires Python 3.11+).

**Linux / macOS**
```bash
python3 -m pip install --user serverforge-cli
```

**Windows** (PowerShell or CMD)
```powershell
python -m pip install --user serverforge-cli
```

Verify the install:
```bash
sforge --help
```

The repository also includes `install.sh` (Linux/macOS) and `install.bat`
(Windows), which run that same command.

> ⚠️ The package installs on any operating system, but the modules run
> Ubuntu/Debian-specific tools (`apt`, `ufw`, `systemctl`, `fail2ban`...).
> Installing it on Windows or macOS is only useful to explore the CLI or to
> manage a remote server over SSH: to actually apply the configuration you
> need to run `sforge` **on the target Linux server itself**.

## Full setup

```bash
sudo sforge --all
```

The `--all` flow runs phase by phase and is idempotent (it won't redo what's
already done). Phases with user-specific configuration (hostname, users, swap)
are interactive: they ask before acting and move on if you say no. Each phase
is shown in a numbered panel (`PHASE 1/10`, `PHASE 2/10`...) and is separated
from the next one by a divider line, so you can follow the progress at a
glance.

## Interface

All output is built with [Rich](https://github.com/Textualize/rich):

- **Command execution**: while a system command is running, an animated
  spinner shows the dimmed command; once it finishes, that line is replaced
  in place with a green `✔` or a red `✘` (with `stderr` printed below on
  failure).
- **Status** (`--swap-status`, `--ufw-status`, `--fail2ban-status`,
  `--show-ntp`): rendered as key/value tables instead of loose lines of text.
- **Lists** (`--list-users`, `--list-cron`, `--ufw-status` rules): rendered as
  column tables.
- **Swap usage**: `--swap-status` includes a colored progress bar
  (green/yellow/red depending on the percentage used).
- **Messages**: `✔` success, `ℹ` info, `⚠` warning, `✘` error — consistent
  across every module.

## Help

```bash
sforge --help            # overview of the 11 available modules
sforge --help ssh        # every flag for one specific module
sforge --help git
```

`--help` with no arguments only shows the module list with a one-line
description each, instead of dumping all ~70 flags at once. To see a module's
full detail (every flag with its description) ask for it explicitly with
`--help <module>`.

## Modules

### 1. System
```bash
sforge --update          # apt update
sforge --upgrade         # apt upgrade -y
sforge --full-upgrade    # apt full-upgrade -y
```

### 2. SSH
```bash
sudo sforge --ssh                    # install, enable and verify
sudo sforge --ssh --ssh-port 2222    # install and change the port
```

### 3. Git
```bash
sforge --install-git
sforge --git-config --git-name "Name" --git-email "mail@example.com"
sforge --git-config --git-scope system --git-name "..." --git-email "..."
sforge --git-config --git-editor nano --git-branch main --git-pull rebase
sforge --git-ssh --git-email "mail@example.com" --ssh-key-type ed25519
sforge --git-show
```

### 4. Prompt customization
```bash
sforge --show-branch     # git branch + repo status
sforge --show-time       # [HH:MM:SS] timestamp
sforge --show-venv       # active virtualenv name
sforge --prompt-status   # see which customizations are active
sforge --remove-branch   # (and --remove-time, --remove-venv)
```

### 5. Timezone
```bash
sforge --show-timezone
sforge --list-timezones-region Europe
sudo sforge --set-timezone Europe/Madrid
sudo sforge --enable-ntp        # automatic clock sync
sforge --show-ntp
```

### 6. UFW (firewall)
```bash
sudo sforge --install-ufw
sudo sforge --allow-port 22 --protocol tcp
sudo sforge --enable-ufw
sudo sforge --ufw-status --ufw-verbose
sudo sforge --deny-port 8080
sudo sforge --delete-rule 22
```

### 7. fail2ban (brute-force protection)
```bash
sudo sforge --install-fail2ban
sudo sforge --protect-ssh --max-retry 3 --ban-time 30m
sudo sforge --enable-fail2ban
sudo sforge --fail2ban-status --jail sshd
```

### 8. Hostname
```bash
sforge --show-hostname
sudo sforge --set-hostname web-prod-01
```

### 9. Users
```bash
sudo sforge --create-user devuser --user-password "..."
sudo sforge --grant-sudo devuser
sudo sforge --revoke-sudo devuser
sudo sforge --add-ssh-key devuser --ssh-key "ssh-ed25519 AAAA..."
sudo sforge --list-users
sudo sforge --user-info devuser
sudo sforge --delete-user devuser --keep-home
```

### 10. Cron
```bash
sforge --add-cron "0 3 * * *" --cron-command "/home/devuser/backup.sh" --cron-comment "Daily backup"
sforge --list-cron
sforge --list-cron-cli          # only tasks managed by this CLI
sforge --remove-cron 1
sforge --remove-cron-cli
sforge --clear-cron             # removes ALL tasks, use with care
```

### 11. Swap
```bash
sudo sforge --create-swap          # 2G by default
sudo sforge --create-swap 1G
sudo sforge --swap-status
sudo sforge --swappiness 10        # recommended for servers
sudo sforge --disable-swap
sudo sforge --remove-swap
```

## What the `--all` flow includes

| Phase | Module | Behavior |
|-------|--------|----------|
| 1 | System | Updates packages |
| 2 | SSH | Installs and secures SSH |
| 3 | Git | Installs + base configuration |
| 4 | Prompt | Applies customizations |
| 5 | UFW | Installs, allows SSH and enables |
| 6 | fail2ban | Installs and protects SSH |
| 7 | Hostname | Asks whether to change it (interactive) |
| 8 | Users | Asks whether to create one (interactive) |
| 9 | Swap | Asks whether to create it (interactive) |

Timezone and Cron are managed manually: the timezone is too specific to
assume a sensible default, and cron tasks are too particular to automate
inside `--all`.

## Architecture

```
src/serverforge_cli/
├── cli.py               → entry point (sforge), orchestrates --all by
│                           phases and resolves --help (overview + detail)
├── commands/             → parses arguments and decides what to run
│   ├── system.py
│   ├── ssh.py
│   ├── git.py
│   ├── command_line_custom.py
│   ├── timezone.py
│   ├── ufw.py
│   ├── fail2ban.py
│   ├── hostname.py
│   ├── users.py
│   ├── cron.py
│   └── swap.py
├── modules/              → actual logic, runs system commands
│   └── (one file per command above)
└── utils.py              → shared Rich-based helpers (icon messages,
                            status/list tables, usage bar, execution
                            spinner, real-user detection behind sudo)
pyproject.toml           → package metadata, dependencies and the
                            `sforge` entry point
tests/                    → pytest suite with mocks
```

Each layer has a single responsibility. `cli.py` doesn't know what each
module does; `commands/` doesn't know how system commands are executed;
`modules/` knows nothing about argparse or the CLI. Adding a new module means
creating its `commands/x.py` + `modules/x.py` pair and registering it in
`commands/__init__.py`, without touching anything else.

An important design detail: when the CLI runs under `sudo`, modules that
configure user-level things (Git, Cron) detect the real user via
`SUDO_USER` and act on their configuration, not root's.

## Development

To modify the code or contribute, install the project in editable mode from
a cloned copy of the repository:

```bash
git clone https://github.com/Manueh9/ServerSetup_CLI
cd ServerSetup_CLI
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

This installs `serverforge-cli` in editable mode along with the development
dependencies (`pytest`, `pytest-mock`, `pytest-cov`).

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=serverforge_cli --cov-report=term-missing
```

Tests mock every system call (`apt`, `systemctl`, `git config`, `crontab`,
`swapon`...) so the suite can run on any machine without root privileges and
without touching the real system. Pure logic (port/hostname validation, cron
schedule parsing, config file parsing) is tested directly. CI on GitHub
Actions runs the full suite on Python 3.11 and 3.12 on every push to `main`
and `develop`.

## Security

- **UFW**: the `--all` flow allows the SSH port *before* enabling the
  firewall, so it doesn't lock you out of remote access.
- **Privileged ports**: a warning is shown when opening ports below 1024.
- **Validation**: usernames, hostnames, ports, swap sizes and cron schedules
  are all validated before being applied.
