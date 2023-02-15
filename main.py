import logging

from app import AppContext
from ui.browser import PageBrowser
from ui.pages import main_page
from utils import InvalidJsonFileError


def main():
    logging.basicConfig(
        filename="./password-trainer.log",
        encoding="utf-8",
        filemode="w",
        level=logging.DEBUG,
    )
    l = logging.getLogger()
    try:
        context = AppContext("./settings.json", "./decks/")
        browser = PageBrowser(main_page, context)
        browser.start()
    except KeyboardInterrupt:
        print("Exit")
    except InvalidJsonFileError as e:
        l.error("Tried loading an invalid JSON file", exc_info=1)
        print(e)
        print("The invalid JSON file: {}".format(e.path))
        return
    return


if __name__ == "__main__":
    main()
