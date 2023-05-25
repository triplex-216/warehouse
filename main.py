import argparse
import datetime
import os
from random import choice
from lib.tui import *
from lib.core import *
from lib.route import *
from lib.misc import *

VERSION = "beta 0.2"

CONF = Config(
    use_random_item=True,
    save_instructions=True,
    default_algorithm="g",
    origin_position=(0, 0),
)
DATASET = "data/qvBox-warehouse-data-s23-v01.txt"


""" Settings Menu """


def input_config_random(conf: Config):
    bool_random = input_data_as_list(
        "Do you want to use a random item when inputted ID is invalid? ", "b", 1
    )
    conf.use_random_item = bool_random[0]
    print(f"Set random item to {bool_random[0]}")


def input_config_save_instructions(conf: Config):
    bool_save_instructions = input_data_as_list(
        "Do you want to save all directions as a text file for future reference? ",
        "b",
        1,
    )
    conf.save_instructions = bool_save_instructions[0]
    print(f"Set save instructions to {bool_save_instructions[0]}")


def input_default_algorithm(conf: Config):
    algs = {
        "b": "Branch and bound",
        "g": "Greedy",
    }

    str_default_algorithm = input_data_as_list(
        "Choose a default algorithm of your choice (b/g)\nb - branch and bound; g - greedy",
        "s",
        1,
    )[0]
    while str_default_algorithm not in algs.keys():
        print(f"Please choose a valid option from b/g")
        str_default_algorithm = input_data_as_list(
            "Choose a default algorithm of your choice (b/g)\nb - branch and bound; g - greedy",
            "s",
            1,
        )[0]
    conf.default_algorithm = str_default_algorithm
    print(f"Set default algorithm to {algs[str_default_algorithm]}")


settings_menu = Menu(
    text="Settings menu",
    options=[
        ("Randomize item", lambda: input_config_random(conf=CONF)),
        (
            "Save instructions to text file",
            lambda: input_config_save_instructions(conf=CONF),
        ),
        (
            "Default algorithm",
            lambda: input_default_algorithm(conf=CONF),
        ),
    ],
)


""" Main Menu """


def start_routing(conf: Config):
    # Read inventory data from text file
    map_data, prod_db = read_inventory_data(DATASET)
    rows, cols = len(map_data), len(map_data[0])

    warn("Only the first item will be added to the list(alpha release only)")
    item_count = input_data_as_list("How many items would you like to fetch? ", "d", 1)[
        0
    ]
    item_ids = input_data_as_list(
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
                debug(f"Item {i} does not exist, replacing it with {random_item_id}! ")

    # DEBUG FEATURE
    # Limit to 1 item
    item_ids = item_ids[:1]

    item_locations = get_item_locations(product_db=prod_db, id_list=item_ids)

    if len(item_locations) == 0:
        warn("The item(s) requested are not available at the moment. ")
        return -1

    route = find_route(
        map=map_data,
        prod_db=prod_db,
        start=conf.origin_position,
        item_ids=item_ids,
        algorithm=conf.default_algorithm,
    )
    # Draw text map
    map_text = draw_text_map(map_data)
    # Add route paths to map
    map_text = add_paths_to_map(map_text, route, item_locations)
    # Add axes to map for easier reading
    map_full = add_axes_to_map(map_text, cols, rows)

    warn("\nWAREHOUSE MAP\n")
    print_map(map_full)

    instr = get_instructions(route=route, prod_db=prod_db, item_ids=item_ids)
    print(instr)

    # TODO respect settings
    # Create the directory "reports" if it does not exist yet
    if not os.path.exists("reports"):
        os.makedirs("reports")

    # Get the current date/time in ISO8601 format, e.g. 2023-05-24 11:42:08
    # and append .txt extension
    save_to_file(
        f"reports/navigation-report-{datetime.datetime.now().replace(microsecond=0)}.txt",
        gen_instruction_metadata() + instr,
    )


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
