from serverforge_cli.modules.timezone import (
    show_current_timezone, list_timezones,
    set_timezone, show_ntp_status,
    enable_ntp, disable_ntp,
)
from serverforge_cli.utils import step

def register_args(parser):
    group = parser.add_argument_group("Timezone")
    group.add_argument("--show-timezone", action="store_true", help="Show current timezone and datetime")
    group.add_argument("--set-timezone", type=str, metavar="TIMEZONE", help="Set system timezone (e.g. Europe/Madrid)")
    group.add_argument("--list-timezones", action="store_true", help="List all available timezones")
    group.add_argument("--list-timezones-region", type=str, metavar="REGION", help="List timezones by region (e.g. Europe)")
    group.add_argument("--show-ntp", action="store_true", help="Show NTP synchronization status")
    group.add_argument("--enable-ntp", action="store_true", help="Enable automatic clock sync via NTP")
    group.add_argument("--disable-ntp", action="store_true", help="Disable NTP synchronization")

def handle(args):
    if args.show_timezone:
        show_current_timezone()
    if args.list_timezones:
        list_timezones()
    if args.list_timezones_region:
        list_timezones(args.list_timezones_region)
    if args.set_timezone:
        set_timezone(args.set_timezone)
    if args.show_ntp:
        show_ntp_status()
    if args.enable_ntp:
        enable_ntp()
    if args.disable_ntp:
        disable_ntp()

def run_all():
    """Called by --all. Enables NTP - timezone must be set manually."""
    enable_ntp()
