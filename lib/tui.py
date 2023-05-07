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
