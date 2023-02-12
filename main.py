from context import AppContext, InvalidJsonFileError
from ui.helpers import PageBrowser
from ui.pages import main_page


def main():
    context = AppContext()
    try:
        context.load_settings()
        context.load_training_data()
    except InvalidJsonFileError as e:
        print(str(e))
        print("Fix the file or delete the file.")
        return
    browser = PageBrowser(main_page, context)
    try:
        browser.start()
    except KeyboardInterrupt:
        print("Exit")
    return


if __name__ == "__main__":
    main()
