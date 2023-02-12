import base64
from getpass import getpass
from context import AppContext
from logic import create_training_entry, hash_password

from .helpers import RouteInfo, prompt_selection


def main_page(_) -> RouteInfo:
    """Main page"""
    s = prompt_selection(
        ["Start Training", "Manage Passwords", "Exit"], "# PASSWORD TRAINER"
    )
    match s:
        case 0:
            return {"next_page": training_page}
        case 1:
            return {"next_page": password_manager_page}
        case 2:
            return {"exit": True}
    return {}


def training_page(ctx: AppContext) -> RouteInfo:
    entries = ctx.get_entries()
    if len(entries) == 0:
        print("No training data entries.\n")
    for entry in ctx.get_entries():
        prompt = entry["prompt"]
        salt = base64.decodebytes(entry["salt"].encode("ascii"))
        correct_hash = base64.decodebytes(entry["data"].encode("ascii"))

        print("\n{}\n".format(prompt))
        while True:
            password = getpass(" > ")
            hash = hash_password(password, entry["hashing"], salt)
            if hash == correct_hash:
                break
            print("\nWrong input. Try again.\n")
    return {"steps_back": 1}


def password_manager_page(ctx: AppContext) -> RouteInfo:
    s = prompt_selection(
        ["Add Password Entry", "Open Password Training File", "Back"],
        "# TRAINING DATA MANAGER",
    )
    match s:
        case 0:
            prompt_password_entry(ctx)
        case 1:
            print("open password training file...")
        case 2:
            return {"steps_back": 1}
    return {}


def prompt_password_entry(ctx: AppContext):
    print("Enter password entry prompt.")
    prompt = input(" > ")
    print()
    while True:
        print("Enter password")
        password1 = getpass(" > ")
        print()
        print("Confirm password")
        password2 = getpass(" > ")
        print()

        if password1 == password2:
            break

        print("The two passwords you entered did not match.\n" "Try again.\n")

    entry = create_training_entry(prompt, password1, ctx)
    ctx.add_training_entry(entry)
    ctx.save_entries()
