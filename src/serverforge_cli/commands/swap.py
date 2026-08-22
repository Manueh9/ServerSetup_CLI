from serverforge_cli.modules.swap import (
    create_swap, disable_swap, remove_swap,
    set_swappiness, show_swap_status, has_swap,
    prompt_swap_setup,
)
from serverforge_cli.utils import step, ok

def register_args(parser):
    group = parser.add_argument_group("Swap")

    group.add_argument("--create-swap",   type=str, nargs="?", const="2G", metavar="SIZE",
                       help="Create swap file (default: 2G if no size given)")
    group.add_argument("--disable-swap",  action="store_true", help="Disable active swap")
    group.add_argument("--remove-swap",   action="store_true", help="Disable and delete the swap file")
    group.add_argument("--swappiness",    type=int, metavar="VALUE",
                       help="Set vm.swappiness (0-100, lower = less aggressive)")
    group.add_argument("--swap-status",   action="store_true", help="Show current swap status")

def handle(args):
    if args.create_swap:
        step(f"Creating swap ({args.create_swap})...")
        create_swap(args.create_swap)

    if args.disable_swap:
        step("Disabling swap...")
        disable_swap()

    if args.remove_swap:
        step("Removing swap...")
        remove_swap()

    if args.swappiness is not None:
        step(f"Setting swappiness to {args.swappiness}...")
        set_swappiness(args.swappiness)

    if args.swap_status:
        step("Swap status:")
        show_swap_status()

def run_all():
    step("Swap configuration...")

    if has_swap():
        ok("Swap is already active")
        show_swap_status()
        return

    size = prompt_swap_setup()
    if size:
        create_swap(size)

