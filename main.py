import argparse
from lib.tui import *
from lib.core import *

VERSION = "alpha 0.1"

CONF = Config()

""" Settings Menu """


def input_config_random(conf: Config):
    bool_random = get_user_input("Want it random? ", "b", 1)
    conf.random_item = bool_random
    print(f"Set random item to {bool_random[0]}")


settings_menu = Menu(
    text="Settings menu",
    options=[
        ("Random?", lambda: input_config_random(CONF)),
    ],
)


""" Main Menu """

def start_routing():
    # Read inventory data from text file
    map_data, prod_db = read_inventory_data("data/qvBox-warehouse-data-s23-v01.txt")

    item_count = get_user_input("How many items would you like to fetch? ", "d", 1)[0]
    item_ids = get_user_input(
        "Please input IDs of the items you wish to add to list", "d", item_count
    )

    mock_item_list = [19699] # Use a specific item during development phase

    # item_locations = get_item_locations(product_db=prod_db, id_list=item_ids)
    item_locations = get_item_locations(product_db=prod_db, id_list=mock_item_list)

    draw_text_map(map_data, item_locations, CONF)


main_menu = Menu(
    text=f"Warehouse Navigator {VERSION}",
    options=[
        ("Start", start_routing),
        ("Settings", settings_menu),
        ("Exit", None),
    ],
)

""" Main """


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
