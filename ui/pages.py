import base64
import logging
from getpass import getpass

from app import AppContext, read_json_file
from deck import DeckContext, DeckData, generate_deck_encryption_settings
from logic import create_training_entry, hash_password
from ui.browser import RouteInfo

from .helpers import print_heading, prompt_input, prompt_password, prompt_selection

l = logging.getLogger(__name__)


def main_page(ctx: AppContext) -> RouteInfo:
    """Main page"""
    deck_ctx = ctx.get_current_deck_context()
    decks = ctx.get_deck_infos()
    if len(decks) == 0:
        return {"next_page": deck_creation_page}
    if deck_ctx is None:
        return {"next_page": deck_selection_page}
    i = prompt_selection(
        ["Start Training", "Manage Passwords", "Exit"], "PASSWORD TRAINER"
    )
    match i:
        case 0:
            return {"next_page": training_page}
        case 1:
            return {"next_page": password_manager_page}
        case 2:
            return {"exit": True}
    return {}


def deck_creation_page(ctx: AppContext) -> RouteInfo:
    print_heading("Deck Creation")
    deck_name = prompt_input("Enter a deck name")

    s = prompt_selection(
        ["Encryption Enabled (recommended)", "No Encryption"],
        "Deck Encryption Selection",
    )

    if s == 0:
        password = prompt_password("Enter deck password")
        encryption = generate_deck_encryption_settings(True)
    else:
        password = None
        encryption = generate_deck_encryption_settings(False)

    l.info("Create a new deck named `%s`", deck_name)
    deck = DeckContext(
        deck_name,
        {"hashing": ctx.get_settings()["hashing"], "encryption": encryption},
        password,
    )
    ctx.load_deck(deck)
    ctx.save_deck()
    return {"steps_back": 1}


def deck_selection_page(ctx: AppContext) -> RouteInfo:
    decks = ctx.get_deck_infos()
    options = [deck["name"] for deck in decks]
    options.append("Exit")
    i = prompt_selection(options, "Deck Selection", "Select a Deck to Load")

    if i >= len(options) - 1:
        return {"exit": True}

    deck_info = decks[i]
    deck_data: DeckData = read_json_file(deck_info["path"])

    password: str | None = None
    if deck_data["encryption"]["enabled"]:
        password = prompt_password("Enter deck password", False)

    deck = DeckContext(deck_info["name"], deck_data, password)
    ctx.load_deck(deck)
    return {"steps_back": 1}


def training_page(ctx: AppContext) -> RouteInfo:
    deck = ctx.get_current_deck_context()
    entries = deck.get_entries()
    hashing = deck.get_hashing()
    if len(entries) == 0:
        print("No training data entries.\n")
    for entry in entries:
        prompt = entry["prompt"]
        salt = base64.decodebytes(entry["salt"].encode("ascii"))
        correct_hash = base64.decodebytes(entry["data"].encode("ascii"))

        print("\n{}\n".format(prompt))
        while True:
            password = getpass(" > ")
            hash = hash_password(password, hashing, salt)
            if hash == correct_hash:
                break
            print("\nWrong input. Try again.\n")
    return {"steps_back": 1}


def password_manager_page(ctx: AppContext) -> RouteInfo:
    i = prompt_selection(
        ["Add Password Entry", "Back"],
        "Deck Data Manager",
    )
    match i:
        case 0:
            prompt_password_entry(ctx)
        case 1:
            return {"steps_back": 1}
    return {}


def prompt_password_entry(ctx: AppContext):
    print("Enter password entry prompt.")
    prompt = input(" > ")
    print()
    password = prompt_password("Enter password")

    deck = ctx.get_current_deck_context()
    entry = create_training_entry(prompt, password, deck)
    deck.append_entry(entry)
    ctx.save_deck()
