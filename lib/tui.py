from .core import Config


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
            # Print text and options
            print(self.text)
            for idx, o in enumerate(self.options):
                print(f"{idx + 1}. {o[0]}")

            # Get user input
            user_option = input("> ")

            # If user entered "q", exit immediately
            if user_option == "q" or user_option == "Q":
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
                res = next_action()  # Propagate function return upwards
                break
            else:
                # If the option's next menu is None, exit current menu
                break

        return res


def get_response(text: str, form: str, count: int):
    """
    Prompt user for input. Format and count can be specified.

    text: Message to be printed
    form: Format of data to input, can be: d(integer), f(float), s(string), or b(boolean)
    count: Number of data to input

    e.g. (form="d", count=10) => 10 Integers
    """
    res_list = []

    if form not in ["d", "f", "s", "b"]:
        raise Exception(
            "Format must be d(integer), f(float), s(string), or b(boolean). "
        )

    match form:
        case "d":
            form_description = "Integer"
        case "f":
            form_description = "Any number"
        case "s":
            form_description = "Text"
        case "b":
            form_description = "Y/N"

    print(text)
    for c in range(count):
        while True:  # Re-prompt for input if fails
            res = input(f"{form_description} ({c+1}/{count})")
            if res == "q" or res == "Q":
                return -1

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
                            print("Please input Y/N")
                            continue

                res_list.append(res)
                break

            except ValueError:
                print("Value error")
                continue

    return res_list


# Draw the text map
def draw_text_map(
    map_data: list[list[int]], pd_list: list[tuple[int, int]], config: Config
):
    # Initialize ASCII map buffer
    cols, rows = len(map_data[0]), len(map_data)
    # Preserve 1 row & 1 col for axes
    map_ascii = [["__"] * (cols) for r in range(rows)]

    # Set worker position
    worker_x = config.worker_position[0]
    worker_y = config.worker_position[1]
    map_ascii[worker_x][worker_y] = "WK"

    for r in range(rows):
        for c in range(cols):
            # Mark all 1's in map_data as non-destination shelves
            # (obstacles) in ASCII map
            if map_data[r][c] == 1:
                map_ascii[r][c] = "**"

    # Mark destination shelves where products need to be fetched
    # from as "SH"
    for pd in pd_list:
        r = pd[0]
        c = pd[1]
        map_ascii[r][c] = "SH"

    # create a new 2D list with axis indices
    map_with_axes = [[" " for j in range(cols + 1)] for i in range(rows + 1)]

    # add the row and column indices
    map_with_axes[0][0] = "  "
    for i in range(rows):
        if rows > 9:
            map_with_axes[i + 1][0] = f"{i:02d}"
        else:
            map_with_axes[i + 1][0] = str(i)
    for j in range(cols):
        if cols > 9:
            map_with_axes[0][j + 1] = f"{j:02d}"
        else:
            map_with_axes[0][j + 1] = str(j)

    # copy over the original list
    for i in range(rows):
        for j in range(cols):
            map_with_axes[i + 1][j + 1] = map_ascii[i][j]

    # print the new list
    for row in reversed(map_with_axes):
        print(" ".join(row))


# Show the detailed route on the map
def route_map(map_data, shortest_path):
    for i in range(1, len(shortest_path)):
        c1 = shortest_path[i - 1]
        c2 = shortest_path[i]

        while c1[0] != c2[0]:
            if c1[0] < c2[0]:
                c1 = (c1[0] + 1, c1[1])
                map_data[c1[0]][c1[1]] = "^ "
            else:
                c1 = (c1[0] - 1, c1[1])
                map_data[c1[0]][c1[1]] = "v "

        while c1[1] != c2[1]:
            if c1[1] < c2[1]:
                c1 = (c1[0], c1[1] + 1)
                map_data[c1[0]][c1[1]] = "> "
            else:
                c1 = (c1[0], c1[1] - 1)
                map_data[c1[0]][c1[1]] = "< "

    return map_data
