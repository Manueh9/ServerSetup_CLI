# Changelog

[🇪🇸 Español](CHANGELOG.md) · 🇬🇧 English

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- OS validation on startup (`is_supported_os`): if the host isn't
  Debian/Ubuntu-based, the CLI now aborts with a clear message before
  running any command, instead of failing halfway through with confusing
  errors (`apt`, `ufw` and `systemctl` don't exist on other distros).
- `sshd_config` validation (`sshd -t`) before restarting the SSH service
  after a port change: if the resulting config is invalid, the service is
  not restarted and remote access is preserved with the previous config.

### Fixed
- The `--help` usage text (and the `prog` shown by `--help <module>`) still
  read `cli.py` instead of `sforge`.
- `--protect-ssh` (fail2ban) raised an unhandled exception when run without
  enough permissions to write `jail.local`, and still tried to restart the
  service with a config that was never written. It now reports a permission
  error and skips the restart when the write fails.
- `--create-user ... --user-password ...` applied the password via
  `chpasswd` outside the centralized command runner and without requesting
  root privileges, so it silently failed when run without `sudo`. It now
  goes through the same runner as every other command, adding `sudo` when
  needed.

## [1.0.0] - 2026-08-22

### Added
- Initial CLI to automate the configuration and hardening of Ubuntu servers,
  split into `commands/` (interface) and `modules/` (logic).
- System update module (`system`).
- SSH installation and configuration, including port changes.
- Git installation and configuration.
- Shell prompt customization (branch, timestamp, virtualenv).
- `ufw` module: install, enable/disable, and manage port rules
  (allow/deny).
- `fail2ban` module: SSH brute-force protection.
- `hostname` module: hostname configuration with an interactive prompt
  inside the `--all` flow.
- `users` module: user management, sudo permissions, groups, and SSH keys.
- `cron` module: scheduled task management (add, list, remove).
- `swap` module: swap file management with `fstab` persistence.
- `timezone` module: system timezone configuration.
- `pytest` test suite covering all modules.
- Modernized visual interface with `rich`: tables, usage bars, a live
  spinner during command execution, and phase separators.
- Two-tier `--help`: module overview plus per-module drill-down.
- Packaged as an installable Python package (`pyproject.toml`), exposing the
  `sforge` console entry point.
- Published the `serverforge-cli` package on [PyPI](https://pypi.org/project/serverforge-cli/),
  installable with `pip install serverforge-cli` on Linux, macOS, and
  Windows.
- `install.sh` and `install.bat` scripts that install the PyPI package with
  a single command.
- "Quick install" section in the README (Spanish and English) with the
  install commands for Linux, macOS, and Windows, plus a note on which
  operating system each module actually needs to run on.
- `LICENSE` (MIT) and `CHANGELOG.md` files.
- Project documentation (`README.md` in Spanish and `README.en.md` in
  English) with architecture, usage examples, and security notes.

### Changed
- Restructured the source code into the standard `src/serverforge_cli/`
  layout (previously at the repository root).
- README usage examples changed from `python3 cli.py --xxx` to
  `sforge --xxx`, matching the entry point installed via pip.
- README "Installation" section renamed to "Development" (clone + virtualenv
  + editable install), with the PyPI install now the primary path for end
  users.

[Unreleased]: https://github.com/Manueh9/ServerSetup_CLI/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Manueh9/ServerSetup_CLI/releases/tag/v1.0.0
