import argparse
from lib.tui import *
from lib.core import *

VERSION = "alpha 0.1"

CONF = Config()


def input_products_ids(conf: Config):
    size = get_response("Input number of products", "d", 1)[0]
    products = get_response("Products IDs", "d", size)


start_menu = Menu(
    text="Start menu",
    options=[
        ("oof", lambda: print("Poof! ")),
        ("Products? ", lambda: input_products_ids(CONF)),
    ],
)


def config_random(conf: Config):
    bool_random = get_response("Want it random? ", "b", 1)
    conf.random_item = bool_random
    print(f"Set random item to {bool_random[0]}")


settings_menu = Menu(
    text="Settings menu",
    options=[
        ("Random?", lambda: config_random(CONF)),
    ],
)

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

    main()
