# class MenuOption:
#     def __init__(self, text: str, form: str, count: int = 1) -> None:
#         self.text = text
#         self.format = form
#         self.count = count


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
