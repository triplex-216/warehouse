import argparse
from lib.tui import *

VERSION = "alpha 0.1"

# Set up argument parser for command line options
# 1. Verbose (debug mode)
# 2. Help
parser = argparse.ArgumentParser(
    prog="Warehouse Navigator",
    description="Find your way around the warehouse! ",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Verbose (Debug) mode",
)
args = parser.parse_args()

start_menu = Menu(
    text="Start menu",
    options=[
        ("oof", lambda: print("Poof! ")),
    ],
)

settings_menu = Menu(text="Settings menu", options=[])

main_menu = Menu(
    text=f"Warehouse Navigator {VERSION}",
    options=[
        ("Start", start_menu),
        ("Settings", settings_menu),
        ("Exit", None),
    ],
)


def main():
    main_menu.enter()


if __name__ == "__main__":
    main()
