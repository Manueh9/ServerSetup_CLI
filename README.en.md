# ServerSetup CLI

![Tests](https://github.com/Manueh9/ServerSetup_CLI/actions/workflows/tests.yml/badge.svg)
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

## Installation

```bash
git clone https://github.com/Manueh9/ServerSetup_CLI
cd ServerSetup_CLI
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Full setup

```bash
sudo python3 cli.py --all
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
python3 cli.py --help            # overview of the 11 available modules
python3 cli.py --help ssh        # every flag for one specific module
python3 cli.py --help git
```

`--help` with no arguments only shows the module list with a one-line
description each, instead of dumping all ~70 flags at once. To see a module's
full detail (every flag with its description) ask for it explicitly with
`--help <module>`.

## Modules

### 1. System
```bash
python3 cli.py --update          # apt update
python3 cli.py --upgrade         # apt upgrade -y
python3 cli.py --full-upgrade    # apt full-upgrade -y
```

### 2. SSH
```bash
sudo python3 cli.py --ssh                    # install, enable and verify
sudo python3 cli.py --ssh --ssh-port 2222    # install and change the port
```

### 3. Git
```bash
python3 cli.py --install-git
python3 cli.py --git-config --git-name "Name" --git-email "mail@example.com"
python3 cli.py --git-config --git-scope system --git-name "..." --git-email "..."
python3 cli.py --git-config --git-editor nano --git-branch main --git-pull rebase
python3 cli.py --git-ssh --git-email "mail@example.com" --ssh-key-type ed25519
python3 cli.py --git-show
```

### 4. Prompt customization
```bash
python3 cli.py --show-branch     # git branch + repo status
python3 cli.py --show-time       # [HH:MM:SS] timestamp
python3 cli.py --show-venv       # active virtualenv name
python3 cli.py --prompt-status   # see which customizations are active
python3 cli.py --remove-branch   # (and --remove-time, --remove-venv)
```

### 5. Timezone
```bash
python3 cli.py --show-timezone
python3 cli.py --list-timezones-region Europe
sudo python3 cli.py --set-timezone Europe/Madrid
sudo python3 cli.py --enable-ntp        # automatic clock sync
python3 cli.py --show-ntp
```

### 6. UFW (firewall)
```bash
sudo python3 cli.py --install-ufw
sudo python3 cli.py --allow-port 22 --protocol tcp
sudo python3 cli.py --enable-ufw
sudo python3 cli.py --ufw-status --ufw-verbose
sudo python3 cli.py --deny-port 8080
sudo python3 cli.py --delete-rule 22
```

### 7. fail2ban (brute-force protection)
```bash
sudo python3 cli.py --install-fail2ban
sudo python3 cli.py --protect-ssh --max-retry 3 --ban-time 30m
sudo python3 cli.py --enable-fail2ban
sudo python3 cli.py --fail2ban-status --jail sshd
```

### 8. Hostname
```bash
python3 cli.py --show-hostname
sudo python3 cli.py --set-hostname web-prod-01
```

### 9. Users
```bash
sudo python3 cli.py --create-user devuser --user-password "..."
sudo python3 cli.py --grant-sudo devuser
sudo python3 cli.py --revoke-sudo devuser
sudo python3 cli.py --add-ssh-key devuser --ssh-key "ssh-ed25519 AAAA..."
sudo python3 cli.py --list-users
sudo python3 cli.py --user-info devuser
sudo python3 cli.py --delete-user devuser --keep-home
```

### 10. Cron
```bash
python3 cli.py --add-cron "0 3 * * *" --cron-command "/home/devuser/backup.sh" --cron-comment "Daily backup"
python3 cli.py --list-cron
python3 cli.py --list-cron-cli          # only tasks managed by this CLI
python3 cli.py --remove-cron 1
python3 cli.py --remove-cron-cli
python3 cli.py --clear-cron             # removes ALL tasks, use with care
```

### 11. Swap
```bash
sudo python3 cli.py --create-swap          # 2G by default
sudo python3 cli.py --create-swap 1G
sudo python3 cli.py --swap-status
sudo python3 cli.py --swappiness 10        # recommended for servers
sudo python3 cli.py --disable-swap
sudo python3 cli.py --remove-swap
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
cli.py                  → entry point, orchestrates --all by phases and
                           resolves --help (overview + per-module detail)
commands/                → parses arguments and decides what to run
  ├── system.py
  ├── ssh.py
  ├── git.py
  ├── command_line_custom.py
  ├── timezone.py
  ├── ufw.py
  ├── fail2ban.py
  ├── hostname.py
  ├── users.py
  ├── cron.py
  └── swap.py
modules/                 → actual logic, runs system commands
  └── (one file per command above)
utils.py                 → shared Rich-based helpers (icon messages, status/
                           list tables, usage bar, execution spinner, real-
                           user detection behind sudo)
tests/                   → pytest suite with mocks
```

Each layer has a single responsibility. `cli.py` doesn't know what each
module does; `commands/` doesn't know how system commands are executed;
`modules/` knows nothing about argparse or the CLI. Adding a new module means
creating its `commands/x.py` + `modules/x.py` pair and registering it in
`commands/__init__.py`, without touching anything else.

An important design detail: when the CLI runs under `sudo`, modules that
configure user-level things (Git, Cron) detect the real user via
`SUDO_USER` and act on their configuration, not root's.

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=modules --cov-report=term-missing
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
