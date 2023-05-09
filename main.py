import argparse
from random import choice
from lib.tui import *
from lib.core import *
from lib.route import *

VERSION = "alpha 0.1"

CONF = Config(
    use_random_item=True,
)
DATASET = "data/qvBox-warehouse-data-s23-v01.txt"


""" Settings Menu """


def input_config_random(conf: Config):
    bool_random = get_user_input(
        "Do you want to use a random item when inputted ID is invalid? ", "b", 1
    )
    conf.use_random_item = bool_random[0]
    print(f"Set random item to {bool_random[0]}")


settings_menu = Menu(
    text="Settings menu",
    options=[
        ("Randomize item", lambda: input_config_random(CONF)),
    ],
)


""" Main Menu """


def start_routing(conf: Config):
    # Read inventory data from text file
    map_data, prod_db = read_inventory_data(DATASET)
    rows, cols = len(map_data), len(map_data[0])

    item_count = get_user_input("How many items would you like to fetch? ", "d", 1)[0]
    item_ids = get_user_input(
        "Please input IDs of the items you wish to add to list", "d", item_count
    )

    # DEBUG FEATURE
    # Pick random item when specified item ID does not exist
    if conf.use_random_item:
        valid_ids = list(prod_db.keys())
        # item_ids = valid_ids[:-10] + [22]  # Test the duplication check
        for idx, i in enumerate(item_ids):
            if i not in valid_ids:
                # Replace invalid ID with random item
                random_item_id = item_ids[0]
                while (
                    random_item_id in item_ids
                ):  # Avoid duplicate ID; chance is extremely low
                    random_item_id = choice(valid_ids)
                item_ids[idx] = random_item_id
                warn(f"Item #{i} does not exist, replacing it with Item #{random_item_id}! ")

    # DEBUG FEATURE
    # Limit to 1 item
    item_ids = item_ids[:1]

    item_locations = get_item_locations(product_db=prod_db, id_list=item_ids)

    if len(item_locations) == 0:
        warn("The item(s) requested are not available at the moment. ")
        return -1

    route = find_route(map=map_data, start=CONF.worker_position, end=item_locations[0])
    route_back = find_route(map=map_data, start=route[-1], end=CONF.worker_position)

    # Draw text map
    map_text = draw_text_map(map_data, item_locations, CONF)
    # Add route paths to map
    map_text = add_paths_to_map(map_text, route)
    map_text = add_paths_to_map(map_text, route_back)
    # Add axes to map for easier reading
    map_full = add_axes_to_map(map_text, rows, cols)

    warn("\nWAREHOUSE MAP\n")
    print_map(map_full)

    print_instructions(route)
    print_instructions(route_back)


main_menu = Menu(
    text=f"Warehouse Navigator {VERSION}",
    options=[
        ("Start", lambda: start_routing(conf=CONF)),
        ("Settings", settings_menu),
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
