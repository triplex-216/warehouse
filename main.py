import argparse
import datetime
import os
import signal
from random import choice
from lib.tui import *
from lib.core import *
from lib.route import *
from lib.misc import *

VERSION = "Final"

CONF = Config(
    use_random_item=True,
    save_instructions=True,
    default_algorithm="b",
    start_position=(0, 0),
    end_position=(0, 0),
    default_timeout_value=15,
    map_data=None,
    prod_db=None,
)

DATASET_FILE = "data/qvBox-warehouse-data-s23-v01.txt"
ORDER_LIST_FILE = "data/qvBox-warehouse-orders-list-part01.txt"

signal.signal(
    signal.SIGINT, signal.SIG_DFL
)  # Catches KeyboardInterrupt and prevents it from raising an error.

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
    str_default_algorithm = input_data_as_list(
        "Choose a default algorithm of your choice (b/n/g/t)\nb - branch and bound; n - nearest neighbor; g - greedy; t - genetic",
        "s",
        1,
    )[0]
    while str_default_algorithm not in ALGS.keys():
        str_default_algorithm = input_data_as_list(
            "Please choose a valid algorithm. (b/n/g/t)",
            "s",
            1,
        )[0]
    conf.default_algorithm = str_default_algorithm
    print(f"Set default algorithm to {ALGS[str_default_algorithm]}")


def input_timeout_value(conf: Config):
    timeout_value = input_data_as_list(
        "Please enter the time you're glad to wait. (up to 60 seconds) ", "d", 1
    )[0]
    while True:
        if timeout_value < 0 or timeout_value > 60:
            timeout_value = input_data_as_list(
                "Invalid time, please try again! ", "d", 1
            )[0]
        else:
            break
    conf.default_timeout_value = timeout_value
    print(f"Set timeout value to {timeout_value}s.")


def input_start_end_pos(conf: Config):
    start_position = input_data_as_list("Please enter the start position ", "c", 1)[0]
    while True:
        if is_valid(conf.map_data, start_position):
            print(f"Set start position to {start_position}.")
            conf.start_position = start_position
            break
        else:
            start_position = input_data_as_list("Please try again ", "c", 1)[0]
            continue

    end_position = input_data_as_list("Please enter the end position ", "c", 1)[0]
    while True:
        if is_valid(conf.map_data, end_position):
            print(f"Set end position to {end_position}.")
            conf.end_position = end_position
            break
        else:
            end_position = input_data_as_list("Please try again ", "c", 1)[0]
            continue

    return start_position, end_position


def show_current_config(conf: Config):
    warn("Showing current config: ")
    print(f"Use random item: {conf.use_random_item}")
    print(f"Save instructions to file: {conf.save_instructions}")
    print(f"Default algorithm: {ALGS[conf.default_algorithm]}")
    print(f"Start position: {conf.start_position}")
    print(f"End position: {conf.end_position}")
    print(f"Time out (seconds): {conf.default_timeout_value}")


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
        (
            "Default timeout value",
            lambda: input_timeout_value(conf=CONF),
        ),
        (
            "Start/End Position",
            lambda: input_start_end_pos(conf=CONF),
        ),
        (
            "Show current configs",
            lambda: show_current_config(conf=CONF),
        ),
    ],
)

""" Start """


def start_routing(conf: Config):
    # Read inventory data from text file
    map_data = conf.map_data
    prod_db = conf.prod_db
    
    while True:
        # Get item ids from user input
        item_ids = get_item_ids(conf)
        item_locations = [prod_db[id] for id in item_ids]
        if len(item_locations) == 0:
            warn("The item(s) requested are not available at the moment. ")
            return -1
        # use node instance
        item_nodes = prod_to_node(prod_db, map_data, item_ids)
        # use single node instance
        start_node = SingleNode(coord=conf.start_position, map=map_data)
        end_node = SingleNode(coord=conf.end_position, map=map_data)

        # start find route
        instr, total_cost, route, timeout = find_route(
            item_nodes=item_nodes,
            start_node=start_node,
            end_node=end_node,
            algorithm=conf.default_algorithm,
            timeout=conf.default_timeout_value,
        )
        
        show_result(map_data, conf, item_locations, instr, total_cost, route, timeout)

        # save result to file
        if conf.save_instructions:
            # Create the directory "reports" if it does not exist yet
            if not os.path.exists("reports"):
                os.makedirs("reports")

            # Get the current date/time in ISO8601 format, e.g. 2023-05-24 11:42:08
            # and append .txt extension
            save_to_file(
                os.path.abspath(
                    f"reports/navigation-report-{str(datetime.datetime.now().replace(microsecond=0)).replace(':', '')}.txt"
                ),
                gen_instruction_metadata() + instr,
            )

        continue_ = input_data_as_list(
            "Do you want to continue fetching? ",
            "b",
            1,
        )[0]
        if not continue_:
            break


def get_item_ids(conf: Config):
    # Allow user to input items' id manually or get them from an existing file
    id_src = input_data_as_list(
        "Do you want to input the order manually or automatically get it from an existing file? (M/A)",
        "s",
        1,
    )[0]

    while True:
        if id_src in ["M", "m"]:
            item_ids = input_item_ids(conf)
            change_pos = input_data_as_list(
                "Do you want to change the start/end position now? ",
                "b",
                1,
            )[0]
            if change_pos:
                input_start_end_pos(conf=conf)
            # DEBUG FEATURE: Pick random item when specified item ID does not exist
            break

        elif id_src in ["A", "a"]:
            file_path = ORDER_LIST_FILE
            order_list = read_order_file(file_path)
            # Check if there's problem with the file
            if len(order_list) == 0:
                warn(
                    "The file doesn't exist or it is empty, please check the file path."
                )
                break

            use_custom_order_id = input_data_as_list(
                "Do you want to pick a specific order next? ",
                "b",
                1,
            )[0]

            if use_custom_order_id:
                item_ids = input_order_id(order_list)
            else:  # Randomly pick an unhandled order
                item_ids = choice(list(order_list.values()))
            break
        else:
            id_src = input_data_as_list("Invalid option, please try again.", "s", 1)[0]

    return item_ids


def input_item_ids(conf):
    item_count = input_data_as_list(
        "How many items would you like to fetch? (0 - 50) ", "d", 1
    )[0]
    while True:
        if 0 < item_count <= 50:
            item_ids = input_data_as_list(
                "Please input IDs of the items you wish to add to list",
                "d",
                item_count,
            )
            if conf.use_random_item:
                valid_ids = list(conf.prod_db.keys())
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
                        debug(
                            f"Item {i} does not exist, replacing it with {random_item_id}! "
                        )
            return item_ids
        else:
            item_count = input_data_as_list(
                "Invalid amount, please try again. (0 - 50) ", "d", 1
            )[0]


def input_order_id(order_list):
    order_id = input_data_as_list(
        f"Please give an valid id of order (1 - {len(order_list)}) ",
        "d",
        1,
    )[0]
    while True:
        try:
            item_ids = order_list[order_id]
            print(f"Now use order {order_id}: {item_ids}")
            return item_ids
        except KeyError:
            order_id = input_data_as_list(
                f"Invalid order id, please try again. (1 - {len(order_list)}) ",
                "d",
                1,
            )[0]


""" Main Menu """

main_menu = Menu(
    text=f"Warehouse Navigator {VERSION}",
    options=[
        ("Start", lambda: start_routing(conf=CONF)),
        ("Settings", settings_menu),
    ],
)

""" Main """


def main():
    # Perform file check before launching
    for path in [DATASET_FILE, ORDER_LIST_FILE]:
        if os.path.exists(path) and os.path.isfile(path):
            continue
        else:
            print(f"File {path} not found! Exiting...")
            return -1

    read_inventory_data(DATASET_FILE, CONF)
    map_text = draw_text_map(CONF.map_data)
    print_map(map_text)

    main_menu.enter()


if __name__ == "__main__":
    multiprocessing.freeze_support()  # For PyInstaller to work

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
