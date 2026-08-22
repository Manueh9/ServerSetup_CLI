import subprocess
from serverforge_cli.utils import ok, warn, error, info, success, step, run_command, status_table
from rich.markup import escape

def _timedatectl(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["timedatectl"] + args, capture_output=True, text=True)

def get_current_timezone() -> str:
    result = _timedatectl(["show", "--property=Timezone", "--value"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"

def show_current_timezone():
    tz = get_current_timezone()
    time = subprocess.run(["date"], capture_output=True, text=True).stdout.strip()
    print()
    info(f"Current timezone : [cyan]{escape(tz)}[/cyan]")
    info(f"Current datetime : [cyan]{escape(time)}[/cyan]")
    print()

def list_timezones(region: str = None):
    result = _timedatectl(["list-timezones"])
    if result.returncode != 0:
        error("Could not retrieve timezone list")
        return

    all_zones = result.stdout.strip().splitlines()

    if region:
        filtered = [z for z in all_zones if z.lower().startswith(region.lower())]
        if not filtered:
            warn(f"No timezones found for region: {region}")
            warn("Available regions: Africa, America, Asia, Atlantic, Australia, Europe, Indian, Pacific")
            return
        zones = filtered
    else:
        zones = all_zones

    print()
    info(f"Available timezones{f' ({region})' if region else ''}:")
    for z in zones:
        print(f"  {z}")
    print(f"\n  {len(zones)} timezone(s) found\n")

def set_timezone(timezone: str) -> bool:
    result = _timedatectl(["list-timezones"])
    valid = result.stdout.strip().splitlines()

    if timezone not in valid:
        error(f"Invalid timezone: {timezone}")
        warn("Use --list-timezones or --list-timezones-region REGION to see valid options")
        return False

    current = get_current_timezone()
    if current == timezone:
        ok(f"Timezone is already set to {timezone}")
        return True

    step(f"Setting timezone to {timezone}...")
    run_command(["timedatectl", "set-timezone", timezone])

    new_tz = get_current_timezone()
    if new_tz == timezone:
        success(f"Timezone changed: {current} -> {timezone}")
        show_current_timezone()
        return True
    else:
        error(f"Failed to set timezone - current: {new_tz}")
        return False

def get_ntp_status() -> bool:
    result = _timedatectl(["show", "--property=NTP", "--value"])
    return result.stdout.strip().lower() == "yes"

def show_ntp_status():
    active = get_ntp_status()
    sync = _timedatectl(["show", "--property=NTPSynchronized", "--value"])
    synced = sync.stdout.strip().lower() == "yes"

    status_table("NTP Status", [
        ("NTP active", "yes" if active else "no"),
        ("NTP synced", "yes" if synced else "no"),
    ])

    if active and synced:
        ok("Clock is synchronized with NTP servers")
    elif active and not synced:
        warn("NTP is active but not yet synchronized - wait a few seconds")
    else:
        warn("NTP is disabled - clock may drift over time")
    print()

def enable_ntp():
    if get_ntp_status():
        ok("NTP is already enabled")
        return
    step("Enabling NTP synchronization...")
    run_command(["timedatectl", "set-ntp", "true"])
    show_ntp_status()

def disable_ntp():
    if not get_ntp_status():
        ok("NTP is already disabled")
        return
    step("Disabling NTP synchronization...")
    run_command(["timedatectl", "set-ntp", "false"])
    show_ntp_status()
