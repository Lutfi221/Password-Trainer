from getpass import getpass
import logging
import re
from typing import Optional

l = logging.getLogger(__name__)


def print_heading(heading="", desc=""):
    if heading:
        print("# " + heading)
        print()
    if desc:
        print(desc)
        print()


def print_list(options: list[str]):
    for i, items in enumerate(options, start=1):
        print("{}. {}".format(i, items))


def prompt_input(
    prompt="", pattern: Optional[re.Pattern] = None, error_msg="Invalid input"
):
    if prompt:
        print(prompt)
        print()

    while True:
        user_input = input(" > ")
        print()
        if (not pattern) or pattern.match(user_input):
            return user_input
        print(error_msg)
        print()


def prompt_selection(options: list[str], heading="", desc="") -> int:
    """Prompt user to select an option from a list of options.

    Parameters
    ----------
    options : list[str]
        List of options

    Returns
    -------
    int
        Zero-based index of the selected option
    """
    error_msg = (
        "\nInvalid input.\n"
        "Select one of the options by "
        "typing a number from {} to {}".format(1, len(options))
    )
    print_heading(heading, desc)
    print_list(options)
    while True:
        print()
        user_input = input(" > ")
        if not user_input.isnumeric():
            print(error_msg)
            continue

        selected = int(user_input)
        if selected >= 1 and selected <= len(options):
            print()
            l.info(
                "User selected option of index %s with text `%s`",
                selected - 1,
                options[selected - 1],
            )
            return selected - 1
        print(error_msg)


def prompt_password(prompt="Enter password", confirm_password=True):
    while True:
        print(prompt)
        password1 = getpass(" > ")
        if not confirm_password:
            return password1

        print()
        print("Confirm password")
        password2 = getpass(" > ")
        print()

        if password1 == password2:
            return password1

        print("The two passwords you entered did not match.\n" "Try again.\n")
