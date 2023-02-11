from context import AppContext
from ui.helpers import PageBrowser
from ui.pages import main_page


def main():
    context = AppContext()
    context.load_settings()
    context.load_entries()
    browser = PageBrowser(main_page, context)
    try:
        browser.start()
    except KeyboardInterrupt:
        print("Exit")
    return


if __name__ == "__main__":
    main()
