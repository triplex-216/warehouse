from numpy import transpose

ALGS = {
    "b": "Branch and bound",
    "g": "Greedy",
    "n": "Nearest neighbor",
    "t": "Genetic",
}
class Menu:
    """
    Menu to be displayed in the TUI (text user interface).
    Must supply with a text to be displayed and options for the user to choose from.
    """

    def __init__(self, text: str, options: list[tuple]) -> None:
        self.text = text
        self.options = options

    def enter(self):
        """
        Enters the menu.
        Prints the text and all options, and prompts the user for an input.
        Returns the input.
        """
        res = 0

        while True:
            option_exit = len(self.options) + 1
            # Print text and options
            print()  # New line
            warn(self.text)
            for idx, o in enumerate(self.options):
                print(f"{idx + 1}. {o[0]}")
            print(f"{option_exit}. Exit menu")

            # Get user input
            user_option = input("> ")

            # If user entered exit code or "q", exit immediately
            if user_option in [str(option_exit), "q", "Q"]:
                return 0

            # Convert user input to integer
            try:
                user_option = int(user_option)
            except ValueError:
                print("Invalid option, please try again. ")
                continue

            if user_option not in range(1, len(self.options) + 1):
                # Invalid option
                print("Invalid option, please try again. ")
                continue

            # Got a valid numeral option
            try:
                next_action = self.options[user_option - 1][1]
            except IndexError:
                print(
                    "Menu structure error! Does this option tuple come with a menu or a None? "
                )
                continue  # Re-prompt for user input

            if type(next_action) is Menu:
                # If option is bound to a menu
                next_action.enter()
            elif callable(next_action):
                # If option is bound to a function
                res = next_action()  # Propagate last function return upwards
                continue  # Stays in the menu
            else:
                # If the option's next menu is None, exit current menu
                break

        return res


""" Input/Ouput """


def input_data_as_list(text: str, form: str, count: int) -> list:
    """
    Prompt user for input. Format and count can be specified.

    text: Message to be printed
    form: Format of data to input, can be: d(integer), f(float), s(string), or b(boolean)
    count: Number of data to input

    e.g. (form="d", count=10) => 10 Integers
    """
    res_list = []

    if form not in ["d", "f", "s", "b", "c"]:
        raise Exception(
            "Format must be d(integer), f(float), s(string), or b(boolean). "
        )

    match form:
        case "d":
            form_description = "integer"
        case "f":
            form_description = "number"
        case "s":
            form_description = ""
        case "b":
            form_description = "Y/N"
        case "c":
            form_description = "x, y - split by a comma"

    print(text, end="")
    if form != "s": 
        print(f"({form_description})")
    else: 
        print("")

    for c in range(count):
        while True:  # Re-prompt for input if fails
            # print(format_hint)
            count_hint = f"({c+1}/{count}) "
            res = input(f"> {count_hint if count > 1 else ''}")

            # Handle response with correct format
            try:
                match form:
                    case "d":
                        res = int(res)
                    case "f":
                        res = float(res)
                    case "s":
                        res = str(res)
                    case "b":
                        if res in ["Y", "y"]:
                            res = True
                        elif res in ["N", "n"]:
                            res = False
                        else:
                            print("Wrong input format, please try again.")
                            continue
                    case "c":
                        res = tuple(
                            int(num) for num in res.split(",")
                        )
                        if len(res) != 2:
                            print("Wrong input format, please try again.")
                            continue

                res_list.append(res)
                break

            except ValueError:
                print("Wrong input format, please try again.")
                continue

    return res_list


def bold_text(text=""):
    return f"\033[1m{text}\033[0m"

def color_text(text, color):
    reset = '\033[0m'
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    if color not in ['g', 'b', 'y', 'r']:
        raise Exception(
            "Color must be g(green), b(blue), y(yellow), r(red). "
        )
    match color:
        case 'g':
            foreground_color = green
        case 'b':
            foreground_color = blue
        case 'y':
            foreground_color = yellow
        case 'r':
            foreground_color = red

    return f"{foreground_color}{text}{reset}"


def warn(text=""):
    """
    Print a line of text in bold text
    """
    print(f"\033[1m{text}\033[0m")


def debug(text=""):
    """
    Print a line of text with [DEBUG]
    """
    print(f"[DEBUG] {text}")


""" Text map """


# Draw the text map
def draw_text_map(map_data: list[list[int]]):
    # Initialize ASCII map buffer
    cols, rows = len(map_data), len(map_data[0])
    map_text = [["__"] * (rows) for _ in range(cols)]  # 40*21 2-d list

    for x in range(cols):
        for y in range(rows):
            # Mark all 1's in map_data as non-destination shelves
            # (obstacles) in ASCII map
            if map_data[x][y] == 1:
                map_text[x][y] = "**"

    return map_text


# Add X and Y axes to the text map
def add_axes_to_map(map_text, rows, cols):
    # create a new 2D list with axis indices
    map_with_axes = [[" " for j in range(rows + 1)] for i in range(cols + 1)]

    # add the row and column indices
    map_with_axes[0][0] = "  "
    for x in range(cols):
        if cols > 9:
            map_with_axes[x + 1][0] = f"{x:02d}"
        else:
            map_with_axes[x + 1][0] = str(x)
    for y in range(rows):
        if rows > 9:
            map_with_axes[0][y + 1] = f"{y:02d}"
        else:
            map_with_axes[0][y + 1] = str(y)

    # copy over the original list
    for x in range(cols):
        for y in range(rows):
            map_with_axes[x + 1][y + 1] = map_text[x][y]

    return map_with_axes


# Show the detailed route on the text map
def add_paths_to_map(map_text, paths, pd_list: list[tuple[int, int]], back=False):
    # Set source position (worker)
    src_x, src_y = paths[0][0], paths[0][1]
    map_text[src_x][src_y] = bold_text("WK")

    # Set all items' shelves
    for pd in pd_list:
        x = pd[0]
        y = pd[1]
        map_text[x][y] = color_text("SH", 'r')

    for curr in paths:
        map_text[curr[0]][curr[1]] = color_text("##", 'b')

    if back:
        dest_x, dest_y = paths[-1][0], paths[-1][1]
        map_text[dest_x][dest_y] = bold_text("OR")  # "OR" for "origin"

    return map_text


# Print generated text maps
def print_map(full_map: str):
    # print the new list
    for row in reversed(transpose(full_map)):
        print(" ".join(row))
    print()  # New line

    legends = f"{bold_text('SH')}: Shelf  {bold_text('WK')}: Worker  {bold_text('OR')}: Origin {bold_text('##')}: Routes  {bold_text('**')}: Shelf (Not a destination)  {bold_text('__')}: Empty"
    print(legends)
    print()

def show_result(map_data, conf, item_locations, instr, total_cost, route, timeout):
    cols, rows = len(map_data), len(map_data[0])
    # Draw text map
    map_text = draw_text_map(map_data)
    # Add route paths to map
    map_text = add_paths_to_map(map_text, route, item_locations)
    # Add axes to map for easier reading
    map_full = add_axes_to_map(map_text, rows, cols)

    # Show result
    warn("\nWAREHOUSE MAP\n")
    print_map(map_full)
    print(instr)
    print(
        f"Total distance is {total_cost}. (Calculated with {'Nearest Neighbor' if timeout else ALGS[conf.default_algorithm]})"
    )
