import json
import logging
import os
from glob import glob
from typing import Optional

from deck import DeckContext, DeckInfo
from settings import Settings

DECK_FILE_SUFFIX = ".deck.json"
"""Extension or suffix for a deck file"""

l = logging.getLogger(__name__)


class AppContext:
    _settings_path: str
    _decks_dir_path: str
    _deck_infos: list[DeckInfo] = []
    _deck_context: DeckContext | None = None
    _settings: Settings = {"hashing": {"algorithm": "scrypt"}}

    def __init__(self, settings_path: str, decks_dir_path: str):
        self._settings_path = settings_path
        self._decks_dir_path = decks_dir_path

        loaded_settings = read_json_file(settings_path, {})
        l.debug("Updating `self.settings` with loaded settings: %s", loaded_settings)
        self._settings.update(loaded_settings)

        self._load_deck_infos()

    def get_current_deck_context(self) -> DeckContext | None:
        return self._deck_context

    def save_deck(self):
        """Save the currently loaded deck into :attr:`AppContext._decks_dir_path`.
        If it's a brand new deck, then a new file will be created.
        """
        data = self._deck_context.generate_encrypted_deck_data()
        path = os.path.join(
            self._decks_dir_path, self._deck_context.name + DECK_FILE_SUFFIX
        )
        is_new_deck = not os.path.isfile(path)
        l.info("Save deck `%s` to `%s`", self._deck_context.name, path)
        write_json_to_file(path, data)

        if is_new_deck:
            self._deck_infos.append({"name": self._deck_context.name, "path": path})

    def get_deck_infos(self) -> list[DeckInfo]:
        return self._deck_infos

    def is_deck_password_valid(deck_name, password) -> bool:
        pass

    def load_deck(self, deck_context: DeckContext):
        """Load deck into app context.

        Parameters
        ----------
        deck_data : DeckData
            Deck data
        password : str | None, optional
            Encryption password if encrypted, by default None
        """
        self._deck_context = deck_context
        l.info("Loaded deck `%s` into `self._deck_context`", deck_context.name)

    def load_deck_from_info(self, deck_info: DeckInfo, password: str | None = None):
        l.info("Loading deck `%s` by DeckInfo", deck_info["name"])
        deck_data = read_json_file(deck_info["path"])
        self.load_deck(DeckContext(deck_info["name"], deck_data, password))

    def get_settings(self) -> Settings:
        return self._settings

    def save_settings():
        pass

    def _load_deck_infos(self):
        """Clear and populate :attr:`AppContext._decks`"""
        self._deck_infos.clear()
        l.debug("Cleared `self._decks`")

        # Adds a trailing path separator
        glob_str = os.path.join(self._decks_dir_path, "")
        glob_str += "*" + DECK_FILE_SUFFIX

        l.info("Searching for decks using glob pattern `{}`".format(glob_str))
        for filepath in glob(glob_str):
            # Gets the filename, and then remove the extension
            deck_name = os.path.basename(filepath)[:-10]
            self._deck_infos.append({"name": deck_name, "path": filepath})
            l.info("Appended deck `{}`".format(deck_name))


class InvalidJsonFileError(Exception):
    path: str
    lineno: int
    colno: int

    def __init__(self, path: str, lineno: int, colno: int):
        super().__init__(
            "Invalid JSON at `{}` line {} column {}".format(path, lineno, colno)
        )
        self.path = path
        self.lineno = lineno
        self.colno = colno


def read_json_file(path: str, default: Optional[any] = None) -> any:
    l.info("Reading json file from {}".format(path))
    if os.stat(path).st_size == 0:
        l.info("JSON file is empty, returning default object")
        return default
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError as e:
        raise InvalidJsonFileError(path, e.lineno, e.colno)
    return data


def write_json_to_file(path: str, data: any):
    l.info("Writing json into file at {}".format(path))
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    return data
