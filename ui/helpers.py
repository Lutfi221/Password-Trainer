from typing import Callable, Optional, TypedDict
from context import AppContext


class RouteInfo(TypedDict):
    steps_back: Optional[int]
    next_page: Optional[Callable[[AppContext], any]]
    go_home: Optional[bool]
    exit: Optional[bool]


Page = Callable[[AppContext], RouteInfo]


class PageBrowser:
    _page_stack: list[Page] = []
    context: AppContext

    def __init__(self, home_page: Page, context: AppContext):
        self._page_stack.append(home_page)
        self.context = context

    def start(self):
        try:
            while self._iteration():
                pass
        except KeyboardInterrupt:
            print("Exit")

    def _iteration(self) -> bool:
        """Load the top page of the :attr:`PageBrowser._pageStack`

        Returns
        -------
        bool
            True if it should loop again, False if the browser should stop.
        """
        # Load the page and get the route info
        route = self._page_stack[-1](self.context)

        if route.get("next_page"):
            self._page_stack.append(route["next_page"])
        elif route.get("steps_back"):
            for _ in range(route["steps_back"]):
                self._page_stack.pop()
        elif route.get("go_home"):
            for _ in range(len(self._page_stack) - 1):
                self._page_stack.pop()
        elif route.get("exit"):
            return False

        return True


def print_list(options: list[str]):
    for i, items in enumerate(options, start=1):
        print("{}. {}".format(i, items))


def prompt_selection(options: list[str], heading="", indent=0) -> int:
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
    if heading:
        print(heading)
        print()
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
            return selected - 1
        print(error_msg)
