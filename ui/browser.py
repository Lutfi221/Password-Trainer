import logging
from typing import Callable, Optional, TypedDict

from app import AppContext

l = logging.getLogger(__name__)


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
        l.info("Load page `%s`", self._page_stack[-1].__name__)
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
